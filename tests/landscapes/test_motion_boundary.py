from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from pygrc.landscapes import (
    BOUNDARY_MOTION_CLASSIFIER_ID,
    BoundaryMotionInferenceResult,
    infer_boundary_motion,
    infer_boundary_motion_report,
)
from pygrc.telemetry.io import build_telemetry_artifact_layout, save_telemetry_artifact_pack
from pygrc.telemetry.schema import (
    GraphCheckpointArtifact,
    GraphCheckpointIndex,
    GraphCheckpointReference,
    RunTelemetryIdentity,
    RunTelemetrySummary,
    StepTelemetryRow,
)


def _identity(family: str = "grc9v3") -> RunTelemetryIdentity:
    return RunTelemetryIdentity(
        run_id=f"{family}_boundary_motion_run",
        model_family=family,
        params_identity="params",
        seed_name="boundary_motion_seed",
        requested_steps=2,
    )


def _summary(identity: RunTelemetryIdentity, family: str) -> RunTelemetrySummary:
    return RunTelemetrySummary(
        identity=identity,
        completed_steps=2,
        final_step_index=1,
        initial_time=0.0,
        final_time=1.0,
        total_event_count=0,
        event_counts_by_kind={},
        initial_observables={},
        final_observables={},
        resolved_params={},
        raw_params={},
        parameter_overrides={},
        status="completed",
        family_extensions={family: {"contract_version": "test"}},
    )


def _steps(identity: RunTelemetryIdentity, family: str) -> tuple[StepTelemetryRow, ...]:
    return (
        StepTelemetryRow(
            identity=identity,
            step_index=0,
            time=0.0,
            event_count=0,
            event_counts_by_kind={},
            observables={"global_gradient_norm_max": 2.0},
            family_extensions={family: {"global_only": True}},
        ),
        StepTelemetryRow(
            identity=identity,
            step_index=1,
            time=1.0,
            event_count=0,
            event_counts_by_kind={},
            observables={"global_gradient_norm_max": 2.0},
            family_extensions={family: {"global_only": True}},
        ),
    )


def _checkpoint(
    identity: RunTelemetryIdentity,
    family: str,
    *,
    checkpoint_id: str,
    step_index: int,
    nodes: tuple[dict[str, object], ...],
    time: float | None = None,
    edges: tuple[dict[str, object], ...] = (),
) -> GraphCheckpointArtifact:
    return GraphCheckpointArtifact(
        identity=identity,
        checkpoint_id=checkpoint_id,
        step_index=step_index,
        time=float(step_index) if time is None else time,
        checkpoint_label=f"step_{step_index}",
        checkpoint_reason="boundary_motion_test",
        graph_kind="weighted_graph",
        node_count=len(nodes),
        edge_count=len(edges),
        node_records=nodes,
        edge_records=edges,
        family_extensions={family: {"contract_version": "test"}},
    )


def _checkpoint_index(
    identity: RunTelemetryIdentity,
    checkpoints: tuple[GraphCheckpointArtifact, ...],
) -> GraphCheckpointIndex:
    return GraphCheckpointIndex(
        identity=identity,
        selection_policy="boundary_motion_test",
        selection_params={},
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
    checkpoints: tuple[GraphCheckpointArtifact, ...],
    *,
    family: str = "grc9v3",
) -> Path:
    identity = checkpoints[0].identity
    layout = build_telemetry_artifact_layout(identity.run_id, root_dir=root)
    save_telemetry_artifact_pack(
        layout,
        step_rows=_steps(identity, family),
        event_rows=(),
        run_summary=_summary(identity, family),
        graph_checkpoint_index=_checkpoint_index(identity, checkpoints),
        graph_checkpoints=checkpoints,
    )
    return layout.run_dir


class BoundaryMotionObserverTest(unittest.TestCase):
    def test_boundary_advance_emits_boundary_motion(self) -> None:
        identity = _identity()
        checkpoints = (
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0000",
                step_index=0,
                nodes=({"node_id": 1, "coherence": 2.0},),
            ),
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0001",
                step_index=1,
                nodes=({"node_id": 1, "coherence": 1.0, "gradient_norm": 2.0},),
            ),
        )
        with tempfile.TemporaryDirectory() as tmp:
            result = infer_boundary_motion(_write_pack(Path(tmp), checkpoints))

        self.assertIsInstance(result, BoundaryMotionInferenceResult)
        self.assertEqual(1, len(result.records))
        record = result.records[0]
        self.assertEqual(BOUNDARY_MOTION_CLASSIFIER_ID, record.classifier_id)
        self.assertEqual("boundary", record.motion_kind)
        self.assertEqual("emerged", record.relationship)
        self.assertEqual("boundary_advance", result.deltas[0].motion_event)
        self.assertEqual(0.5, result.deltas[0].normal_velocity)

    def test_frontier_port_loss_emits_port_front_recession(self) -> None:
        identity = _identity()
        checkpoints = (
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0000",
                step_index=0,
                nodes=({"node_id": 1, "occupied_ports": [1, 2, 3]},),
            ),
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0001",
                step_index=1,
                nodes=({"node_id": 1, "occupied_ports": [1, 2]},),
            ),
        )
        with tempfile.TemporaryDirectory() as tmp:
            result = infer_boundary_motion(_write_pack(Path(tmp), checkpoints))

        self.assertEqual(1, len(result.records))
        self.assertEqual("frontier_recession", result.deltas[0].motion_event)
        self.assertEqual("port_frontier", result.deltas[0].boundary_kind)
        self.assertIn("motion_boundary.port_frontier", result.records[0].evidence.telemetry_fields)

    def test_frontier_port_gain_emits_port_front_advance(self) -> None:
        identity = _identity()
        checkpoints = (
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0000",
                step_index=0,
                nodes=({"node_id": 1, "occupied_ports": [1, 2]},),
            ),
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0001",
                step_index=1,
                nodes=({"node_id": 1, "occupied_ports": [1, 2, 3]},),
            ),
        )
        with tempfile.TemporaryDirectory() as tmp:
            result = infer_boundary_motion(_write_pack(Path(tmp), checkpoints))

        self.assertEqual(1, len(result.records))
        self.assertEqual("frontier_advance", result.deltas[0].motion_event)
        self.assertEqual("port_frontier", result.deltas[0].boundary_kind)

    def test_boundary_normal_velocity_uses_checkpoint_time_when_available(self) -> None:
        identity = _identity()
        checkpoints = (
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0000",
                step_index=0,
                time=0.0,
                nodes=({"node_id": 1, "coherence": 2.0, "gradient_norm": 2.0},),
            ),
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0001",
                step_index=1,
                time=4.0,
                nodes=({"node_id": 1, "coherence": 1.0, "gradient_norm": 2.0},),
            ),
        )
        with tempfile.TemporaryDirectory() as tmp:
            result = infer_boundary_motion(_write_pack(Path(tmp), checkpoints))

        self.assertEqual("boundary_advance", result.deltas[0].motion_event)
        self.assertEqual(0.125, result.deltas[0].normal_velocity)

    def test_basin_membership_change_emits_boundary_shift(self) -> None:
        identity = _identity()
        checkpoints = (
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0000",
                step_index=0,
                nodes=({"node_id": 1, "gradient_norm": 2.0, "basin_id": "basin_a"},),
            ),
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0001",
                step_index=1,
                nodes=({"node_id": 1, "gradient_norm": 2.0, "basin_id": "basin_b"},),
            ),
        )
        with tempfile.TemporaryDirectory() as tmp:
            result = infer_boundary_motion(_write_pack(Path(tmp), checkpoints))

        self.assertEqual(1, len(result.records))
        self.assertEqual("boundary_membership_shift", result.deltas[0].motion_event)
        self.assertEqual("drifted", result.records[0].relationship)
        self.assertIn("basin_membership_changed", result.records[0].evidence.degradation_reasons)

    def test_global_step_aggregates_do_not_produce_per_node_boundary_claims(self) -> None:
        identity = _identity()
        checkpoints = (
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0000",
                step_index=0,
                nodes=({"node_id": 1, "coherence": 1.0},),
            ),
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0001",
                step_index=1,
                nodes=({"node_id": 1, "coherence": 1.0},),
            ),
        )
        with tempfile.TemporaryDirectory() as tmp:
            result = infer_boundary_motion(_write_pack(Path(tmp), checkpoints))

        self.assertEqual((), result.records)
        self.assertEqual((), result.observations)

    def test_bridge_edges_are_flagged_on_boundary_records(self) -> None:
        identity = _identity()
        edge = {
            "edge_id": 10,
            "source_node_id": 1,
            "target_node_id": 2,
            "grcl9_edge_kind": "bridge",
        }
        checkpoints = (
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0000",
                step_index=0,
                nodes=({"node_id": 1, "gradient_norm": 2.0}, {"node_id": 2}),
                edges=(edge,),
            ),
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0001",
                step_index=1,
                nodes=({"node_id": 1, "gradient_norm": 2.0}, {"node_id": 2}),
                edges=(edge,),
            ),
        )
        with tempfile.TemporaryDirectory() as tmp:
            result = infer_boundary_motion(_write_pack(Path(tmp), checkpoints))

        self.assertEqual("boundary_stabilization", result.deltas[0].motion_event)
        self.assertIn("incident_bridge_edge_flagged", result.records[0].evidence.degradation_reasons)
        self.assertEqual((10,), result.records[0].evidence.edge_ids)

    def test_single_checkpoint_static_ridge_does_not_promote_to_motion(self) -> None:
        identity = _identity()
        checkpoints = (
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0000",
                step_index=0,
                nodes=({"node_id": 1, "gradient_norm": 2.0},),
            ),
        )
        with tempfile.TemporaryDirectory() as tmp:
            result = infer_boundary_motion(_write_pack(Path(tmp), checkpoints))

        self.assertEqual(1, len(result.observations))
        self.assertEqual((), result.records)
        self.assertEqual((), result.deltas)

    def test_pressure_boundary_label_alone_is_not_geometric_ridge_claim(self) -> None:
        identity = _identity()
        checkpoints = (
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0000",
                step_index=0,
                nodes=({"node_id": 1, "payload": {"front_capacity_source": "pressure_boundary"}},),
            ),
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0001",
                step_index=1,
                nodes=({"node_id": 1, "payload": {"front_capacity_source": "pressure_boundary"}},),
            ),
        )
        with tempfile.TemporaryDirectory() as tmp:
            result = infer_boundary_motion(_write_pack(Path(tmp), checkpoints))

        self.assertEqual((), result.records)
        self.assertEqual((), result.observations)

    def test_report_serializes_boundary_records(self) -> None:
        identity = _identity()
        checkpoints = (
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0000",
                step_index=0,
                nodes=({"node_id": 1, "coherence": 2.0},),
            ),
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0001",
                step_index=1,
                nodes=({"node_id": 1, "coherence": 1.0, "gradient_norm": 2.0},),
            ),
        )
        with tempfile.TemporaryDirectory() as tmp:
            report = infer_boundary_motion_report(_write_pack(Path(tmp), checkpoints))

        payload = report.to_mapping()
        self.assertEqual(1, len(payload["records"]))
        self.assertEqual("boundary", payload["records"][0]["motion_kind"])


if __name__ == "__main__":
    unittest.main()

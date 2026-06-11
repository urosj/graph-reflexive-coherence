from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from pygrc.landscapes import (
    REPRESENTATIVE_MOTION_CLASSIFIER_ID,
    RepresentativeMotionInferenceResult,
    infer_representative_motion,
    infer_representative_motion_report,
    load_motion_window,
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
        run_id=f"{family}_representative_motion_run",
        model_family=family,
        params_identity="params",
        seed_name="representative_motion_seed",
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
            observables={},
            family_extensions={family: {}},
        ),
        StepTelemetryRow(
            identity=identity,
            step_index=1,
            time=1.0,
            event_count=0,
            event_counts_by_kind={},
            observables={},
            family_extensions={family: {}},
        ),
    )


def _checkpoint(
    identity: RunTelemetryIdentity,
    family: str,
    *,
    checkpoint_id: str,
    step_index: int,
    nodes: tuple[dict[str, object], ...],
    edges: tuple[dict[str, object], ...] = (),
) -> GraphCheckpointArtifact:
    return GraphCheckpointArtifact(
        identity=identity,
        checkpoint_id=checkpoint_id,
        step_index=step_index,
        time=float(step_index),
        checkpoint_label=f"step_{step_index}",
        checkpoint_reason="representative_motion_test",
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
        selection_policy="representative_motion_test",
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


def _stable_sink_checkpoints(family: str = "grc9v3") -> tuple[GraphCheckpointArtifact, ...]:
    identity = _identity(family)
    nodes = (
        {"node_id": 1, "coherence": 3.0, "basin_id": "basin_a", "is_sink": True},
        {"node_id": 2, "coherence": 1.0, "basin_id": "basin_a"},
    )
    return (
        _checkpoint(identity, family, checkpoint_id="checkpoint_0000", step_index=0, nodes=nodes),
        _checkpoint(identity, family, checkpoint_id="checkpoint_0001", step_index=1, nodes=nodes),
    )


class RepresentativeMotionObserverTest(unittest.TestCase):
    def test_stable_sink_representative_records_stationary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = infer_representative_motion(
                _write_pack(Path(tmp), _stable_sink_checkpoints())
            )

        self.assertIsInstance(result, RepresentativeMotionInferenceResult)
        self.assertEqual(1, len(result.records))
        record = result.records[0]
        self.assertEqual(REPRESENTATIVE_MOTION_CLASSIFIER_ID, record.classifier_id)
        self.assertEqual("representative", record.motion_kind)
        self.assertEqual("stationary", record.relationship)
        self.assertEqual((1,), record.old_carriers.node_ids)
        self.assertEqual((1,), record.new_carriers.node_ids)
        self.assertIn("no_identity_motion_claim", record.non_claims)
        self.assertIn("representative_change_not_identity_walking", record.non_claims)
        self.assertEqual("sink", result.selections[0].selection_mode)

    def test_representative_switch_records_drifted_not_walked(self) -> None:
        identity = _identity()
        checkpoints = (
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0000",
                step_index=0,
                nodes=(
                    {
                        "node_id": 1,
                        "coherence": 3.0,
                        "basin_id": "basin_a",
                        "payload": {"coordinates": [0.0, 0.0]},
                    },
                    {
                        "node_id": 2,
                        "coherence": 1.0,
                        "basin_id": "basin_a",
                        "payload": {"coordinates": [2.0, 0.0]},
                    },
                ),
            ),
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0001",
                step_index=1,
                nodes=(
                    {
                        "node_id": 1,
                        "coherence": 1.0,
                        "basin_id": "basin_a",
                        "payload": {"coordinates": [0.0, 0.0]},
                    },
                    {
                        "node_id": 2,
                        "coherence": 3.0,
                        "basin_id": "basin_a",
                        "payload": {"coordinates": [2.0, 0.0]},
                    },
                ),
            ),
        )
        with tempfile.TemporaryDirectory() as tmp:
            result = infer_representative_motion(_write_pack(Path(tmp), checkpoints))

        self.assertEqual(1, len(result.records))
        record = result.records[0]
        self.assertEqual("drifted", record.relationship)
        self.assertNotEqual("walked", record.relationship)
        self.assertEqual((1,), record.old_carriers.node_ids)
        self.assertEqual((2,), record.new_carriers.node_ids)
        self.assertIn("representative_change_not_identity_walking", record.non_claims)
        self.assertEqual(
            ("centroid_nearest_node", "centroid_nearest_node"),
            tuple(selection.selection_mode for selection in result.selections),
        )

    def test_missing_coordinates_falls_back_to_graph_medoid_proxy(self) -> None:
        identity = _identity()
        checkpoints = (
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0000",
                step_index=0,
                nodes=(
                    {"node_id": 1, "basin_id": "basin_a"},
                    {"node_id": 2, "basin_id": "basin_a"},
                    {"node_id": 3, "basin_id": "basin_a"},
                ),
                edges=(
                    {"edge_id": 10, "source_node_id": 1, "target_node_id": 2},
                    {"edge_id": 11, "source_node_id": 2, "target_node_id": 3},
                ),
            ),
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0001",
                step_index=1,
                nodes=(
                    {"node_id": 1, "basin_id": "basin_a"},
                    {"node_id": 2, "basin_id": "basin_a"},
                    {"node_id": 3, "basin_id": "basin_a"},
                ),
                edges=(
                    {"edge_id": 10, "source_node_id": 1, "target_node_id": 2},
                    {"edge_id": 11, "source_node_id": 2, "target_node_id": 3},
                ),
            ),
        )
        with tempfile.TemporaryDirectory() as tmp:
            result = infer_representative_motion(_write_pack(Path(tmp), checkpoints))

        self.assertEqual(1, len(result.records))
        self.assertEqual((2,), result.records[0].old_carriers.node_ids)
        self.assertEqual("graph_medoid_proxy", result.selections[0].selection_mode)
        self.assertIn("coordinate_surface_unavailable", result.records[0].evidence.degradation_reasons)
        self.assertEqual("partial", result.records[0].evidence_quality)

    def test_port_front_candidate_is_used_before_medoid_for_grc9v3(self) -> None:
        identity = _identity()
        checkpoints = (
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0000",
                step_index=0,
                nodes=(
                    {"node_id": 1, "basin_id": "basin_a"},
                    {"node_id": 2, "basin_id": "basin_a", "occupied_ports": [1, 2]},
                    {"node_id": 3, "basin_id": "basin_a"},
                ),
            ),
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0001",
                step_index=1,
                nodes=(
                    {"node_id": 1, "basin_id": "basin_a"},
                    {"node_id": 2, "basin_id": "basin_a", "occupied_ports": [1, 2]},
                    {"node_id": 3, "basin_id": "basin_a"},
                ),
            ),
        )
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = _write_pack(Path(tmp), checkpoints)
            loaded = load_motion_window(run_dir, allow_short_persistence_window=True)
            result = infer_representative_motion(loaded)

        self.assertTrue(loaded.checkpoint_evidence[0].port_matrix_available)
        self.assertTrue(loaded.checkpoint_evidence[0].nodes[2].port_matrix_available)
        self.assertIn(
            "port_front_candidate",
            loaded.checkpoint_evidence[0].nodes[2].representative_modes,
        )
        self.assertEqual("port_front_candidate", result.selections[0].selection_mode)
        self.assertIn("port_front_candidate", result.selections[0].candidate_modes)
        self.assertEqual((2,), result.records[0].old_carriers.node_ids)

    def test_diagnostic_window_caps_confidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = infer_representative_motion(
                _write_pack(Path(tmp), _stable_sink_checkpoints()),
                allow_short_persistence_window=False,
            )

        self.assertEqual("diagnostic_only", result.records[0].evidence_quality)
        self.assertEqual(0.25, result.records[0].confidence)

    def test_report_serializes_representative_records(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = infer_representative_motion_report(
                _write_pack(Path(tmp), _stable_sink_checkpoints())
            )

        payload = report.to_mapping()
        self.assertEqual(1, len(payload["records"]))
        self.assertEqual("representative", payload["records"][0]["motion_kind"])


if __name__ == "__main__":
    unittest.main()

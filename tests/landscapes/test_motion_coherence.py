from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from pygrc.landscapes import (
    COHERENCE_MOTION_CLASSIFIER_ID,
    CoherenceMotionInferenceResult,
    infer_coherence_motion,
    infer_coherence_motion_report,
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
        run_id=f"{family}_coherence_motion_run",
        model_family=family,
        params_identity="params",
        seed_name="coherence_motion_seed",
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
    edges: tuple[dict[str, object], ...],
    budget_target: float = 4.0,
) -> GraphCheckpointArtifact:
    return GraphCheckpointArtifact(
        identity=identity,
        checkpoint_id=checkpoint_id,
        step_index=step_index,
        time=float(step_index),
        checkpoint_label=f"step_{step_index}",
        checkpoint_reason="coherence_motion_test",
        graph_kind="weighted_graph",
        node_count=len(nodes),
        edge_count=len(edges),
        node_records=nodes,
        edge_records=edges,
        family_extensions={family: {"budget_target": budget_target}},
    )


def _checkpoint_index(
    identity: RunTelemetryIdentity,
    checkpoints: tuple[GraphCheckpointArtifact, ...],
) -> GraphCheckpointIndex:
    return GraphCheckpointIndex(
        identity=identity,
        selection_policy="coherence_motion_test",
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


def _write_transfer_pack(
    root: Path,
    *,
    family: str = "grc9v3",
    signed_flux: float = 0.75,
    budget_target: float = 4.0,
    indirect: bool = False,
) -> Path:
    identity = _identity(family)
    if indirect:
        edges = (
            {"edge_id": 10, "source_node_id": 1, "target_node_id": 3, "signed_flux": 0.4},
            {"edge_id": 11, "source_node_id": 3, "target_node_id": 2, "signed_flux": 0.4},
        )
    else:
        edges = (
            {"edge_id": 10, "source_node_id": 1, "target_node_id": 2, "signed_flux": signed_flux},
        )
    checkpoints = (
        _checkpoint(
            identity,
            family,
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
                    "payload": {"coordinates": [1.0, 0.0]},
                },
                {
                    "node_id": 3,
                    "coherence": 0.0,
                    "basin_id": "basin_a",
                    "payload": {"coordinates": [0.5, 0.0]},
                },
            ),
            edges=edges,
            budget_target=budget_target,
        ),
        _checkpoint(
            identity,
            family,
            checkpoint_id="checkpoint_0001",
            step_index=1,
            nodes=(
                {
                    "node_id": 1,
                    "coherence": 2.0,
                    "basin_id": "basin_a",
                    "payload": {"coordinates": [0.0, 0.0], "continuity_delta": -1.0},
                },
                {
                    "node_id": 2,
                    "coherence": 2.0,
                    "basin_id": "basin_a",
                    "payload": {"coordinates": [1.0, 0.0], "continuity_delta": 1.0},
                },
                {
                    "node_id": 3,
                    "coherence": 0.0,
                    "basin_id": "basin_a",
                    "payload": {"coordinates": [0.5, 0.0], "continuity_delta": 0.0},
                },
            ),
            edges=edges,
            budget_target=budget_target,
        ),
    )
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


class CoherenceMotionObserverTest(unittest.TestCase):
    def test_direct_flux_transfer_produces_coherence_motion_record(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = infer_coherence_motion(_write_transfer_pack(Path(tmp)))

        self.assertIsInstance(result, CoherenceMotionInferenceResult)
        self.assertEqual("conserved_zero", result.budget_accountability)
        self.assertEqual("unit_measure_assumed", result.quadrature_mode)
        self.assertEqual(1, len(result.records))
        record = result.records[0]
        self.assertEqual(COHERENCE_MOTION_CLASSIFIER_ID, record.classifier_id)
        self.assertEqual("coherence", record.motion_kind)
        self.assertEqual("drifted", record.relationship)
        self.assertEqual((1,), record.old_carriers.node_ids)
        self.assertEqual((2,), record.new_carriers.node_ids)
        self.assertEqual((10,), record.evidence.edge_ids)
        self.assertEqual(1.0, record.transferred_mass)
        self.assertIn("no_identity_motion_claim", record.non_claims)

    def test_zero_flux_control_does_not_produce_false_positive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = infer_coherence_motion(_write_transfer_pack(Path(tmp), signed_flux=0.0))

        self.assertEqual(0, len(result.records))

    def test_indirect_flux_transfer_is_ambiguous(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = infer_coherence_motion(_write_transfer_pack(Path(tmp), indirect=True))

        self.assertEqual(1, len(result.records))
        record = result.records[0]
        self.assertEqual("ambiguous", record.relationship)
        self.assertEqual("partial", record.evidence_quality)
        self.assertEqual((10, 11), record.evidence.edge_ids)
        self.assertIn("multi_edge_or_indirect_transfer", record.evidence.degradation_reasons)

    def test_budget_leak_degrades_confidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = infer_coherence_motion(_write_transfer_pack(Path(tmp), budget_target=10.0))

        self.assertEqual("leak_error", result.budget_accountability)
        self.assertEqual(1, len(result.records))
        record = result.records[0]
        self.assertEqual("degraded", record.evidence_quality)
        self.assertLess(record.confidence, 0.5)
        self.assertEqual("leak_error", record.evidence.budget_accountability)
        self.assertIn("budget_leak", record.evidence.degradation_reasons)

    def test_identity_fields_are_not_required_for_coherence_motion(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = infer_coherence_motion(_write_transfer_pack(Path(tmp), family="grc9"))

        self.assertEqual("grc9", result.records[0].source_runtime_family)
        self.assertEqual((), result.records[0].competing_claims)

    def test_basin_drift_estimate_uses_weighted_coordinates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = infer_coherence_motion(_write_transfer_pack(Path(tmp)))

        self.assertEqual(1, len(result.drift_estimates))
        estimate = result.drift_estimates[0]
        self.assertEqual("basin_a", estimate.basin_id)
        self.assertAlmostEqual(0.25, estimate.displacement[0])
        self.assertAlmostEqual(0.25, estimate.velocity[0])
        self.assertAlmostEqual(0.25, estimate.speed)

    def test_report_serializes_without_identity_claims(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = infer_coherence_motion_report(_write_transfer_pack(Path(tmp)))

        payload = report.to_mapping()
        self.assertEqual(1, len(payload["records"]))
        self.assertEqual("coherence", payload["records"][0]["motion_kind"])
        self.assertIn("no_identity_motion_claim", payload["records"][0]["non_claims"])


if __name__ == "__main__":
    unittest.main()

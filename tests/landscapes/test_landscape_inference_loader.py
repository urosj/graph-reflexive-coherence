from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from pygrc.landscapes import (
    LandscapeSeed,
    landscape_seed_from_data,
    landscape_seed_to_data,
    load_landscape_inference_artifacts,
    select_landscape_inference_window,
    validate_landscape_inference_seed_extensions,
)
from pygrc.telemetry.io import (
    build_telemetry_artifact_layout,
    load_telemetry_artifact_pack,
    save_telemetry_artifact_pack,
)
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
        run_id=f"{family}_run",
        model_family=family,
        params_identity="params",
        seed_name="seed",
        requested_steps=3,
    )


def _summary(identity: RunTelemetryIdentity, family: str) -> RunTelemetrySummary:
    return RunTelemetrySummary(
        identity=identity,
        completed_steps=3,
        final_step_index=2,
        initial_time=0.0,
        final_time=0.2,
        total_event_count=1,
        event_counts_by_kind={"event": 1},
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
            event_count=1 if index == 1 else 0,
            event_counts_by_kind={"event": 1} if index == 1 else {},
            observables={},
            family_extensions={family: {"step_marker": index}},
        )
        for index in range(3)
    )


def _events(identity: RunTelemetryIdentity, family: str) -> tuple[EventTelemetryRow, ...]:
    return (
        EventTelemetryRow(
            identity=identity,
            step_index=1,
            event_index=0,
            event_kind="event",
            source_family=family,
            payload={},
            family_extensions={family: {"event_marker": True}},
        ),
    )


def _checkpoint(identity: RunTelemetryIdentity, family: str) -> GraphCheckpointArtifact:
    return GraphCheckpointArtifact(
        identity=identity,
        checkpoint_id="checkpoint_0001",
        step_index=1,
        time=0.1,
        checkpoint_label="step_1",
        checkpoint_reason="test",
        graph_kind="weighted_graph",
        node_count=1,
        edge_count=0,
        node_records=({"node_id": 1, "coherence": 1.0},),
        edge_records=(),
        family_extensions={family: {"checkpoint_marker": True}},
    )


def _checkpoint_index(
    identity: RunTelemetryIdentity,
    family: str,
) -> GraphCheckpointIndex:
    return GraphCheckpointIndex(
        identity=identity,
        selection_policy="test",
        selection_params={"every_step": True},
        checkpoints=(
            GraphCheckpointReference(
                checkpoint_id="checkpoint_0001",
                step_index=1,
                time=0.1,
                checkpoint_label="step_1",
                path="checkpoint_0001.json",
            ),
        ),
        family_extensions={family: {"index_marker": True}},
    )


def _write_pack(root: Path, family: str, *, checkpoints: bool = False) -> Path:
    identity = _identity(family)
    layout = build_telemetry_artifact_layout(
        identity.run_id,
        root_dir=root,
    )
    save_telemetry_artifact_pack(
        layout,
        step_rows=_steps(identity, family),
        event_rows=_events(identity, family),
        run_summary=_summary(identity, family),
        graph_checkpoint_index=_checkpoint_index(identity, family) if checkpoints else None,
        graph_checkpoints=(_checkpoint(identity, family),) if checkpoints else (),
    )
    return layout.run_dir


class LandscapeInferenceLoaderTest(unittest.TestCase):
    def test_loader_detects_supported_runtime_families(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for family in ("grcv3", "grc9", "grc9v3"):
                result = load_landscape_inference_artifacts(_write_pack(root, family))
                self.assertEqual(family, result.source_runtime_family)
                self.assertIsInstance(result.inferred_seed, LandscapeSeed)
                self.assertEqual([], result.inferred_seed.primitives)
                self.assertEqual("whole_run", result.inference_window.policy)
                self.assertEqual((0, 2), (result.inference_window.start_step, result.inference_window.end_step))
                validate_landscape_inference_seed_extensions(result.inferred_seed)

    def test_minimal_inferred_seed_round_trips_through_landscape_io(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = load_landscape_inference_artifacts(_write_pack(Path(tmp), "grc9v3"))
            payload = landscape_seed_to_data(result.inferred_seed)
            restored = landscape_seed_from_data(payload)
            validate_landscape_inference_seed_extensions(restored)
            self.assertEqual("inferred_observed_landscape", restored.meta.source_kind)
            self.assertEqual([], restored.primitives)
            self.assertIn("landscape_inference", restored.extensions)

    def test_missing_checkpoint_index_produces_availability_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = load_landscape_inference_artifacts(_write_pack(Path(tmp), "grc9"))
            self.assertFalse(result.availability.graph_checkpoint_index_available)
            self.assertEqual(0, result.availability.graph_checkpoint_count)
            self.assertTrue(result.availability.step_rows_available)
            self.assertTrue(result.availability.event_rows_available)
            self.assertTrue(result.availability.run_summary_available)

    def test_loader_loads_checkpoint_index_when_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = load_landscape_inference_artifacts(
                _write_pack(Path(tmp), "grc9v3", checkpoints=True)
            )
            self.assertTrue(result.availability.graph_checkpoint_index_available)
            self.assertEqual(1, result.availability.graph_checkpoint_count)
            self.assertEqual(1, len(result.telemetry_pack.graph_checkpoints))

    def test_window_selection_modes_are_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = _write_pack(Path(tmp), "grcv3")
            pack = load_telemetry_artifact_pack(
                build_telemetry_artifact_layout("grcv3_run", root_dir=Path(tmp))
            )

            explicit = load_landscape_inference_artifacts(
                run_dir,
                window_policy="explicit",
                start_step=1,
                end_step=2,
            ).inference_window
            self.assertEqual((1, 2, "explicit"), (explicit.start_step, explicit.end_step, explicit.policy))

            final = select_landscape_inference_window(pack, policy="final", final_step_count=2)
            self.assertEqual((1, 2, "final"), (final.start_step, final.end_step, final.policy))

            event_centered = load_landscape_inference_artifacts(
                run_dir,
                window_policy="event_centered",
                event_step=1,
                radius=1,
            ).inference_window
            self.assertEqual(
                (0, 2, "event_centered"),
                (event_centered.start_step, event_centered.end_step, event_centered.policy),
            )


if __name__ == "__main__":
    unittest.main()

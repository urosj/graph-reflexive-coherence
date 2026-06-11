"""Recorder tests for runtime telemetry capture helpers."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from pygrc import telemetry
from pygrc.core import GRCEvent, StepResult


class TelemetryRecorderTest(unittest.TestCase):
    """Validate Iteration 4 runner-level telemetry capture."""

    def test_capture_run_telemetry_always_returns_in_memory_summary(self) -> None:
        result = telemetry.capture_run_telemetry(
            model_family="grcv2",
            params_identity="params123",
            seed_name="Cell-1",
            seed_source_reference="rc-sim/configs/landscapes/cell-1.json",
            seed_path="configs/landscapes/seed/cell-1.seed.yaml",
            param_family="balanced_baseline",
            rng_seed=7,
            requested_steps=2,
            initial_observables={"num_nodes": 2},
            step_results=[
                StepResult(
                    step_index=1,
                    time=0.1,
                    events=[GRCEvent(kind="spark", step_index=1, source_family="grcv2")],
                    observables={"num_nodes": 2},
                ),
                StepResult(
                    step_index=2,
                    time=0.2,
                    events=[],
                    observables={"num_nodes": 3},
                ),
            ],
            final_observables={"num_nodes": 3},
        )

        self.assertEqual(2, len(result.step_rows))
        self.assertEqual(1, len(result.event_rows))
        self.assertEqual(2, result.run_summary.completed_steps)
        self.assertIsNone(result.artifact_layout)

    def test_capture_run_telemetry_can_write_artifacts_when_enabled(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = telemetry.capture_run_telemetry(
                model_family="grcv2",
                params_identity="params123",
                seed_name="Cell-1",
                seed_source_reference="rc-sim/configs/landscapes/cell-1.json",
                seed_path="configs/landscapes/seed/cell-1.seed.yaml",
                param_family="balanced_baseline",
                rng_seed=7,
                requested_steps=1,
                initial_observables={"num_nodes": 2},
                step_results=[
                    StepResult(
                        step_index=1,
                        time=0.1,
                        events=[],
                        observables={"num_nodes": 2},
                    )
                ],
                final_observables={"num_nodes": 2},
                config=telemetry.TelemetryCaptureConfig(
                    root_dir=Path(temp_dir) / "outputs",
                    experiment_path=Path("grcv2") / "manual-smoke",
                    write_artifacts=True,
                ),
            )

            self.assertIsNotNone(result.artifact_layout)
            layout = result.artifact_layout
            assert layout is not None
            self.assertEqual(
                Path(temp_dir) / "outputs" / "grcv2" / "manual-smoke",
                layout.root_dir,
            )
            loaded_pack = telemetry.load_telemetry_artifact_pack(layout)

        self.assertEqual(result.identity.run_id, loaded_pack.layout.run_id)
        self.assertEqual(1, loaded_pack.run_summary.completed_steps)
        self.assertEqual((), loaded_pack.event_rows)

    def test_capture_run_telemetry_supports_step_event_and_summary_extensions(self) -> None:
        step_results = [
            StepResult(
                step_index=1,
                time=0.1,
                events=[
                    GRCEvent(kind="spark_candidate", step_index=1, source_family="grcv3"),
                    GRCEvent(kind="spark", step_index=1, source_family="grcv3"),
                ],
                observables={"active_basin_count": 2.0},
            ),
            StepResult(
                step_index=2,
                time=0.2,
                events=[],
                observables={"active_basin_count": 3.0},
            ),
        ]

        result = telemetry.capture_run_telemetry(
            model_family="grcv3",
            params_identity="params456",
            seed_name="phase5_reference_primary",
            seed_source_reference="implementation/Phase-5-RepresentativeRuntime.md",
            seed_path="synthetic/grcv3/phase5_reference/primary",
            param_family=None,
            rng_seed=None,
            requested_steps=2,
            initial_observables={"active_basin_count": 1.0},
            step_results=step_results,
            final_observables={"active_basin_count": 3.0},
            step_family_extensions=[
                {"grcv3": {"step_marker": "s1"}},
                {"grcv3": {"step_marker": "s2"}},
            ],
            event_family_extensions_by_step=[
                [
                    {"grcv3": {"event_marker": "candidate"}},
                    {"grcv3": {"event_marker": "confirmed"}},
                ],
                [],
            ],
            summary_family_extensions={"grcv3": {"summary_marker": "done"}},
        )

        self.assertEqual("s1", result.step_rows[0].family_extensions["grcv3"]["step_marker"])
        self.assertEqual("s2", result.step_rows[1].family_extensions["grcv3"]["step_marker"])
        self.assertEqual(
            "candidate",
            result.event_rows[0].family_extensions["grcv3"]["event_marker"],
        )
        self.assertEqual(
            "confirmed",
            result.event_rows[1].family_extensions["grcv3"]["event_marker"],
        )
        self.assertEqual(
            "done",
            result.run_summary.family_extensions["grcv3"]["summary_marker"],
        )

    def test_capture_run_telemetry_rejects_mismatched_extension_lengths(self) -> None:
        step_results = [
            StepResult(
                step_index=1,
                time=0.1,
                events=[GRCEvent(kind="spark", step_index=1, source_family="grcv3")],
                observables={"active_basin_count": 2.0},
            )
        ]

        with self.assertRaises(ValueError):
            telemetry.capture_run_telemetry(
                model_family="grcv3",
                params_identity="params456",
                seed_name="phase5_reference_primary",
                seed_source_reference="implementation/Phase-5-RepresentativeRuntime.md",
                seed_path="synthetic/grcv3/phase5_reference/primary",
                param_family=None,
                rng_seed=None,
                requested_steps=1,
                initial_observables={"active_basin_count": 1.0},
                step_results=step_results,
                final_observables={"active_basin_count": 2.0},
                step_family_extensions=[],
            )

        with self.assertRaises(ValueError):
            telemetry.capture_run_telemetry(
                model_family="grcv3",
                params_identity="params456",
                seed_name="phase5_reference_primary",
                seed_source_reference="implementation/Phase-5-RepresentativeRuntime.md",
                seed_path="synthetic/grcv3/phase5_reference/primary",
                param_family=None,
                rng_seed=None,
                requested_steps=1,
                initial_observables={"active_basin_count": 1.0},
                step_results=step_results,
                final_observables={"active_basin_count": 2.0},
                event_family_extensions_by_step=[[]],
            )


if __name__ == "__main__":
    unittest.main()

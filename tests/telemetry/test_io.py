"""I/O tests for the shared telemetry artifact layer."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from pygrc import telemetry
from pygrc.core import GRCEvent, StepResult


def _identity() -> telemetry.RunTelemetryIdentity:
    return telemetry.RunTelemetryIdentity(
        run_id="run123",
        model_family="grcv2",
        params_identity="params123",
        seed_name="Cell-4",
        seed_source_reference="rc-sim/configs/landscapes/cell-4.json",
        seed_path="configs/landscapes/seed/cell-4.seed.yaml",
        param_family="balanced_baseline",
        rng_seed=11,
        requested_steps=4,
    )


def _step_rows() -> tuple[telemetry.StepTelemetryRow, ...]:
    identity = _identity()
    first = telemetry.step_row_from_step_result(
        StepResult(
            step_index=1,
            time=0.1,
            events=[GRCEvent(kind="spark", step_index=1, payload={"node_id": 4})],
            observables={"num_nodes": 2, "average_conductance": 0.8},
            bookkeeping={"checkpoint": "step_0001"},
        ),
        identity=identity,
        family_extensions={"grcv2": {"lane": "balanced_baseline"}},
    )
    second = telemetry.step_row_from_step_result(
        StepResult(
            step_index=2,
            time=0.2,
            events=[],
            observables={"num_nodes": 2, "average_conductance": 0.7},
        ),
        identity=identity,
        family_extensions={"grcv2": {"lane": "balanced_baseline"}},
    )
    return (first, second)


def _event_rows() -> tuple[telemetry.EventTelemetryRow, ...]:
    return telemetry.event_rows_from_events(
        [
            GRCEvent(kind="spark", step_index=1, payload={"node_id": 4}, source_family="grcv2"),
            GRCEvent(kind="birth", step_index=2, payload={"edge_id": 9}, source_family="grcv2"),
        ],
        identity=_identity(),
    )


def _summary() -> telemetry.RunTelemetrySummary:
    return telemetry.run_summary_from_step_results(
        [
            StepResult(
                step_index=1,
                time=0.1,
                events=[GRCEvent(kind="spark", step_index=1, source_family="grcv2")],
                observables={"average_conductance": 0.8},
            ),
            StepResult(
                step_index=2,
                time=0.2,
                events=[],
                observables={"average_conductance": 0.7},
            ),
        ],
        identity=_identity(),
        initial_observables={"average_conductance": 0.9, "num_edges": 9},
        final_observables={"average_conductance": 0.7, "num_edges": 10},
        resolved_params={"dt": 0.1, "evolution": {"alpha": 0.5}},
        raw_params={"dt": 0.1, "evolution": {"alpha": 0.5}},
        parameter_overrides={"evolution": {"alpha": 0.6}},
        family_extensions={"grcv2": {"lane": "balanced_baseline"}},
    )


class TelemetryIoTest(unittest.TestCase):
    """Validate Iteration 3 artifact layout and I/O helpers."""

    def test_build_telemetry_artifact_layout_uses_relative_default_root(self) -> None:
        layout = telemetry.build_telemetry_artifact_layout("run123")

        self.assertEqual(Path("outputs"), layout.root_dir)
        self.assertEqual(Path("outputs/run123"), layout.run_dir)
        self.assertEqual(Path("outputs/run123/telemetry"), layout.telemetry_dir)
        self.assertEqual(
            Path("outputs/run123/telemetry/steps.jsonl"),
            layout.step_rows_path,
        )
        self.assertFalse(layout.run_dir.is_absolute())

    def test_build_telemetry_artifact_layout_supports_relative_experiment_path(self) -> None:
        layout = telemetry.build_telemetry_artifact_layout(
            "run123",
            experiment_path=Path("grcv2") / "cell-1",
        )

        self.assertEqual(Path("outputs/grcv2/cell-1"), layout.root_dir)
        self.assertEqual(Path("outputs/grcv2/cell-1/run123"), layout.run_dir)
        self.assertEqual(
            Path("outputs/grcv2/cell-1/run123/telemetry"),
            layout.telemetry_dir,
        )

    def test_build_telemetry_artifact_layout_rejects_parent_traversal(self) -> None:
        with self.assertRaises(telemetry.TelemetryArtifactError):
            telemetry.build_telemetry_artifact_layout(
                "run123",
                experiment_path=Path("grcv2") / ".." / "escape",
            )

    def test_build_telemetry_artifact_layout_rejects_empty_or_whitespace_experiment_path(self) -> None:
        with self.assertRaises(telemetry.TelemetryArtifactError):
            telemetry.build_telemetry_artifact_layout("run123", experiment_path="")
        with self.assertRaises(telemetry.TelemetryArtifactError):
            telemetry.build_telemetry_artifact_layout("run123", experiment_path="   ")
        with self.assertRaises(telemetry.TelemetryArtifactError):
            telemetry.build_telemetry_artifact_layout("run123", experiment_path=Path("."))

    def test_step_event_and_summary_roundtrip_through_disk(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir) / "outputs"
            layout = telemetry.build_telemetry_artifact_layout("run123", root_dir=root_dir)

            telemetry.save_step_rows(layout.step_rows_path, _step_rows())
            telemetry.save_event_rows(layout.event_rows_path, _event_rows())
            telemetry.save_run_summary(layout.run_summary_path, _summary())

            loaded_steps = telemetry.load_step_rows(layout.step_rows_path)
            loaded_events = telemetry.load_event_rows(layout.event_rows_path)
            loaded_summary = telemetry.load_run_summary(layout.run_summary_path)

        self.assertEqual(2, len(loaded_steps))
        self.assertEqual(2, len(loaded_events))
        self.assertEqual(2, loaded_summary.completed_steps)
        self.assertEqual(0.0, loaded_summary.initial_time)
        self.assertEqual(0.2, loaded_summary.final_time)
        self.assertEqual(0.1, loaded_summary.resolved_params["dt"])
        self.assertEqual(0.6, loaded_summary.parameter_overrides["evolution"]["alpha"])
        self.assertEqual("balanced_baseline", loaded_steps[0].family_extensions["grcv2"]["lane"])

    def test_run_artifact_pack_roundtrip_is_loadable_without_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir) / "outputs"
            layout = telemetry.build_telemetry_artifact_layout("run123", root_dir=root_dir)
            comparison = telemetry.TelemetryComparisonReport(
                family="grcv2",
                common={"run_ids": ["run123", "run124"], "metric": "average_conductance"},
                extensions={"grcv2": {"lane": "balanced_baseline"}},
            )
            experiment = telemetry.TelemetryExperimentReport(
                family="grcv2",
                common={"report_name": "cell4_baseline", "run_id": "run123"},
            )

            telemetry.save_telemetry_artifact_pack(
                layout,
                step_rows=_step_rows(),
                event_rows=_event_rows(),
                run_summary=_summary(),
            )
            telemetry.save_comparison_report(layout.comparison_report_path, comparison)
            telemetry.save_experiment_report(layout.experiment_report_path, experiment)
            loaded_pack = telemetry.load_telemetry_artifact_pack(layout)

        self.assertEqual("run123", loaded_pack.layout.run_id)
        self.assertEqual(2, len(loaded_pack.step_rows))
        self.assertEqual(2, len(loaded_pack.event_rows))
        self.assertEqual("Cell-4", loaded_pack.run_summary.identity.seed_name)
        assert loaded_pack.experiment_report is not None
        assert loaded_pack.comparison_report is not None
        self.assertEqual("run123", loaded_pack.experiment_report.common["run_id"])
        self.assertEqual("comparison_report", loaded_pack.comparison_report.kind)

    def test_run_artifact_pack_loads_missing_reports_as_none(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir) / "outputs"
            layout = telemetry.build_telemetry_artifact_layout("run123", root_dir=root_dir)

            telemetry.save_telemetry_artifact_pack(
                layout,
                step_rows=_step_rows(),
                event_rows=(),
                run_summary=_summary(),
            )
            loaded_pack = telemetry.load_telemetry_artifact_pack(layout)

        self.assertIsNone(loaded_pack.experiment_report)
        self.assertIsNone(loaded_pack.comparison_report)

    def test_comparison_and_experiment_reports_roundtrip(self) -> None:
        comparison = telemetry.TelemetryComparisonReport(
            family="grcv2",
            common={"run_ids": ["run123", "run124"], "metric": "average_conductance"},
            extensions={"grcv2": {"lane": "balanced_baseline"}},
        )
        experiment = telemetry.TelemetryExperimentReport(
            family="grcv2",
            common={"report_name": "cell4_baseline", "run_id": "run123"},
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            comparison_path = Path(temp_dir) / telemetry.COMPARISON_REPORT_FILENAME
            experiment_path = Path(temp_dir) / telemetry.EXPERIMENT_REPORT_FILENAME

            telemetry.save_comparison_report(comparison_path, comparison)
            telemetry.save_experiment_report(experiment_path, experiment)

            loaded_comparison = telemetry.load_comparison_report(comparison_path)
            loaded_experiment = telemetry.load_experiment_report(experiment_path)

        self.assertEqual("comparison_report", loaded_comparison.kind)
        self.assertEqual("experiment_report", loaded_experiment.kind)
        self.assertEqual("balanced_baseline", loaded_comparison.extensions["grcv2"]["lane"])

    def test_invalid_json_report_is_rejected_strictly(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = Path(temp_dir) / telemetry.RUN_SUMMARY_FILENAME
            report_path.write_text("{not valid json", encoding="utf-8")

            with self.assertRaises(telemetry.TelemetryArtifactError):
                telemetry.load_run_summary(report_path)

    def test_missing_step_observables_is_rejected_strictly(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            step_rows_path = Path(temp_dir) / telemetry.STEP_ROWS_FILENAME
            step_rows_path.write_text(
                (
                    '{"identity":{"run_id":"run123","model_family":"grcv2","params_identity":"params123"},'
                    '"step_index":1,"time":0.1,"event_count":0,"event_counts_by_kind":{},'
                    '"bookkeeping":{},"family_extensions":{}}\n'
                ),
                encoding="utf-8",
            )

            with self.assertRaises(telemetry.TelemetryArtifactError):
                telemetry.load_step_rows(step_rows_path)


if __name__ == "__main__":
    unittest.main()

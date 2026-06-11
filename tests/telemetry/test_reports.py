"""Post-processing and report tests for telemetry-backed experiment helpers."""

from __future__ import annotations

from pathlib import Path
import unittest

from pygrc import telemetry
from pygrc.core import GRCEvent, StepResult


def _identity(run_id: str) -> telemetry.RunTelemetryIdentity:
    return telemetry.RunTelemetryIdentity(
        run_id=run_id,
        model_family="grcv2",
        params_identity="params123",
        seed_name="Cell-4",
        seed_source_reference="rc-sim/configs/landscapes/cell-4.json",
        seed_path="configs/landscapes/seed/cell-4.seed.yaml",
        param_family="balanced_baseline",
        rng_seed=11,
        requested_steps=3,
    )


def _step_rows(run_id: str) -> tuple[telemetry.StepTelemetryRow, ...]:
    identity = _identity(run_id)
    return (
        telemetry.step_row_from_step_result(
            StepResult(
                step_index=1,
                time=0.1,
                events=[GRCEvent(kind="spark", step_index=1, source_family="grcv2")],
                observables={"average_conductance": 0.8, "num_nodes": 2},
            ),
            identity=identity,
            family_extensions={"grcv2": {"lane": "balanced_baseline"}},
        ),
        telemetry.step_row_from_step_result(
            StepResult(
                step_index=2,
                time=0.2,
                events=[GRCEvent(kind="birth", step_index=2, source_family="grcv2")],
                observables={"average_conductance": 0.6, "num_nodes": 3},
            ),
            identity=identity,
            family_extensions={"grcv2": {"lane": "balanced_baseline"}},
        ),
    )


def _summary(run_id: str, *, final_edges: int = 11) -> telemetry.RunTelemetrySummary:
    return telemetry.run_summary_from_step_results(
        [
            StepResult(
                step_index=1,
                time=0.1,
                events=[GRCEvent(kind="spark", step_index=1, source_family="grcv2")],
                observables={"average_conductance": 0.8, "num_edges": 9},
            ),
            StepResult(
                step_index=2,
                time=0.2,
                events=[GRCEvent(kind="birth", step_index=2, source_family="grcv2")],
                observables={"average_conductance": 0.6, "num_edges": final_edges},
            ),
        ],
        identity=_identity(run_id),
        initial_observables={"average_conductance": 0.9, "num_edges": 9},
        final_observables={"average_conductance": 0.6, "num_edges": final_edges},
        resolved_params={"dt": 0.1, "evolution": {"alpha": 0.5}},
        raw_params={"dt": 0.1, "evolution": {"alpha": 0.5}},
        parameter_overrides={"evolution": {"alpha": 0.55}},
        family_extensions={"grcv2": {"lane": "balanced_baseline"}},
    )


class TelemetryReportsTest(unittest.TestCase):
    """Validate Iteration 5 post-processing and report helpers."""

    def test_build_artifact_references_preserves_relative_experiment_grouping(self) -> None:
        layout = telemetry.build_telemetry_artifact_layout(
            "run123",
            experiment_path=Path("grcv2") / "cell-4",
        )

        refs = telemetry.build_artifact_references(layout)

        self.assertEqual("run123", refs["run_id"])
        self.assertEqual("outputs/grcv2/cell-4/run123", refs["run_dir"])
        self.assertEqual(
            "outputs/grcv2/cell-4/run123/telemetry",
            refs["telemetry_dir"],
        )
        self.assertEqual(
            "outputs/grcv2/cell-4/run123/telemetry/steps.jsonl",
            refs["step_rows"],
        )

    def test_build_artifact_references_do_not_leak_absolute_root(self) -> None:
        layout = telemetry.build_telemetry_artifact_layout(
            "run123",
            root_dir=Path("/tmp/absolute-root"),
        )

        refs = telemetry.build_artifact_references(layout)

        self.assertEqual("run123", refs["run_id"])
        self.assertEqual("run123", refs["run_dir"])
        self.assertEqual("run123/telemetry", refs["telemetry_dir"])
        self.assertEqual("run123/telemetry/steps.jsonl", refs["step_rows"])
        self.assertNotIn("/tmp/absolute-root", str(refs))

    def test_summarize_numeric_observable_trajectory_computes_ranges_and_delta(self) -> None:
        summary = telemetry.summarize_numeric_observable_trajectory(
            _step_rows("run123"),
            initial_observables={"average_conductance": 0.9, "num_nodes": 2},
            final_observables={"average_conductance": 0.6, "num_nodes": 3},
        )

        self.assertEqual(0.9, summary["average_conductance"]["initial"])
        self.assertEqual(0.6, summary["average_conductance"]["final"])
        self.assertEqual(0.6, summary["average_conductance"]["minimum"])
        self.assertAlmostEqual(-0.3, summary["average_conductance"]["delta"])
        self.assertEqual(1.0, summary["num_nodes"]["delta"])

    def test_build_run_experiment_report_cites_artifact_identity_and_summary_metrics(self) -> None:
        layout = telemetry.build_telemetry_artifact_layout("run123")
        report = telemetry.build_run_experiment_report(
            _summary("run123"),
            step_rows=_step_rows("run123"),
            artifact_layout=layout,
        )

        self.assertEqual("experiment_report", report.kind)
        self.assertEqual("trajectory_summary_v1", report.common["report_type"])
        self.assertEqual("run123", report.common["run_id"])
        self.assertEqual(0.1, report.common["resolved_params"]["dt"])
        self.assertEqual(0.55, report.common["parameter_overrides"]["evolution"]["alpha"])
        self.assertEqual(
            "outputs/run123/telemetry/steps.jsonl",
            report.common["source_artifacts"]["step_rows"],
        )
        self.assertEqual(
            ("average_conductance", "num_edges"),
            report.common["changed_observables"],
        )
        self.assertAlmostEqual(
            -0.3,
            report.common["numeric_observable_trajectory"]["average_conductance"]["delta"],
        )

    def test_compare_run_summaries_builds_stable_pairwise_payload(self) -> None:
        left = _summary("run123", final_edges=10)
        right = _summary("run124", final_edges=12)
        comparison = telemetry.compare_run_summaries(
            left,
            right,
            left_artifact_layout=telemetry.build_telemetry_artifact_layout("run123"),
            right_artifact_layout=telemetry.build_telemetry_artifact_layout("run124"),
        )

        self.assertEqual("comparison_report", comparison.kind)
        self.assertEqual("run_summary_comparison_v1", comparison.common["report_type"])
        self.assertEqual("run123", comparison.common["left_run_id"])
        self.assertEqual("run124", comparison.common["right_run_id"])
        self.assertEqual(0.1, comparison.common["left_resolved_params"]["dt"])
        self.assertEqual(0.55, comparison.common["right_parameter_overrides"]["evolution"]["alpha"])
        self.assertEqual(
            2.0,
            comparison.common["final_observables_right_minus_left"]["num_edges"],
        )
        self.assertEqual(
            "outputs/run124/telemetry/steps.jsonl",
            comparison.common["right_source_artifacts"]["step_rows"],
        )


if __name__ == "__main__":
    unittest.main()

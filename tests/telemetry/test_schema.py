"""Schema tests for the shared telemetry contract."""

from __future__ import annotations

import unittest

import pygrc
from pygrc.core import GRCEvent, StepResult
from pygrc import telemetry


class TelemetrySchemaTest(unittest.TestCase):
    """Validate Iteration 2 telemetry row and summary contracts."""

    def test_top_level_package_exports_telemetry(self) -> None:
        self.assertIs(pygrc.telemetry, telemetry)

    def test_build_run_id_is_stable_for_same_inputs(self) -> None:
        left = telemetry.build_run_id(
            model_family="grcv2",
            params_identity="params123",
            seed_name="Cell-1",
            seed_source_reference="rc-sim/configs/landscapes/cell-1.json",
            seed_path="configs/landscapes/seed/cell-1.seed.yaml",
            param_family="balanced_baseline",
            rng_seed=7,
            requested_steps=3,
        )
        right = telemetry.build_run_id(
            model_family="grcv2",
            params_identity="params123",
            seed_name="Cell-1",
            seed_source_reference="rc-sim/configs/landscapes/cell-1.json",
            seed_path="configs/landscapes/seed/cell-1.seed.yaml",
            param_family="balanced_baseline",
            rng_seed=7,
            requested_steps=3,
        )

        self.assertEqual(left, right)

    def test_step_row_from_step_result_records_identity_observables_and_event_counts(
        self,
    ) -> None:
        identity = telemetry.RunTelemetryIdentity(
            run_id="run123",
            model_family="grcv2",
            params_identity="params123",
            seed_name="Cell-1",
            param_family="balanced_baseline",
            requested_steps=3,
        )
        step_result = StepResult(
            step_index=2,
            time=0.2,
            events=[
                GRCEvent(kind="spark", step_index=2, payload={"node_id": 4}, source_family="grcv2"),
                GRCEvent(kind="spark", step_index=2, payload={"node_id": 5}, source_family="grcv2"),
                GRCEvent(kind="birth", step_index=2, payload={"edge_id": 9}, source_family="grcv2"),
            ],
            observables={"budget_current": 1.79, "num_nodes": 2},
            bookkeeping={"checkpoint": "step_0002"},
        )

        row = telemetry.step_row_from_step_result(
            step_result,
            identity=identity,
            family_extensions={"grcv2": {"lane": "balanced_baseline"}},
        )
        record = row.to_record()

        self.assertEqual(2, row.step_index)
        self.assertEqual(3, row.event_count)
        self.assertEqual(2, row.event_counts_by_kind["spark"])
        self.assertEqual(1, row.event_counts_by_kind["birth"])
        self.assertEqual(1.79, row.observables["budget_current"])
        self.assertEqual("run123", record.common["run_id"])
        self.assertEqual("grcv2", record.common["model_family"])
        self.assertEqual("step", record.kind)
        self.assertEqual("balanced_baseline", record.extensions["grcv2"]["lane"])

    def test_event_rows_from_events_assign_step_local_order(self) -> None:
        identity = telemetry.RunTelemetryIdentity(
            run_id="run123",
            model_family="grcv2",
            params_identity="params123",
        )
        events = [
            GRCEvent(kind="spark", step_index=4, payload={"node_id": 7}, source_family="grcv2"),
            GRCEvent(kind="birth", step_index=4, payload={"edge_id": 1}, source_family="grcv2"),
        ]

        rows = telemetry.event_rows_from_events(events, identity=identity)
        first_record = rows[0].to_record()

        self.assertEqual(2, len(rows))
        self.assertEqual(0, rows[0].event_index)
        self.assertEqual(1, rows[1].event_index)
        self.assertEqual("spark", rows[0].event_kind)
        self.assertEqual("birth", rows[1].event_kind)
        self.assertEqual({"node_id": 7}, dict(rows[0].payload))
        self.assertEqual("event", first_record.kind)

    def test_run_summary_from_step_results_aligns_initial_time_with_initial_observables(
        self,
    ) -> None:
        identity = telemetry.RunTelemetryIdentity(
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
        step_results = [
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
            StepResult(
                step_index=3,
                time=0.3,
                events=[GRCEvent(kind="birth", step_index=3, source_family="grcv2")],
                observables={"average_conductance": 0.6},
            ),
        ]

        summary = telemetry.run_summary_from_step_results(
            step_results,
            identity=identity,
            initial_observables={"average_conductance": 0.9, "num_edges": 9},
            final_observables={"average_conductance": 0.6, "num_edges": 11},
            resolved_params={"dt": 0.1, "evolution": {"alpha": 0.5}},
            raw_params={"dt": 0.1, "evolution": {"alpha": 0.5}},
            parameter_overrides={"evolution": {"alpha": 0.55}},
            family_extensions={"grcv2": {"baseline_lane": "balanced_baseline"}},
        )
        record = summary.to_record()

        self.assertEqual(3, summary.completed_steps)
        self.assertEqual(3, summary.final_step_index)
        self.assertEqual(0.0, summary.initial_time)
        self.assertEqual(0.3, summary.final_time)
        self.assertEqual(2, summary.total_event_count)
        self.assertEqual(1, summary.event_counts_by_kind["spark"])
        self.assertEqual(1, summary.event_counts_by_kind["birth"])
        self.assertEqual(0.9, summary.initial_observables["average_conductance"])
        self.assertEqual(0.6, summary.final_observables["average_conductance"])
        self.assertEqual(0.1, summary.resolved_params["dt"])
        self.assertEqual(0.55, summary.parameter_overrides["evolution"]["alpha"])
        self.assertEqual("completed", summary.status)
        self.assertEqual("run_summary", record.kind)
        self.assertEqual(0.1, record.common["resolved_params"]["dt"])
        self.assertEqual(11, record.common["rng_seed"])
        self.assertEqual("balanced_baseline", record.extensions["grcv2"]["baseline_lane"])

    def test_row_payloads_are_frozen_by_boundary(self) -> None:
        identity = telemetry.RunTelemetryIdentity(
            run_id="run123",
            model_family="grcv2",
            params_identity="params123",
        )
        row = telemetry.StepTelemetryRow(
            identity=identity,
            step_index=0,
            time=0.0,
            event_count=0,
            event_counts_by_kind={},
            observables={"metric": {"value": 1.0}},
        )

        self.assertEqual(1.0, row.observables["metric"]["value"])
        with self.assertRaises(TypeError):
            row.observables["new_metric"] = 2.0  # type: ignore[index]


if __name__ == "__main__":
    unittest.main()

"""Representative runtime evidence tests for GRC9V3."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from pygrc.models import GRC9V3

from scripts.run_grc9v3_representative_runtime import (
    DEFAULT_FIXTURE_NAME,
    build_representative_hybrid_model,
    run_representative_runtime,
)


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class GRC9V3RepresentativeRuntimeTest(unittest.TestCase):
    """Validate the Phase 7 Iteration 8 evidence lane."""

    def test_appendix_e_fixture_produces_one_spark_and_two_daughter_sinks(self) -> None:
        model = build_representative_hybrid_model()

        result = model.step()
        state = model.get_state()

        self.assertEqual(
            [
                "hybrid_spark_candidate",
                "hybrid_mechanical_expansion",
                "hybrid_spark_completed",
                "choice_detected",
            ],
            [event.kind for event in result.events],
        )
        stabilization = state.cached_quantities["last_child_basin_stabilization"]
        self.assertTrue(stabilization["stabilization_pass"])
        self.assertEqual(2, stabilization["stable_child_basin_count"])
        self.assertEqual(
            stabilization["module_sink_nodes"],
            stabilization["stabilized_child_node_ids"],
        )
        self.assertEqual(
            set(stabilization["stabilized_child_node_ids"]),
            set(state.sink_set),
        )
        self.assertEqual({"root": ["12", "16"]}, state.hierarchy)

    def test_representative_artifacts_are_replayable_and_self_consistent(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report = run_representative_runtime(
                outputs_root=Path(temp_dir),
                experiment_id="phase7-test",
                steps=3,
            )
            run_dir = Path(report["run_dir"])

            steps_path = run_dir / "steps.jsonl"
            events_path = run_dir / "events.jsonl"
            summary_path = run_dir / "run_summary.json"
            final_snapshot_path = run_dir / "final_snapshot.json"
            checkpoint_dir = run_dir / "checkpoints"

            self.assertTrue(steps_path.exists())
            self.assertTrue(events_path.exists())
            self.assertTrue(summary_path.exists())
            self.assertTrue(final_snapshot_path.exists())
            self.assertTrue((checkpoint_dir / "step-00000000.json").exists())
            self.assertTrue((checkpoint_dir / "step-00000003.json").exists())

            step_rows = _read_jsonl(steps_path)
            event_rows = _read_jsonl(events_path)
            run_summary = json.loads(summary_path.read_text(encoding="utf-8"))
            restored_final = GRC9V3.load(str(final_snapshot_path))

        self.assertEqual(3, len(step_rows))
        self.assertEqual(len(event_rows), run_summary["event_count"])
        self.assertEqual(
            sum(1 for row in event_rows if row["kind"] == "hybrid_spark_completed"),
            run_summary["hybrid_spark_completed_count"],
        )
        self.assertEqual(2, run_summary["daughter_sink_count"])
        self.assertEqual(DEFAULT_FIXTURE_NAME, run_summary["fixture_name"])
        self.assertTrue(report["replay"]["step_rows_match"])
        self.assertTrue(report["replay"]["event_rows_match"])
        self.assertTrue(report["replay"]["digests_match"])
        self.assertEqual(run_summary["final_step_index"], restored_final.get_state().step_index)
        self.assertEqual(
            run_summary["hybrid_spark_completed_count"],
            sum(
                1
                for event in restored_final.get_state().event_log
                if event.kind == "hybrid_spark_completed"
            ),
        )


if __name__ == "__main__":
    unittest.main()

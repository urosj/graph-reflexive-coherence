"""Representative telemetry lane tests for Phase T-GRC9V3."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from pygrc import telemetry
from scripts.run_grc9v3_representative_telemetry import (
    DEFAULT_EXPERIMENT_PATH,
    run_grc9v3_representative_telemetry,
)


class GRC9V3RepresentativeTelemetryTest(unittest.TestCase):
    """Validate the artifact-backed GRC9V3 representative telemetry lane."""

    def test_representative_telemetry_writes_replayable_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report = run_grc9v3_representative_telemetry(
                outputs_root=Path(temp_dir),
                steps=3,
            )
            layout = telemetry.build_telemetry_artifact_layout(
                report["run_id"],
                root_dir=Path(temp_dir),
                experiment_path=DEFAULT_EXPERIMENT_PATH,
            )
            pack = telemetry.load_telemetry_artifact_pack(layout)

            self.assertTrue(Path(report["initial_snapshot_path"]).exists())
            self.assertTrue(Path(report["final_snapshot_path"]).exists())
            self.assertTrue(Path(report["experiment_report_path"]).exists())
            self.assertTrue(report["replay_step_rows_match"])
            self.assertTrue(report["replay_event_rows_match"])
            self.assertTrue(report["replay_digest_match"])

            self.assertEqual(3, len(pack.step_rows))
            self.assertEqual(7, len(pack.event_rows))
            self.assertEqual(4, len(pack.graph_checkpoints))
            self.assertEqual({"grc9v3"}, set(pack.step_rows[0].family_extensions))
            self.assertEqual({"grc9v3"}, set(pack.event_rows[0].family_extensions))
            self.assertEqual({"grc9v3"}, set(pack.run_summary.family_extensions))
            self.assertEqual(
                telemetry.GRC9V3_TELEMETRY_CONTRACT_VERSION,
                pack.step_rows[0].family_extensions["grc9v3"]["contract_version"],
            )
            self.assertEqual(
                telemetry.GRC9V3_TELEMETRY_CONTRACT_VERSION,
                pack.event_rows[0].family_extensions["grc9v3"]["contract_version"],
            )
            self.assertEqual(
                "appendix_e_cell_division",
                pack.step_rows[0].family_extensions["grc9v3"]["lane_context"][
                    "representative_lane_name"
                ],
            )
            self.assertEqual(
                "implementation/Phase-7-RepresentativeRuntime.md",
                pack.event_rows[0].family_extensions["grc9v3"]["lane_context"][
                    "source_runtime_artifact"
                ],
            )
            self.assertEqual(
                "appendix_e_cell_division",
                pack.run_summary.family_extensions["grc9v3"]["lane_context"][
                    "representative_lane_name"
                ],
            )
            appendix = pack.run_summary.family_extensions["grc9v3"][
                "representative_appendix_e_summary"
            ]
            self.assertEqual(2, appendix["daughter_sink_count"])
            self.assertEqual((12, 16), appendix["daughter_sink_node_ids"])
            self.assertTrue(appendix["replay_digest_match"])
            assert pack.graph_checkpoint_index is not None
            self.assertEqual("initial+every_step", pack.graph_checkpoint_index.selection_policy)
            self.assertEqual(
                telemetry.GRC9V3_TELEMETRY_CONTRACT_VERSION,
                pack.graph_checkpoint_index.family_extensions["grc9v3"]["contract_version"],
            )
            self.assertEqual(
                (0, 1, 2, 3),
                tuple(reference.step_index for reference in pack.graph_checkpoint_index.checkpoints),
            )
            self.assertEqual("initial", pack.graph_checkpoints[0].checkpoint_label)
            self.assertEqual("final", pack.graph_checkpoints[-1].checkpoint_label)
            final_checkpoint_extension = pack.graph_checkpoints[-1].family_extensions["grc9v3"]
            self.assertEqual("enabled", final_checkpoint_extension["overlay_status"])
            for overlay_name in (
                "node_overlay",
                "port_overlay",
                "edge_overlay",
                "module_overlay",
                "choice_overlay",
            ):
                self.assertIn(overlay_name, final_checkpoint_extension)
            self.assertIn("12", final_checkpoint_extension["node_overlay"])
            self.assertTrue(
                final_checkpoint_extension["node_overlay"]["12"]["is_module_node"]
            )
            self.assertIn(
                "basin_mass",
                final_checkpoint_extension["node_overlay"]["12"],
            )
            self.assertIn("basin_mass", pack.graph_checkpoints[-1].node_records[0])
            self.assertEqual(
                2,
                final_checkpoint_extension["module_overlay"]["latest"][
                    "stable_child_basin_count"
                ],
            )
            self.assertIn(
                "14",
                final_checkpoint_extension["choice_overlay"]["collapse_registry"],
            )
            self.assertEqual({}, pack.step_rows[-1].family_extensions["grc9v3"].get("node_overlay", {}))
            assert pack.experiment_report is not None
            self.assertTrue(pack.experiment_report.common["replay_step_rows_match"])
            self.assertTrue(pack.experiment_report.common["replay_event_rows_match"])
            self.assertTrue(pack.experiment_report.common["replay_digest_match"])
            self.assertEqual(
                telemetry.GRC9V3_TELEMETRY_CONTRACT_VERSION,
                pack.experiment_report.extensions["grc9v3"]["contract_version"],
            )
            self.assertEqual(
                "appendix_e_cell_division",
                pack.experiment_report.extensions["grc9v3"]["representative_fixture"],
            )
            self.assertEqual(
                "scripts/run_grc9v3_representative_runtime.py",
                pack.experiment_report.extensions["grc9v3"]["phase7_runtime_source"],
            )

    def test_representative_telemetry_one_step_run_is_replayable(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report = run_grc9v3_representative_telemetry(
                outputs_root=Path(temp_dir),
                steps=1,
            )
            layout = telemetry.build_telemetry_artifact_layout(
                report["run_id"],
                root_dir=Path(temp_dir),
                experiment_path=DEFAULT_EXPERIMENT_PATH,
            )
            pack = telemetry.load_telemetry_artifact_pack(layout)

            self.assertTrue(report["replay_step_rows_match"])
            self.assertTrue(report["replay_event_rows_match"])
            self.assertTrue(report["replay_digest_match"])
            self.assertEqual(1, len(pack.step_rows))
            self.assertEqual(4, len(pack.event_rows))
            self.assertEqual(2, len(pack.graph_checkpoints))
            self.assertEqual("initial", pack.graph_checkpoints[0].checkpoint_label)
            self.assertEqual("final", pack.graph_checkpoints[-1].checkpoint_label)
            lifecycle = pack.run_summary.family_extensions["grc9v3"][
                "lifecycle_event_counts"
            ]
            self.assertEqual(1, lifecycle["hybrid_spark_candidate_count"])
            self.assertEqual(1, lifecycle["hybrid_mechanical_expansion_count"])
            self.assertEqual(1, lifecycle["hybrid_spark_completed_count"])
            self.assertEqual(1, lifecycle["choice_detected_count"])

    def test_checkpoint_overlays_can_be_disabled(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report = run_grc9v3_representative_telemetry(
                outputs_root=Path(temp_dir),
                steps=1,
                include_checkpoint_overlays=False,
            )
            layout = telemetry.build_telemetry_artifact_layout(
                report["run_id"],
                root_dir=Path(temp_dir),
                experiment_path=DEFAULT_EXPERIMENT_PATH,
            )
            pack = telemetry.load_telemetry_artifact_pack(layout)

            extension = pack.graph_checkpoints[-1].family_extensions["grc9v3"]
            self.assertEqual("disabled", extension["overlay_status"])
            self.assertNotIn("node_overlay", extension)
            self.assertNotIn("port_overlay", extension)

    def test_checkpoint_overlay_payload_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as first_dir, tempfile.TemporaryDirectory() as second_dir:
            first_report = run_grc9v3_representative_telemetry(
                outputs_root=Path(first_dir),
                steps=3,
            )
            second_report = run_grc9v3_representative_telemetry(
                outputs_root=Path(second_dir),
                steps=3,
            )
            first_layout = telemetry.build_telemetry_artifact_layout(
                first_report["run_id"],
                root_dir=Path(first_dir),
                experiment_path=DEFAULT_EXPERIMENT_PATH,
            )
            second_layout = telemetry.build_telemetry_artifact_layout(
                second_report["run_id"],
                root_dir=Path(second_dir),
                experiment_path=DEFAULT_EXPERIMENT_PATH,
            )
            first_pack = telemetry.load_telemetry_artifact_pack(first_layout)
            second_pack = telemetry.load_telemetry_artifact_pack(second_layout)

            self.assertEqual(
                first_pack.graph_checkpoints[-1].family_extensions["grc9v3"],
                second_pack.graph_checkpoints[-1].family_extensions["grc9v3"],
            )


if __name__ == "__main__":
    unittest.main()

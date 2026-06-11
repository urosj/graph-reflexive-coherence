"""Tests for replayable GRC9V3 discovery control sessions."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from pygrc import telemetry
from pygrc.discovery import (
    GRC9V3_COMPLEX_HYBRID_STEP_COUNTS,
    GRC9V3_DISCOVERY_LOW_STEP_COUNTS,
    GRC9V3_PRESSURE_BOUNDARY_STEP_COUNTS,
    run_grc9v3_complex_hybrid_session,
    run_grc9v3_discovery_control_session,
    run_grc9v3_pressure_boundary_session,
)
from pygrc.discovery.grc9v3_discovery_runner import (
    CHECKPOINT_SURFACE,
    _validate_step_count_coverage,
)


class GRC9V3DiscoveryRunnerTest(unittest.TestCase):
    def test_control_session_writes_replayable_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "S0999"
            session = run_grc9v3_discovery_control_session(
                session_id="S0999",
                session_root=root,
                step_counts={key: 1 for key in GRC9V3_DISCOVERY_LOW_STEP_COUNTS},
            )

            payload = session.to_mapping()
            self.assertEqual(19, payload["lane_count"])
            self.assertEqual(19, payload["total_steps"])
            self.assertTrue(payload["all_replay_step_rows_match"])
            self.assertTrue(payload["all_replay_event_rows_match"])
            self.assertTrue(payload["all_replay_digests_match"])
            self.assertIn(
                "quiescent_hybrid_control_no_event_control",
                payload["first_pass_interpretation"]["no_event_lanes_confirmed"],
            )
            self.assertTrue((root / "session_manifest.json").exists())
            self.assertTrue((root / "reports" / "run_report.json").exists())
            self.assertTrue((root / "reports" / "initial_results.md").exists())

            first_lane = session.lanes[0]
            layout = telemetry.build_telemetry_artifact_layout(
                first_lane.seed.lane_name,
                root_dir=root / "generated_lanes",
            )
            pack = telemetry.load_telemetry_artifact_pack(layout)
            self.assertEqual(1, len(pack.step_rows))
            self.assertEqual(2, len(pack.graph_checkpoints))
            self.assertEqual({"grc9v3"}, set(pack.step_rows[0].family_extensions) - {"discovery"})
            self.assertEqual(
                telemetry.GRC9V3_TELEMETRY_CONTRACT_VERSION,
                pack.step_rows[0].family_extensions["grc9v3"]["contract_version"],
            )
            assert pack.graph_checkpoint_index is not None
            self.assertEqual(
                telemetry.GRC9V3_TELEMETRY_CONTRACT_VERSION,
                pack.graph_checkpoint_index.family_extensions["grc9v3"]["contract_version"],
            )
            self.assertEqual(
                CHECKPOINT_SURFACE,
                pack.graph_checkpoint_index.family_extensions["grc9v3"][
                    "checkpoint_surface"
                ],
            )
            self.assertEqual(
                CHECKPOINT_SURFACE,
                pack.graph_checkpoints[0].family_extensions["grc9v3"][
                    "checkpoint_surface"
                ],
            )
            assert pack.experiment_report is not None
            self.assertTrue(pack.experiment_report.common["replay_step_rows_match"])
            self.assertTrue(pack.experiment_report.common["replay_event_rows_match"])
            self.assertTrue(pack.experiment_report.common["replay_digest_match"])
            self.assertIn(
                "seed_parameters",
                pack.experiment_report.extensions["grc9v3"],
            )

    def test_manifest_records_exact_replay_command_and_seed_parameters(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "S0998"
            session = run_grc9v3_discovery_control_session(
                session_id="S0998",
                session_root=root,
                step_counts={key: 1 for key in GRC9V3_DISCOVERY_LOW_STEP_COUNTS},
            )

            manifest = json.loads((root / "session_manifest.json").read_text())
            report = json.loads((root / "reports" / "run_report.json").read_text())
            self.assertIn("--session-id S0998", manifest["replay_command"])
            self.assertIn("replay_environment_note", manifest)
            self.assertEqual(session.to_mapping(), report)
            for lane in session.lanes:
                layout = telemetry.build_telemetry_artifact_layout(
                    lane.seed.lane_name,
                    root_dir=root / "generated_lanes",
                )
                pack = telemetry.load_telemetry_artifact_pack(layout)
                assert pack.experiment_report is not None
                self.assertEqual(
                    lane.seed.seed_parameters,
                    pack.experiment_report.extensions["grc9v3"]["seed_parameters"],
                )

    def test_default_session_tree_updates_experimental_log(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "phenomenology_discovery" / "sessions" / "S0996"
            run_grc9v3_discovery_control_session(
                session_id="S0996",
                session_root=root,
                step_counts={key: 1 for key in GRC9V3_DISCOVERY_LOW_STEP_COUNTS},
            )

            log_path = root.parent.parent / "ExperimentalLog.md"
            log_text = log_path.read_text()
            self.assertIn("| `S0996` | `completed` | `generated_run` |", log_text)
            self.assertIn("Iteration 5 low-step generated control runs", log_text)

            run_grc9v3_discovery_control_session(
                session_id="S0996",
                session_root=root,
                step_counts={key: 1 for key in GRC9V3_DISCOVERY_LOW_STEP_COUNTS},
            )
            self.assertEqual(
                1,
                (root.parent.parent / "ExperimentalLog.md")
                .read_text()
                .count("| `S0996` |"),
            )

    def test_refined_control_session_emits_repaired_lifecycle_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "S0997"
            session = run_grc9v3_discovery_control_session(
                session_id="S0997",
                session_root=root,
                step_counts={key: 1 for key in GRC9V3_DISCOVERY_LOW_STEP_COUNTS},
                refined_controls=True,
            )
            by_lane = {lane.seed.lane_name: lane for lane in session.lanes}

            self.assertEqual("I05_1_theory_first_seed_refinement", session.iteration)
            self.assertEqual(
                0,
                by_lane["quiescent_hybrid_control_no_event_control"].event_count,
            )
            self.assertEqual(
                {"collapse": 1},
                by_lane["choice_collapse_positive_control"].event_counts_by_kind,
            )
            self.assertEqual(
                {"growth": 1},
                by_lane["growth_pressure_positive_control"].event_counts_by_kind,
            )
            self.assertEqual(
                {},
                by_lane["growth_pressure_negative_control"].event_counts_by_kind,
            )
            manifest = json.loads((root / "session_manifest.json").read_text())
            self.assertIn("--refined-controls", manifest["replay_command"])

    def test_appendix_e_pass_fail_mode_separates_negative_control(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "S0995"
            session = run_grc9v3_discovery_control_session(
                session_id="S0995",
                session_root=root,
                step_counts={key: 1 for key in GRC9V3_DISCOVERY_LOW_STEP_COUNTS},
                appendix_e_pass_fail_controls=True,
            )
            by_lane = {lane.seed.lane_name: lane for lane in session.lanes}

            self.assertEqual(
                "I05_2_appendix_e_pass_fail_separation",
                session.iteration,
            )
            self.assertEqual(
                1,
                by_lane[
                    "appendix_e_cell_division_positive_control"
                ].event_counts_by_kind.get("hybrid_spark_completed"),
            )
            self.assertEqual(
                {},
                by_lane[
                    "appendix_e_cell_division_negative_control"
                ].event_counts_by_kind,
            )
            self.assertTrue(
                by_lane[
                    "appendix_e_cell_division_negative_control"
                ].seed.seed_parameters["appendix_e_no_completion_control"]
            )
            manifest = json.loads((root / "session_manifest.json").read_text())
            self.assertIn(
                "--appendix-e-pass-fail-controls",
                manifest["replay_command"],
            )

    def test_step_count_coverage_rejects_missing_planned_family(self) -> None:
        with self.assertRaisesRegex(ValueError, "missing GRC9V3 discovery step counts"):
            _validate_step_count_coverage(
                {"hybrid_spark_gate": 1},
                ("hybrid_spark_gate", "missing_family"),
            )

    def test_complex_hybrid_session_writes_replayable_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "S0994"
            session = run_grc9v3_complex_hybrid_session(
                session_id="S0994",
                session_root=root,
                step_counts=GRC9V3_COMPLEX_HYBRID_STEP_COUNTS,
            )
            by_lane = {lane.seed.lane_name: lane for lane in session.lanes}

            self.assertEqual("I07_complex_hybrid_examples", session.iteration)
            self.assertEqual(7, len(session.lanes))
            self.assertTrue(session.to_mapping()["all_replay_step_rows_match"])
            self.assertTrue(session.to_mapping()["all_replay_event_rows_match"])
            self.assertTrue(session.to_mapping()["all_replay_digests_match"])
            self.assertIn(
                "hybrid_spark_completed",
                by_lane[
                    "complex_spark_expansion_hierarchy_complex_control"
                ].event_counts_by_kind,
            )
            self.assertIn(
                "collapse",
                by_lane[
                    "complex_spark_expansion_choice_collapse_complex_control"
                ].event_counts_by_kind,
            )
            self.assertIn(
                "growth",
                by_lane[
                    "complex_expansion_growth_budget_coarse_complex_control"
                ].event_counts_by_kind,
            )
            growth_lane = by_lane["complex_expansion_growth_budget_coarse_complex_control"]
            self.assertTrue(growth_lane.event_sequence_analysis["has_sequence_delta"])
            self.assertEqual(
                {},
                growth_lane.event_sequence_analysis[
                    "missing_predicted_event_counts"
                ],
            )
            self.assertEqual(
                2,
                growth_lane.event_sequence_analysis["unexpected_event_counts"][
                    "choice_detected"
                ],
            )
            layout = telemetry.build_telemetry_artifact_layout(
                "complex_expansion_growth_budget_coarse_complex_control",
                root_dir=root / "generated_lanes",
            )
            pack = telemetry.load_telemetry_artifact_pack(layout)
            self.assertTrue(
                any(
                    row.family_extensions["grc9v3"]["coarse_cache"][
                        "coarse_cache_invalidated"
                    ]
                    for row in pack.step_rows
                )
            )
            self.assertEqual(
                {},
                by_lane[
                    "complex_spark_choice_no_saturation_perturbation_perturbation_control"
                ].event_counts_by_kind,
            )

            manifest = json.loads((root / "session_manifest.json").read_text())
            self.assertIn("--complex-hybrid-examples", manifest["replay_command"])
            self.assertEqual("complex_generated_run", manifest["session_kind"])

    def test_pressure_boundary_session_records_specific_growth_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "S0993"
            session = run_grc9v3_pressure_boundary_session(
                session_id="S0993",
                session_root=root,
                step_counts={key: 1 for key in GRC9V3_PRESSURE_BOUNDARY_STEP_COUNTS},
            )
            by_lane = {lane.seed.lane_name: lane for lane in session.lanes}

            self.assertEqual(
                "PressureBoundary_I04_2_grc9v3_pressure_boundary_evidence",
                session.iteration,
            )
            self.assertEqual(4, len(session.lanes))
            self.assertTrue(session.to_mapping()["all_replay_step_rows_match"])
            self.assertTrue(session.to_mapping()["all_replay_event_rows_match"])
            self.assertTrue(session.to_mapping()["all_replay_digests_match"])
            self.assertEqual(
                {"growth": 1},
                by_lane[
                    "pressure_boundary_growth_positive_control_positive_control"
                ].event_counts_by_kind,
            )
            self.assertEqual(
                {},
                by_lane[
                    "pressure_boundary_growth_no_growth_control_positive_control"
                ].event_counts_by_kind,
            )
            self.assertEqual(
                {"growth": 1},
                by_lane[
                    "generic_front_capacity_growth_comparison_positive_control"
                ].event_counts_by_kind,
            )

            pressure_layout = telemetry.build_telemetry_artifact_layout(
                "pressure_boundary_growth_positive_control_positive_control",
                root_dir=root / "generated_lanes",
            )
            generic_layout = telemetry.build_telemetry_artifact_layout(
                "generic_front_capacity_growth_comparison_positive_control",
                root_dir=root / "generated_lanes",
            )
            pressure_summary = telemetry.load_telemetry_artifact_pack(
                pressure_layout
            ).run_summary
            generic_summary = telemetry.load_telemetry_artifact_pack(
                generic_layout
            ).run_summary
            assert pressure_summary is not None
            assert generic_summary is not None
            pressure_counts = pressure_summary.family_extensions["grc9v3"][
                "lifecycle_event_counts"
            ]
            generic_counts = generic_summary.family_extensions["grc9v3"][
                "lifecycle_event_counts"
            ]
            self.assertEqual(1, pressure_counts["front_capacity_growth_count"])
            self.assertEqual(1, pressure_counts["pressure_boundary_growth_count"])
            self.assertEqual(0, pressure_counts["legacy_broad_growth_count"])
            self.assertEqual(1, generic_counts["front_capacity_growth_count"])
            self.assertEqual(0, generic_counts["pressure_boundary_growth_count"])

            manifest = json.loads((root / "session_manifest.json").read_text())
            self.assertEqual(
                "pressure_boundary_generated_run",
                manifest["session_kind"],
            )
            self.assertIn("--pressure-boundary-examples", manifest["replay_command"])


if __name__ == "__main__":
    unittest.main()

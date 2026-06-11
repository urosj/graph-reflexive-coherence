"""Tests for GRCL-9 lowering replay sessions."""

from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
import unittest

from pygrc.landscapes.extensions.grcl9 import (
    GRCL9GrowthLocus,
    GRCL9SourceDocument,
    GRCL9SparkCandidateRegion,
)
from pygrc.telemetry import run_grcl9_lowering_replay_session
from pygrc.telemetry.grcl9_replay import _run_replay_lane
from pygrc.telemetry.io import (
    EVENT_ROWS_FILENAME,
    GRAPH_CHECKPOINT_INDEX_FILENAME,
    GRAPH_CHECKPOINTS_DIRNAME,
    RUN_SUMMARY_FILENAME,
    STEP_ROWS_FILENAME,
    TELEMETRY_DIRNAME,
)


class GRCL9ReplayTest(unittest.TestCase):
    def test_replay_session_writes_replayable_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_grcl9_lowering_replay_session(
                session_id="S9001",
                output_root=Path(temp_dir) / "grcl9" / "lowering",
                fixture_names=(
                    "spark_column_proxy_eps_pass",
                    "spark_column_proxy_eps_fail",
                ),
                requested_steps=2,
            )

            self.assertEqual("S9001", result.session_id)
            self.assertEqual(2, len(result.lanes))
            self.assertTrue(result.session_manifest_path.exists())
            self.assertTrue(result.experimental_log_path.exists())
            self.assertTrue(result.replay_script_path.exists())
            self.assertTrue(os.access(result.replay_script_path, os.X_OK))

            manifest = _read_json(result.session_manifest_path)
            self.assertEqual("grcl9_lowering_replay", manifest["program"])
            self.assertEqual("grc9", manifest["runtime_family"])
            self.assertEqual(2, manifest["summary"]["lane_count"])

            for lane in result.lanes:
                with self.subTest(fixture=lane.fixture_name):
                    self.assertTrue(Path(lane.source_fixture_path).exists())
                    self.assertTrue(Path(lane.lowered_state_path).exists())
                    self.assertTrue(Path(lane.selector_report_path).exists())

                    telemetry_dir = Path(lane.artifact_root) / TELEMETRY_DIRNAME
                    self.assertTrue((telemetry_dir / STEP_ROWS_FILENAME).exists())
                    self.assertTrue((telemetry_dir / EVENT_ROWS_FILENAME).exists())
                    self.assertTrue((telemetry_dir / RUN_SUMMARY_FILENAME).exists())
                    self.assertTrue(
                        (
                            telemetry_dir
                            / GRAPH_CHECKPOINTS_DIRNAME
                            / GRAPH_CHECKPOINT_INDEX_FILENAME
                        ).exists()
                    )
                    self.assertGreaterEqual(lane.checkpoint_count, 3)

    def test_replay_records_selector_misses_explicitly(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_grcl9_lowering_replay_session(
                session_id="S9002",
                output_root=Path(temp_dir) / "grcl9" / "lowering",
                fixture_names=("spark_instability_tau_pass",),
                requested_steps=2,
            )

            lane = result.lanes[0]
            self.assertEqual("missed", lane.selector_status)
            report = _read_json(Path(lane.selector_report_path))

            self.assertEqual("missed", report["status"])
            self.assertEqual(
                "spark_instability_count",
                report["selector_results"][0]["selector_id"],
            )
            self.assertTrue(report["failure_notes"])

    def test_lowered_state_records_grcl9_provenance_and_bridge_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_grcl9_lowering_replay_session(
                session_id="S9003",
                output_root=Path(temp_dir) / "grcl9" / "lowering",
                fixture_names=("post_expansion_fission_min_mass_pass",),
                requested_steps=1,
            )

            lowered = _read_json(Path(result.lanes[0].lowered_state_path))
            caches = lowered["cached_quantities"]
            self.assertIn("grcl9_provenance", caches)
            self.assertIn("grcl9_motif_registry", caches)
            self.assertEqual([2], caches["grcl9_bridge_edge_ids"])
            edge_payloads = {
                edge["edge_id"]: edge["payload"]
                for edge in lowered["topology"]["edges"]
            }
            self.assertEqual("bridge", edge_payloads[2]["grcl9_edge_kind"])

    def test_collapse_discovery_selectors_distinguish_runtime_loss_from_control(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_grcl9_lowering_replay_session(
                session_id="S9004",
                output_root=Path(temp_dir) / "grcl9" / "lowering",
                source_mode="landscape_seed_examples",
                fixture_names=(
                    "cell_basin_merge_runtime_collapse_probe",
                    "cell_basin_merge_runtime_stability_control",
                ),
                requested_steps=1,
            )

            self.assertTrue(
                all(lane.selector_status == "passed" for lane in result.lanes),
                [lane.to_mapping() for lane in result.lanes],
            )
            by_name = {lane.fixture_name: lane for lane in result.lanes}
            collapse_report = _read_json(
                Path(by_name["cell_basin_merge_runtime_collapse_probe"].selector_report_path)
            )
            control_report = _read_json(
                Path(by_name["cell_basin_merge_runtime_stability_control"].selector_report_path)
            )

            self.assertEqual(
                "runtime_collapse_like_observed",
                collapse_report["selector_results"][0]["observed_value"]["classification"],
            )
            self.assertEqual(
                ["fission_sink_b"],
                collapse_report["selector_results"][0]["observed_value"]["lost_source_sink_roles"],
            )
            self.assertEqual(
                "structural_only",
                control_report["selector_results"][0]["observed_value"]["classification"],
            )
            self.assertEqual(
                [],
                control_report["selector_results"][0]["observed_value"]["lost_source_sink_roles"],
            )

    def test_long_window_developed_basin_collapse_selector_records_centroid_target(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_grcl9_lowering_replay_session(
                session_id="S9005",
                output_root=Path(temp_dir) / "grcl9" / "lowering",
                source_mode="landscape_seed_examples",
                fixture_names=("cell_developed_basin_centroid_collapse_long_window",),
                requested_steps=24,
            )

            lane = result.lanes[0]
            self.assertEqual("passed", lane.selector_status)
            self.assertEqual(25, lane.checkpoint_count)

            report = _read_json(Path(lane.selector_report_path))
            observed = report["selector_results"][0]["observed_value"]

            self.assertEqual("runtime_collapse_like_observed", observed["classification"])
            self.assertTrue(observed["runtime_collapse_like_long_window"])
            self.assertEqual(["fission_sink_b"], observed["lost_source_sink_roles"])
            self.assertEqual("group_centroid", observed["target_selection_policy"])
            self.assertEqual("group_centroid", observed["target_selection_kind"])
            self.assertIsNotNone(observed["target_selected_node_id"])
            self.assertGreater(len(observed["source_basin_a_node_ids"]), 2)
            self.assertGreater(len(observed["source_basin_b_node_ids"]), 2)

    def test_full_capacity_cascade_records_all_runtime_signatures(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_grcl9_lowering_replay_session(
                session_id="S9006",
                output_root=Path(temp_dir) / "grcl9" / "lowering",
                source_mode="legacy_growth_landscape_seed_examples",
                fixture_names=("cell_full_capacity_phenomenology_cascade",),
                requested_steps=24,
                force_legacy_growth=True,
            )

            lane = result.lanes[0]
            self.assertEqual("passed", lane.selector_status)
            self.assertEqual(25, lane.checkpoint_count)
            self.assertEqual({"expansion": 1, "growth": 60, "spark": 1}, lane.event_counts_by_kind)

            report = _read_json(Path(lane.selector_report_path))
            by_selector = {
                item["selector_id"]: item["observed_value"]
                for item in report["selector_results"]
            }

            self.assertEqual(1, by_selector["spark_column_proxy_count"])
            self.assertGreater(by_selector["expansion_module_size"], 0)
            self.assertGreater(by_selector["growth_count"], 0)
            self.assertTrue(
                by_selector["runtime_collapse_like_long_window"][
                    "runtime_collapse_like_long_window"
                ]
            )
            self.assertEqual(
                "group_centroid",
                by_selector["runtime_collapse_like_long_window"]["target_selection_policy"],
            )

    def test_corrected_front_capacity_source_replays_in_corrected_growth_mode(self) -> None:
        source = GRCL9SourceDocument(
            fixture_name="front_growth_replay",
            manifest_entry_id="grcl9_lowering_growth_pressure_v1",
            constructs=(
                GRCL9SparkCandidateRegion(
                    construct_id="spark_region",
                    motif_id="growth_pressure",
                    candidate_id="candidate",
                    coherence_allocation={"candidate": 1.0},
                    neighbor_coherence_profile={"active_degree": 9},
                    spark_gate_intent="saturation_column_proxy",
                ),
                GRCL9GrowthLocus(
                    construct_id="front_growth",
                    motif_id="growth_pressure",
                    parent_id="candidate",
                    inactive_parent_port=5,
                    pressure_profile={"class": "controlled_high"},
                    lambda_birth=1.5,
                    growth_semantics="front_capacity",
                    front_capacity_source="spark_expansion_front",
                    front_source_construct_id="spark_region",
                ),
            ),
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            lane = _run_replay_lane(
                source=source,
                requested_steps=1,
                session_id="S9007",
                lanes_root=root / "lanes",
                sources_root=root / "source_fixtures",
                lowered_root=root / "lowered_states",
                reports_root=root / "reports",
            )

            self.assertEqual("front_capacity", lane.growth_semantics_status)
            self.assertEqual(
                "grc9_front_capacity",
                lane.growth_parent_eligibility_mode,
            )
            self.assertFalse(lane.legacy_broad_growth_non_evidence)

            step_row = _read_jsonl(
                Path(lane.artifact_root) / TELEMETRY_DIRNAME / STEP_ROWS_FILENAME
            )[0]
            grc9_extension = step_row["family_extensions"]["grc9"]
            self.assertEqual(
                "grc9_front_capacity",
                grc9_extension["backend_config"]["growth_parent_eligibility_mode"],
            )
            self.assertEqual(
                "grc9_front_capacity",
                step_row["family_extensions"]["grcl9"][
                    "growth_parent_eligibility_mode"
                ],
            )

    def test_pressure_boundary_source_replays_with_pressure_boundary_summary(self) -> None:
        source = GRCL9SourceDocument(
            fixture_name="pressure_boundary_replay",
            manifest_entry_id="grcl9_lowering_growth_pressure_v1",
            expected_selector_ids=("growth_count", "pressure_boundary_growth_provenance"),
            constructs=(
                GRCL9SparkCandidateRegion(
                    construct_id="spark_region",
                    motif_id="growth_pressure",
                    candidate_id="candidate",
                    coherence_allocation={"candidate": 1.0},
                    neighbor_coherence_profile={"active_degree": 9},
                    spark_gate_intent="saturation_column_proxy",
                ),
                GRCL9GrowthLocus(
                    construct_id="pressure_boundary_growth",
                    motif_id="growth_pressure",
                    parent_id="candidate",
                    inactive_parent_port=5,
                    pressure_profile={"class": "controlled_high"},
                    lambda_birth=100.0,
                    growth_semantics="front_capacity",
                    front_capacity_source="pressure_boundary",
                ),
            ),
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            lane = _run_replay_lane(
                source=source,
                requested_steps=1,
                session_id="S9008",
                lanes_root=root / "lanes",
                sources_root=root / "source_fixtures",
                lowered_root=root / "lowered_states",
                reports_root=root / "reports",
            )

            self.assertEqual("passed", lane.selector_status)
            summary = _read_json(Path(lane.artifact_root) / TELEMETRY_DIRNAME / RUN_SUMMARY_FILENAME)
            grc9 = summary["family_extensions"]["grc9"]
            grcl9 = summary["family_extensions"]["grcl9"]
            self.assertEqual(
                1,
                grc9["growth_summary"]["pressure_boundary_growth_count"],
            )
            sources = grcl9["growth_parent_capacity_sources"]
            self.assertIn(
                "pressure_boundary",
                {
                    record["front_capacity_source"]
                    for record in sources.values()
                },
            )

    def test_legacy_growth_replay_requires_force_flag(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaisesRegex(ValueError, "force-legacy-growth"):
                run_grcl9_lowering_replay_session(
                    session_id="S9008",
                    output_root=Path(temp_dir) / "grcl9" / "lowering",
                    source_mode="legacy_growth_landscape_seed_examples",
                    fixture_names=("growth_pressure_lambda_high",),
                    requested_steps=1,
                )

    def test_forced_legacy_growth_replay_is_explicit_non_evidence_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_grcl9_lowering_replay_session(
                session_id="S9008",
                output_root=Path(temp_dir) / "grcl9" / "lowering",
                source_mode="legacy_growth_landscape_seed_examples",
                fixture_names=("growth_pressure_lambda_high",),
                requested_steps=1,
                force_legacy_growth=True,
            )

            lane = result.lanes[0]
            self.assertEqual("legacy_growth_locus", lane.growth_semantics_status)
            self.assertEqual(
                "legacy_any_inactive_port",
                lane.growth_parent_eligibility_mode,
            )
            self.assertTrue(lane.legacy_broad_growth_non_evidence)

            manifest = _read_json(result.session_manifest_path)
            self.assertEqual(
                "legacy_growth_landscape_seed_examples",
                manifest["source_mode"],
            )
            self.assertTrue(manifest["force_legacy_growth"])
            self.assertEqual(
                "forced_replay_only_non_evidence",
                manifest["legacy_growth_guard"],
            )
            manifest_lane = manifest["lanes"][0]
            self.assertEqual(
                "legacy_any_inactive_port",
                manifest_lane["growth_parent_eligibility_mode"],
            )
            self.assertTrue(manifest_lane["legacy_broad_growth_non_evidence"])

            step_row = _read_jsonl(
                Path(lane.artifact_root) / TELEMETRY_DIRNAME / STEP_ROWS_FILENAME
            )[0]
            grcl9_extension = step_row["family_extensions"]["grcl9"]
            self.assertEqual(
                "legacy_broad_growth_non_evidence",
                grcl9_extension["growth_replay_metadata"]["growth_evidence_status"],
            )


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


if __name__ == "__main__":
    unittest.main()

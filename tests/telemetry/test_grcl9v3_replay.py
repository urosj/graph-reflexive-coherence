"""Tests for GRCL-9V3 lowered-source replay sessions."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from pygrc import telemetry
from pygrc.landscapes.extensions.grcl9v3 import (
    GRCL9V3GrowthLocus,
    GRCL9V3SourceDocument,
)
from pygrc.telemetry.grcl9v3_replay import (
    _first_event_after,
    _relay_role_summary,
    _run_replay_lane,
)


class GRCL9V3ReplaySessionTest(unittest.TestCase):
    def test_replay_session_writes_replayable_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = telemetry.run_grcl9v3_lowering_replay_session(
                session_id="S0001",
                output_root=Path(tmpdir),
                fixture_names=(
                    "growth_pressure_positive_control",
                    "quiescent_hybrid_control_no_event_control",
                ),
                requested_steps=1,
            )

            self.assertEqual("S0001", result.session_id)
            self.assertEqual(2, len(result.lanes))
            self.assertTrue(result.session_manifest_path.exists())
            self.assertTrue(result.replay_script_path.exists())
            self.assertTrue(result.experimental_log_path.exists())

            manifest = _read_json(result.session_manifest_path)
            self.assertEqual("grcl9v3_lowering_replay", manifest["session_kind"])
            self.assertEqual(2, manifest["lane_count"])
            self.assertIn("pygrc.telemetry.grcl9v3_replay", manifest["replay_command"])
            self.assertIn("--steps 1", manifest["replay_command"])
            self.assertIn("--fixture growth_pressure_positive_control", manifest["replay_command"])
            self.assertIn(
                "--fixture quiescent_hybrid_control_no_event_control",
                manifest["replay_command"],
            )
            replay_script = result.replay_script_path.read_text(encoding="utf-8")
            self.assertIn(manifest["replay_command"], replay_script)

            for lane in result.lanes:
                with self.subTest(fixture=lane.fixture_name):
                    self.assertTrue(Path(lane.source_fixture_path).exists())
                    self.assertTrue(Path(lane.lowered_state_path).exists())
                    self.assertTrue(Path(lane.replay_report_path).exists())
                    self.assertTrue(lane.replay_step_rows_match)
                    self.assertTrue(lane.replay_event_rows_match)
                    self.assertTrue(lane.replay_digest_match)

                    artifact_root = Path(lane.artifact_root)
                    telemetry_root = artifact_root / "telemetry"
                    self.assertTrue((telemetry_root / "steps.jsonl").exists())
                    self.assertTrue((telemetry_root / "events.jsonl").exists())
                    self.assertTrue((telemetry_root / "run_summary.json").exists())
                    checkpoint_index_path = telemetry_root / "graph_checkpoints" / "index.json"
                    self.assertTrue(checkpoint_index_path.exists())

                    step_row = _read_jsonl(telemetry_root / "steps.jsonl")[0]
                    self.assertEqual(
                        "implementation/GRCL-9V3-ImplementationPlan.md",
                        step_row["family_extensions"]["grc9v3"]["lane_context"][
                            "source_reference"
                        ],
                    )
                    self.assertIn(
                        "expected_region_caches",
                        step_row["family_extensions"]["grcl9v3"],
                    )
                    self.assertTrue(
                        step_row["family_extensions"]["grcl9v3"][
                            "expected_region_cache_names"
                        ]
                    )
                    checkpoint_index = _read_json(checkpoint_index_path)
                    self.assertEqual(2, len(checkpoint_index["checkpoints"]))
                    self.assertEqual(
                        "grcl9v3_lowering_replay_v1",
                        checkpoint_index["family_extensions"]["grcl9v3"]["replay_version"],
                    )
                    checkpoint_path = checkpoint_index_path.parent / checkpoint_index[
                        "checkpoints"
                    ][-1]["path"]
                    checkpoint = _read_json(checkpoint_path)
                    self.assertIn("basin_mass", checkpoint["node_records"][0])
                    self.assertIn(
                        "basin_mass",
                        next(
                            iter(
                                checkpoint["family_extensions"]["grc9v3"][
                                    "node_overlay"
                                ].values()
                            )
                        ),
                    )
                    run_summary = _read_json(telemetry_root / "run_summary.json")
                    self.assertIn("grc9v3", run_summary["family_extensions"])
                    self.assertIn("grcl9v3", run_summary["family_extensions"])
                    self.assertEqual(
                        lane.fixture_name,
                        run_summary["family_extensions"]["grcl9v3"]["fixture_name"],
                    )
                    self.assertIn(
                        "expected_region_caches",
                        run_summary["family_extensions"]["grcl9v3"],
                    )

    def test_replay_session_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            kwargs = {
                "output_root": Path(tmpdir),
                "fixture_names": ("quiescent_hybrid_control_no_event_control",),
                "requested_steps": 1,
            }
            first = telemetry.run_grcl9v3_lowering_replay_session(
                session_id="S0001",
                **kwargs,
            )
            second = telemetry.run_grcl9v3_lowering_replay_session(
                session_id="S0002",
                **kwargs,
            )

            first_lane = first.lanes[0]
            second_lane = second.lanes[0]
            self.assertEqual(first_lane.run_id, second_lane.run_id)
            self.assertEqual(first_lane.event_counts_by_kind, second_lane.event_counts_by_kind)
            self.assertEqual(
                _read_json(Path(first_lane.replay_report_path))["final_snapshot_digest"],
                _read_json(Path(second_lane.replay_report_path))["final_snapshot_digest"],
            )
            log_text = first.experimental_log_path.read_text(encoding="utf-8")
            self.assertIn("| S0001 |", log_text)
            self.assertIn("| S0002 |", log_text)

    def test_replay_session_can_use_seed_backed_landscape_examples(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = telemetry.run_grcl9v3_lowering_replay_session(
                session_id="S0004",
                output_root=Path(tmpdir),
                fixture_names=(
                    "corrected_front_growth_positive_control",
                    "quiescent_hybrid_control_no_event_control",
                ),
                requested_steps=1,
                source_mode="landscape_seed_examples",
            )

            manifest = _read_json(result.session_manifest_path)
            self.assertEqual("landscape_seed_examples", manifest["source_mode"])
            self.assertIn("--source-mode landscape_seed_examples", manifest["replay_command"])
            self.assertTrue(
                (result.session_root / "grcl9v3_landscape_examples").is_dir()
            )
            self.assertTrue(
                (result.session_root / "grcl9v3_landscape_seeds").is_dir()
            )
            seed_names = {
                path.name
                for path in (result.session_root / "grcl9v3_landscape_seeds").iterdir()
            }
            self.assertIn(
                "grcl9v3-corrected-front-growth-positive.seed.yaml",
                seed_names,
            )
            self.assertIn("grcl9v3-quiescent-hybrid-control.seed.yaml", seed_names)

            for lane in result.lanes:
                source = _read_json(Path(lane.source_fixture_path))
                provenance = source["compiled_source_provenance"]
                self.assertIn("source_seed_reference", provenance)
                self.assertIn(
                    "configs/landscapes/seed/grcl9v3-",
                    provenance["source_seed_reference"],
                )
                example_path = (
                    result.session_root
                    / "grcl9v3_landscape_examples"
                    / f"{lane.fixture_name}.json"
                )
                self.assertTrue(example_path.exists())

    def test_replay_session_can_run_hessian_backend_probe_pairs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = telemetry.run_grcl9v3_lowering_replay_session(
                session_id="S0013",
                output_root=Path(tmpdir),
                fixture_names=(
                    "hessian_probe_anisotropic_spark_row_basis_control",
                    "hessian_probe_anisotropic_spark_weighted_least_squares_control",
                ),
                requested_steps=1,
                source_mode="hessian_backend_probe",
            )

            self.assertEqual(2, len(result.lanes))
            manifest = _read_json(result.session_manifest_path)
            self.assertEqual("hessian_backend_probe", manifest["source_mode"])
            self.assertIn("--source-mode hessian_backend_probe", manifest["replay_command"])
            report_path = Path(
                manifest["extra_report_paths"]["hessian_backend_probe_report"]
            )
            self.assertTrue(report_path.exists())
            report = _read_json(report_path)
            self.assertEqual("grcl9v3_hessian_backend_probe_report_v1", report["report_version"])
            self.assertEqual(1, report["complete_pair_count"])
            self.assertEqual(["anisotropic_spark"], report["ranked_pair_ids_by_largest_delta"])

            by_lane = {lane.fixture_name: lane for lane in result.lanes}
            row_steps = _read_jsonl(
                Path(by_lane["hessian_probe_anisotropic_spark_row_basis_control"].artifact_root)
                / "telemetry"
                / "steps.jsonl"
            )
            wls_steps = _read_jsonl(
                Path(
                    by_lane[
                        "hessian_probe_anisotropic_spark_weighted_least_squares_control"
                    ].artifact_root
                )
                / "telemetry"
                / "steps.jsonl"
            )
            self.assertEqual(
                "row_basis_diagonal",
                row_steps[0]["family_extensions"]["grc9v3"]["backend_config"][
                    "hessian_backend"
                ],
            )
            self.assertEqual(
                "weighted_least_squares",
                wls_steps[0]["family_extensions"]["grc9v3"]["backend_config"][
                    "hessian_backend"
                ],
            )

    def test_replay_session_can_run_collapse_learning_probe(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = telemetry.run_grcl9v3_lowering_replay_session(
                session_id="S0035",
                output_root=Path(tmpdir),
                fixture_names=(
                    "collapse_learning_probe_lambda_005_control",
                    "collapse_learning_probe_lambda_020_control",
                ),
                requested_steps=1,
                source_mode="collapse_learning_probe",
            )

            self.assertEqual(2, len(result.lanes))
            manifest = _read_json(result.session_manifest_path)
            self.assertEqual("collapse_learning_probe", manifest["source_mode"])
            self.assertIn("--source-mode collapse_learning_probe", manifest["replay_command"])
            report_path = Path(
                manifest["extra_report_paths"]["collapse_learning_probe_report"]
            )
            self.assertTrue(report_path.exists())
            report = _read_json(report_path)
            self.assertEqual(
                "grcl9v3_collapse_learning_probe_report_v1",
                report["report_version"],
            )
            self.assertEqual(
                "multi_center_delayed_collapse_learning",
                report["source_fixture"],
            )
            self.assertEqual(2, report["lane_count"])
            lambdas = {lane["lambda_birth"] for lane in report["lanes"]}
            self.assertEqual({0.05, 0.2}, lambdas)

            for lane in result.lanes:
                source = _read_json(Path(lane.source_fixture_path))
                notes = source["notes"]
                self.assertEqual(
                    "multi_center_delayed_collapse_learning",
                    notes["collapse_learning_probe_source_fixture"],
                )
                self.assertEqual(
                    notes["collapse_learning_probe_lambda_birth"],
                    notes["runtime_diagnostic_overrides"]["lambda_birth"],
                )

    def test_replay_session_can_run_growth_collapse_relay_probe(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = telemetry.run_grcl9v3_lowering_replay_session(
                session_id="S0038",
                output_root=Path(tmpdir),
                fixture_names=("growth_collapse_relay_probe_lambda_020_control",),
                requested_steps=1,
                source_mode="growth_collapse_relay_probe",
            )

            self.assertEqual(1, len(result.lanes))
            manifest = _read_json(result.session_manifest_path)
            self.assertEqual("growth_collapse_relay_probe", manifest["source_mode"])
            self.assertIn(
                "--source-mode growth_collapse_relay_probe",
                manifest["replay_command"],
            )
            report_path = Path(
                manifest["extra_report_paths"]["growth_collapse_relay_probe_report"]
            )
            self.assertTrue(report_path.exists())
            report = _read_json(report_path)
            self.assertEqual(
                "grcl9v3_growth_collapse_relay_probe_report_v1",
                report["report_version"],
            )
            self.assertEqual(1, report["lane_count"])
            lane_summary = report["lanes"][0]
            self.assertIn("growth_child_later_collapsed_sink_count", lane_summary)
            self.assertIn("collapsed_sink_later_growth_parent_count", lane_summary)
            self.assertIn("full_growth_collapse_relay_count", lane_summary)

            source = _read_json(Path(result.lanes[0].source_fixture_path))
            notes = source["notes"]
            self.assertEqual(
                "multi_center_delayed_collapse_learning",
                notes["relay_probe_source_fixture"],
            )
            self.assertEqual(
                [
                    "growth_events",
                    "choice_collapse_events",
                    "basin_assignment_learning",
                    "growth_collapse_relay_diagnostics",
                ],
                notes["relay_probe_expected_selector_ids"],
            )

    def test_replay_session_can_run_quarantined_legacy_growth_seed(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = telemetry.run_grcl9v3_lowering_replay_session(
                session_id="S0092",
                output_root=Path(tmpdir),
                fixture_names=("multi_center_delayed_collapse_learning",),
                requested_steps=1,
                source_mode="legacy_growth_landscape_seed_examples",
            )

            self.assertEqual(1, len(result.lanes))
            manifest = _read_json(result.session_manifest_path)
            self.assertEqual(
                "legacy_growth_landscape_seed_examples",
                manifest["source_mode"],
            )
            self.assertIn(
                "legacy/grcl9v3-overaggressive-growth",
                " ".join(manifest["input_documents"]),
            )
            self.assertIn(
                "--source-mode legacy_growth_landscape_seed_examples",
                manifest["replay_command"],
            )

    def test_pressure_boundary_source_metadata_is_mirrored_into_replay_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            lane = _run_replay_lane(
                source=_pressure_boundary_source_document(),
                requested_steps=1,
                session_id="S0041",
                lanes_root=root / "lanes",
                sources_root=root / "source_fixtures",
                lowered_root=root / "lowered_states",
                reports_root=root / "reports",
            )

            summary = _read_json(Path(lane.artifact_root) / "telemetry" / "run_summary.json")
            lifecycle = summary["family_extensions"]["grc9v3"]["lifecycle_event_counts"]
            grcl9v3 = summary["family_extensions"]["grcl9v3"]
            sources = grcl9v3["growth_parent_capacity_sources"]

            self.assertEqual("front_capacity", grcl9v3["growth_semantics_status"])
            self.assertEqual(
                "grcl9v3_front_capacity",
                grcl9v3["growth_parent_eligibility_mode"],
            )
            self.assertIn(
                "grcl9v3_expected_pressure_boundary_region_ids",
                grcl9v3["expected_region_cache_names"],
            )
            self.assertTrue(
                any(
                    record["front_capacity_source"] == "pressure_boundary"
                    for record in sources.values()
                )
            )
            self.assertEqual(1, lane.event_counts_by_kind["growth"])
            self.assertEqual(1, lifecycle["front_capacity_growth_count"])
            self.assertEqual(1, lifecycle["pressure_boundary_growth_count"])
            self.assertEqual(0, lifecycle["legacy_broad_growth_count"])

    def test_replay_session_can_run_pressure_boundary_probe_source_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = telemetry.run_grcl9v3_lowering_replay_session(
                session_id="S0042",
                output_root=Path(tmpdir),
                source_mode="pressure_boundary_probe",
                fixture_names=("pressure_boundary_growth_positive_control",),
                requested_steps=1,
            )

            self.assertEqual(1, len(result.lanes))
            manifest = _read_json(result.session_manifest_path)
            self.assertEqual("pressure_boundary_probe", manifest["source_mode"])
            self.assertIn("--source-mode pressure_boundary_probe", manifest["replay_command"])
            lane = result.lanes[0]
            self.assertEqual(1, lane.event_counts_by_kind.get("growth"))
            summary = _read_json(Path(lane.artifact_root) / "telemetry" / "run_summary.json")
            lifecycle = summary["family_extensions"]["grc9v3"][
                "lifecycle_event_counts"
            ]
            grcl9v3 = summary["family_extensions"]["grcl9v3"]
            self.assertEqual(1, lifecycle["front_capacity_growth_count"])
            self.assertEqual(1, lifecycle["pressure_boundary_growth_count"])
            self.assertEqual(0, lifecycle["legacy_broad_growth_count"])
            self.assertEqual(
                "grcl9v3_front_capacity",
                grcl9v3["growth_parent_eligibility_mode"],
            )
            self.assertTrue(
                any(
                    record["front_capacity_source"] == "pressure_boundary"
                    for record in grcl9v3["growth_parent_capacity_sources"].values()
                )
            )

    def test_replay_session_can_run_relay_port_probe(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = telemetry.run_grcl9v3_lowering_replay_session(
                session_id="S0040",
                output_root=Path(tmpdir),
                fixture_names=("relay_port_probe_support_040_alpha_035_control",),
                requested_steps=1,
                source_mode="relay_port_probe",
            )

            self.assertEqual(1, len(result.lanes))
            manifest = _read_json(result.session_manifest_path)
            self.assertEqual("relay_port_probe", manifest["source_mode"])
            self.assertIn("--source-mode relay_port_probe", manifest["replay_command"])
            report_path = Path(manifest["extra_report_paths"]["relay_port_probe_report"])
            self.assertTrue(report_path.exists())
            report = _read_json(report_path)
            self.assertEqual(
                "grcl9v3_relay_port_probe_report_v1",
                report["report_version"],
            )
            self.assertEqual(1, report["lane_count"])
            source = _read_json(Path(result.lanes[0].source_fixture_path))
            notes = source["notes"]
            self.assertEqual(
                "multi_center_delayed_collapse_learning",
                notes["relay_port_probe_source_fixture"],
            )
            self.assertEqual(
                "relay_port",
                notes["relay_port_probe_growth_profile"]["geometry"],
            )
            self.assertEqual(
                notes["relay_port_probe_runtime_overrides"]["alpha_seed"],
                notes["runtime_diagnostic_overrides"]["alpha_seed"],
            )
            growth_constructs = [
                construct
                for construct in source["constructs"]
                if construct["construct_kind"] == "growth_locus"
            ]
            self.assertTrue(growth_constructs)
            self.assertTrue(
                all(
                    construct["outward_pressure_profile"]["geometry"] == "relay_port"
                    for construct in growth_constructs
                )
            )

    def test_relay_role_summary_orders_by_step_before_event_index(self) -> None:
        summary = _relay_role_summary(
            (
                {
                    "event_index": 4,
                    "step_index": 0,
                    "event_kind": "growth",
                    "payload": {"parent_node_id": 7, "child_node_id": 9},
                },
                {
                    "event_index": 0,
                    "step_index": 1,
                    "event_kind": "collapse",
                    "payload": {"collapsed_sink_id": 7},
                },
            )
        )

        self.assertEqual(0, summary["collapsed_sink_later_growth_parent_count"])

    def test_first_event_after_orders_by_step_before_event_index(self) -> None:
        growth = {"event_index": 9, "step_index": 0, "event_kind": "growth"}
        later_collapse = {"event_index": 0, "step_index": 1, "event_kind": "collapse"}

        self.assertEqual(
            later_collapse,
            _first_event_after((growth, later_collapse), "collapse", growth),
        )


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _pressure_boundary_source_document() -> GRCL9V3SourceDocument:
    return GRCL9V3SourceDocument(
        fixture_name="pressure_boundary_growth_fixture",
        manifest_entry_id="composed_grcl9v3_hybrid_composition_v1",
        expected_selector_ids=("pressure_boundary_growth_provenance",),
        constructs=(
            GRCL9V3GrowthLocus(
                construct_id="pressure_boundary_growth",
                motif_id="grc9v3-motif-s0006-growth-pressure-positive-control",
                source_role="positive_control",
                ownership="grc9_mechanical",
                parent_region_id="pressure_parent",
                inactive_parent_port=6,
                outward_pressure_profile={
                    "pressure": "boundary_front",
                    "support_conductance": 2.0,
                    "support_flux": 2.0,
                },
                lambda_birth=1.0,
                growth_semantics="front_capacity",
                front_capacity_source="pressure_boundary",
            ),
        ),
        compiled_source_provenance={
            "composed_source_ancestry": ("pressure_boundary", "growth")
        },
    )


if __name__ == "__main__":
    unittest.main()

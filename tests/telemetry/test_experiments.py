"""Telemetry experiment and trace tests for the telemetry phase."""

from __future__ import annotations

import contextlib
from dataclasses import dataclass
import io
import json
from pathlib import Path
import tempfile
from typing import Any, Callable
import unittest

from pygrc import telemetry
from pygrc.core import digest_snapshot
from pygrc.telemetry import experiments as telemetry_experiments
from tests.telemetry._experiments_test_support import (
    RICH_BASIN_BOUNDARY_CHANNEL_SEED,
    RICH_COLLAPSE_EXAMPLE_SEED,
    RICH_V3_WEAK_TO_STABLE_SEED,
    RICH_V4_ASYMMETRIC_CENTER_COUPLING_SEED,
    RICH_V4_ASYMMETRIC_CENTER_COUPLING_SINGLE_INTERMEDIATE_SEED,
    RICH_V4_ASYMMETRIC_PAIR_MEDIATION_SEED,
    RICH_V4_ASYMMETRIC_PAIR_MEDIATION_SINGLE_INTERMEDIATE_SEED,
    RICH_V4_CARRIER_SITE_SETTLEMENT_REGIME_SEED,
    RICH_V4_CARRIER_SITE_SPLIT_CHILD_INHERITING_SETTLEMENT_SEED,
    RICH_V4_CENTER_COUPLING_SEED,
    RICH_V4_MEDIATED_SPILL_BRANCH_FAN_IN_SEED,
    RICH_V4_MEDIATED_SPILL_BRANCH_SEED,
    RICH_V4_MEDIATED_SPILL_BRANCH_SINGLE_INTERMEDIATE_SEED,
    RICH_V4_OPEN_CENTER_CONTROL_SEED,
    RICH_V4_OPEN_CENTER_SINGLE_INTERMEDIATE_SEED,
    RICH_V4_PATH_NODE_ANCHORED_SETTLEMENT_SEED,
    RICH_V4_PATH_NODE_SETTLEMENT_REGIME_SINGLE_INTERMEDIATE_SEED,
    RICH_V4_PATH_NODE_SPLIT_CHILD_INHERITING_SETTLEMENT_SEED,
    RICH_V4_ROLE_LOCKED_ASYMMETRIC_PAIR_MEDIATION_SEED,
    RICH_V4_ROLE_LOCKED_ASYMMETRIC_PAIR_MEDIATION_SINGLE_INTERMEDIATE_SEED,
    RICH_V4_ROLE_LOCKED_MEDIATED_SPILL_BRANCH_SEED,
    RICH_V4_ROLE_LOCKED_MEDIATED_SPILL_BRANCH_SINGLE_INTERMEDIATE_SEED,
    RICH_V4_SINGLE_INTERMEDIATE_SEED,
    RICH_V4_TRANSFER_MEDIATION_SEED,
    _load_grcv3_broad_collapse_survey_script_module,
    _load_grcv3_candidate_transition_trace_script_module,
    _load_grcv3_collapse_regime_trace_script_module,
    _load_grcv3_landscape_script_module,
    _load_grcv3_path_failure_trace_script_module,
    _load_grcv3_post_collapse_geometry_exclusion_trace_script_module,
    _load_grcv3_post_spark_collapse_boundary_trace_script_module,
    _load_grcv3_post_spark_delay_authorability_trace_script_module,
    _load_grcv3_post_spark_late_window_stability_trace_script_module,
    _load_grcv3_pre_spark_collapse_decomposition_trace_script_module,
    _load_grcv3_representative_script_module,
    _load_grcv3_secondary_support_authorability_trace_script_module,
    _load_grcv3_settlement_locus_trace_script_module,
    _load_grcv3_settlement_reentry_neighborhood_trace_script_module,
    _load_grcv3_settlement_reentry_secondary_support_counterfactual_trace_script_module,
    _load_grcv3_settlement_reentry_support_isolation_trace_script_module,
    _load_grcv3_settlement_reentry_trace_script_module,
)


class TelemetryRepresentativeExperimentTest(unittest.TestCase):
    """Representative experiment coverage."""

    def test_run_grc9_representative_experiment_emits_artifacts_and_eventful_reports(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = telemetry.run_grc9_representative_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                lane_name="phase6_mechanical_baseline",
                num_steps=4,
            )

            self.assertEqual("phase6_mechanical_baseline", result.lane_name)
            self.assertEqual(4, result.num_steps)
            self.assertIsNotNone(result.primary_run.telemetry.artifact_layout)
            self.assertIsNotNone(result.replay_run.telemetry.artifact_layout)
            primary_layout = result.primary_run.telemetry.artifact_layout
            replay_layout = result.replay_run.telemetry.artifact_layout
            assert primary_layout is not None
            assert replay_layout is not None

            self.assertEqual(
                Path(temp_dir)
                / "outputs"
                / "representative"
                / "grc9"
                / "phase6_mechanical_baseline"
                / "primary",
                primary_layout.root_dir,
            )
            self.assertEqual(
                Path(temp_dir)
                / "outputs"
                / "representative"
                / "grc9"
                / "phase6_mechanical_baseline"
                / "replay",
                replay_layout.root_dir,
            )
            self.assertTrue(primary_layout.step_rows_path.exists())
            self.assertTrue(primary_layout.event_rows_path.exists())
            self.assertTrue(primary_layout.run_summary_path.exists())
            self.assertTrue(primary_layout.experiment_report_path.exists())
            self.assertTrue(primary_layout.comparison_report_path.exists())
            self.assertTrue(replay_layout.step_rows_path.exists())
            self.assertTrue(replay_layout.event_rows_path.exists())
            self.assertTrue(replay_layout.run_summary_path.exists())
            self.assertTrue(replay_layout.experiment_report_path.exists())
            self.assertTrue(replay_layout.comparison_report_path.exists())

            loaded_primary_steps = telemetry.load_step_rows(primary_layout.step_rows_path)
            loaded_primary_events = telemetry.load_event_rows(primary_layout.event_rows_path)
            loaded_primary_summary = telemetry.load_run_summary(primary_layout.run_summary_path)
            loaded_primary_report = telemetry.load_experiment_report(
                primary_layout.experiment_report_path
            )
            loaded_comparison = telemetry.load_comparison_report(
                replay_layout.comparison_report_path
            )

        self.assertEqual(4, len(loaded_primary_steps))
        self.assertEqual(
            "phase6_iter10_v1",
            loaded_primary_steps[0].family_extensions["grc9"]["contract_version"],
        )
        self.assertEqual(
            "topology_updated_current_flux_diagnostic",
            loaded_primary_steps[0].family_extensions["grc9"]["abundance_contract"],
        )
        self.assertEqual(
            ("expansion", "growth", "spark"),
            tuple(sorted({row.event_kind for row in loaded_primary_events})),
        )
        self.assertEqual(
            "trajectory_summary_v1",
            loaded_primary_report.common["report_type"],
        )
        self.assertIn(
            "expansion_count",
            loaded_primary_report.common["changed_observables"],
        )
        self.assertIn(
            "column_profile_sparsity",
            loaded_primary_summary.final_observables,
        )
        self.assertEqual(
            result.primary_run.final_snapshot_digest,
            result.replay_run.final_snapshot_digest,
        )
        self.assertTrue(
            all(
                delta == 0.0
                for delta in loaded_comparison.common["final_observables_right_minus_left"].values()
            )
        )
        self.assertGreater(
            loaded_primary_summary.event_counts_by_kind["growth"],
            0,
        )
        self.assertEqual(
            1,
            loaded_primary_summary.event_counts_by_kind["expansion"],
        )

    def test_run_grc9_phase_t_representative_lane_emits_richer_extensions(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = telemetry.run_grc9_representative_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                lane_name=telemetry.DEFAULT_GRC9_PHASE_T_REPRESENTATIVE_LANE,
                num_steps=4,
            )
            primary_layout = result.primary_run.telemetry.artifact_layout
            replay_layout = result.replay_run.telemetry.artifact_layout
            assert primary_layout is not None
            assert replay_layout is not None

            self.assertEqual(
                Path(temp_dir)
                / "outputs"
                / "representative"
                / "grc9"
                / telemetry.DEFAULT_GRC9_PHASE_T_REPRESENTATIVE_LANE
                / "primary",
                primary_layout.root_dir,
            )
            self.assertTrue(primary_layout.step_rows_path.exists())
            self.assertTrue(primary_layout.event_rows_path.exists())
            self.assertTrue(primary_layout.run_summary_path.exists())
            self.assertTrue(primary_layout.experiment_report_path.exists())
            self.assertTrue(primary_layout.comparison_report_path.exists())
            self.assertTrue(replay_layout.step_rows_path.exists())
            self.assertTrue(replay_layout.run_summary_path.exists())

            loaded_primary_steps = telemetry.load_step_rows(primary_layout.step_rows_path)
            loaded_primary_events = telemetry.load_event_rows(primary_layout.event_rows_path)
            loaded_primary_summary = telemetry.load_run_summary(primary_layout.run_summary_path)
            loaded_comparison = telemetry.load_comparison_report(
                replay_layout.comparison_report_path
            )

        first_step_extension = loaded_primary_steps[0].family_extensions["grc9"]
        self.assertEqual(
            telemetry.GRC9_TELEMETRY_CONTRACT_VERSION,
            first_step_extension["contract_version"],
        )
        self.assertIn("backend_config", first_step_extension)
        self.assertIn("port_chart", first_step_extension)
        self.assertIn("column_diagnostic", first_step_extension)
        self.assertEqual(
            telemetry.DEFAULT_GRC9_PHASE_T_REPRESENTATIVE_LANE,
            first_step_extension["lane_context"]["lane_name"],
        )

        event_payloads = [row.family_extensions["grc9"] for row in loaded_primary_events]
        self.assertIn("spark_evidence", next(payload for payload in event_payloads if payload["event_domain"] == "spark"))
        expansion_payload = next(
            payload for payload in event_payloads if payload["event_domain"] == "expansion"
        )
        self.assertIn("reassigned_edge_count_by_column", expansion_payload["expansion_evidence"])
        growth_payload = next(
            payload for payload in event_payloads if payload["event_domain"] == "growth"
        )
        self.assertIn("birth_probability", growth_payload["growth_evidence"])

        summary_extension = loaded_primary_summary.family_extensions["grc9"]
        self.assertIn("lifecycle_event_counts", summary_extension)
        self.assertIn("expansion_summary", summary_extension)
        self.assertIn("growth_summary", summary_extension)
        self.assertEqual(
            result.primary_run.final_snapshot_digest,
            result.replay_run.final_snapshot_digest,
        )
        self.assertTrue(
            all(
                delta == 0.0
                for delta in loaded_comparison.common[
                    "final_observables_right_minus_left"
                ].values()
            )
        )

    def test_run_grc9_representative_experiment_can_emit_checkpoint_artifacts(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = telemetry.run_grc9_representative_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                lane_name=telemetry.DEFAULT_GRC9_PHASE_T_REPRESENTATIVE_LANE,
                num_steps=2,
                record_graph_checkpoints=True,
                checkpoint_every_n_steps=1,
                include_flow_overlays=True,
            )

            primary_telemetry = result.primary_run.telemetry
            replay_telemetry = result.replay_run.telemetry
            self.assertIsNotNone(primary_telemetry.graph_checkpoint_index)
            self.assertIsNotNone(replay_telemetry.graph_checkpoint_index)
            self.assertEqual(3, len(primary_telemetry.graph_checkpoints))
            self.assertEqual(3, len(replay_telemetry.graph_checkpoints))
            primary_layout = primary_telemetry.artifact_layout
            replay_layout = replay_telemetry.artifact_layout
            assert primary_layout is not None
            assert replay_layout is not None
            self.assertTrue(primary_layout.graph_checkpoint_index_path.exists())
            self.assertTrue(replay_layout.graph_checkpoint_index_path.exists())

            primary_pack = telemetry.load_telemetry_artifact_pack(primary_layout)
            replay_pack = telemetry.load_telemetry_artifact_pack(replay_layout)

        self.assertIsNotNone(primary_pack.graph_checkpoint_index)
        self.assertEqual(3, len(primary_pack.graph_checkpoints))
        self.assertEqual(
            ("initial", "interval", "final"),
            tuple(checkpoint.checkpoint_label for checkpoint in primary_pack.graph_checkpoints),
        )
        self.assertEqual("port_graph", primary_pack.graph_checkpoints[0].graph_kind)
        self.assertEqual(
            "fixed_nine_slot_port_chart",
            primary_pack.graph_checkpoints[0].layout_mode,
        )
        self.assertTrue(
            all(
                checkpoint.flow_representation
                in {"signed_edge_flux", "zero_signed_edge_flux"}
                for checkpoint in primary_pack.graph_checkpoints
            )
        )
        self.assertEqual(
            telemetry.GRC9_TELEMETRY_CONTRACT_VERSION,
            primary_pack.graph_checkpoints[0].family_extensions["grc9"][
                "contract_version"
            ],
        )
        self.assertEqual(3, len(replay_pack.graph_checkpoints))

    def test_build_grc9_diagnostic_probe_exercises_paper_facing_diagnostics(
        self,
    ) -> None:
        probe = telemetry.build_grc9_diagnostic_probe()

        self.assertEqual(
            telemetry.DEFAULT_GRC9_DIAGNOSTIC_PROBE_NAME,
            probe["probe_name"],
        )
        self.assertEqual(
            telemetry.GRC9_TELEMETRY_CONTRACT_VERSION,
            probe["contract_version"],
        )
        json.dumps(probe, sort_keys=True)

        identity = probe["step_extension"]["identity_abundance"]
        self.assertEqual(2.0, identity["scale_weighted_abundance_gamma"])
        self.assertGreater(identity["scale_weighted_abundance"], 0.0)

        expansion = probe["run_summary_extension"]["expansion_summary"]
        self.assertEqual(1, expansion["identity_fission_candidate_count"])
        self.assertEqual(1, expansion["identity_fission_confirmed_count"])
        self.assertEqual(2, expansion["identity_fission_max_persistence_steps"])

        calibration = probe["run_summary_extension"]["calibration_summary"]
        self.assertEqual("calibrated_fraction", calibration["spark_threshold_mode"])
        self.assertEqual(0.125, calibration["burn_in_M_H"])
        self.assertEqual(0.0625, calibration["burn_in_M_C"])

        sign_crossing = probe["sign_crossing_event_extensions"][0]
        self.assertEqual("spark", sign_crossing["event_domain"])
        self.assertTrue(sign_crossing["spark_evidence"]["sign_crossing_gate_pass"])
        self.assertEqual(
            "saturation_sign_crossing",
            sign_crossing["spark_evidence"]["spark_kind"],
        )

        coarse_checks = probe["coarse_reconstruction_checks"]
        self.assertEqual(0.0, coarse_checks["conductance"]["max_abs_error"])
        self.assertLessEqual(
            coarse_checks["signed_flux"]["max_abs_error"],
            1e-9,
        )
        self.assertEqual(
            "artifact_backed",
            probe["diagnostic_status"]["identity_fission_confirmed"],
        )
        self.assertNotIn("identity_fission_confirmed", probe["runtime_gaps"])
        self.assertEqual(
            "out_of_scope",
            probe["runtime_gaps"]["grcl9_lowering"],
        )
        self.assertEqual(
            "out_of_scope",
            probe["runtime_gaps"]["grc9v3_semantics"],
        )
        self.assertEqual(
            "out_of_scope",
            probe["runtime_gaps"]["lorentzian_causal_layer"],
        )

    def test_run_grcv2_representative_experiment_emits_artifacts_and_reports(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = telemetry.run_grcv2_representative_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                num_steps=3,
                family_name="balanced_baseline",
                rng_seed=7,
            )

            self.assertEqual("balanced_baseline", result.family_name)
            self.assertEqual(3, result.num_steps)
            self.assertIsNotNone(result.cell1_run.telemetry)
            self.assertIsNotNone(result.cell4_run.telemetry)
            assert result.cell1_run.telemetry is not None
            assert result.cell4_run.telemetry is not None
            self.assertIsNotNone(result.cell1_run.telemetry.artifact_layout)
            self.assertIsNotNone(result.cell4_run.telemetry.artifact_layout)
            cell1_layout = result.cell1_run.telemetry.artifact_layout
            cell4_layout = result.cell4_run.telemetry.artifact_layout
            assert cell1_layout is not None
            assert cell4_layout is not None
            self.assertEqual(
                Path(temp_dir)
                / "outputs"
                / "representative"
                / "grcv2"
                / "balanced_baseline"
                / "cell-1",
                cell1_layout.root_dir,
            )
            self.assertEqual(
                Path(temp_dir)
                / "outputs"
                / "representative"
                / "grcv2"
                / "balanced_baseline"
                / "cell-4",
                cell4_layout.root_dir,
            )

            self.assertTrue(cell1_layout.step_rows_path.exists())
            self.assertTrue(cell1_layout.event_rows_path.exists())
            self.assertTrue(cell1_layout.run_summary_path.exists())
            self.assertTrue(cell1_layout.experiment_report_path.exists())
            self.assertTrue(cell1_layout.comparison_report_path.exists())
            self.assertTrue(cell4_layout.step_rows_path.exists())
            self.assertTrue(cell4_layout.event_rows_path.exists())
            self.assertTrue(cell4_layout.run_summary_path.exists())
            self.assertTrue(cell4_layout.experiment_report_path.exists())
            self.assertTrue(cell4_layout.comparison_report_path.exists())

            loaded_cell1_events = telemetry.load_event_rows(cell1_layout.event_rows_path)
            loaded_cell4_events = telemetry.load_event_rows(cell4_layout.event_rows_path)
            loaded_cell1_report = telemetry.load_experiment_report(
                cell1_layout.experiment_report_path
            )
            loaded_cell4_report = telemetry.load_experiment_report(
                cell4_layout.experiment_report_path
            )
            loaded_comparison = telemetry.load_comparison_report(
                cell4_layout.comparison_report_path
            )

        self.assertEqual("trajectory_summary_v1", loaded_cell1_report.common["report_type"])
        self.assertEqual("trajectory_summary_v1", loaded_cell4_report.common["report_type"])
        self.assertEqual("run_summary_comparison_v1", loaded_comparison.common["report_type"])
        self.assertEqual((), loaded_cell1_events)
        self.assertEqual((), loaded_cell4_events)
        self.assertIn("resolved_params", loaded_cell1_report.common)
        self.assertIn("raw_params", loaded_cell1_report.common)
        self.assertIn("parameter_overrides", loaded_cell1_report.common)
        self.assertIn("left_resolved_params", loaded_comparison.common)
        self.assertIn("right_resolved_params", loaded_comparison.common)
        self.assertEqual(3, loaded_cell1_report.common["checkpoint_overview"]["step_count"])
        self.assertEqual(3, loaded_cell4_report.common["checkpoint_overview"]["step_count"])
        self.assertIn(
            "average_conductance",
            loaded_cell4_report.common["numeric_observable_trajectory"],
        )
        self.assertIn(
            "final_observables_right_minus_left",
            loaded_comparison.common,
        )

    def test_run_grcv2_representative_experiment_defaults_to_behavior_only_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = telemetry.run_grcv2_representative_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                num_steps=3,
                family_name="balanced_baseline",
                rng_seed=7,
            )

            assert result.cell1_run.telemetry is not None
            assert result.cell4_run.telemetry is not None
            cell1_layout = result.cell1_run.telemetry.artifact_layout
            cell4_layout = result.cell4_run.telemetry.artifact_layout
            assert cell1_layout is not None
            assert cell4_layout is not None

            self.assertIsNone(result.cell1_run.telemetry.graph_checkpoint_index)
            self.assertEqual((), result.cell1_run.telemetry.graph_checkpoints)
            self.assertIsNone(result.cell4_run.telemetry.graph_checkpoint_index)
            self.assertEqual((), result.cell4_run.telemetry.graph_checkpoints)
            self.assertFalse(cell1_layout.graph_checkpoint_index_path.exists())
            self.assertFalse(cell4_layout.graph_checkpoint_index_path.exists())

    def test_run_grcv3_representative_experiment_emits_artifacts_and_replay_stable_reports(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = telemetry.run_grcv3_representative_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                lane_name="phase5_reference",
                num_steps=3,
            )

            self.assertEqual("phase5_reference", result.lane_name)
            self.assertEqual(3, result.num_steps)
            self.assertIsNotNone(result.primary_run.telemetry.artifact_layout)
            self.assertIsNotNone(result.replay_run.telemetry.artifact_layout)
            primary_layout = result.primary_run.telemetry.artifact_layout
            replay_layout = result.replay_run.telemetry.artifact_layout
            assert primary_layout is not None
            assert replay_layout is not None

            self.assertEqual(
                Path(temp_dir)
                / "outputs"
                / "representative"
                / "grcv3"
                / "phase5_reference"
                / "primary",
                primary_layout.root_dir,
            )
            self.assertEqual(
                Path(temp_dir)
                / "outputs"
                / "representative"
                / "grcv3"
                / "phase5_reference"
                / "replay",
                replay_layout.root_dir,
            )
            self.assertTrue(primary_layout.step_rows_path.exists())
            self.assertTrue(primary_layout.event_rows_path.exists())
            self.assertTrue(primary_layout.run_summary_path.exists())
            self.assertTrue(primary_layout.experiment_report_path.exists())
            self.assertTrue(primary_layout.comparison_report_path.exists())
            self.assertTrue(replay_layout.step_rows_path.exists())
            self.assertTrue(replay_layout.event_rows_path.exists())
            self.assertTrue(replay_layout.run_summary_path.exists())
            self.assertTrue(replay_layout.experiment_report_path.exists())
            self.assertTrue(replay_layout.comparison_report_path.exists())

            loaded_primary_steps = telemetry.load_step_rows(primary_layout.step_rows_path)
            loaded_primary_events = telemetry.load_event_rows(primary_layout.event_rows_path)
            loaded_primary_summary = telemetry.load_run_summary(primary_layout.run_summary_path)
            loaded_primary_report = telemetry.load_experiment_report(
                primary_layout.experiment_report_path
            )
            loaded_comparison = telemetry.load_comparison_report(
                replay_layout.comparison_report_path
            )

        self.assertEqual(3, len(loaded_primary_steps))
        self.assertEqual((), loaded_primary_events)
        self.assertEqual("phase_t_iter26_v1", loaded_primary_steps[0].family_extensions["grcv3"]["contract_version"])
        self.assertIn("backend_summary", loaded_primary_steps[0].family_extensions["grcv3"])
        self.assertIn("final_basin_summary", loaded_primary_summary.family_extensions["grcv3"])
        self.assertEqual("trajectory_summary_v1", loaded_primary_report.common["report_type"])
        self.assertEqual("run_summary_comparison_v1", loaded_comparison.common["report_type"])
        self.assertEqual(
            result.primary_run.final_snapshot_digest,
            result.replay_run.final_snapshot_digest,
        )
        self.assertEqual(
            digest_snapshot(result.primary_run.model.snapshot()),
            digest_snapshot(result.replay_run.model.snapshot()),
        )
        self.assertTrue(
            all(
                delta == 0.0
                for delta in loaded_comparison.common["final_observables_right_minus_left"].values()
            )
        )
        self.assertEqual(
            0,
            loaded_comparison.common["total_event_count_right_minus_left"],
        )

    def test_run_grcv3_representative_experiment_can_emit_checkpoint_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = telemetry.run_grcv3_representative_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                lane_name="phase5_reference",
                num_steps=2,
                record_graph_checkpoints=True,
                checkpoint_every_n_steps=1,
                include_flow_overlays=True,
            )

            primary_telemetry = result.primary_run.telemetry
            replay_telemetry = result.replay_run.telemetry
            self.assertIsNotNone(primary_telemetry.graph_checkpoint_index)
            self.assertIsNotNone(replay_telemetry.graph_checkpoint_index)
            self.assertEqual(3, len(primary_telemetry.graph_checkpoints))
            self.assertEqual(3, len(replay_telemetry.graph_checkpoints))
            primary_layout = primary_telemetry.artifact_layout
            replay_layout = replay_telemetry.artifact_layout
            assert primary_layout is not None
            assert replay_layout is not None
            self.assertTrue(primary_layout.graph_checkpoint_index_path.exists())
            self.assertTrue(replay_layout.graph_checkpoint_index_path.exists())

            primary_pack = telemetry.load_telemetry_artifact_pack(primary_layout)
            replay_pack = telemetry.load_telemetry_artifact_pack(replay_layout)

        self.assertIsNotNone(primary_pack.graph_checkpoint_index)
        self.assertEqual(3, len(primary_pack.graph_checkpoints))
        self.assertEqual(
            ("initial", "interval", "final"),
            tuple(checkpoint.checkpoint_label for checkpoint in primary_pack.graph_checkpoints),
        )
        self.assertEqual("weighted_graph", primary_pack.graph_checkpoints[0].graph_kind)
        self.assertEqual(
            "not_available_pre_step",
            primary_pack.graph_checkpoints[0].flow_representation,
        )
        self.assertTrue(
            any(
                checkpoint.flow_representation == "signed_edge_flux"
                for checkpoint in primary_pack.graph_checkpoints[1:]
            )
        )
        self.assertIn("gradient_norm", primary_pack.graph_checkpoints[0].node_records[0])
        self.assertIn("net_flux", primary_pack.graph_checkpoints[0].node_records[0])
        self.assertIn("base_conductance", primary_pack.graph_checkpoints[0].edge_records[0])
        self.assertEqual(
            "phase_t_iter26_v1",
            primary_pack.graph_checkpoints[0].family_extensions["grcv3"]["contract_version"],
        )
        self.assertEqual(3, len(replay_pack.graph_checkpoints))

    def test_grcv3_representative_script_rejects_non_positive_steps(self) -> None:
        script_module = _load_grcv3_representative_script_module()
        stderr_buffer = io.StringIO()

        with self.assertRaises(SystemExit) as ctx:
            with contextlib.redirect_stderr(stderr_buffer):
                script_module.main(["--steps", "0"])

        self.assertEqual(2, ctx.exception.code)
        self.assertIn("--steps must be > 0", stderr_buffer.getvalue())

    def test_grcv3_basin_summary_does_not_fallback_to_node_count(self) -> None:
        model = telemetry_experiments._build_grcv3_representative_model()
        state = model.get_state()
        state.basins.clear()
        state.hierarchy.clear()
        state.cached_quantities["geometric_identity"] = {}

        summary = telemetry_experiments._build_grcv3_basin_summary(model)

        self.assertEqual(0, summary.active_basin_count)
        self.assertEqual(len(state.nodes), summary.attributed_node_count)

    def test_grcv3_rich_v4_probe_transient_observability_is_emitted(self) -> None:
        run = telemetry_experiments.run_grcv3_landscape_seed(
            RICH_V4_TRANSFER_MEDIATION_SEED,
            profile_name="seed_baseline",
            num_steps=50,
        )
        replay_model = telemetry_experiments.build_grcv3_from_landscape_seed(
            run.request.seed,
            params=telemetry_experiments._to_plain_data(run.model.get_params().raw_config),
            profile_name=run.request.profile_name,
            validate_seed=False,
        )
        replay_model.rebuild_basin_attributes()
        replay_model.rebuild_identity_state()
        initial_transient = telemetry_experiments._build_grcv3_landscape_step_observability(
            replay_model
        )
        step_transients = []
        for _ in range(50):
            replay_model.step()
            step_transients.append(
                telemetry_experiments._build_grcv3_landscape_step_observability(
                    replay_model
                )
            )

        step_extension = telemetry_experiments._build_grcv3_step_extension(
            replay_model,
            transient_landscape=step_transients[-1],
        )
        run_summary_extension = telemetry_experiments._build_grcv3_run_summary_extension(
            run.model,
            run.step_results,
            transient_landscape=telemetry_experiments._build_grcv3_landscape_run_summary(
                run.model,
                initial_observability=initial_transient,
                step_observability=tuple(step_transients),
                step_results=run.step_results,
            ),
        )

        self.assertIsNotNone(step_extension.transient_landscape)
        assert step_extension.transient_landscape is not None
        self.assertEqual(
            "transfer_mediation",
            step_extension.transient_landscape.monitoring_surface_kind,
        )
        self.assertTrue(
            any(
                site.primitive_id == "spindle_core"
                for site in step_extension.transient_landscape.observed_sites
            )
        )
        self.assertIsNotNone(run_summary_extension.transient_landscape)
        assert run_summary_extension.transient_landscape is not None
        self.assertEqual(
            "transfer_mediation",
            run_summary_extension.transient_landscape.monitoring_surface_kind,
        )
        self.assertIn(
            "spindle_core",
            run_summary_extension.transient_landscape.monitored_node_ids_by_primitive_id,
        )
        event_kinds = {
            observation.event_kind
            for observation in run_summary_extension.transient_landscape.event_aligned_observations
        }
        self.assertIn("spark_candidate", event_kinds)
        self.assertIn("spark", event_kinds)
        primitive_summary = next(
            summary
            for summary in run_summary_extension.transient_landscape.primitive_summaries
            if summary.primitive_id == "spindle_core"
        )
        self.assertIsNotNone(primitive_summary.first_spark_candidate_step)
        self.assertIsNotNone(primitive_summary.first_spark_step)
        self.assertIsNotNone(primitive_summary.first_split_init_step)


class TelemetryFailureTraceTest(unittest.TestCase):
    """Failure-trace and candidate-transition coverage."""

    def test_grcv3_rich_v4_path_failure_trace_identifies_geometry_failure(self) -> None:
        trace = telemetry.build_grcv3_landscape_path_failure_trace(
            baseline_seed_path=RICH_V4_TRANSFER_MEDIATION_SEED,
            comparison_seed_path=RICH_V4_SINGLE_INTERMEDIATE_SEED,
            profile_name="seed_baseline",
            primitive_id="spindle_core",
            num_steps=6,
        )

        self.assertEqual("spindle_core", trace["primitive_id"])
        self.assertEqual(6, trace["num_steps"])
        self.assertEqual(0, trace["earliest_material_divergence_step"])
        self.assertEqual(
            "probe_shell_gradient_norm_divergence",
            trace["earliest_material_divergence_reason"],
        )
        self.assertEqual(
            "probe_shell_ingress_arrives_but_fails_to_form_weak_axis_geometry",
            trace["diagnosed_failure_mode"],
        )
        step0 = next(step for step in trace["steps"] if step["step_index"] == 0)
        step1 = next(step for step in trace["steps"] if step["step_index"] == 1)
        self.assertGreater(
            abs(
                step0["baseline"]["probe_roles"]["north"]["gradient_norm"]
                - step0["comparison"]["probe_roles"]["north"]["gradient_norm"]
            ),
            0.1,
        )
        self.assertGreater(
            step1["baseline"]["edge_roles"]["basin_patch_load_carrier_transfer"][
                "total_abs_flux"
            ],
            0.0,
        )
        self.assertGreater(
            step1["comparison"]["edge_roles"]["basin_patch_transfer_path_egress"][
                "total_abs_flux"
            ],
            0.0,
        )
        self.assertLess(
            step1["baseline"]["center_site"]["min_signed_eigenvalue"],
            step1["comparison"]["center_site"]["min_signed_eigenvalue"],
        )

    def test_grcv3_rich_v4_open_center_path_failure_trace_keeps_the_same_geometry_failure(
        self,
    ) -> None:
        trace = telemetry.build_grcv3_landscape_path_failure_trace(
            baseline_seed_path=RICH_V4_OPEN_CENTER_CONTROL_SEED,
            comparison_seed_path=RICH_V4_OPEN_CENTER_SINGLE_INTERMEDIATE_SEED,
            profile_name="seed_baseline",
            primitive_id="spindle_core",
            num_steps=6,
        )

        self.assertEqual("spindle_core", trace["primitive_id"])
        self.assertEqual(6, trace["num_steps"])
        self.assertEqual(0, trace["earliest_material_divergence_step"])
        self.assertEqual(
            "probe_shell_gradient_norm_divergence",
            trace["earliest_material_divergence_reason"],
        )
        self.assertEqual(
            "probe_shell_ingress_arrives_but_fails_to_form_weak_axis_geometry",
            trace["diagnosed_failure_mode"],
        )
        step1 = next(step for step in trace["steps"] if step["step_index"] == 1)
        self.assertGreater(
            step1["baseline"]["edge_roles"]["basin_patch_load_carrier_transfer"][
                "total_abs_flux"
            ],
            0.0,
        )
        self.assertGreater(
            step1["comparison"]["edge_roles"]["basin_patch_transfer_path_egress"][
                "total_abs_flux"
            ],
            0.0,
        )
        self.assertLess(
            step1["baseline"]["center_site"]["min_signed_eigenvalue"],
            step1["comparison"]["center_site"]["min_signed_eigenvalue"],
        )

    def test_grcv3_rich_v4_asymmetric_center_coupling_trace_moves_the_path_lane_to_a_later_failure_mode(
        self,
    ) -> None:
        trace = telemetry.build_grcv3_landscape_path_failure_trace(
            baseline_seed_path=RICH_V4_ASYMMETRIC_CENTER_COUPLING_SEED,
            comparison_seed_path=RICH_V4_ASYMMETRIC_CENTER_COUPLING_SINGLE_INTERMEDIATE_SEED,
            profile_name="seed_baseline",
            primitive_id="spindle_core",
            num_steps=6,
        )

        self.assertEqual("spindle_core", trace["primitive_id"])
        self.assertEqual(6, trace["num_steps"])
        self.assertEqual(0, trace["earliest_material_divergence_step"])
        self.assertEqual(
            "probe_shell_gradient_norm_divergence",
            trace["earliest_material_divergence_reason"],
        )
        self.assertEqual(
            "final_candidate_transition_blocked_after_geometry_near_correct",
            trace["diagnosed_failure_mode"],
        )
        step1 = next(step for step in trace["steps"] if step["step_index"] == 1)
        self.assertGreater(
            step1["baseline"]["edge_roles"]["basin_patch_load_carrier_transfer"][
                "total_abs_flux"
            ],
            0.0,
        )
        self.assertGreater(
            step1["comparison"]["edge_roles"]["basin_patch_transfer_path_egress"][
                "total_abs_flux"
            ],
            0.0,
        )
        self.assertLess(step1["baseline"]["center_site"]["min_signed_eigenvalue"], 0.0)
        self.assertLess(step1["comparison"]["center_site"]["min_signed_eigenvalue"], 0.0)

    def test_grcv3_rich_v4_candidate_transition_trace_identifies_unsettled_candidate_sites(
        self,
    ) -> None:
        trace = telemetry.build_grcv3_landscape_candidate_transition_trace(
            baseline_seed_path=RICH_V4_ASYMMETRIC_CENTER_COUPLING_SEED,
            comparison_seed_path=RICH_V4_ASYMMETRIC_CENTER_COUPLING_SINGLE_INTERMEDIATE_SEED,
            profile_name="seed_baseline",
            primitive_id="spindle_core",
            num_steps=12,
        )

        self.assertEqual("spindle_core", trace["primitive_id"])
        self.assertEqual(12, trace["num_steps"])
        self.assertEqual(6, trace["baseline_first_candidate_step"])
        self.assertEqual(
            "candidate_sites_never_settle_enough_to_enter_spark_gate",
            trace["diagnosed_transition_blocker"],
        )
        self.assertEqual(
            7,
            trace["baseline_center_negative_curvature_run_length_at_candidate_step"],
        )
        self.assertEqual(
            7,
            trace["comparison_center_negative_curvature_run_length_at_baseline_candidate_step"],
        )
        self.assertEqual(2, len(trace["baseline_candidate_sites"]))
        first_site = trace["baseline_candidate_sites"][0]
        self.assertIn(
            first_site["baseline_site"]["realized_key"],
            {"spindle_core::carrier:0", "spindle_core::carrier:2"},
        )
        self.assertTrue(first_site["baseline_site"]["candidate_gate_pass"])
        self.assertIsNotNone(first_site["comparison_site"])
        comparison_site = first_site["comparison_site"]
        assert comparison_site is not None
        self.assertFalse(comparison_site["candidate_gate_pass"])
        self.assertFalse(comparison_site["gradient_below_threshold"])
        self.assertGreater(
            comparison_site["gradient_norm"],
            first_site["baseline_site"]["gradient_norm"],
        )

    def test_grcv3_rich_v4_asymmetric_pair_mediation_trace_localizes_direct_candidate_site_but_not_path_settlement(
        self,
    ) -> None:
        trace = telemetry.build_grcv3_landscape_candidate_transition_trace(
            baseline_seed_path=RICH_V4_ASYMMETRIC_PAIR_MEDIATION_SEED,
            comparison_seed_path=RICH_V4_ASYMMETRIC_PAIR_MEDIATION_SINGLE_INTERMEDIATE_SEED,
            profile_name="seed_baseline",
            primitive_id="spindle_core",
            num_steps=12,
        )

        self.assertEqual("spindle_core", trace["primitive_id"])
        self.assertEqual(12, trace["num_steps"])
        self.assertEqual(8, trace["baseline_first_candidate_step"])
        self.assertEqual(
            "candidate_sites_never_settle_enough_to_enter_spark_gate",
            trace["diagnosed_transition_blocker"],
        )
        self.assertEqual(1, len(trace["baseline_candidate_sites"]))
        first_site = trace["baseline_candidate_sites"][0]
        self.assertEqual(
            "spindle_core::carrier:0",
            first_site["baseline_site"]["realized_key"],
        )
        self.assertTrue(first_site["baseline_site"]["candidate_gate_pass"])
        self.assertIsNotNone(first_site["comparison_site"])
        comparison_site = first_site["comparison_site"]
        assert comparison_site is not None
        self.assertFalse(comparison_site["candidate_gate_pass"])
        self.assertFalse(comparison_site["gradient_below_threshold"])
        self.assertGreater(
            comparison_site["gradient_norm"],
            first_site["baseline_site"]["gradient_norm"],
        )

    def test_grcv3_rich_v4_mediated_spill_branch_trace_recovers_path_candidate_at_path_node(
        self,
    ) -> None:
        trace = telemetry.build_grcv3_landscape_candidate_transition_trace(
            baseline_seed_path=RICH_V4_MEDIATED_SPILL_BRANCH_SEED,
            comparison_seed_path=RICH_V4_MEDIATED_SPILL_BRANCH_SINGLE_INTERMEDIATE_SEED,
            profile_name="seed_baseline",
            primitive_id="spindle_core",
            num_steps=12,
        )

        self.assertEqual(8, trace["baseline_first_candidate_step"])
        self.assertEqual(5, trace["comparison_first_candidate_step"])
        self.assertEqual(
            "candidate_sites_never_settle_enough_to_enter_spark_gate",
            trace["diagnosed_transition_blocker"],
        )
        self.assertEqual(1, len(trace["comparison_candidate_sites"]))
        comparison_site = trace["comparison_candidate_sites"][0]["comparison_site"]
        self.assertEqual("basin_transfer_path_node", comparison_site["motif_role"])
        self.assertTrue(
            str(comparison_site["realized_key"]).startswith("spindle_core::transfer_path:")
        )
        self.assertTrue(comparison_site["candidate_gate_pass"])


class TelemetrySettlementTraceTest(unittest.TestCase):
    """Settlement-locus and reentry coverage."""

    def test_grcv3_rich_v4_settlement_locus_regime_trace_distinguishes_carrier_and_path_regimes(
        self,
    ) -> None:
        trace = telemetry.build_grcv3_landscape_settlement_locus_regime_trace(
            baseline_seed_path=RICH_V4_MEDIATED_SPILL_BRANCH_SEED,
            comparison_seed_path=RICH_V4_MEDIATED_SPILL_BRANCH_SINGLE_INTERMEDIATE_SEED,
            profile_name="seed_baseline",
            primitive_id="spindle_core",
            num_steps=12,
        )

        baseline_regime = trace["baseline_regime"]
        comparison_regime = trace["comparison_regime"]

        self.assertEqual("carrier_site_regime", baseline_regime["regime_label"])
        self.assertEqual("path_node_regime", comparison_regime["regime_label"])
        self.assertEqual(8, baseline_regime["first_event_steps"]["spark_candidate"])
        self.assertEqual(9, baseline_regime["first_event_steps"]["split_complete"])
        self.assertEqual(5, comparison_regime["first_event_steps"]["spark_candidate"])
        self.assertEqual(6, comparison_regime["first_event_steps"]["split_complete"])
        self.assertEqual(
            "carrier_site",
            baseline_regime["first_lifecycle_anchor"]["site"]["site_kind"],
        )
        self.assertEqual(
            "path_node",
            comparison_regime["first_lifecycle_anchor"]["site"]["site_kind"],
        )
        self.assertTrue(
            baseline_regime["first_lifecycle_anchor"]["stable_through_split_complete"]
        )
        self.assertTrue(
            comparison_regime["first_lifecycle_anchor"]["stable_through_split_complete"]
        )
        self.assertEqual(
            0,
            baseline_regime["pre_first_candidate_signature"]["path_node_count"],
        )
        self.assertEqual(
            4,
            comparison_regime["pre_first_candidate_signature"]["path_node_count"],
        )
        self.assertFalse(baseline_regime["later_candidate_migration"]["occurs"])
        self.assertTrue(comparison_regime["later_candidate_migration"]["occurs"])
        self.assertIn(
            "split_child",
            comparison_regime["later_candidate_migration"]["site_kinds"],
        )

    def test_grcv3_rich_v4_explicit_settlement_regime_trace_matches_known_regimes(
        self,
    ) -> None:
        trace = telemetry.build_grcv3_landscape_settlement_locus_regime_trace(
            baseline_seed_path=RICH_V4_CARRIER_SITE_SETTLEMENT_REGIME_SEED,
            comparison_seed_path=RICH_V4_PATH_NODE_SETTLEMENT_REGIME_SINGLE_INTERMEDIATE_SEED,
            profile_name="seed_baseline",
            primitive_id="spindle_core",
            num_steps=12,
        )

        self.assertEqual(
            "carrier_site_regime",
            trace["baseline_regime"]["regime_label"],
        )
        self.assertEqual(
            "path_node_regime",
            trace["comparison_regime"]["regime_label"],
        )
        self.assertEqual(
            "carrier_site",
            trace["baseline_regime"]["first_lifecycle_anchor"]["site"]["site_kind"],
        )
        self.assertEqual(
            "path_node",
            trace["comparison_regime"]["first_lifecycle_anchor"]["site"]["site_kind"],
        )
        self.assertFalse(trace["baseline_regime"]["later_candidate_migration"]["occurs"])
        self.assertTrue(trace["comparison_regime"]["later_candidate_migration"]["occurs"])

    def test_grcv3_rich_v4_settlement_regime_decomposition_keeps_path_anchor_but_stops_later_migration(
        self,
    ) -> None:
        inheriting_trace = telemetry.build_grcv3_landscape_settlement_locus_regime_trace(
            baseline_seed_path=RICH_V4_CARRIER_SITE_SETTLEMENT_REGIME_SEED,
            comparison_seed_path=RICH_V4_PATH_NODE_SPLIT_CHILD_INHERITING_SETTLEMENT_SEED,
            profile_name="seed_baseline",
            primitive_id="spindle_core",
            num_steps=12,
        )
        anchored_trace = telemetry.build_grcv3_landscape_settlement_locus_regime_trace(
            baseline_seed_path=RICH_V4_CARRIER_SITE_SETTLEMENT_REGIME_SEED,
            comparison_seed_path=RICH_V4_PATH_NODE_ANCHORED_SETTLEMENT_SEED,
            profile_name="seed_baseline",
            primitive_id="spindle_core",
            num_steps=12,
        )

        self.assertEqual(
            "path_node_regime",
            inheriting_trace["comparison_regime"]["regime_label"],
        )
        self.assertTrue(
            inheriting_trace["comparison_regime"]["later_candidate_migration"]["occurs"]
        )
        self.assertEqual(
            "path_node_regime",
            anchored_trace["comparison_regime"]["regime_label"],
        )
        self.assertEqual(
            "path_node",
            anchored_trace["comparison_regime"]["first_lifecycle_anchor"]["site"]["site_kind"],
        )
        self.assertFalse(
            anchored_trace["comparison_regime"]["later_candidate_migration"]["occurs"]
        )
        self.assertEqual(
            {
                "spark_candidate": 5,
                "split_init": 5,
                "spark": 5,
                "split_complete": 6,
            },
            anchored_trace["comparison_regime"]["first_event_steps"],
        )

    def test_grcv3_rich_v4_carrier_site_split_child_inheriting_does_not_open_new_regime(
        self,
    ) -> None:
        anchored_trace = telemetry.build_grcv3_landscape_settlement_locus_regime_trace(
            baseline_seed_path=RICH_V4_CARRIER_SITE_SETTLEMENT_REGIME_SEED,
            comparison_seed_path=RICH_V4_CARRIER_SITE_SPLIT_CHILD_INHERITING_SETTLEMENT_SEED,
            profile_name="seed_baseline",
            primitive_id="spindle_core",
            num_steps=12,
        )

        self.assertEqual(
            "carrier_site_regime",
            anchored_trace["baseline_regime"]["regime_label"],
        )
        self.assertEqual(
            "carrier_site_regime",
            anchored_trace["comparison_regime"]["regime_label"],
        )
        self.assertEqual(
            "carrier_site",
            anchored_trace["comparison_regime"]["first_lifecycle_anchor"]["site"]["site_kind"],
        )
        self.assertFalse(
            anchored_trace["comparison_regime"]["later_candidate_migration"]["occurs"]
        )
        self.assertEqual(
            {
                "spark_candidate": 8,
                "split_init": 8,
                "spark": 8,
                "split_complete": 9,
            },
            anchored_trace["comparison_regime"]["first_event_steps"],
        )

    def test_grcv3_rich_v4_role_locked_spill_policy_closes_settlement_regimes(
        self,
    ) -> None:
        carrier_role_trace = telemetry.build_grcv3_landscape_settlement_locus_regime_trace(
            baseline_seed_path=RICH_V4_ROLE_LOCKED_ASYMMETRIC_PAIR_MEDIATION_SEED,
            comparison_seed_path=RICH_V4_ROLE_LOCKED_ASYMMETRIC_PAIR_MEDIATION_SINGLE_INTERMEDIATE_SEED,
            profile_name="seed_baseline",
            primitive_id="spindle_core",
            num_steps=12,
        )
        mediated_role_trace = telemetry.build_grcv3_landscape_settlement_locus_regime_trace(
            baseline_seed_path=RICH_V4_ROLE_LOCKED_MEDIATED_SPILL_BRANCH_SEED,
            comparison_seed_path=RICH_V4_ROLE_LOCKED_MEDIATED_SPILL_BRANCH_SINGLE_INTERMEDIATE_SEED,
            profile_name="seed_baseline",
            primitive_id="spindle_core",
            num_steps=12,
        )

        for trace in (carrier_role_trace, mediated_role_trace):
            for regime_key in ("baseline_regime", "comparison_regime"):
                regime = trace[regime_key]
                self.assertIsNone(regime["regime_label"])
                self.assertEqual(
                    {
                        "spark_candidate": None,
                        "split_init": None,
                        "spark": None,
                        "split_complete": None,
                    },
                    regime["first_event_steps"],
                )
                self.assertIsNone(regime["first_lifecycle_anchor"]["site"])
                self.assertFalse(regime["later_candidate_migration"]["occurs"])

    def test_grcv3_rich_v4_path_node_regime_is_topology_specific_to_single_intermediate(
        self,
    ) -> None:
        single_trace = telemetry.build_grcv3_landscape_settlement_locus_regime_trace(
            baseline_seed_path=RICH_V4_MEDIATED_SPILL_BRANCH_SEED,
            comparison_seed_path=RICH_V4_MEDIATED_SPILL_BRANCH_SINGLE_INTERMEDIATE_SEED,
            profile_name="seed_baseline",
            primitive_id="spindle_core",
            num_steps=12,
        )
        fan_in_trace = telemetry.build_grcv3_landscape_settlement_locus_regime_trace(
            baseline_seed_path=RICH_V4_MEDIATED_SPILL_BRANCH_SEED,
            comparison_seed_path=RICH_V4_MEDIATED_SPILL_BRANCH_FAN_IN_SEED,
            profile_name="seed_baseline",
            primitive_id="spindle_core",
            num_steps=12,
        )

        self.assertEqual(
            "path_node_regime",
            single_trace["comparison_regime"]["regime_label"],
        )
        self.assertTrue(
            single_trace["comparison_regime"]["later_candidate_migration"]["occurs"]
        )
        self.assertIsNone(fan_in_trace["comparison_regime"]["regime_label"])
        self.assertEqual(
            {
                "spark_candidate": None,
                "split_init": None,
                "spark": None,
                "split_complete": None,
            },
            fan_in_trace["comparison_regime"]["first_event_steps"],
        )
        self.assertIsNone(fan_in_trace["comparison_regime"]["first_lifecycle_anchor"]["site"])
        self.assertFalse(
            fan_in_trace["comparison_regime"]["later_candidate_migration"]["occurs"]
        )

    def test_grcv3_rich_v4_post_split_reentry_trace_isolates_child_settlement_block(
        self,
    ) -> None:
        trace = telemetry.build_grcv3_landscape_settlement_reentry_trace(
            baseline_seed_path=RICH_V4_PATH_NODE_SPLIT_CHILD_INHERITING_SETTLEMENT_SEED,
            comparison_seed_path=RICH_V4_CARRIER_SITE_SPLIT_CHILD_INHERITING_SETTLEMENT_SEED,
            profile_name="seed_baseline",
            primitive_id="spindle_core",
            num_steps=12,
        )

        baseline_lane = trace["baseline_lane"]
        comparison_lane = trace["comparison_lane"]

        self.assertEqual(6, baseline_lane["first_split_complete_step"])
        self.assertEqual(9, comparison_lane["first_split_complete_step"])
        self.assertEqual(10, baseline_lane["first_reentry_gate_pass_step"])
        self.assertIsNone(comparison_lane["first_reentry_gate_pass_step"])
        self.assertEqual(11, baseline_lane["first_reentry_candidate_step"])
        self.assertIsNone(comparison_lane["first_reentry_candidate_step"])
        self.assertEqual("path_node_regime", baseline_lane["regime"]["regime_label"])
        self.assertEqual("carrier_site_regime", comparison_lane["regime"]["regime_label"])

        baseline_gate_record = next(
            record
            for record in baseline_lane["descendant_records"]
            if record["step_index"] == 10
        )
        self.assertTrue(
            all(
                bool(site["candidate_gate_pass"])
                for site in baseline_gate_record["descendant_sites"]
            )
        )

        comparison_final_record = comparison_lane["descendant_records"][-1]
        self.assertEqual(12, comparison_final_record["step_index"])
        self.assertTrue(
            all(
                not bool(site["candidate_gate_pass"])
                for site in comparison_final_record["descendant_sites"]
            )
        )
        self.assertTrue(
            all(
                not bool(site["gradient_below_threshold"])
                for site in comparison_final_record["descendant_sites"]
            )
        )
        self.assertEqual(
            "derived_child_sites_never_settle_enough_to_enter_spark_gate",
            trace["diagnosed_reentry_blocker"],
        )

    def test_grcv3_rich_v4_reentry_neighborhood_trace_isolates_neighbor_role_mix(
        self,
    ) -> None:
        trace = telemetry.build_grcv3_landscape_settlement_reentry_neighborhood_trace(
            baseline_seed_path=RICH_V4_PATH_NODE_SPLIT_CHILD_INHERITING_SETTLEMENT_SEED,
            comparison_seed_path=RICH_V4_CARRIER_SITE_SPLIT_CHILD_INHERITING_SETTLEMENT_SEED,
            profile_name="seed_baseline",
            primitive_id="spindle_core",
            num_steps=12,
        )

        self.assertEqual(10, trace["matched_step_index"])
        baseline_matched = trace["baseline_neighborhood_boundary"]["matched_step_record"]
        comparison_matched = trace["comparison_neighborhood_boundary"]["matched_step_record"]
        assert baseline_matched is not None
        assert comparison_matched is not None
        self.assertEqual(10, baseline_matched["step_index"])
        self.assertEqual(10, comparison_matched["step_index"])
        self.assertEqual(
            ["basin_load_carrier", "basin_support"],
            baseline_matched["aggregate"]["common_neighbor_motif_roles"],
        )
        self.assertEqual(
            ["basin_support", "ridge_support"],
            comparison_matched["aggregate"]["common_neighbor_motif_roles"],
        )
        self.assertLess(
            float(baseline_matched["aggregate"]["mean_gradient_norm"]),
            float(comparison_matched["aggregate"]["mean_gradient_norm"]),
        )
        self.assertEqual(
            "derived_child_reentry_correlates_with_carrier_neighbor_vs_ridge_support_neighbor_mix",
            trace["diagnosed_neighborhood_boundary"],
        )

    def test_grcv3_rich_v4_reentry_support_isolation_trace_isolates_secondary_role(
        self,
    ) -> None:
        trace = telemetry.build_grcv3_landscape_settlement_reentry_support_isolation_trace(
            baseline_seed_path=RICH_V4_PATH_NODE_SPLIT_CHILD_INHERITING_SETTLEMENT_SEED,
            comparison_seed_path=RICH_V4_CARRIER_SITE_SPLIT_CHILD_INHERITING_SETTLEMENT_SEED,
            profile_name="seed_baseline",
            primitive_id="spindle_core",
            num_steps=12,
        )

        baseline_support = trace["baseline_support_isolation"]
        comparison_support = trace["comparison_support_isolation"]
        self.assertEqual([3], baseline_support["degree_set"])
        self.assertEqual([3], comparison_support["degree_set"])
        self.assertLess(
            abs(
                float(baseline_support["support_weight"])
                - float(comparison_support["support_weight"])
            ),
            0.05,
        )
        self.assertEqual(
            ["basin_load_carrier"],
            baseline_support["secondary_roles"],
        )
        self.assertEqual(
            ["ridge_support"],
            comparison_support["secondary_roles"],
        )
        self.assertEqual(
            "reentry_correlates_with_secondary_carrier_neighbor_rather_than_secondary_ridge_support",
            trace["diagnosed_support_isolation"],
        )

    def test_grcv3_rich_v4_secondary_support_counterfactual_trace_is_decisive(
        self,
    ) -> None:
        trace = telemetry.build_grcv3_landscape_settlement_reentry_secondary_support_counterfactual_trace(
            baseline_seed_path=RICH_V4_PATH_NODE_SPLIT_CHILD_INHERITING_SETTLEMENT_SEED,
            comparison_seed_path=RICH_V4_CARRIER_SITE_SPLIT_CHILD_INHERITING_SETTLEMENT_SEED,
            profile_name="seed_baseline",
            primitive_id="spindle_core",
            num_steps=12,
        )

        self.assertEqual(11, trace["baseline_lane"]["first_reentry_candidate_step"])
        self.assertIsNone(
            trace["baseline_counterfactual_lane"]["first_reentry_candidate_step"]
        )
        self.assertEqual(
            6,
            trace["baseline_counterfactual_lane"]["counterfactual_applied_step"],
        )
        self.assertTrue(
            all(
                edge["neighbor_motif_role"] == "basin_load_carrier"
                for edge in trace["baseline_counterfactual_lane"]["counterfactual_removed_edges"]
            )
        )
        self.assertIsNone(trace["comparison_lane"]["first_reentry_candidate_step"])
        self.assertIsNone(
            trace["comparison_counterfactual_lane"]["first_reentry_candidate_step"]
        )
        self.assertEqual(
            9,
            trace["comparison_counterfactual_lane"]["counterfactual_applied_step"],
        )
        self.assertTrue(
            all(
                edge["neighbor_motif_role"] == "ridge_support"
                for edge in trace["comparison_counterfactual_lane"]["counterfactual_removed_edges"]
            )
        )
        self.assertEqual(
            "secondary_basin_load_carrier_is_necessary_but_removing_secondary_ridge_support_is_not_sufficient",
            trace["diagnosed_counterfactual_boundary"],
        )

    def test_grcv3_rich_v4_secondary_support_authorability_trace_shows_existing_structure_is_sufficient(
        self,
    ) -> None:
        trace = telemetry.build_grcv3_landscape_secondary_support_authorability_trace(
            structural_path_seed_path=RICH_V4_MEDIATED_SPILL_BRANCH_SINGLE_INTERMEDIATE_SEED,
            explicit_path_seed_path=RICH_V4_PATH_NODE_SPLIT_CHILD_INHERITING_SETTLEMENT_SEED,
            structural_direct_seed_path=RICH_V4_MEDIATED_SPILL_BRANCH_SEED,
            explicit_direct_seed_path=RICH_V4_CARRIER_SITE_SPLIT_CHILD_INHERITING_SETTLEMENT_SEED,
            profile_name="seed_baseline",
            primitive_id="spindle_core",
            num_steps=12,
        )

        self.assertTrue(trace["structural_path_summary"]["target_condition_present"])
        self.assertTrue(trace["explicit_path_summary"]["target_condition_present"])
        self.assertFalse(trace["structural_direct_summary"]["target_condition_present"])
        self.assertFalse(trace["explicit_direct_summary"]["target_condition_present"])
        self.assertEqual(
            11,
            trace["structural_path_summary"]["first_reentry_candidate_step"],
        )
        self.assertEqual(
            11,
            trace["explicit_path_summary"]["first_reentry_candidate_step"],
        )
        self.assertEqual(
            ["basin_load_carrier"],
            trace["structural_path_summary"]["secondary_roles"],
        )
        self.assertEqual(
            ["basin_load_carrier"],
            trace["explicit_path_summary"]["secondary_roles"],
        )
        self.assertTrue(
            trace["path_to_explicit_comparison"]["transfer_mediation"]["same"]
        )
        self.assertFalse(
            trace["path_to_explicit_comparison"]["settlement_regime"]["same"]
        )
        self.assertFalse(
            trace["structural_path_to_direct_comparison"]["transfer_mediation"]["same"]
        )
        self.assertTrue(
            trace["structural_path_to_direct_comparison"]["interior_load_carriers"]["same"]
        )
        self.assertTrue(
            trace["structural_path_to_direct_comparison"]["channel_geometry"]["same"]
        )
        self.assertTrue(
            trace["structural_path_to_direct_comparison"]["boundary_geometry"]["same"]
        )
        self.assertEqual(
            "existing_transfer_mediation_already_authors_descendant_secondary_basin_load_carrier_support_condition",
            trace["diagnosed_authorability_result"],
        )


class TelemetryCollapseTraceTest(unittest.TestCase):
    """Collapse-trace coverage."""

    def test_grcv3_rich_v4_collapse_regime_trace_shows_path_specific_support_to_carrier_collapse(
        self,
    ) -> None:
        trace = telemetry.build_grcv3_landscape_collapse_regime_trace(
            direct_seed_path=RICH_V4_MEDIATED_SPILL_BRANCH_SEED,
            path_seed_path=RICH_V4_MEDIATED_SPILL_BRANCH_SINGLE_INTERMEDIATE_SEED,
            split_path_seed_path=RICH_V4_PATH_NODE_SPLIT_CHILD_INHERITING_SETTLEMENT_SEED,
            split_direct_seed_path=RICH_V4_CARRIER_SITE_SPLIT_CHILD_INHERITING_SETTLEMENT_SEED,
            profile_name="seed_baseline",
            primitive_id="spindle_core",
            num_steps=24,
        )

        self.assertIsNone(trace["direct_lane"]["first_collapse_step"])
        self.assertIsNone(trace["split_direct_lane"]["first_collapse_step"])
        self.assertEqual(17, trace["path_lane"]["first_collapse_step"])
        self.assertEqual(17, trace["split_path_lane"]["first_collapse_step"])
        self.assertEqual(
            "path_node",
            trace["path_lane"]["first_spark_site"]["site_kind"],
        )
        self.assertEqual(
            "basin_support",
            trace["path_lane"]["first_collapse_source_site"]["site_kind"],
        )
        self.assertEqual(
            "carrier_site",
            trace["path_lane"]["first_collapse_sink_site"]["site_kind"],
        )
        self.assertFalse(trace["path_lane"]["collapse_source_matches_first_spark_locus_family"])
        self.assertTrue(trace["path_lane"]["collapse_after_split_occurs"])
        self.assertFalse(trace["split_path_lane"]["later_split_child_collapse_participation"])
        self.assertEqual(
            "collapse_is_path_regime_specific_support_to_carrier_resolution_and_not_split_child_driven_under_current_structure",
            trace["diagnosed_collapse_read"],
        )

    def test_grcv3_broad_collapse_survey_shows_plural_heterogeneous_collapse_lanes(
        self,
    ) -> None:
        survey = telemetry.build_grcv3_landscape_broad_collapse_survey()

        self.assertEqual(3, survey["lane_count"])
        self.assertEqual(3, survey["collapse_capable_lane_count"])
        self.assertEqual(
            [
                "collapse_example",
                "basin_boundary_channel_fulltest_lane",
            ],
            survey["collapse_without_prior_spark_lane_names"],
        )
        self.assertEqual(
            [
                "transfer_mediation_artifact_lane",
            ],
            survey["collapse_after_split_lane_names"],
        )
        self.assertEqual([], survey["later_split_child_collapse_lane_names"])

        lane_by_name = {
            lane["lane_name"]: lane for lane in survey["lane_summaries"]
        }
        self.assertEqual(3, lane_by_name["collapse_example"]["first_collapse_step"])
        self.assertEqual(
            "basin_support",
            lane_by_name["collapse_example"]["first_collapse_source_site"]["site_kind"],
        )
        self.assertEqual(
            "junction_branch",
            lane_by_name["collapse_example"]["first_collapse_sink_site"]["site_kind"],
        )
        self.assertEqual(
            "collapse_without_prior_spark",
            lane_by_name["collapse_example"]["collapse_relative_to_first_spark"],
        )

        self.assertEqual(
            71,
            lane_by_name["transfer_mediation_artifact_lane"]["first_collapse_step"],
        )
        self.assertEqual(
            "carrier_site",
            lane_by_name["transfer_mediation_artifact_lane"]["first_spark_site"]["site_kind"],
        )
        self.assertEqual(
            "basin_center",
            lane_by_name["transfer_mediation_artifact_lane"]["first_collapse_source_site"]["site_kind"],
        )
        self.assertEqual(
            "basin_support",
            lane_by_name["transfer_mediation_artifact_lane"]["first_collapse_sink_site"]["site_kind"],
        )
        self.assertEqual(
            "collapse_from_different_locus_family_than_first_spark",
            lane_by_name["transfer_mediation_artifact_lane"]["collapse_relative_to_first_spark"],
        )

        self.assertEqual(
            100,
            lane_by_name["basin_boundary_channel_fulltest_lane"]["first_collapse_step"],
        )
        self.assertEqual(
            "ridge_support",
            lane_by_name["basin_boundary_channel_fulltest_lane"]["first_collapse_sink_site"]["site_kind"],
        )
        self.assertEqual(
            "recorded_collapse_lanes_are_plural_and_heterogeneous_so_broader_controlled_comparison_is_still_required",
            survey["diagnosed_broadened_collapse_read"],
        )

    def test_grcv3_pre_spark_collapse_decomposition_tracks_existing_structure(
        self,
    ) -> None:
        trace = telemetry.build_grcv3_landscape_pre_spark_collapse_decomposition_trace(
            baseline_seed_path=RICH_COLLAPSE_EXAMPLE_SEED,
            comparison_seed_path=RICH_BASIN_BOUNDARY_CHANNEL_SEED,
            baseline_profile_name="hot_exploratory",
            comparison_profile_name="seed_baseline",
            baseline_primitive_id="decision_core",
            comparison_primitive_id="core_basin",
            baseline_num_steps=10,
            comparison_num_steps=160,
        )

        self.assertIsNone(trace["baseline_lane"]["first_spark_site"])
        self.assertIsNone(trace["comparison_lane"]["first_spark_site"])
        self.assertEqual(3, trace["baseline_lane"]["first_collapse_step"])
        self.assertEqual(100, trace["comparison_lane"]["first_collapse_step"])
        self.assertEqual(
            "basin_support",
            trace["baseline_lane"]["first_collapse_source_site"]["site_kind"],
        )
        self.assertEqual(
            "basin_support",
            trace["comparison_lane"]["first_collapse_source_site"]["site_kind"],
        )
        self.assertEqual(
            "junction_branch",
            trace["baseline_lane"]["first_collapse_sink_site"]["site_kind"],
        )
        self.assertEqual(
            "ridge_support",
            trace["comparison_lane"]["first_collapse_sink_site"]["site_kind"],
        )
        self.assertEqual(
            ["basin_center", "basin_support", "valley_channel"],
            trace["baseline_lane"]["first_collapse_source_summary"]["neighborhood_signature"][
                "neighbor_site_kinds"
            ],
        )
        self.assertEqual(
            ["basin_center", "basin_support", "ridge_support"],
            trace["comparison_lane"]["first_collapse_source_summary"][
                "neighborhood_signature"
            ]["neighbor_site_kinds"],
        )
        self.assertFalse(trace["family_comparison"]["realization"]["same"])
        self.assertFalse(trace["family_comparison"]["interfaces"]["same"])
        self.assertFalse(trace["family_comparison"]["boundary_geometry"]["same"])
        self.assertFalse(trace["family_comparison"]["channel_geometry"]["same"])
        self.assertEqual(
            "pre_spark_collapse_sink_difference_tracks_existing_junction_vs_boundary_channel_structure_so_no_new_collapse_family_is_justified_yet",
            trace["diagnosed_pre_spark_collapse_decomposition"],
        )

    def test_grcv3_post_spark_collapse_boundary_is_already_authored_by_transfer_mediation(
        self,
    ) -> None:
        trace = telemetry.build_grcv3_landscape_post_spark_collapse_boundary_trace(
            baseline_seed_path=RICH_V4_TRANSFER_MEDIATION_SEED,
            blocked_control_seed_path=RICH_V4_CENTER_COUPLING_SEED,
            refined_control_seed_path=RICH_V4_ASYMMETRIC_CENTER_COUPLING_SEED,
            profile_name="seed_baseline",
            primitive_id="spindle_core",
            num_steps=120,
        )

        self.assertEqual(71, trace["baseline_lane"]["first_collapse_step"])
        self.assertEqual(99, trace["blocked_control_lane"]["first_collapse_step"])
        self.assertEqual(72, trace["refined_control_lane"]["first_collapse_step"])
        self.assertEqual(
            "carrier_site",
            trace["baseline_lane"]["first_spark_site"]["site_kind"],
        )
        self.assertEqual(
            "basin_support",
            trace["blocked_control_lane"]["first_spark_site"]["site_kind"],
        )
        self.assertEqual(
            "carrier_site",
            trace["refined_control_lane"]["first_spark_site"]["site_kind"],
        )
        self.assertEqual(
            "basin_center",
            trace["baseline_lane"]["first_collapse_source_site"]["site_kind"],
        )
        self.assertEqual(
            "basin_support",
            trace["baseline_lane"]["first_collapse_sink_site"]["site_kind"],
        )
        self.assertEqual(
            "carrier_site",
            trace["blocked_control_lane"]["first_collapse_source_site"]["site_kind"],
        )
        self.assertEqual(
            "ridge_support",
            trace["blocked_control_lane"]["first_collapse_sink_site"]["site_kind"],
        )
        self.assertEqual(
            "basin_center",
            trace["refined_control_lane"]["first_collapse_source_site"]["site_kind"],
        )
        self.assertEqual(
            "basin_support",
            trace["refined_control_lane"]["first_collapse_sink_site"]["site_kind"],
        )
        self.assertFalse(trace["baseline_to_blocked_comparison"]["transfer_mediation"]["same"])
        self.assertFalse(trace["baseline_to_refined_comparison"]["transfer_mediation"]["same"])
        self.assertTrue(trace["baseline_to_blocked_comparison"]["interfaces"]["same"])
        self.assertTrue(trace["baseline_to_blocked_comparison"]["boundary_geometry"]["same"])
        self.assertTrue(trace["baseline_to_blocked_comparison"]["channel_geometry"]["same"])
        self.assertTrue(
            trace["baseline_to_blocked_comparison"]["interior_load_carriers"]["same"]
        )
        self.assertTrue(trace["baseline_to_refined_comparison"]["local_geometry"]["same"])
        self.assertEqual(
            "existing_transfer_mediation_center_coupling_classes_already_author_post_spark_collapse_boundary",
            trace["diagnosed_post_spark_collapse_boundary"],
        )

    def test_grcv3_post_spark_late_window_stability_shows_blocked_lane_only_later_partially_converges(
        self,
    ) -> None:
        trace = telemetry.build_grcv3_landscape_post_spark_late_window_stability_trace(
            baseline_seed_path=RICH_V4_TRANSFER_MEDIATION_SEED,
            blocked_control_seed_path=RICH_V4_CENTER_COUPLING_SEED,
            refined_control_seed_path=RICH_V4_ASYMMETRIC_CENTER_COUPLING_SEED,
            profile_name="seed_baseline",
            primitive_id="spindle_core",
            num_steps=150,
            late_window_start_step=100,
        )

        self.assertEqual(1, trace["baseline_post_window"]["post_window_collapse_count"])
        self.assertEqual(1, trace["refined_control_post_window"]["post_window_collapse_count"])
        self.assertEqual(5, trace["blocked_control_post_window"]["post_window_collapse_count"])
        self.assertEqual(
            116,
            trace["baseline_post_window"]["first_post_window_matching_baseline_pattern_step"],
        )
        self.assertEqual(
            117,
            trace["refined_control_post_window"]["first_post_window_matching_baseline_pattern_step"],
        )
        self.assertEqual(
            121,
            trace["blocked_control_post_window"]["first_post_window_matching_baseline_pattern_step"],
        )
        self.assertEqual(
            101,
            trace["blocked_control_post_window"]["first_post_window_collapse_step"],
        )
        first_blocked_post_window = trace["blocked_control_post_window"][
            "first_post_window_collapse_record"
        ]
        assert first_blocked_post_window is not None
        self.assertEqual(
            "carrier_site",
            first_blocked_post_window["source_site"]["site_kind"],
        )
        self.assertEqual(
            "split_child",
            first_blocked_post_window["sink_site"]["site_kind"],
        )
        self.assertEqual(
            ["basin_center", "carrier_site", "split_child"],
            trace["blocked_control_post_window"]["post_window_collapse_source_site_kinds"],
        )
        self.assertEqual(
            ["basin_support", "split_child"],
            trace["blocked_control_post_window"]["post_window_collapse_sink_site_kinds"],
        )
        self.assertTrue(
            trace["blocked_control_post_window"][
                "eventually_matches_baseline_collapse_pattern_after_window"
            ]
        )
        self.assertTrue(
            trace["blocked_control_post_window"][
                "has_distinct_post_window_collapse_before_baseline_match"
            ]
        )
        self.assertEqual(
            "blocked_control_eventually_reaches_baseline_collapse_pattern_only_after_a_distinct_carrier_split_child_cascade_so_late_window_interpretation_remains_open",
            trace["diagnosed_post_spark_late_window_stability"],
        )

    def test_grcv3_post_spark_delay_authorability_shows_existing_transfer_mediation_is_sufficient(
        self,
    ) -> None:
        trace = telemetry.build_grcv3_landscape_post_spark_delay_authorability_trace(
            baseline_seed_path=RICH_V4_TRANSFER_MEDIATION_SEED,
            blocked_control_seed_path=RICH_V4_CENTER_COUPLING_SEED,
            refined_control_seed_path=RICH_V4_ASYMMETRIC_CENTER_COUPLING_SEED,
            profile_name="seed_baseline",
            primitive_id="spindle_core",
            num_steps=150,
            late_window_start_step=100,
        )

        self.assertFalse(trace["blocked_to_refined_comparison"]["transfer_mediation"]["same"])
        self.assertTrue(trace["blocked_to_refined_comparison"]["interfaces"]["same"])
        self.assertTrue(trace["blocked_to_refined_comparison"]["boundary_geometry"]["same"])
        self.assertTrue(trace["blocked_to_refined_comparison"]["channel_geometry"]["same"])
        self.assertTrue(
            trace["blocked_to_refined_comparison"]["interior_load_carriers"]["same"]
        )
        self.assertTrue(trace["blocked_to_refined_comparison"]["local_geometry"]["same"])
        self.assertTrue(
            trace["blocked_control_post_window"][
                "has_distinct_post_window_collapse_before_baseline_match"
            ]
        )
        self.assertFalse(
            trace["refined_control_post_window"][
                "has_distinct_post_window_collapse_before_baseline_match"
            ]
        )
        self.assertEqual(
            "existing_transfer_mediation_center_coupling_classes_already_author_blocked_lane_late_cascade_delay_before_shared_convergence",
            trace["diagnosed_post_spark_delay_authorability"],
        )

    def test_grcv3_post_collapse_geometry_exclusion_shows_sink_reroute_is_geometry_mediated(
        self,
    ) -> None:
        trace = telemetry.build_grcv3_landscape_post_collapse_geometry_exclusion_trace(
            blocked_control_seed_path=RICH_V4_CENTER_COUPLING_SEED,
            refined_control_seed_path=RICH_V4_ASYMMETRIC_CENTER_COUPLING_SEED,
            profile_name="seed_baseline",
            primitive_id="spindle_core",
            num_steps=150,
            late_window_start_step=100,
        )

        self.assertEqual(
            ["split_child", "basin_support"],
            trace["blocked_post_window_sink_kind_sequence"],
        )
        self.assertEqual(
            ["carrier_site", "split_child", "basin_center"],
            trace["blocked_post_window_source_kind_sequence"],
        )
        initial_record = trace["blocked_initial_collapse_record"]
        reroute_record = trace["blocked_first_post_initial_reroute_record"]
        shared_record = trace["blocked_first_shared_pattern_record"]
        assert initial_record is not None
        assert reroute_record is not None
        assert shared_record is not None
        self.assertEqual("ridge_support", initial_record["sink_site"]["site_kind"])
        self.assertEqual("split_child", reroute_record["sink_site"]["site_kind"])
        self.assertEqual("basin_support", shared_record["sink_site"]["site_kind"])
        self.assertEqual(
            ["basin_support", "ridge_support", "split_child"],
            initial_record["source_site_summary"]["neighborhood_signature"]["neighbor_site_kinds"],
        )
        self.assertEqual(
            ["split_child", "valley_channel"],
            reroute_record["source_site_summary"]["neighborhood_signature"]["neighbor_site_kinds"],
        )
        self.assertEqual(
            ["basin_support"],
            shared_record["source_site_summary"]["neighborhood_signature"]["neighbor_site_kinds"],
        )
        self.assertFalse(trace["blocked_to_refined_comparison"]["transfer_mediation"]["same"])
        self.assertTrue(trace["blocked_to_refined_comparison"]["interfaces"]["same"])
        self.assertFalse(trace["refined_has_distinct_pre_shared_reroute"])
        self.assertEqual(
            "existing_transfer_mediation_center_coupling_classes_already_author_geometry_mediated_shift_away_from_initial_collapsed_sink",
            trace["diagnosed_post_collapse_geometry_exclusion"],
        )


class TelemetryLandscapeExperimentTest(unittest.TestCase):
    """Landscape experiment runner coverage."""

    def test_run_grc9_landscape_experiment_emits_artifacts_and_reports(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = telemetry.run_grc9_landscape_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                profile_name="phase6_seed_baseline",
                num_steps=2,
            )

            self.assertEqual("phase6_seed_baseline", result.profile_name)
            self.assertEqual(2, result.num_steps)
            self.assertIsNotNone(result.cell1_run.telemetry)
            self.assertIsNotNone(result.cell4_run.telemetry)
            assert result.cell1_run.telemetry is not None
            assert result.cell4_run.telemetry is not None
            cell1_layout = result.cell1_run.telemetry.artifact_layout
            cell4_layout = result.cell4_run.telemetry.artifact_layout
            assert cell1_layout is not None
            assert cell4_layout is not None

            self.assertEqual(
                Path(temp_dir)
                / "outputs"
                / "representative"
                / "grc9_landscape"
                / "phase6_seed_baseline"
                / "cell-1",
                cell1_layout.root_dir,
            )
            self.assertEqual(
                Path(temp_dir)
                / "outputs"
                / "representative"
                / "grc9_landscape"
                / "phase6_seed_baseline"
                / "cell-4",
                cell4_layout.root_dir,
            )
            self.assertTrue(cell1_layout.step_rows_path.exists())
            self.assertTrue(cell1_layout.event_rows_path.exists())
            self.assertTrue(cell1_layout.run_summary_path.exists())
            self.assertTrue(cell1_layout.experiment_report_path.exists())
            self.assertTrue(cell1_layout.comparison_report_path.exists())
            self.assertTrue(cell4_layout.step_rows_path.exists())
            self.assertTrue(cell4_layout.event_rows_path.exists())
            self.assertTrue(cell4_layout.run_summary_path.exists())
            self.assertTrue(cell4_layout.experiment_report_path.exists())
            self.assertTrue(cell4_layout.comparison_report_path.exists())

            loaded_cell1_steps = telemetry.load_step_rows(cell1_layout.step_rows_path)
            loaded_cell1_summary = telemetry.load_run_summary(cell1_layout.run_summary_path)
            loaded_comparison = telemetry.load_comparison_report(
                cell4_layout.comparison_report_path
            )

        self.assertEqual(2, len(loaded_cell1_steps))
        self.assertEqual(
            "structural_graph_graft_v1",
            loaded_cell1_steps[0].family_extensions["grc9"]["source_lowering_mode"],
        )
        self.assertEqual("phase6_seed_baseline", loaded_cell1_summary.identity.param_family)
        self.assertIn(
            "final_expansion_count",
            loaded_cell1_summary.family_extensions["grc9"],
        )
        self.assertEqual("run_summary_comparison_v1", loaded_comparison.common["report_type"])

    def test_run_grc9_phase_t_landscape_profile_emits_richer_extensions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = telemetry.run_grc9_landscape_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                profile_name=telemetry.DEFAULT_GRC9_PHASE_T_LANDSCAPE_PROFILE,
                num_steps=2,
            )

            self.assertEqual(
                telemetry.DEFAULT_GRC9_PHASE_T_LANDSCAPE_PROFILE,
                result.profile_name,
            )
            assert result.cell1_run.telemetry is not None
            assert result.cell4_run.telemetry is not None
            cell1_layout = result.cell1_run.telemetry.artifact_layout
            cell4_layout = result.cell4_run.telemetry.artifact_layout
            assert cell1_layout is not None
            assert cell4_layout is not None

            self.assertEqual(
                Path(temp_dir)
                / "outputs"
                / "representative"
                / "grc9_landscape"
                / telemetry.DEFAULT_GRC9_PHASE_T_LANDSCAPE_PROFILE
                / "cell-1",
                cell1_layout.root_dir,
            )
            self.assertTrue(cell1_layout.step_rows_path.exists())
            self.assertTrue(cell1_layout.event_rows_path.exists())
            self.assertTrue(cell1_layout.run_summary_path.exists())
            self.assertTrue(cell1_layout.experiment_report_path.exists())
            self.assertTrue(cell1_layout.comparison_report_path.exists())
            self.assertTrue(cell4_layout.step_rows_path.exists())
            self.assertTrue(cell4_layout.event_rows_path.exists())
            self.assertTrue(cell4_layout.run_summary_path.exists())

            loaded_cell1_steps = telemetry.load_step_rows(cell1_layout.step_rows_path)
            loaded_cell1_events = telemetry.load_event_rows(cell1_layout.event_rows_path)
            loaded_cell1_summary = telemetry.load_run_summary(cell1_layout.run_summary_path)
            loaded_cell4_steps = telemetry.load_step_rows(cell4_layout.step_rows_path)
            loaded_comparison = telemetry.load_comparison_report(
                cell4_layout.comparison_report_path
            )

        self.assertEqual(2, len(loaded_cell1_steps))
        self.assertEqual(2, len(loaded_cell4_steps))
        step_extension = loaded_cell1_steps[0].family_extensions["grc9"]
        self.assertEqual(
            telemetry.GRC9_TELEMETRY_CONTRACT_VERSION,
            step_extension["contract_version"],
        )
        self.assertEqual(
            "structural_graph_graft_v1",
            step_extension["lane_context"]["source_lowering_mode"],
        )
        self.assertEqual(
            telemetry.DEFAULT_GRC9_PHASE_T_LANDSCAPE_PROFILE,
            step_extension["lane_context"]["profile_name"],
        )
        self.assertIn("backend_config", step_extension)
        self.assertIn("identity_abundance", step_extension)
        self.assertIn("coarse_graining", step_extension)

        self.assertTrue(
            all("grc9" in row.family_extensions for row in loaded_cell1_events)
        )
        summary_extension = loaded_cell1_summary.family_extensions["grc9"]
        self.assertEqual(
            "structural_graph_graft_v1",
            summary_extension["lane_context"]["source_lowering_mode"],
        )
        self.assertIn("lifecycle_event_counts", summary_extension)
        self.assertIn("final_identity_summary", summary_extension)
        self.assertEqual(
            telemetry.DEFAULT_GRC9_PHASE_T_LANDSCAPE_PROFILE,
            loaded_cell1_summary.identity.param_family,
        )
        self.assertEqual("run_summary_comparison_v1", loaded_comparison.common["report_type"])

    def test_run_grc9_landscape_experiment_can_emit_checkpoint_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = telemetry.run_grc9_landscape_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                profile_name=telemetry.DEFAULT_GRC9_PHASE_T_LANDSCAPE_PROFILE,
                num_steps=2,
                record_graph_checkpoints=True,
                checkpoint_every_n_steps=1,
                include_flow_overlays=True,
            )

            assert result.cell1_run.telemetry is not None
            assert result.cell4_run.telemetry is not None
            cell1_telemetry = result.cell1_run.telemetry
            cell4_telemetry = result.cell4_run.telemetry
            self.assertIsNotNone(cell1_telemetry.graph_checkpoint_index)
            self.assertIsNotNone(cell4_telemetry.graph_checkpoint_index)
            self.assertEqual(3, len(cell1_telemetry.graph_checkpoints))
            self.assertEqual(3, len(cell4_telemetry.graph_checkpoints))
            cell1_layout = cell1_telemetry.artifact_layout
            cell4_layout = cell4_telemetry.artifact_layout
            assert cell1_layout is not None
            assert cell4_layout is not None
            self.assertTrue(cell1_layout.graph_checkpoint_index_path.exists())
            self.assertTrue(cell4_layout.graph_checkpoint_index_path.exists())

            cell1_pack = telemetry.load_telemetry_artifact_pack(cell1_layout)
            cell4_pack = telemetry.load_telemetry_artifact_pack(cell4_layout)

        self.assertIsNotNone(cell1_pack.graph_checkpoint_index)
        self.assertIsNotNone(cell4_pack.graph_checkpoint_index)
        self.assertEqual(3, len(cell1_pack.graph_checkpoints))
        self.assertEqual(
            ("initial", "interval", "final"),
            tuple(checkpoint.checkpoint_label for checkpoint in cell1_pack.graph_checkpoints),
        )
        self.assertEqual("port_graph", cell1_pack.graph_checkpoints[0].graph_kind)
        self.assertEqual(
            "port_chart_module_overlay_v1",
            cell1_pack.graph_checkpoints[0].family_extensions["grc9"][
                "checkpoint_payload"
            ],
        )
        self.assertEqual(3, len(cell4_pack.graph_checkpoints))

    def test_run_grcv3_landscape_experiment_emits_artifacts_and_reports(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = telemetry.run_grcv3_landscape_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                profile_name="seed_baseline",
                num_steps=3,
            )

            self.assertEqual("seed_baseline", result.profile_name)
            self.assertEqual(3, result.num_steps)
            self.assertIsNotNone(result.cell1_run.telemetry)
            self.assertIsNotNone(result.cell4_run.telemetry)
            assert result.cell1_run.telemetry is not None
            assert result.cell4_run.telemetry is not None
            cell1_layout = result.cell1_run.telemetry.artifact_layout
            cell4_layout = result.cell4_run.telemetry.artifact_layout
            assert cell1_layout is not None
            assert cell4_layout is not None

            self.assertEqual(
                Path(temp_dir)
                / "outputs"
                / "representative"
                / "grcv3_landscape"
                / "seed_baseline"
                / "cell-1",
                cell1_layout.root_dir,
            )
            self.assertEqual(
                Path(temp_dir)
                / "outputs"
                / "representative"
                / "grcv3_landscape"
                / "seed_baseline"
                / "cell-4",
                cell4_layout.root_dir,
            )
            self.assertTrue(cell1_layout.step_rows_path.exists())
            self.assertTrue(cell1_layout.event_rows_path.exists())
            self.assertTrue(cell1_layout.run_summary_path.exists())
            self.assertTrue(cell1_layout.experiment_report_path.exists())
            self.assertTrue(cell1_layout.comparison_report_path.exists())
            self.assertTrue(cell4_layout.step_rows_path.exists())
            self.assertTrue(cell4_layout.event_rows_path.exists())
            self.assertTrue(cell4_layout.run_summary_path.exists())
            self.assertTrue(cell4_layout.experiment_report_path.exists())
            self.assertTrue(cell4_layout.comparison_report_path.exists())

            loaded_cell1_steps = telemetry.load_step_rows(cell1_layout.step_rows_path)
            loaded_cell1_summary = telemetry.load_run_summary(cell1_layout.run_summary_path)
            loaded_comparison = telemetry.load_comparison_report(
                cell4_layout.comparison_report_path
            )

        self.assertEqual(3, len(loaded_cell1_steps))
        self.assertEqual(
            "phase_t_iter26_v1",
            loaded_cell1_steps[0].family_extensions["grcv3"]["contract_version"],
        )
        self.assertIn(
            "final_hierarchy_state",
            loaded_cell1_summary.family_extensions["grcv3"],
        )
        self.assertEqual("seed_baseline", loaded_cell1_summary.identity.param_family)
        self.assertEqual("run_summary_comparison_v1", loaded_comparison.common["report_type"])
        self.assertIn(
            "final_observables_right_minus_left",
            loaded_comparison.common,
        )

    def test_run_grcv3_landscape_experiment_can_emit_checkpoint_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = telemetry.run_grcv3_landscape_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                profile_name="seed_baseline",
                num_steps=3,
                record_graph_checkpoints=True,
                checkpoint_every_n_steps=1,
                include_flow_overlays=True,
            )

            assert result.cell1_run.telemetry is not None
            assert result.cell4_run.telemetry is not None
            cell1_telemetry = result.cell1_run.telemetry
            cell4_telemetry = result.cell4_run.telemetry
            self.assertIsNotNone(cell1_telemetry.graph_checkpoint_index)
            self.assertIsNotNone(cell4_telemetry.graph_checkpoint_index)
            self.assertEqual(4, len(cell1_telemetry.graph_checkpoints))
            self.assertEqual(4, len(cell4_telemetry.graph_checkpoints))
            cell1_layout = cell1_telemetry.artifact_layout
            cell4_layout = cell4_telemetry.artifact_layout
            assert cell1_layout is not None
            assert cell4_layout is not None
            self.assertTrue(cell1_layout.graph_checkpoint_index_path.exists())
            self.assertTrue(cell4_layout.graph_checkpoint_index_path.exists())

            cell1_pack = telemetry.load_telemetry_artifact_pack(cell1_layout)
            cell4_pack = telemetry.load_telemetry_artifact_pack(cell4_layout)

        self.assertIsNotNone(cell1_pack.graph_checkpoint_index)
        self.assertIsNotNone(cell4_pack.graph_checkpoint_index)
        self.assertEqual(4, len(cell1_pack.graph_checkpoints))
        self.assertEqual(4, len(cell4_pack.graph_checkpoints))
        self.assertEqual(
            ("initial", "interval", "interval", "final"),
            tuple(checkpoint.checkpoint_label for checkpoint in cell1_pack.graph_checkpoints),
        )
        self.assertEqual("weighted_graph", cell1_pack.graph_checkpoints[0].graph_kind)
        self.assertEqual(
            "not_available_pre_step",
            cell1_pack.graph_checkpoints[0].flow_representation,
        )
        self.assertTrue(
            all(
                checkpoint.flow_representation == "signed_edge_flux"
                for checkpoint in cell1_pack.graph_checkpoints[1:]
            )
        )
        self.assertEqual(
            "phase_t_iter26_v1",
            cell1_pack.graph_checkpoints[0].family_extensions["grcv3"]["contract_version"],
        )
        self.assertIn("gradient_norm", cell1_pack.graph_checkpoints[0].node_records[0])
        self.assertIn("net_flux", cell1_pack.graph_checkpoints[0].node_records[0])
        self.assertIn("base_conductance", cell1_pack.graph_checkpoints[0].edge_records[0])
        self.assertEqual(4, len(cell4_pack.graph_checkpoints))

    def test_grcv3_landscape_script_rejects_non_positive_steps(self) -> None:
        script_module = _load_grcv3_landscape_script_module()
        stderr_buffer = io.StringIO()

        with self.assertRaises(SystemExit) as ctx:
            with contextlib.redirect_stderr(stderr_buffer):
                script_module.main(["--steps", "0"])

        self.assertEqual(2, ctx.exception.code)
        self.assertIn("--steps must be > 0", stderr_buffer.getvalue())


class TelemetryScriptTest(unittest.TestCase):
    """Telemetry script coverage using shared generated test scaffolding."""

    def _assert_script_rejects_non_positive_steps(
        self,
        load_module: Callable[[], Any],
        argv: list[str],
        stderr_fragment: str,
    ) -> None:
        script_module = load_module()
        stderr_buffer = io.StringIO()

        with self.assertRaises(SystemExit) as ctx:
            with contextlib.redirect_stderr(stderr_buffer):
                script_module.main(argv)

        self.assertEqual(2, ctx.exception.code)
        self.assertIn(stderr_fragment, stderr_buffer.getvalue())

    def _assert_script_emits_output(
        self,
        load_module: Callable[[], Any],
        argv_factory: Callable[[Path | None], list[str]],
        assert_output: Callable[[unittest.TestCase, Any, Path | None], None],
        *,
        parse_json: bool = True,
        use_temp_dir: bool = False,
    ) -> None:
        script_module = load_module()
        stdout_buffer = io.StringIO()
        temp_dir_context: contextlib.AbstractContextManager[str | None]
        if use_temp_dir:
            temp_dir_context = tempfile.TemporaryDirectory()
        else:
            temp_dir_context = contextlib.nullcontext()

        with temp_dir_context as temp_dir:
            temp_dir_path = Path(temp_dir) if temp_dir is not None else None
            with contextlib.redirect_stdout(stdout_buffer):
                exit_code = script_module.main(argv_factory(temp_dir_path))

            self.assertEqual(0, exit_code)
            payload: Any
            if parse_json:
                payload = json.loads(stdout_buffer.getvalue())
            else:
                payload = stdout_buffer.getvalue()
            assert_output(self, payload, temp_dir_path)


@dataclass(frozen=True)
class _ScriptRejectSpec:
    method_name: str
    load_module: Callable[[], Any]
    argv: tuple[str, ...]
    stderr_fragment: str


@dataclass(frozen=True)
class _ScriptEmitSpec:
    method_name: str
    load_module: Callable[[], Any]
    argv_factory: Callable[[Path | None], list[str]]
    assert_output: Callable[[unittest.TestCase, Any, Path | None], None]
    parse_json: bool = True
    use_temp_dir: bool = False


def _script_args(*args: str) -> Callable[[Path | None], list[str]]:
    def build_args(_temp_dir: Path | None) -> list[str]:
        return list(args)

    return build_args


def _assert_landscape_checkpoint_output(
    testcase: unittest.TestCase,
    summary_text: str,
    temp_dir_path: Path | None,
) -> None:
    assert temp_dir_path is not None
    testcase.assertIn('"cell1_run_id"', summary_text)
    testcase.assertIn('"cell4_run_id"', summary_text)
    testcase.assertTrue(
        any(
            path.name == "index.json"
            for path in (temp_dir_path / "outputs").rglob("index.json")
        )
    )


def _assert_path_failure_trace_output(
    testcase: unittest.TestCase,
    summary: dict[str, Any],
    _temp_dir_path: Path | None,
) -> None:
    testcase.assertEqual(0, summary["earliest_material_divergence_step"])
    testcase.assertEqual(
        "probe_shell_ingress_arrives_but_fails_to_form_weak_axis_geometry",
        summary["diagnosed_failure_mode"],
    )


def _assert_candidate_transition_trace_output(
    testcase: unittest.TestCase,
    summary: dict[str, Any],
    _temp_dir_path: Path | None,
) -> None:
    testcase.assertEqual(6, summary["baseline_first_candidate_step"])
    testcase.assertEqual(
        "candidate_sites_never_settle_enough_to_enter_spark_gate",
        summary["diagnosed_transition_blocker"],
    )


def _assert_settlement_locus_trace_output(
    testcase: unittest.TestCase,
    summary: dict[str, Any],
    _temp_dir_path: Path | None,
) -> None:
    testcase.assertEqual("carrier_site_regime", summary["baseline_regime"]["regime_label"])
    testcase.assertEqual("path_node_regime", summary["comparison_regime"]["regime_label"])
    testcase.assertEqual(5, summary["comparison_regime"]["first_event_steps"]["spark_candidate"])


def _assert_settlement_reentry_trace_output(
    testcase: unittest.TestCase,
    summary: dict[str, Any],
    _temp_dir_path: Path | None,
) -> None:
    testcase.assertEqual(10, summary["baseline_lane"]["first_reentry_gate_pass_step"])
    testcase.assertIsNone(summary["comparison_lane"]["first_reentry_gate_pass_step"])
    testcase.assertEqual(
        "derived_child_sites_never_settle_enough_to_enter_spark_gate",
        summary["diagnosed_reentry_blocker"],
    )


def _assert_settlement_reentry_neighborhood_trace_output(
    testcase: unittest.TestCase,
    summary: dict[str, Any],
    _temp_dir_path: Path | None,
) -> None:
    testcase.assertEqual(10, summary["matched_step_index"])
    testcase.assertEqual(
        "derived_child_reentry_correlates_with_carrier_neighbor_vs_ridge_support_neighbor_mix",
        summary["diagnosed_neighborhood_boundary"],
    )


def _assert_settlement_reentry_support_isolation_trace_output(
    testcase: unittest.TestCase,
    summary: dict[str, Any],
    _temp_dir_path: Path | None,
) -> None:
    testcase.assertEqual(
        "reentry_correlates_with_secondary_carrier_neighbor_rather_than_secondary_ridge_support",
        summary["diagnosed_support_isolation"],
    )


def _assert_secondary_support_counterfactual_trace_output(
    testcase: unittest.TestCase,
    summary: dict[str, Any],
    _temp_dir_path: Path | None,
) -> None:
    testcase.assertEqual(
        "secondary_basin_load_carrier_is_necessary_but_removing_secondary_ridge_support_is_not_sufficient",
        summary["diagnosed_counterfactual_boundary"],
    )


def _assert_secondary_support_authorability_trace_output(
    testcase: unittest.TestCase,
    summary: dict[str, Any],
    _temp_dir_path: Path | None,
) -> None:
    testcase.assertEqual(
        "existing_transfer_mediation_already_authors_descendant_secondary_basin_load_carrier_support_condition",
        summary["diagnosed_authorability_result"],
    )


def _assert_collapse_regime_trace_output(
    testcase: unittest.TestCase,
    summary: dict[str, Any],
    _temp_dir_path: Path | None,
) -> None:
    testcase.assertIsNone(summary["direct_lane"]["first_collapse_step"])
    testcase.assertEqual(17, summary["path_lane"]["first_collapse_step"])
    testcase.assertEqual(
        "collapse_is_path_regime_specific_support_to_carrier_resolution_and_not_split_child_driven_under_current_structure",
        summary["diagnosed_collapse_read"],
    )


def _assert_broad_collapse_survey_output(
    testcase: unittest.TestCase,
    summary: dict[str, Any],
    _temp_dir_path: Path | None,
) -> None:
    testcase.assertEqual(3, summary["lane_count"])
    testcase.assertEqual(
        "recorded_collapse_lanes_are_plural_and_heterogeneous_so_broader_controlled_comparison_is_still_required",
        summary["diagnosed_broadened_collapse_read"],
    )


def _assert_pre_spark_collapse_decomposition_output(
    testcase: unittest.TestCase,
    summary: dict[str, Any],
    _temp_dir_path: Path | None,
) -> None:
    testcase.assertEqual(3, summary["baseline_lane"]["first_collapse_step"])
    testcase.assertEqual(100, summary["comparison_lane"]["first_collapse_step"])
    testcase.assertEqual(
        "pre_spark_collapse_sink_difference_tracks_existing_junction_vs_boundary_channel_structure_so_no_new_collapse_family_is_justified_yet",
        summary["diagnosed_pre_spark_collapse_decomposition"],
    )


def _assert_post_spark_collapse_boundary_output(
    testcase: unittest.TestCase,
    summary: dict[str, Any],
    _temp_dir_path: Path | None,
) -> None:
    testcase.assertEqual(71, summary["baseline_lane"]["first_collapse_step"])
    testcase.assertEqual(99, summary["blocked_control_lane"]["first_collapse_step"])
    testcase.assertEqual(
        "existing_transfer_mediation_center_coupling_classes_already_author_post_spark_collapse_boundary",
        summary["diagnosed_post_spark_collapse_boundary"],
    )


def _assert_post_spark_late_window_stability_output(
    testcase: unittest.TestCase,
    summary: dict[str, Any],
    _temp_dir_path: Path | None,
) -> None:
    testcase.assertEqual(5, summary["blocked_control_post_window"]["post_window_collapse_count"])
    testcase.assertEqual(
        121,
        summary["blocked_control_post_window"]["first_post_window_matching_baseline_pattern_step"],
    )
    testcase.assertEqual(
        "blocked_control_eventually_reaches_baseline_collapse_pattern_only_after_a_distinct_carrier_split_child_cascade_so_late_window_interpretation_remains_open",
        summary["diagnosed_post_spark_late_window_stability"],
    )


def _assert_post_spark_delay_authorability_output(
    testcase: unittest.TestCase,
    summary: dict[str, Any],
    _temp_dir_path: Path | None,
) -> None:
    testcase.assertEqual(
        121,
        summary["blocked_control_post_window"]["first_post_window_matching_baseline_pattern_step"],
    )
    testcase.assertEqual(
        "existing_transfer_mediation_center_coupling_classes_already_author_blocked_lane_late_cascade_delay_before_shared_convergence",
        summary["diagnosed_post_spark_delay_authorability"],
    )


def _assert_post_collapse_geometry_exclusion_output(
    testcase: unittest.TestCase,
    summary: dict[str, Any],
    _temp_dir_path: Path | None,
) -> None:
    testcase.assertEqual(
        ["split_child", "basin_support"],
        summary["blocked_post_window_sink_kind_sequence"],
    )
    testcase.assertEqual(
        "existing_transfer_mediation_center_coupling_classes_already_author_geometry_mediated_shift_away_from_initial_collapsed_sink",
        summary["diagnosed_post_collapse_geometry_exclusion"],
    )


def _landscape_checkpoint_args(temp_dir_path: Path | None) -> list[str]:
    assert temp_dir_path is not None
    return [
        "--outputs-root",
        str(temp_dir_path / "outputs"),
        "--profile",
        "seed_baseline",
        "--steps",
        "2",
        "--record-graph-checkpoints",
        "--checkpoint-every-n-steps",
        "1",
        "--include-flow-overlays",
    ]


_SCRIPT_REJECT_SPECS = (
    _ScriptRejectSpec(
        "test_grcv3_path_failure_trace_script_rejects_non_positive_steps",
        _load_grcv3_path_failure_trace_script_module,
        ("--steps", "0"),
        "--steps must be > 0",
    ),
    _ScriptRejectSpec(
        "test_grcv3_candidate_transition_trace_script_rejects_non_positive_steps",
        _load_grcv3_candidate_transition_trace_script_module,
        ("--steps", "0"),
        "--steps must be > 0",
    ),
    _ScriptRejectSpec(
        "test_grcv3_settlement_locus_trace_script_rejects_non_positive_steps",
        _load_grcv3_settlement_locus_trace_script_module,
        ("--steps", "0"),
        "--steps must be > 0",
    ),
    _ScriptRejectSpec(
        "test_grcv3_settlement_reentry_trace_script_rejects_non_positive_steps",
        _load_grcv3_settlement_reentry_trace_script_module,
        ("--steps", "0"),
        "--steps must be > 0",
    ),
    _ScriptRejectSpec(
        "test_grcv3_settlement_reentry_neighborhood_trace_script_rejects_non_positive_steps",
        _load_grcv3_settlement_reentry_neighborhood_trace_script_module,
        ("--steps", "0"),
        "--steps must be > 0",
    ),
    _ScriptRejectSpec(
        "test_grcv3_settlement_reentry_support_isolation_trace_script_rejects_non_positive_steps",
        _load_grcv3_settlement_reentry_support_isolation_trace_script_module,
        ("--steps", "0"),
        "--steps must be > 0",
    ),
    _ScriptRejectSpec(
        "test_grcv3_settlement_reentry_secondary_support_counterfactual_trace_script_rejects_non_positive_steps",
        _load_grcv3_settlement_reentry_secondary_support_counterfactual_trace_script_module,
        ("--steps", "0"),
        "--steps must be > 0",
    ),
    _ScriptRejectSpec(
        "test_grcv3_secondary_support_authorability_trace_script_rejects_non_positive_steps",
        _load_grcv3_secondary_support_authorability_trace_script_module,
        ("--steps", "0"),
        "--steps must be > 0",
    ),
    _ScriptRejectSpec(
        "test_grcv3_collapse_regime_trace_script_rejects_non_positive_steps",
        _load_grcv3_collapse_regime_trace_script_module,
        ("--steps", "0"),
        "--steps must be > 0",
    ),
    _ScriptRejectSpec(
        "test_grcv3_pre_spark_collapse_decomposition_trace_script_rejects_non_positive_steps",
        _load_grcv3_pre_spark_collapse_decomposition_trace_script_module,
        ("--baseline-steps", "0"),
        "--baseline-steps must be > 0",
    ),
    _ScriptRejectSpec(
        "test_grcv3_post_spark_collapse_boundary_trace_script_rejects_non_positive_steps",
        _load_grcv3_post_spark_collapse_boundary_trace_script_module,
        ("--steps", "0"),
        "--steps must be > 0",
    ),
    _ScriptRejectSpec(
        "test_grcv3_post_spark_late_window_stability_trace_script_rejects_non_positive_steps",
        _load_grcv3_post_spark_late_window_stability_trace_script_module,
        ("--steps", "0"),
        "--steps must be > 0",
    ),
    _ScriptRejectSpec(
        "test_grcv3_post_spark_delay_authorability_trace_script_rejects_non_positive_steps",
        _load_grcv3_post_spark_delay_authorability_trace_script_module,
        ("--steps", "0"),
        "--steps must be > 0",
    ),
    _ScriptRejectSpec(
        "test_grcv3_post_collapse_geometry_exclusion_trace_script_rejects_non_positive_steps",
        _load_grcv3_post_collapse_geometry_exclusion_trace_script_module,
        ("--steps", "0"),
        "--steps must be > 0",
    ),
)

_SCRIPT_EMIT_SPECS = (
    _ScriptEmitSpec(
        "test_grcv3_landscape_script_can_emit_checkpoint_artifacts",
        _load_grcv3_landscape_script_module,
        _landscape_checkpoint_args,
        _assert_landscape_checkpoint_output,
        parse_json=False,
        use_temp_dir=True,
    ),
    _ScriptEmitSpec(
        "test_grcv3_path_failure_trace_script_emits_trace",
        _load_grcv3_path_failure_trace_script_module,
        _script_args(
            "--baseline-seed",
            str(RICH_V4_TRANSFER_MEDIATION_SEED),
            "--comparison-seed",
            str(RICH_V4_SINGLE_INTERMEDIATE_SEED),
            "--profile",
            "seed_baseline",
            "--steps",
            "2",
        ),
        _assert_path_failure_trace_output,
    ),
    _ScriptEmitSpec(
        "test_grcv3_candidate_transition_trace_script_emits_trace",
        _load_grcv3_candidate_transition_trace_script_module,
        _script_args(
            "--baseline-seed",
            str(RICH_V4_ASYMMETRIC_CENTER_COUPLING_SEED),
            "--comparison-seed",
            str(RICH_V4_ASYMMETRIC_CENTER_COUPLING_SINGLE_INTERMEDIATE_SEED),
            "--profile",
            "seed_baseline",
            "--steps",
            "8",
        ),
        _assert_candidate_transition_trace_output,
    ),
    _ScriptEmitSpec(
        "test_grcv3_settlement_locus_trace_script_emits_trace",
        _load_grcv3_settlement_locus_trace_script_module,
        _script_args(
            "--baseline-seed",
            str(RICH_V4_MEDIATED_SPILL_BRANCH_SEED),
            "--comparison-seed",
            str(RICH_V4_MEDIATED_SPILL_BRANCH_SINGLE_INTERMEDIATE_SEED),
            "--profile",
            "seed_baseline",
            "--steps",
            "12",
        ),
        _assert_settlement_locus_trace_output,
    ),
    _ScriptEmitSpec(
        "test_grcv3_settlement_reentry_trace_script_emits_trace",
        _load_grcv3_settlement_reentry_trace_script_module,
        _script_args(
            "--baseline-seed",
            str(RICH_V4_PATH_NODE_SPLIT_CHILD_INHERITING_SETTLEMENT_SEED),
            "--comparison-seed",
            str(RICH_V4_CARRIER_SITE_SPLIT_CHILD_INHERITING_SETTLEMENT_SEED),
            "--profile",
            "seed_baseline",
            "--steps",
            "12",
        ),
        _assert_settlement_reentry_trace_output,
    ),
    _ScriptEmitSpec(
        "test_grcv3_settlement_reentry_neighborhood_trace_script_emits_trace",
        _load_grcv3_settlement_reentry_neighborhood_trace_script_module,
        _script_args(
            "--baseline-seed",
            str(RICH_V4_PATH_NODE_SPLIT_CHILD_INHERITING_SETTLEMENT_SEED),
            "--comparison-seed",
            str(RICH_V4_CARRIER_SITE_SPLIT_CHILD_INHERITING_SETTLEMENT_SEED),
            "--profile",
            "seed_baseline",
            "--steps",
            "12",
        ),
        _assert_settlement_reentry_neighborhood_trace_output,
    ),
    _ScriptEmitSpec(
        "test_grcv3_settlement_reentry_support_isolation_trace_script_emits_trace",
        _load_grcv3_settlement_reentry_support_isolation_trace_script_module,
        _script_args(
            "--baseline-seed",
            str(RICH_V4_PATH_NODE_SPLIT_CHILD_INHERITING_SETTLEMENT_SEED),
            "--comparison-seed",
            str(RICH_V4_CARRIER_SITE_SPLIT_CHILD_INHERITING_SETTLEMENT_SEED),
            "--profile",
            "seed_baseline",
            "--steps",
            "12",
        ),
        _assert_settlement_reentry_support_isolation_trace_output,
    ),
    _ScriptEmitSpec(
        "test_grcv3_settlement_reentry_secondary_support_counterfactual_trace_script_emits_trace",
        _load_grcv3_settlement_reentry_secondary_support_counterfactual_trace_script_module,
        _script_args(
            "--baseline-seed",
            str(RICH_V4_PATH_NODE_SPLIT_CHILD_INHERITING_SETTLEMENT_SEED),
            "--comparison-seed",
            str(RICH_V4_CARRIER_SITE_SPLIT_CHILD_INHERITING_SETTLEMENT_SEED),
            "--profile",
            "seed_baseline",
            "--steps",
            "12",
        ),
        _assert_secondary_support_counterfactual_trace_output,
    ),
    _ScriptEmitSpec(
        "test_grcv3_secondary_support_authorability_trace_script_emits_trace",
        _load_grcv3_secondary_support_authorability_trace_script_module,
        _script_args(
            "--structural-path-seed",
            str(RICH_V4_MEDIATED_SPILL_BRANCH_SINGLE_INTERMEDIATE_SEED),
            "--explicit-path-seed",
            str(RICH_V4_PATH_NODE_SPLIT_CHILD_INHERITING_SETTLEMENT_SEED),
            "--structural-direct-seed",
            str(RICH_V4_MEDIATED_SPILL_BRANCH_SEED),
            "--explicit-direct-seed",
            str(RICH_V4_CARRIER_SITE_SPLIT_CHILD_INHERITING_SETTLEMENT_SEED),
            "--profile",
            "seed_baseline",
            "--steps",
            "12",
        ),
        _assert_secondary_support_authorability_trace_output,
    ),
    _ScriptEmitSpec(
        "test_grcv3_collapse_regime_trace_script_emits_trace",
        _load_grcv3_collapse_regime_trace_script_module,
        _script_args(
            "--direct-seed",
            str(RICH_V4_MEDIATED_SPILL_BRANCH_SEED),
            "--path-seed",
            str(RICH_V4_MEDIATED_SPILL_BRANCH_SINGLE_INTERMEDIATE_SEED),
            "--split-path-seed",
            str(RICH_V4_PATH_NODE_SPLIT_CHILD_INHERITING_SETTLEMENT_SEED),
            "--split-direct-seed",
            str(RICH_V4_CARRIER_SITE_SPLIT_CHILD_INHERITING_SETTLEMENT_SEED),
            "--profile",
            "seed_baseline",
            "--steps",
            "24",
        ),
        _assert_collapse_regime_trace_output,
    ),
    _ScriptEmitSpec(
        "test_grcv3_broad_collapse_survey_script_emits_trace",
        _load_grcv3_broad_collapse_survey_script_module,
        _script_args(),
        _assert_broad_collapse_survey_output,
    ),
    _ScriptEmitSpec(
        "test_grcv3_pre_spark_collapse_decomposition_trace_script_emits_trace",
        _load_grcv3_pre_spark_collapse_decomposition_trace_script_module,
        _script_args(
            "--baseline-seed",
            str(RICH_COLLAPSE_EXAMPLE_SEED),
            "--comparison-seed",
            str(RICH_BASIN_BOUNDARY_CHANNEL_SEED),
            "--baseline-profile",
            "hot_exploratory",
            "--comparison-profile",
            "seed_baseline",
            "--baseline-primitive-id",
            "decision_core",
            "--comparison-primitive-id",
            "core_basin",
            "--baseline-steps",
            "10",
            "--comparison-steps",
            "160",
        ),
        _assert_pre_spark_collapse_decomposition_output,
    ),
    _ScriptEmitSpec(
        "test_grcv3_post_spark_collapse_boundary_trace_script_emits_trace",
        _load_grcv3_post_spark_collapse_boundary_trace_script_module,
        _script_args(
            "--baseline-seed",
            str(RICH_V4_TRANSFER_MEDIATION_SEED),
            "--blocked-control-seed",
            str(RICH_V4_CENTER_COUPLING_SEED),
            "--refined-control-seed",
            str(RICH_V4_ASYMMETRIC_CENTER_COUPLING_SEED),
            "--profile",
            "seed_baseline",
            "--primitive-id",
            "spindle_core",
            "--steps",
            "120",
        ),
        _assert_post_spark_collapse_boundary_output,
    ),
    _ScriptEmitSpec(
        "test_grcv3_post_spark_late_window_stability_trace_script_emits_trace",
        _load_grcv3_post_spark_late_window_stability_trace_script_module,
        _script_args(
            "--baseline-seed",
            str(RICH_V4_TRANSFER_MEDIATION_SEED),
            "--blocked-control-seed",
            str(RICH_V4_CENTER_COUPLING_SEED),
            "--refined-control-seed",
            str(RICH_V4_ASYMMETRIC_CENTER_COUPLING_SEED),
            "--profile",
            "seed_baseline",
            "--primitive-id",
            "spindle_core",
            "--steps",
            "150",
            "--late-window-start-step",
            "100",
        ),
        _assert_post_spark_late_window_stability_output,
    ),
    _ScriptEmitSpec(
        "test_grcv3_post_spark_delay_authorability_trace_script_emits_trace",
        _load_grcv3_post_spark_delay_authorability_trace_script_module,
        _script_args(
            "--baseline-seed",
            str(RICH_V4_TRANSFER_MEDIATION_SEED),
            "--blocked-control-seed",
            str(RICH_V4_CENTER_COUPLING_SEED),
            "--refined-control-seed",
            str(RICH_V4_ASYMMETRIC_CENTER_COUPLING_SEED),
            "--profile",
            "seed_baseline",
            "--primitive-id",
            "spindle_core",
            "--steps",
            "150",
            "--late-window-start-step",
            "100",
        ),
        _assert_post_spark_delay_authorability_output,
    ),
    _ScriptEmitSpec(
        "test_grcv3_post_collapse_geometry_exclusion_trace_script_emits_trace",
        _load_grcv3_post_collapse_geometry_exclusion_trace_script_module,
        _script_args(
            "--blocked-control-seed",
            str(RICH_V4_CENTER_COUPLING_SEED),
            "--refined-control-seed",
            str(RICH_V4_ASYMMETRIC_CENTER_COUPLING_SEED),
            "--profile",
            "seed_baseline",
            "--primitive-id",
            "spindle_core",
            "--steps",
            "150",
            "--late-window-start-step",
            "100",
        ),
        _assert_post_collapse_geometry_exclusion_output,
    ),
)


def _make_script_reject_test(spec: _ScriptRejectSpec) -> Callable[[TelemetryScriptTest], None]:
    def test(self: TelemetryScriptTest) -> None:
        self._assert_script_rejects_non_positive_steps(
            spec.load_module,
            list(spec.argv),
            spec.stderr_fragment,
        )

    test.__name__ = spec.method_name
    return test


def _make_script_emit_test(spec: _ScriptEmitSpec) -> Callable[[TelemetryScriptTest], None]:
    def test(self: TelemetryScriptTest) -> None:
        self._assert_script_emits_output(
            spec.load_module,
            spec.argv_factory,
            spec.assert_output,
            parse_json=spec.parse_json,
            use_temp_dir=spec.use_temp_dir,
        )

    test.__name__ = spec.method_name
    return test


for _reject_spec in _SCRIPT_REJECT_SPECS:
    setattr(
        TelemetryScriptTest,
        _reject_spec.method_name,
        _make_script_reject_test(_reject_spec),
    )

for _emit_spec in _SCRIPT_EMIT_SPECS:
    setattr(
        TelemetryScriptTest,
        _emit_spec.method_name,
        _make_script_emit_test(_emit_spec),
    )


if __name__ == "__main__":
    unittest.main()

"""Checkpoint telemetry tests for the Phase T follow-on artifact layer."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from pygrc import models, telemetry
from pygrc.telemetry import experiments as telemetry_experiments
from pygrc.landscapes import (
    BasinSeedPrimitive,
    LandscapeSeed,
    SeedConstitutiveProfile,
    SeedDocumentMeta,
    SeedPotential,
    SeedTransportIntent,
    ValleySeedPrimitive,
)


RICH_V4_TRANSFER_MEDIATION_SEED = Path(
    "configs/landscapes/seed/grcv3-rich-v4-transfer-mediation-probe.seed.yaml"
)


def _identity() -> telemetry.RunTelemetryIdentity:
    return telemetry.RunTelemetryIdentity(
        run_id="run123",
        model_family="grcv2",
        params_identity="params123",
        seed_name="Cell-1",
        seed_source_reference="rc-sim/configs/landscapes/cell-1.json",
        seed_path="configs/landscapes/seed/cell-1.seed.yaml",
        param_family="balanced_baseline",
        rng_seed=7,
        requested_steps=2,
    )


def _checkpoint_artifact() -> telemetry.GraphCheckpointArtifact:
    return telemetry.GraphCheckpointArtifact(
        identity=_identity(),
        checkpoint_id="step-00000001",
        step_index=1,
        time=0.1,
        checkpoint_label="interval",
        checkpoint_reason="interval",
        graph_kind="weighted_graph",
        node_count=2,
        edge_count=1,
        node_records=(
            {"node_id": 0, "coherence": 0.6},
            {"node_id": 1, "coherence": 0.4},
        ),
        edge_records=(
            {
                "edge_id": 0,
                "source_node_id": 0,
                "target_node_id": 1,
                "base_conductance": 0.75,
                "signed_flux": 0.12,
            },
        ),
        event_step_range={"start_step_inclusive": 1, "end_step_inclusive": 1},
        event_count_window=1,
        event_counts_by_kind_window={"birth": 1},
        flow_representation="signed_edge_flux",
        flow_cadence="checkpoint_only",
        label_computation_modes={"flux_coupling": "absolute_flux"},
        topology_extensions={"next_node_id": 2, "next_edge_id": 1},
        family_extensions={"grcv2": {"budget_target": 1.0}},
    )


def _transport_seed() -> LandscapeSeed:
    return LandscapeSeed(
        seed_schema="pygrc.landscape_seed",
        seed_version="0.1",
        meta=SeedDocumentMeta(name="transport", source_kind="unit"),
        constitutive_profile=SeedConstitutiveProfile(
            lambda_c=1.0,
            xi_c=1.0,
            zeta_c=1.0,
            kappa_c=1.0,
            dt=0.1,
            budget_b=10.0,
            potential=SeedPotential(type="double_well", params={"a": 1.0, "b": 1.2}),
        ),
        primitives=[
            BasinSeedPrimitive(id="a", coherence_prior=2.0),
            BasinSeedPrimitive(id="b", coherence_prior=3.0),
            ValleySeedPrimitive(id="channel", from_id="a", to_id="b", coherence_prior=0.5),
        ],
        transport_intent=[
            SeedTransportIntent(
                id="intent",
                mode="directed_bias",
                sources=["a"],
                targets=["b"],
                carrier_id="channel",
                magnitude_hint=0.5,
                priority=0.25,
            )
        ],
    )


class TelemetryCheckpointTest(unittest.TestCase):
    """Validate checkpoint schema, I/O, and first GRCV2 export path."""

    def test_graph_checkpoint_and_index_roundtrip(self) -> None:
        checkpoint = _checkpoint_artifact()
        index = telemetry.GraphCheckpointIndex(
            identity=_identity(),
            selection_policy="initial+final+every_n_steps",
            selection_params={
                "include_initial": True,
                "include_final": True,
                "every_n_steps": 1,
            },
            checkpoints=(
                telemetry.GraphCheckpointReference(
                    checkpoint_id=checkpoint.checkpoint_id,
                    step_index=checkpoint.step_index,
                    time=checkpoint.time,
                    checkpoint_label=checkpoint.checkpoint_label,
                    checkpoint_reason=checkpoint.checkpoint_reason,
                    path=f"{checkpoint.checkpoint_id}.json",
                    event_step_range=checkpoint.event_step_range,
                    event_count_window=checkpoint.event_count_window,
                    event_counts_by_kind_window=checkpoint.event_counts_by_kind_window,
                ),
            ),
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            root_dir = Path(temp_dir) / "outputs"
            layout = telemetry.build_telemetry_artifact_layout("run123", root_dir=root_dir)

            telemetry.save_graph_checkpoint(
                telemetry.build_graph_checkpoint_path(layout, checkpoint.checkpoint_id),
                checkpoint,
            )
            telemetry.save_graph_checkpoint_index(layout.graph_checkpoint_index_path, index)

            loaded_checkpoint = telemetry.load_graph_checkpoint(
                telemetry.build_graph_checkpoint_path(layout, checkpoint.checkpoint_id)
            )
            loaded_index = telemetry.load_graph_checkpoint_index(layout.graph_checkpoint_index_path)

        self.assertEqual("signed_edge_flux", loaded_checkpoint.flow_representation)
        self.assertEqual(1, loaded_checkpoint.event_count_window)
        self.assertEqual("step-00000001.json", loaded_index.checkpoints[0].path)

    def test_run_grcv2_landscape_seed_can_emit_checkpoint_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = models.run_grcv2_landscape_seed(
                Path("configs/landscapes/seed/cell-1.seed.yaml"),
                family_name="balanced_baseline",
                rng_seed=7,
                num_steps=2,
                telemetry_root=Path(temp_dir) / "outputs",
                telemetry_experiment_path=Path("grcv2") / "checkpoint-smoke",
                record_graph_checkpoints=True,
                checkpoint_every_n_steps=1,
                include_flow_overlays=True,
            )

            assert result.telemetry is not None
            self.assertIsNotNone(result.telemetry.graph_checkpoint_index)
            self.assertEqual(3, len(result.telemetry.graph_checkpoints))
            layout = result.telemetry.artifact_layout
            assert layout is not None
            self.assertTrue(layout.graph_checkpoint_index_path.exists())
            self.assertTrue(layout.graph_checkpoints_dir.exists())

            loaded_pack = telemetry.load_telemetry_artifact_pack(layout)

        self.assertIsNotNone(loaded_pack.graph_checkpoint_index)
        self.assertEqual(3, len(loaded_pack.graph_checkpoints))
        self.assertEqual("step-00000000", loaded_pack.graph_checkpoints[0].checkpoint_id)
        self.assertEqual("initial", loaded_pack.graph_checkpoints[0].checkpoint_label)
        self.assertEqual("final", loaded_pack.graph_checkpoints[-1].checkpoint_label)
        self.assertTrue(
            any(
                checkpoint.flow_representation == "signed_edge_flux"
                for checkpoint in loaded_pack.graph_checkpoints[1:]
            )
        )
        self.assertTrue(
            all(checkpoint.graph_kind == "weighted_graph" for checkpoint in loaded_pack.graph_checkpoints)
        )
        self.assertEqual(
            "structural_support",
            loaded_pack.graph_checkpoints[0].edge_records[0]["directionality_semantics"],
        )
        post_step_edge_record = loaded_pack.graph_checkpoints[1].edge_records[0]
        self.assertIn("signed_flux_source", post_step_edge_record)
        self.assertIn("signed_flux_target", post_step_edge_record)
        self.assertEqual(
            -post_step_edge_record["signed_flux_source"],
            post_step_edge_record["signed_flux_target"],
        )
        self.assertIn("geometric_length_available", post_step_edge_record)

    def test_checkpoint_export_preserves_transport_bias_and_mass_scale_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = models.run_grcv2_landscape_seed(
                _transport_seed(),
                family_name="balanced_baseline",
                rng_seed=7,
                num_steps=1,
                telemetry_root=Path(temp_dir) / "outputs",
                telemetry_experiment_path=Path("grcv2") / "checkpoint-transport-smoke",
                record_graph_checkpoints=True,
                checkpoint_every_n_steps=1,
                include_flow_overlays=True,
            )

            assert result.telemetry is not None
            layout = result.telemetry.artifact_layout
            assert layout is not None
            loaded_pack = telemetry.load_telemetry_artifact_pack(layout)

        initial_checkpoint = loaded_pack.graph_checkpoints[0]
        post_step_checkpoint = loaded_pack.graph_checkpoints[1]
        edge_record = initial_checkpoint.edge_records[0]
        self.assertAlmostEqual(1.75, edge_record["transport_intent_multiplier"])
        self.assertIn("landscape_base_conductance", edge_record)
        self.assertFalse(edge_record["geometric_length_available"])
        self.assertEqual("transport_channel", edge_record["directionality_semantics"])
        self.assertAlmostEqual(
            2.0,
            initial_checkpoint.family_extensions["grcv2"]["mass_scale"],
        )
        self.assertEqual(
            "strict_always_on",
            initial_checkpoint.family_extensions["grcv2"]["seed_validation_mode"],
        )
        self.assertIn("signed_flux_source", post_step_checkpoint.edge_records[0])

    def test_run_grcv2_landscape_seed_can_stream_dense_checkpoints_in_chunks(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = models.run_grcv2_landscape_seed(
                Path("configs/landscapes/seed/cell-1.seed.yaml"),
                family_name="balanced_baseline",
                rng_seed=7,
                num_steps=3,
                telemetry_root=Path(temp_dir) / "outputs",
                telemetry_experiment_path=Path("grcv2") / "checkpoint-dense-smoke",
                record_graph_checkpoints=True,
                checkpoint_every_step=True,
                checkpoint_storage_mode="jsonl_chunks",
                checkpoint_chunk_size=2,
                include_flow_overlays=True,
            )

            assert result.telemetry is not None
            self.assertIsNotNone(result.telemetry.graph_checkpoint_index)
            self.assertEqual(0, len(result.telemetry.graph_checkpoints))
            layout = result.telemetry.artifact_layout
            assert layout is not None
            self.assertTrue(layout.graph_checkpoint_index_path.exists())
            self.assertTrue(
                telemetry.build_graph_checkpoint_chunk_path(layout, 1).exists()
            )
            self.assertTrue(
                telemetry.build_graph_checkpoint_chunk_path(layout, 2).exists()
            )

            loaded_pack = telemetry.load_telemetry_artifact_pack(layout)

        assert loaded_pack.graph_checkpoint_index is not None
        self.assertEqual(4, len(loaded_pack.graph_checkpoints))
        self.assertEqual(
            ("initial", "interval", "interval", "final"),
            tuple(checkpoint.checkpoint_label for checkpoint in loaded_pack.graph_checkpoints),
        )
        self.assertEqual(
            ("jsonl_chunk", "jsonl_chunk", "jsonl_chunk", "jsonl_chunk"),
            tuple(
                reference.storage_kind
                for reference in loaded_pack.graph_checkpoint_index.checkpoints
            ),
        )
        self.assertEqual(
            (0, 1, 0, 1),
            tuple(
                reference.chunk_line_index
                for reference in loaded_pack.graph_checkpoint_index.checkpoints
            ),
        )

    def test_dense_chunk_streaming_requires_artifact_root(self) -> None:
        with self.assertRaises(ValueError):
            models.run_grcv2_landscape_seed(
                Path("configs/landscapes/seed/cell-1.seed.yaml"),
                family_name="balanced_baseline",
                rng_seed=7,
                num_steps=2,
                record_graph_checkpoints=True,
                checkpoint_every_step=True,
                checkpoint_storage_mode="jsonl_chunks",
            )

    def test_export_grcv3_graph_checkpoint_surface(self) -> None:
        from pygrc.models.grc_v3_checkpoints import export_grcv3_graph_checkpoint

        identity = telemetry.RunTelemetryIdentity(
            run_id="grcv3-run",
            model_family="grcv3",
            params_identity="params-grcv3",
            seed_name="phase5_reference_primary",
            seed_source_reference="implementation/Phase-5-RepresentativeRuntime.md",
            seed_path="synthetic/grcv3/phase5_reference/primary",
            requested_steps=1,
        )
        model = telemetry_experiments._build_grcv3_representative_model()
        model.rebuild_basin_attributes()
        model.rebuild_identity_state()
        checkpoint = export_grcv3_graph_checkpoint(
            model,
            identity=identity,
            checkpoint_id="step-00000000",
            checkpoint_label="initial",
            checkpoint_reason="initial",
            event_step_range={"start_step_inclusive": 0, "end_step_inclusive": 0},
            event_count_window=0,
            event_counts_by_kind_window={},
            include_flow_overlays=True,
        )

        self.assertEqual("weighted_graph", checkpoint.graph_kind)
        self.assertEqual("not_available_pre_step", checkpoint.flow_representation)
        self.assertEqual("phase_t_iter26_v1", checkpoint.family_extensions["grcv3"]["contract_version"])
        self.assertIn("backend_summary", checkpoint.family_extensions["grcv3"])
        self.assertIn("hierarchy_summary", checkpoint.family_extensions["grcv3"])
        self.assertIn("spark_summary", checkpoint.family_extensions["grcv3"])
        self.assertIn("choice_summary", checkpoint.family_extensions["grcv3"])
        self.assertIn("gradient", checkpoint.node_records[0])
        self.assertIn("gradient_norm", checkpoint.node_records[0])
        self.assertIn("hessian", checkpoint.node_records[0])
        self.assertIn("net_flux", checkpoint.node_records[0])
        self.assertIn("base_conductance", checkpoint.edge_records[0])
        self.assertIn("geometric_length_available", checkpoint.edge_records[0])

    def test_export_grc9_graph_checkpoint_surface(self) -> None:
        from pygrc.models.grc_9_checkpoints import export_grc9_graph_checkpoint

        identity = telemetry.RunTelemetryIdentity(
            run_id="grc9-run",
            model_family="grc9",
            params_identity="params-grc9",
            seed_name="phase_t_grc9_iter6_representative_primary",
            seed_source_reference="implementation/Phase-T-GRC9-TelemetryContract.md",
            seed_path="synthetic/grc9/phase_t/primary",
            requested_steps=1,
        )
        model = telemetry_experiments._build_grc9_representative_model()
        model.step()
        checkpoint_a = export_grc9_graph_checkpoint(
            model,
            identity=identity,
            checkpoint_id="step-00000001",
            checkpoint_label="interval",
            checkpoint_reason="interval",
            event_step_range={"start_step_inclusive": 1, "end_step_inclusive": 1},
            event_count_window=2,
            event_counts_by_kind_window={"spark": 1, "expansion": 1},
            include_flow_overlays=True,
        )
        checkpoint_b = export_grc9_graph_checkpoint(
            model,
            identity=identity,
            checkpoint_id="step-00000001",
            checkpoint_label="interval",
            checkpoint_reason="interval",
            event_step_range={"start_step_inclusive": 1, "end_step_inclusive": 1},
            event_count_window=2,
            event_counts_by_kind_window={"spark": 1, "expansion": 1},
            include_flow_overlays=True,
        )

        self.assertEqual(checkpoint_a, checkpoint_b)
        self.assertEqual("port_graph", checkpoint_a.graph_kind)
        self.assertEqual("fixed_nine_slot_port_chart", checkpoint_a.layout_mode)
        self.assertEqual(2, checkpoint_a.layout_dimensions)
        self.assertEqual("checkpoint_only", checkpoint_a.flow_cadence)
        self.assertIn(
            checkpoint_a.flow_representation,
            ("signed_edge_flux", "zero_signed_edge_flux"),
        )
        self.assertIn("row_occupancy", checkpoint_a.node_records[0])
        self.assertIn("column_occupancy", checkpoint_a.node_records[0])
        self.assertIn("source_port_id", checkpoint_a.edge_records[0])
        self.assertIn("target_port_id", checkpoint_a.edge_records[0])
        grc9_extension = checkpoint_a.family_extensions["grc9"]
        self.assertEqual(
            telemetry.GRC9_TELEMETRY_CONTRACT_VERSION,
            grc9_extension["contract_version"],
        )
        self.assertEqual(
            "port_chart_module_overlay_v1",
            grc9_extension["checkpoint_payload"],
        )
        self.assertTrue(grc9_extension["port_overlays"])
        self.assertTrue(
            all(
                len(port_overlay) == 9
                for port_overlay in grc9_extension["port_overlays"].values()
            )
        )
        module_overlay = next(iter(grc9_extension["module_overlays"].values()))
        self.assertIn("core_node_id", module_overlay)
        self.assertIn("internal_edge_ids", module_overlay)
        self.assertTrue(module_overlay["internal_edge_ids"])
        self.assertEqual(
            ["1", "2", "3"],
            sorted(grc9_extension["latest_reassigned_boundary_edges_by_column"]),
        )
        self.assertTrue(
            any(record["internal_module_edge"] for record in checkpoint_a.edge_records)
        )
        self.assertTrue(
            any(record["reassigned_boundary_edge"] for record in checkpoint_a.edge_records)
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            layout = telemetry.build_telemetry_artifact_layout(
                "grc9-run",
                root_dir=Path(temp_dir),
            )
            telemetry.save_graph_checkpoint(
                telemetry.build_graph_checkpoint_path(layout, checkpoint_a.checkpoint_id),
                checkpoint_a,
            )
            loaded_checkpoint = telemetry.load_graph_checkpoint(
                telemetry.build_graph_checkpoint_path(layout, checkpoint_a.checkpoint_id)
            )

        self.assertEqual(
            checkpoint_a.family_extensions["grc9"],
            loaded_checkpoint.family_extensions["grc9"],
        )

    def test_grc9_phase_t_behavior_only_lane_does_not_emit_checkpoints(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = telemetry.run_grc9_representative_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                lane_name=telemetry.DEFAULT_GRC9_PHASE_T_REPRESENTATIVE_LANE,
                num_steps=2,
            )
            primary_telemetry = result.primary_run.telemetry
            layout = primary_telemetry.artifact_layout
            assert layout is not None

            self.assertIsNone(primary_telemetry.graph_checkpoint_index)
            self.assertEqual((), primary_telemetry.graph_checkpoints)
            self.assertFalse(layout.graph_checkpoint_index_path.exists())

    def test_export_grcv3_rich_v4_checkpoint_includes_monitoring_metadata(self) -> None:
        from pygrc.models.grc_v3_checkpoints import export_grcv3_graph_checkpoint

        identity = telemetry.RunTelemetryIdentity(
            run_id="grcv3-rich-v4",
            model_family="grcv3",
            params_identity="params-rich-v4",
            seed_name="grcv3-rich-v4-transfer-mediation-probe",
            seed_source_reference="implementation/GRCL-V3-ImplementationChecklist.md",
            seed_path=str(RICH_V4_TRANSFER_MEDIATION_SEED),
            requested_steps=1,
        )
        model = models.build_grcv3_from_landscape_seed(
            RICH_V4_TRANSFER_MEDIATION_SEED,
            params=models.resolve_grcv3_landscape_params(
                RICH_V4_TRANSFER_MEDIATION_SEED,
                profile_name="seed_baseline",
            ),
            profile_name="seed_baseline",
        )
        model.rebuild_basin_attributes()
        model.rebuild_identity_state()
        checkpoint = export_grcv3_graph_checkpoint(
            model,
            identity=identity,
            checkpoint_id="step-00000000",
            checkpoint_label="initial",
            checkpoint_reason="initial",
            event_step_range={"start_step_inclusive": 0, "end_step_inclusive": 0},
            event_count_window=0,
            event_counts_by_kind_window={},
            include_flow_overlays=True,
        )

        self.assertEqual(
            "transfer_mediation",
            checkpoint.family_extensions["grcv3"]["landscape_monitoring_surface_kind"],
        )
        self.assertIn(
            "spindle_core",
            checkpoint.family_extensions["grcv3"][
                "landscape_monitored_node_ids_by_primitive_id"
            ],
        )

    def test_run_grcv3_landscape_experiment_can_emit_checkpoint_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = telemetry.run_grcv3_landscape_experiment(
                telemetry_root=Path(temp_dir) / "outputs",
                telemetry_experiment_path=Path("grcv3_landscape") / "checkpoint-smoke",
                profile_name="seed_baseline",
                num_steps=2,
                record_graph_checkpoints=True,
                checkpoint_every_n_steps=1,
                include_flow_overlays=True,
            )

            assert result.cell1_run.telemetry is not None
            self.assertIsNotNone(result.cell1_run.telemetry.graph_checkpoint_index)
            self.assertEqual(3, len(result.cell1_run.telemetry.graph_checkpoints))
            layout = result.cell1_run.telemetry.artifact_layout
            assert layout is not None
            self.assertTrue(layout.graph_checkpoint_index_path.exists())
            self.assertTrue(layout.graph_checkpoints_dir.exists())

            loaded_pack = telemetry.load_telemetry_artifact_pack(layout)

        self.assertIsNotNone(loaded_pack.graph_checkpoint_index)
        self.assertEqual(3, len(loaded_pack.graph_checkpoints))
        self.assertEqual("step-00000000", loaded_pack.graph_checkpoints[0].checkpoint_id)
        self.assertEqual("initial", loaded_pack.graph_checkpoints[0].checkpoint_label)
        self.assertEqual("final", loaded_pack.graph_checkpoints[-1].checkpoint_label)
        self.assertTrue(
            all(
                checkpoint.graph_kind == "weighted_graph"
                for checkpoint in loaded_pack.graph_checkpoints
            )
        )
        self.assertEqual(
            "phase_t_iter26_v1",
            loaded_pack.graph_checkpoints[0].family_extensions["grcv3"]["contract_version"],
        )


if __name__ == "__main__":
    unittest.main()

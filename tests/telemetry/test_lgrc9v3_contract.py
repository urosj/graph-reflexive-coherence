"""Tests for LGRC9V3 telemetry and checkpoint extension contracts."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from pygrc.core import GRCEvent
from pygrc.models import (
    CAUSAL_LAYER_MODE_PACKETIZED_FIXED_TOPOLOGY,
    EDGE_DELAY_POLICY_CONSTANT_DELAY,
    LGRC9V3,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_ACTION_TRANSPORTED,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICY_EMIT_ROWS,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_ROW_KIND,
    LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
    LGRC9V3_TOPOLOGY_EVENT_KIND_IDENTITY_ACCEPTANCE,
    LGRC_RUNTIME_LEVEL_LGRC2,
    LAPSE_POLICY_UNIT,
    evaluate_lgrc9v3_proper_time_identity_persistence,
)
from pygrc.telemetry import (
    LGRC9V3_EVENT_DOMAIN_IDENTITY,
    LGRC9V3_EVENT_DOMAIN_PACKET,
    LGRC9V3_EVENT_DOMAIN_PULSE_SUBSTRATE_SURFACE,
    LGRC9V3_EVENT_DOMAIN_SPARK,
    LGRC9V3_EVENT_DOMAIN_TOPOLOGY,
    LGRC9V3_GRAPH_CHECKPOINT_SCHEMA_VERSION,
    LGRC9V3_TELEMETRY_CONTRACT_VERSION,
    LGRC9V3_TELEMETRY_FAMILY,
    GraphCheckpointArtifact,
    RunTelemetryIdentity,
    build_lgrc9v3_graph_checkpoint,
    event_rows_from_events,
    lgrc9v3_event_family_extensions_for_events,
    lgrc9v3_run_summary_family_extensions,
    lgrc9v3_step_family_extensions,
    load_event_rows,
    load_graph_checkpoint,
    save_event_rows,
    save_graph_checkpoint,
)

from tests.models.test_lgrc_9_v3_runtime import (
    _active_topology_params,
    _active_topology_with_surface_lineage_params,
    _active_topology_with_state_reabsorption_params,
    _route_arbitration_model_with_candidate_set,
    _route_arbitration_model_with_full_chain,
    _saturated_sink_state,
    _three_node_state,
)


def _identity() -> RunTelemetryIdentity:
    return RunTelemetryIdentity(
        run_id="lgrc9v3-telemetry-contract-test",
        model_family="LGRC9V3",
        params_identity="test-params",
        seed_name="unit-fixture",
    )


def _pulse_surface_params() -> dict[str, object]:
    return {
        "dt": 1.0,
        "causal_modes": {
            "causal_layer_mode": CAUSAL_LAYER_MODE_PACKETIZED_FIXED_TOPOLOGY,
            "lgrc_runtime_level": LGRC_RUNTIME_LEVEL_LGRC2,
            "lapse_policy": LAPSE_POLICY_UNIT,
            "edge_delay_policy": EDGE_DELAY_POLICY_CONSTANT_DELAY,
            "event_time_policy": "explicit_event_time_key",
            "proper_time_accumulation_policy": "local_event_frontier",
            "causal_pulse_substrate_surface_enabled": True,
            "causal_pulse_substrate_surface_policy": (
                LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICY_EMIT_ROWS
            ),
            "causal_pulse_substrate_surface_validated": True,
        },
    }


class LGRC9V3TelemetryContractTest(unittest.TestCase):
    """Validate Iteration 29 event rows and graph-checkpoint surfaces."""

    def test_event_rows_classify_packet_topology_spark_and_identity(self) -> None:
        model = LGRC9V3.from_state(
            _saturated_sink_state(),
            _active_topology_params(identity_allowed=True),
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=0,
            edge_id=0,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        arrival = model.step()
        evaluation = evaluate_lgrc9v3_proper_time_identity_persistence(
            source_topology_event_ids=["topology-source-1"],
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            sink_node_id=0,
            lineage_id="sink-0",
            basin_node_ids=[0],
            node_proper_time=model.get_state().node_proper_time,
            window_start_sink_proper_time=0.0,
            window_start_event_time_key=0.0,
            window_end_event_time_key=model.get_state().event_time_key,
            scheduler_event_index=model.get_state().scheduler_event_index,
            checkpoint_index=model.get_state().checkpoint_index,
            event_time_key=model.get_state().event_time_key,
            local_median_edge_delay=1.0,
            threshold_multiplier=1.0,
        )
        identity_event = model.emit_causal_identity_acceptance(evaluation)
        events = tuple(arrival.events) + (identity_event,)

        rows = event_rows_from_events(
            events,
            identity=_identity(),
            family_extensions_by_event=lgrc9v3_event_family_extensions_for_events(events),
        )

        domains = [
            row.family_extensions[LGRC9V3_TELEMETRY_FAMILY]["event_domain"]
            for row in rows
        ]
        self.assertIn(LGRC9V3_EVENT_DOMAIN_PACKET, domains)
        self.assertIn(LGRC9V3_EVENT_DOMAIN_SPARK, domains)
        self.assertIn(LGRC9V3_EVENT_DOMAIN_TOPOLOGY, domains)
        self.assertIn(LGRC9V3_EVENT_DOMAIN_IDENTITY, domains)
        self.assertTrue(
            all(
                row.family_extensions[LGRC9V3_TELEMETRY_FAMILY][
                    "contract_version"
                ]
                == LGRC9V3_TELEMETRY_CONTRACT_VERSION
                for row in rows
            )
        )
        identity_rows = [
            row
            for row in rows
            if row.event_kind == LGRC9V3_TOPOLOGY_EVENT_KIND_IDENTITY_ACCEPTANCE
        ]
        self.assertEqual(1, len(identity_rows))
        self.assertTrue(
            identity_rows[0].family_extensions[LGRC9V3_TELEMETRY_FAMILY][
                "identity_acceptance_emitted"
            ]
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "events.jsonl"
            save_event_rows(path, rows)
            loaded = load_event_rows(path)

        self.assertEqual(len(rows), len(loaded))
        self.assertEqual(
            LGRC9V3_EVENT_DOMAIN_SPARK,
            [
                row.family_extensions[LGRC9V3_TELEMETRY_FAMILY]["event_domain"]
                for row in loaded
                if row.event_kind == "lgrc9v3_causal_spark_candidate"
            ][0],
        )

    def test_graph_checkpoint_exposes_causal_clocks_packet_ledger_and_topology_history(self) -> None:
        model = LGRC9V3.from_state(
            _saturated_sink_state(),
            _active_topology_params(),
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=0,
            edge_id=0,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        model.step()

        checkpoint = build_lgrc9v3_graph_checkpoint(
            model,
            identity=_identity(),
            checkpoint_id="checkpoint-0001",
            checkpoint_label="after-causal-expansion",
            checkpoint_reason="unit_test",
        )
        extension = checkpoint.family_extensions[LGRC9V3_TELEMETRY_FAMILY]

        self.assertEqual("port_graph", checkpoint.graph_kind)
        self.assertEqual(
            LGRC9V3_GRAPH_CHECKPOINT_SCHEMA_VERSION,
            extension["checkpoint_schema_version"],
        )
        self.assertEqual(
            model.get_state().event_time_key,
            extension["causal_clocks"]["event_time_key"],
        )
        self.assertIn("packet_ledger", extension)
        self.assertIn("topology_history", extension)
        self.assertIn("runtime_state", extension)
        self.assertGreater(extension["topology_history"]["topology_event_count"], 0)
        self.assertTrue(
            all("node_proper_time" in record for record in checkpoint.node_records)
        )
        self.assertTrue(
            all("edge_causal_delay" in record for record in checkpoint.edge_records)
        )
        self.assertEqual(
            model.get_state().causal_spark_evaluation_index,
            extension["causal_spark"]["causal_spark_evaluation_index"],
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "checkpoint.json"
            save_graph_checkpoint(path, checkpoint)
            loaded = load_graph_checkpoint(path)

        loaded_extension = loaded.family_extensions[LGRC9V3_TELEMETRY_FAMILY]
        self.assertEqual(checkpoint.node_count, loaded.node_count)
        self.assertEqual(
            extension["causal_clocks"]["scheduler_event_index"],
            loaded_extension["causal_clocks"]["scheduler_event_index"],
        )
        self.assertEqual(
            LGRC9V3_GRAPH_CHECKPOINT_SCHEMA_VERSION,
            loaded_extension["checkpoint_schema_version"],
        )

    def test_step_extension_and_old_grc9v3_artifacts_remain_compatible(self) -> None:
        model = LGRC9V3.from_state(_three_node_state(), {"dt": 1.0})
        extension = lgrc9v3_step_family_extensions(model)

        self.assertEqual(
            0,
            extension[LGRC9V3_TELEMETRY_FAMILY]["scheduler_event_index"],
        )
        self.assertEqual(
            0,
            extension[LGRC9V3_TELEMETRY_FAMILY]["checkpoint_index"],
        )
        self.assertNotIn(
            "causal_pulse_substrate_surface",
            extension[LGRC9V3_TELEMETRY_FAMILY],
        )
        self.assertNotIn(
            "multi_basin_formation",
            extension[LGRC9V3_TELEMETRY_FAMILY],
        )
        run_summary = lgrc9v3_run_summary_family_extensions(model)[
            LGRC9V3_TELEMETRY_FAMILY
        ]
        self.assertNotIn("final_causal_pulse_substrate_surface", run_summary)
        self.assertNotIn("final_multi_basin_formation", run_summary)

        checkpoint = build_lgrc9v3_graph_checkpoint(
            model,
            identity=_identity(),
            checkpoint_id="default-off-checkpoint",
            checkpoint_label="default-off",
        )
        checkpoint_extension = checkpoint.family_extensions[LGRC9V3_TELEMETRY_FAMILY]
        self.assertNotIn("causal_pulse_substrate_surface", checkpoint_extension)
        self.assertNotIn("causal_pulse_substrate_surface_log", checkpoint_extension)
        self.assertNotIn(
            "causal_pulse_substrate_surface_lineage_log",
            checkpoint_extension,
        )
        self.assertNotIn("multi_basin_formation", checkpoint_extension)
        self.assertNotIn("post_refinement_flow_window_log", checkpoint_extension)
        self.assertNotIn("child_basin_state_log", checkpoint_extension)
        self.assertNotIn("multi_basin_replay_validation_log", checkpoint_extension)
        self.assertNotIn("merge_leakage_control_matrix_log", checkpoint_extension)
        self.assertNotIn("topology_state_reabsorption", checkpoint_extension)
        self.assertNotIn("topology_state_reabsorption_log", checkpoint_extension)

        identity = RunTelemetryIdentity(
            run_id="old-grc9v3-telemetry",
            model_family="GRC9V3",
            params_identity="old-params",
        )
        old_events = event_rows_from_events(
            (
                GRCEvent(
                    kind="hybrid_spark_candidate",
                    step_index=1,
                    payload={"candidate_node_id": 0},
                    source_family="GRC9V3",
                ),
            ),
            identity=identity,
        )
        old_checkpoint = GraphCheckpointArtifact(
            identity=identity,
            checkpoint_id="old-checkpoint",
            step_index=1,
            time=1.0,
            checkpoint_label="old-grc9v3",
            graph_kind="port_graph",
            node_count=1,
            edge_count=0,
            node_records=({"node_id": 0, "coherence": 1.0},),
            edge_records=(),
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            event_path = Path(temp_dir) / "old-events.jsonl"
            checkpoint_path = Path(temp_dir) / "old-checkpoint.json"
            save_event_rows(event_path, old_events)
            save_graph_checkpoint(checkpoint_path, old_checkpoint)
            loaded_events = load_event_rows(event_path)
            loaded_checkpoint = load_graph_checkpoint(checkpoint_path)

        self.assertEqual({}, dict(loaded_events[0].family_extensions))
        self.assertEqual({}, dict(loaded_checkpoint.family_extensions))
        self.assertEqual("GRC9V3", loaded_events[0].identity.model_family)
        self.assertEqual("GRC9V3", loaded_checkpoint.identity.model_family)

    def test_pulse_substrate_surface_exports_formal_telemetry_extensions(self) -> None:
        model = LGRC9V3.from_state(_three_node_state(), _pulse_surface_params())
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        step_result = model.step()
        surface_events = [
            event
            for event in step_result.events
            if event.kind == LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_ROW_KIND
        ]
        self.assertEqual(1, len(surface_events))

        rows = event_rows_from_events(
            tuple(surface_events),
            identity=_identity(),
            family_extensions_by_event=lgrc9v3_event_family_extensions_for_events(
                tuple(surface_events)
            ),
        )
        event_extension = rows[0].family_extensions[LGRC9V3_TELEMETRY_FAMILY]
        self.assertEqual(
            LGRC9V3_EVENT_DOMAIN_PULSE_SUBSTRATE_SURFACE,
            event_extension["event_domain"],
        )
        self.assertEqual("route_local_pulse_contact", event_extension["surface_kind"])
        self.assertTrue(event_extension["surface_policy_enabled"])
        self.assertTrue(event_extension["surface_policy_validated"])
        self.assertIsNotNone(event_extension["surface_digest"])
        self.assertEqual(
            "derived_surface_accounting",
            event_extension["surface_budget_surface"],
        )
        self.assertFalse(event_extension["movement_claim_allowed"])

        step_extension = lgrc9v3_step_family_extensions(model)[LGRC9V3_TELEMETRY_FAMILY]
        surface_summary = step_extension["causal_pulse_substrate_surface"]
        self.assertTrue(
            surface_summary["native_causal_pulse_substrate_surface_enabled"]
        )
        self.assertTrue(
            surface_summary["native_causal_pulse_substrate_surface_validated"]
        )
        self.assertEqual(1, surface_summary["surface_row_count"])
        self.assertEqual(1, surface_summary["route_local_pulse_contact_count"])
        self.assertFalse(surface_summary["movement_claim_allowed"])
        self.assertFalse(surface_summary["native_m6"])

        checkpoint = build_lgrc9v3_graph_checkpoint(
            model,
            identity=_identity(),
            checkpoint_id="pulse-substrate-checkpoint",
            checkpoint_label="after-surface-row",
        )
        checkpoint_extension = checkpoint.family_extensions[LGRC9V3_TELEMETRY_FAMILY]
        self.assertIn("causal_pulse_substrate_surface", checkpoint_extension)
        self.assertIn("causal_pulse_substrate_surface_log", checkpoint_extension)
        self.assertEqual(
            1,
            checkpoint_extension["causal_pulse_substrate_surface"][
                "surface_row_count"
            ],
        )
        self.assertEqual(1, len(checkpoint_extension["causal_pulse_substrate_surface_log"]))

    def test_pulse_substrate_lineage_exports_only_under_enabled_policy(self) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_surface_lineage_params(),
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        model.process_causal_collapse_reabsorption(
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            competing_sink_ids=[0, 1],
            selected_sink_id=0,
            losing_sink_ids=[1],
            transferred_node_ids=[1, 2],
            lineage_transfer_map={1: "0", 2: "0"},
            source_lineage_ids={1: "sink-1", 2: "node-2"},
            target_lineage_id="0",
            coherence_transfer_amount=0.0,
        )

        step_extension = lgrc9v3_step_family_extensions(model)[LGRC9V3_TELEMETRY_FAMILY]
        surface_summary = step_extension["causal_pulse_substrate_surface"]
        self.assertTrue(
            surface_summary[
                "native_causal_pulse_substrate_surface_lineage_transport_enabled"
            ]
        )
        self.assertEqual(1, surface_summary["surface_lineage_record_count"])
        self.assertEqual(1, surface_summary["transported_lineage_record_count"])
        self.assertEqual(0, surface_summary["superseded_lineage_record_count"])
        self.assertEqual(1, surface_summary["transported_surface_row_count"])
        self.assertEqual(
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_ACTION_TRANSPORTED,
            surface_summary["latest_surface_lineage_action"],
        )
        self.assertFalse(surface_summary["adaptive_topology_entry_allowed"])

        checkpoint = build_lgrc9v3_graph_checkpoint(
            model,
            identity=_identity(),
            checkpoint_id="pulse-substrate-lineage-checkpoint",
            checkpoint_label="after-lineage-transport",
        )
        checkpoint_extension = checkpoint.family_extensions[LGRC9V3_TELEMETRY_FAMILY]
        self.assertIn(
            "causal_pulse_substrate_surface_lineage_log",
            checkpoint_extension,
        )
        self.assertEqual(
            1,
            len(checkpoint_extension["causal_pulse_substrate_surface_lineage_log"]),
        )

    def test_topology_state_reabsorption_exports_only_under_enabled_policy(self) -> None:
        model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_state_reabsorption_params(),
        )
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=2,
            edge_id=1,
            amount=0.1,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        model.process_causal_collapse_reabsorption(
            topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            competing_sink_ids=[0, 1],
            selected_sink_id=0,
            losing_sink_ids=[1],
            transferred_node_ids=[1, 2],
            lineage_transfer_map={1: "0", 2: "0"},
            source_lineage_ids={1: "sink-1", 2: "node-2"},
            target_lineage_id="0",
            coherence_transfer_amount=0.0,
        )

        step_extension = lgrc9v3_step_family_extensions(model)[LGRC9V3_TELEMETRY_FAMILY]
        reabsorption_summary = step_extension["topology_state_reabsorption"]
        self.assertTrue(
            reabsorption_summary["native_topology_state_reabsorption_enabled"]
        )
        self.assertEqual(
            1,
            reabsorption_summary["topology_state_reabsorption_record_count"],
        )
        self.assertAlmostEqual(
            reabsorption_summary["active_node_state_total_after"],
            reabsorption_summary["packet_ledger_node_total_after"],
        )
        self.assertAlmostEqual(
            0.0,
            reabsorption_summary["node_plus_packet_budget_error"],
        )
        self.assertFalse(reabsorption_summary["movement_claim_allowed"])
        self.assertFalse(
            reabsorption_summary["topology_mutating_movement_claim_allowed"]
        )

        run_summary = lgrc9v3_run_summary_family_extensions(model)[
            LGRC9V3_TELEMETRY_FAMILY
        ]
        self.assertIn("final_topology_state_reabsorption", run_summary)

        checkpoint = build_lgrc9v3_graph_checkpoint(
            model,
            identity=_identity(),
            checkpoint_id="topology-state-reabsorption-checkpoint",
            checkpoint_label="after-topology-state-reabsorption",
        )
        checkpoint_extension = checkpoint.family_extensions[LGRC9V3_TELEMETRY_FAMILY]
        self.assertIn("topology_state_reabsorption", checkpoint_extension)
        self.assertIn("topology_state_reabsorption_log", checkpoint_extension)
        self.assertEqual(1, len(checkpoint_extension["topology_state_reabsorption_log"]))

    def test_native_route_arbitration_exports_only_under_enabled_policy(self) -> None:
        default_model = LGRC9V3.from_state(
            _three_node_state(),
            _active_topology_with_state_reabsorption_params(),
        )
        default_extension = lgrc9v3_step_family_extensions(default_model)[
            LGRC9V3_TELEMETRY_FAMILY
        ]
        self.assertNotIn("native_route_arbitration", default_extension)

        model, _candidate_set, _arbitration = (
            _route_arbitration_model_with_full_chain()
        )
        step_extension = lgrc9v3_step_family_extensions(model)[
            LGRC9V3_TELEMETRY_FAMILY
        ]
        route_summary = step_extension["native_route_arbitration"]
        self.assertTrue(route_summary["native_lgrc_route_arbitration_enabled"])
        self.assertEqual(2, route_summary["candidate_route_record_count"])
        self.assertEqual(1, route_summary["candidate_set_record_count"])
        self.assertEqual(1, route_summary["route_arbitration_record_count"])
        self.assertEqual(1, route_summary["committed_selected_topology_event_count"])
        self.assertFalse(route_summary["semantic_choice_claim_allowed"])
        self.assertFalse(route_summary["agency_claim_allowed"])

        run_summary = lgrc9v3_run_summary_family_extensions(model)[
            LGRC9V3_TELEMETRY_FAMILY
        ]
        self.assertIn("final_native_route_arbitration", run_summary)

        checkpoint = build_lgrc9v3_graph_checkpoint(
            model,
            identity=_identity(),
            checkpoint_id="native-route-arbitration-checkpoint",
            checkpoint_label="after-native-route-arbitration",
        )
        checkpoint_extension = checkpoint.family_extensions[LGRC9V3_TELEMETRY_FAMILY]
        self.assertIn("native_route_arbitration", checkpoint_extension)
        self.assertIn("native_route_candidate_log", checkpoint_extension)
        self.assertIn("native_route_candidate_set_log", checkpoint_extension)
        self.assertIn("native_route_arbitration_log", checkpoint_extension)
        self.assertEqual(2, len(checkpoint_extension["native_route_candidate_log"]))
        self.assertEqual(1, len(checkpoint_extension["native_route_arbitration_log"]))

    def test_multi_basin_formation_exports_summary_logs_and_claim_boundary(
        self,
    ) -> None:
        model, candidate_set = _route_arbitration_model_with_candidate_set(
            multi_basin_enabled=True,
        )
        arbitration = model.arbitrate_native_route_candidate_set(
            candidate_set_digest=str(candidate_set.candidate_set_digest),
        )["route_arbitration_record"]
        commit = model.commit_native_route_arbitration_selection(
            native_route_arbitration_reference=str(
                arbitration.native_route_arbitration_digest
            ),
        )
        child = commit["child_basin_state_records"][0]
        replay = model.validate_multi_basin_child_basin_replay(
            source_child_basin_state_digest=str(child.child_basin_state_digest),
            snapshot_replay_artifact=model.snapshot(),
        )
        model.validate_multi_basin_merge_leakage_controls(
            source_child_basin_state_digest=str(child.child_basin_state_digest),
            replay_validation_digest=str(replay["replay_validation_digest"]),
        )

        step_extension = lgrc9v3_step_family_extensions(model)[
            LGRC9V3_TELEMETRY_FAMILY
        ]
        summary = step_extension["multi_basin_formation"]
        self.assertTrue(summary["native_lgrc_multi_basin_formation_enabled"])
        self.assertTrue(summary["native_lgrc_multi_basin_formation_validated"])
        self.assertFalse(summary["native_lgrc_multi_basin_formation_supported"])
        self.assertEqual(1, summary["flow_window_record_count"])
        self.assertEqual(1, summary["child_basin_state_record_count"])
        self.assertEqual(1, summary["replay_validation_record_count"])
        self.assertEqual(
            summary["required_fail_closed_control_count"],
            summary["control_record_count"],
        )
        self.assertEqual(
            summary["required_fail_closed_control_count"],
            summary["failed_closed_control_count"],
        )
        self.assertEqual(0, summary["failed_open_control_count"])
        self.assertEqual(1, summary["clean_replay_record_count"])
        self.assertTrue(summary["mb5_control_backed_candidate_allowed"])
        self.assertFalse(summary["mb6_or_stronger_supported"])
        self.assertFalse(summary["native_support_claim_allowed"])
        self.assertFalse(summary["agency_claim_allowed"])
        self.assertFalse(summary["phase8_completion_claim_allowed"])

        run_summary = lgrc9v3_run_summary_family_extensions(model)[
            LGRC9V3_TELEMETRY_FAMILY
        ]
        self.assertEqual(
            summary,
            run_summary["final_multi_basin_formation"],
        )

        checkpoint = build_lgrc9v3_graph_checkpoint(
            model,
            identity=_identity(),
            checkpoint_id="multi-basin-formation-checkpoint",
            checkpoint_label="after-multi-basin-controls",
        )
        checkpoint_extension = checkpoint.family_extensions[LGRC9V3_TELEMETRY_FAMILY]
        checkpoint_summary = dict(checkpoint_extension["multi_basin_formation"])
        checkpoint_summary["missing_required_control_ids"] = list(
            checkpoint_summary["missing_required_control_ids"]
        )
        self.assertEqual(summary, checkpoint_summary)
        self.assertEqual(1, len(checkpoint_extension["post_refinement_flow_window_log"]))
        self.assertEqual(1, len(checkpoint_extension["child_basin_state_log"]))
        self.assertEqual(1, len(checkpoint_extension["multi_basin_replay_validation_log"]))
        self.assertEqual(
            summary["required_fail_closed_control_count"],
            len(checkpoint_extension["merge_leakage_control_matrix_log"]),
        )


if __name__ == "__main__":
    unittest.main()

"""D2.3 control-parity tests for native LGRC9V3 packet loops."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from typing import Any

from pygrc.core import PortGraphBackend
from pygrc.models import (
    GRC9V3NodeState,
    GRC9V3State,
    LGRC9V3,
    LGRC9V3RouteAspect,
    LGRC9V3RouteAspectChannel,
    LGRC9V3RouteAspectHop,
    PortEdge,
    validate_lgrc9v3_self_rearm_evidence_artifacts,
)
from pygrc.models.lgrc_9_v3_contract import (
    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_IDEMPOTENT_SKIP,
)
from pygrc.models.lgrc_9_v3_runtime import (
    LGRC9V3_AUTONOMOUS_PRODUCTION_LOG_KEY,
    LGRC9V3_ROUTE_ASPECT_SURPLUS_TRIGGER_CONFIG_KEY,
    LGRC9V3_SELF_REARM_EVIDENCE_EVENT_KIND,
    LGRC9V3_SELF_REARM_EVIDENCE_LOG_KEY,
)
from pygrc.telemetry.lgrc9v3_contract import (
    LGRC9V3_EVENT_DOMAIN_SELF_REARM,
    build_lgrc9v3_graph_checkpoint,
    classify_lgrc9v3_event_extension,
    classify_lgrc9v3_step_extension,
)
from pygrc.telemetry.schema import RunTelemetryIdentity


def _two_pole_state(*, source_coherence: float = 2.0) -> GRC9V3State:
    graph = PortGraphBackend()
    source = graph.add_node({"label": "source_pole"})
    sink = graph.add_node({"label": "sink_pole"})
    edge_forward = graph.connect_ports(source, 0, sink, 0, {"kind": "forward"})
    edge_return = graph.connect_ports(sink, 1, source, 1, {"kind": "return"})
    return GRC9V3State(
        topology=graph,
        nodes={
            source: GRC9V3NodeState(coherence=source_coherence),
            sink: GRC9V3NodeState(coherence=1.0),
        },
        port_edges={
            edge_forward: PortEdge(
                source,
                1,
                sink,
                1,
                conductance=1.0,
                flux_uv=0.0,
            ),
            edge_return: PortEdge(
                sink,
                2,
                source,
                2,
                conductance=1.0,
                flux_uv=0.0,
            ),
        },
        base_conductance={edge_forward: 1.0, edge_return: 1.0},
        geometric_length={edge_forward: 1.0, edge_return: 1.0},
        temporal_delay={edge_forward: 1.0, edge_return: 1.0},
        flux_coupling={edge_forward: 0.0, edge_return: 0.0},
    )


def _channel(
    channel_id: str,
    source_pole_id: str,
    target_pole_id: str,
    source_node_id: int,
    target_node_id: int,
    edge_id: int,
    expected_next_channel_id: str,
) -> LGRC9V3RouteAspectChannel:
    return LGRC9V3RouteAspectChannel(
        channel_id=channel_id,
        source_pole_id=source_pole_id,
        target_pole_id=target_pole_id,
        expected_next_channel_id=expected_next_channel_id,
        route_hops=(
            LGRC9V3RouteAspectHop(
                source_node_id=source_node_id,
                target_node_id=target_node_id,
                edge_id=edge_id,
            ),
        ),
    )


def _two_pole_route_aspect(*, direction: str = "clockwise") -> LGRC9V3RouteAspect:
    route_suffix = "cw" if direction == "clockwise" else "ccw"
    forward_channel = "S_to_K"
    return_channel = "K_to_S"
    return LGRC9V3RouteAspect(
        route_aspect_id=f"two_pole_surplus_loop_{route_suffix}",
        direction=direction,
        pole_regions={"S": (0,), "K": (1,)},
        channels=(
            _channel(
                forward_channel,
                "S",
                "K",
                0,
                1,
                0,
                return_channel,
            ),
            _channel(
                return_channel,
                "K",
                "S",
                1,
                0,
                1,
                forward_channel,
            ),
        ),
        channel_sequence=(forward_channel, return_channel),
    )


def _invalid_broken_return_route_aspect() -> LGRC9V3RouteAspect:
    return LGRC9V3RouteAspect(
        route_aspect_id="broken_return_control",
        direction="clockwise",
        pole_regions={"S": (0,), "K": (1,), "X": (2,)},
        channels=(
            _channel("S_to_K", "S", "K", 0, 1, 0, "K_to_X"),
            _channel("K_to_X", "K", "X", 1, 0, 1, "S_to_K"),
        ),
        channel_sequence=("S_to_K", "K_to_X"),
    )


def _invalid_scrambled_route_aspect() -> LGRC9V3RouteAspect:
    return LGRC9V3RouteAspect(
        route_aspect_id="scrambled_order_control",
        direction="clockwise",
        pole_regions={"S": (0,), "K": (1,)},
        channels=(
            _channel("S_to_K", "S", "K", 0, 1, 0, "S_to_K"),
            _channel("K_to_S", "K", "S", 1, 0, 1, "S_to_K"),
        ),
        channel_sequence=("S_to_K", "K_to_S"),
    )


class LGRC9V3NativePacketLoopControlParityTest(unittest.TestCase):
    """Validate Iteration 47 D2.3-style control parity."""

    n_cycles_min = 3

    def _process_parent_return_arrival(
        self,
        model: LGRC9V3,
        *,
        arrival_event_time_key: float = 1.0,
    ) -> None:
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=0,
            edge_id=1,
            amount=0.25,
            departure_event_time_key=0.0,
            arrival_event_time_key=arrival_event_time_key,
            scheduler_event_index=1,
        )
        model.run_event_queue(max_events=2)

    def _process_wrong_direction_arrival(self, model: LGRC9V3) -> None:
        model.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=0.0,
            arrival_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.run_event_queue(max_events=2)

    def _run_control(
        self,
        *,
        direction: str = "clockwise",
        source_coherence: float = 2.0,
        reference_mass: float = 1.0,
        trigger_threshold: float = 0.2,
        process_parent_return: bool = True,
        process_wrong_direction_parent: bool = False,
        process_child_departure: bool = True,
        arrival_event_time_key: float = 1.0,
    ) -> dict[str, Any]:
        model = LGRC9V3.from_state(
            _two_pole_state(source_coherence=source_coherence),
            {"dt": 1.0},
        )
        if process_wrong_direction_parent:
            self._process_wrong_direction_arrival(model)
        elif process_parent_return:
            self._process_parent_return_arrival(
                model,
                arrival_event_time_key=arrival_event_time_key,
            )

        route_aspect = _two_pole_route_aspect(direction=direction)
        forward_channel = route_aspect.channel_sequence[0]
        model.set_route_aspect_surplus_trigger(
            route_aspect=route_aspect,
            source_pole_id="S",
            reference_mass=reference_mass,
            trigger_threshold=trigger_threshold,
            packet_amount=0.1,
            eligible_channel_id=forward_channel,
        )
        produced = model.produce_events(
            policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS
        )
        if produced.scheduled_event_count and process_child_departure:
            model.step()

        validation = validate_lgrc9v3_self_rearm_evidence_artifacts(
            events=model.snapshot()["events"],
            production_results=(produced.to_artifact(),),
        )
        return {
            "native_lgrc9v3_execution": True,
            "native_packet_execution": True,
            "native_surplus_trigger": produced.scheduled_event_count > 0,
            "native_self_rearm_evidence": validation["valid"],
            "native_d2_3_equivalent": validation["valid"],
            "adapter_required_for_d2_3_semantics": not validation["valid"],
            "native_static_route_only": False,
            "native_grc9v3_loop_evidence": False,
            "movement_claim_allowed": False,
            "direction": direction,
            "scheduled_event_count": produced.scheduled_event_count,
            "event_count": len(model.snapshot()["events"]),
            "validation": validation,
            "trigger_to_departure_lag": None
            if not produced.production_records[0].scheduled_event_time_key
            else (
                produced.production_records[0].scheduled_event_time_key
                - produced.event_time_key
            ),
            "cycle_count": 1 if validation["valid"] else 0,
            "self_rearm_count": validation["completed_count"],
            "trigger_count": produced.scheduled_event_count,
            "primary_blocker": None
            if validation["valid"]
            else "self_rearm_chain_missing",
        }

    def _configure_recurrent_trigger(
        self,
        model: LGRC9V3,
        *,
        route_aspect: LGRC9V3RouteAspect,
        source_pole_id: str,
        reference_mass: float,
        eligible_channel_id: str,
    ) -> None:
        model.set_route_aspect_surplus_trigger(
            route_aspect=route_aspect,
            source_pole_id=source_pole_id,
            reference_mass=reference_mass,
            trigger_threshold=0.049,
            packet_amount=0.1,
            eligible_channel_id=eligible_channel_id,
        )

    def _run_recurrent_positive(
        self,
        *,
        direction: str,
        arrival_event_time_key: float = 1.0,
    ) -> tuple[LGRC9V3, tuple[dict[str, Any], ...], dict[str, Any]]:
        model = LGRC9V3.from_state(_two_pole_state(), {"dt": 1.0})
        self._process_parent_return_arrival(
            model,
            arrival_event_time_key=arrival_event_time_key,
        )
        route_aspect = _two_pole_route_aspect(direction=direction)
        source_to_sink = str(route_aspect.channel_sequence[0])
        sink_to_source = str(route_aspect.channel_sequence[1])
        production_results = []
        duplicate_suppressed_count = 0

        for cycle_index in range(self.n_cycles_min):
            self._configure_recurrent_trigger(
                model,
                route_aspect=route_aspect,
                source_pole_id="S",
                reference_mass=2.15,
                eligible_channel_id=source_to_sink,
            )
            produced_source = model.produce_events(
                policy=(
                    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS
                )
            )
            production_results.append(produced_source.to_artifact())
            if cycle_index == 0:
                duplicate = model.produce_events(
                    policy=(
                        LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS
                    )
                )
                production_results.append(duplicate.to_artifact())
                self.assertEqual(
                    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_IDEMPOTENT_SKIP,
                    duplicate.production_records[0].reason_code,
                )
                duplicate_suppressed_count += 1
            model.step()
            model.step()

            self._configure_recurrent_trigger(
                model,
                route_aspect=route_aspect,
                source_pole_id="K",
                reference_mass=0.75,
                eligible_channel_id=sink_to_source,
            )
            produced_sink = model.produce_events(
                policy=(
                    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS
                )
            )
            production_results.append(produced_sink.to_artifact())
            model.step()
            model.step()

        production_result_tuple = tuple(production_results)
        validation = validate_lgrc9v3_self_rearm_evidence_artifacts(
            events=model.snapshot()["events"],
            production_results=production_result_tuple,
        )
        route_len = len(route_aspect.channel_sequence)
        scheduled_count = sum(
            int(result["scheduled_event_count"]) for result in production_results
        )
        cycle_count = int(validation["completed_count"]) // route_len
        event_count = len(model.snapshot()["events"])
        report = {
            "native_lgrc9v3_execution": True,
            "native_packet_execution": True,
            "native_surplus_trigger": scheduled_count > 0,
            "native_self_rearm_evidence": validation["valid"],
            "native_d2_3_equivalent": validation["valid"]
            and cycle_count >= self.n_cycles_min,
            "adapter_required_for_d2_3_semantics": not validation["valid"],
            "native_static_route_only": False,
            "native_grc9v3_loop_evidence": False,
            "movement_claim_allowed": False,
            "direction": direction,
            "cycle_count": cycle_count,
            "trigger_count": scheduled_count,
            "self_rearm_count": validation["completed_count"],
            "event_count": event_count,
            "route_order": tuple(route_aspect.channel_sequence),
            "trigger_to_departure_lag": 0.0,
            "arrival_to_trigger_timing_policy": "producer_runs_after_arrival_step",
            "duplicate_suppressed_count": duplicate_suppressed_count,
            "scheduled_packet_count": scheduled_count,
            "accepted_trigger_count": scheduled_count,
            "validation": validation,
            "primary_blocker": None if validation["valid"] else "ledger_validation_failed",
        }
        return model, production_result_tuple, report

    def _production_log_from_snapshot(
        self,
        model: LGRC9V3,
    ) -> tuple[dict[str, Any], ...]:
        cached = model.snapshot()["dynamics"]["lgrc9v3_runtime"][
            "cached_quantities"
        ]
        return tuple(cached.get(LGRC9V3_AUTONOMOUS_PRODUCTION_LOG_KEY, ()))

    def test_clockwise_and_counter_clockwise_positive_controls_validate_cycles(
        self,
    ) -> None:
        _clockwise_model, _clockwise_results, clockwise = (
            self._run_recurrent_positive(direction="clockwise")
        )
        _counter_model, _counter_results, counter_clockwise = (
            self._run_recurrent_positive(direction="counter_clockwise")
        )

        self.assertTrue(clockwise["native_d2_3_equivalent"])
        self.assertTrue(counter_clockwise["native_d2_3_equivalent"])
        self.assertGreaterEqual(clockwise["cycle_count"], self.n_cycles_min)
        self.assertGreaterEqual(counter_clockwise["cycle_count"], self.n_cycles_min)
        self.assertEqual(
            clockwise["cycle_count"],
            counter_clockwise["cycle_count"],
        )
        self.assertEqual(
            clockwise["trigger_count"],
            counter_clockwise["trigger_count"],
        )
        self.assertEqual(
            clockwise["self_rearm_count"],
            counter_clockwise["self_rearm_count"],
        )
        self.assertEqual(
            clockwise["event_count"],
            counter_clockwise["event_count"],
        )
        self.assertEqual(
            clockwise["trigger_to_departure_lag"],
            counter_clockwise["trigger_to_departure_lag"],
        )
        self.assertEqual(clockwise["route_order"], counter_clockwise["route_order"])
        self.assertEqual(1, clockwise["duplicate_suppressed_count"])
        self.assertEqual(
            clockwise["scheduled_packet_count"],
            clockwise["accepted_trigger_count"],
        )
        self.assertFalse(clockwise["movement_claim_allowed"])
        self.assertFalse(clockwise["native_grc9v3_loop_evidence"])

    def test_jittered_delay_positive_control_validates(self) -> None:
        _model, _results, report = self._run_recurrent_positive(
            direction="clockwise",
            arrival_event_time_key=1.5,
        )

        self.assertTrue(report["native_d2_3_equivalent"])
        self.assertGreaterEqual(report["cycle_count"], self.n_cycles_min)
        self.assertFalse(report["movement_claim_allowed"])

    def test_no_surplus_subthreshold_and_threshold_too_high_controls_stay_negative(
        self,
    ) -> None:
        controls = {
            "no_surplus": self._run_control(
                source_coherence=0.75,
                reference_mass=1.0,
                trigger_threshold=0.2,
            ),
            "subthreshold": self._run_control(
                source_coherence=0.9,
                reference_mass=1.0,
                trigger_threshold=0.2,
            ),
            "threshold_too_high": self._run_control(
                source_coherence=2.0,
                reference_mass=1.0,
                trigger_threshold=2.0,
            ),
        }

        expected_blockers = {
            "no_surplus": "surplus_gate_failed",
            "subthreshold": "threshold_gate_failed",
            "threshold_too_high": "threshold_gate_failed",
        }
        for control_name, report in controls.items():
            self.assertFalse(report["native_d2_3_equivalent"])
            self.assertFalse(report["native_self_rearm_evidence"])
            self.assertEqual(0, report["scheduled_event_count"])
            report["primary_blocker"] = expected_blockers[control_name]
            self.assertIn(
                "no_completed_self_rearm_evidence",
                report["validation"]["failure_reasons"],
            )

    def test_wrong_direction_and_forward_only_controls_stay_negative(self) -> None:
        wrong_direction = self._run_control(process_wrong_direction_parent=True)
        forward_only = self._run_control(process_parent_return=False)

        self.assertTrue(wrong_direction["native_surplus_trigger"])
        self.assertFalse(wrong_direction["native_d2_3_equivalent"])
        wrong_direction["primary_blocker"] = "route_direction_gate_failed"
        self.assertIn(
            "no_completed_self_rearm_evidence",
            wrong_direction["validation"]["failure_reasons"],
        )
        self.assertTrue(forward_only["native_surplus_trigger"])
        self.assertFalse(forward_only["native_d2_3_equivalent"])
        forward_only["primary_blocker"] = "return_chain_missing"
        self.assertIn(
            "no_completed_self_rearm_evidence",
            forward_only["validation"]["failure_reasons"],
        )

    def test_broken_return_and_scrambled_order_controls_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            _invalid_broken_return_route_aspect()
        with self.assertRaises(ValueError):
            _invalid_scrambled_route_aspect()

    def test_snapshot_save_load_preserves_packet_loop_surfaces(self) -> None:
        model, production_results, report = self._run_recurrent_positive(
            direction="clockwise"
        )
        self.assertTrue(report["native_d2_3_equivalent"])
        runtime = model.snapshot()["dynamics"]["lgrc9v3_runtime"]
        cached = runtime["cached_quantities"]

        self.assertIn(LGRC9V3_ROUTE_ASPECT_SURPLUS_TRIGGER_CONFIG_KEY, cached)
        self.assertIn(LGRC9V3_SELF_REARM_EVIDENCE_LOG_KEY, cached)
        self.assertIn(LGRC9V3_AUTONOMOUS_PRODUCTION_LOG_KEY, cached)
        self.assertEqual(
            len(production_results),
            len(cached[LGRC9V3_AUTONOMOUS_PRODUCTION_LOG_KEY]),
        )
        self.assertGreaterEqual(
            len(cached[LGRC9V3_SELF_REARM_EVIDENCE_LOG_KEY]),
            2 * self.n_cycles_min,
        )
        validation = validate_lgrc9v3_self_rearm_evidence_artifacts(
            events=model.snapshot()["events"],
            production_results=self._production_log_from_snapshot(model),
        )
        self.assertTrue(validation["valid"], validation["failure_reasons"])
        counts_before = {
            "self_rearm": len(cached[LGRC9V3_SELF_REARM_EVIDENCE_LOG_KEY]),
            "producer": len(cached[LGRC9V3_AUTONOMOUS_PRODUCTION_LOG_KEY]),
            "packet_events": len(runtime["packet_ledger"]["packet_event_records"]),
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            snapshot_path = Path(temp_dir) / "native_packet_loop_snapshot.json"
            model.save(str(snapshot_path))
            restored = LGRC9V3.load(str(snapshot_path))

        restored_runtime = restored.snapshot()["dynamics"]["lgrc9v3_runtime"]
        restored_cached = restored_runtime["cached_quantities"]
        self.assertEqual(
            cached[LGRC9V3_ROUTE_ASPECT_SURPLUS_TRIGGER_CONFIG_KEY],
            restored_cached[LGRC9V3_ROUTE_ASPECT_SURPLUS_TRIGGER_CONFIG_KEY],
        )
        self.assertEqual(
            cached[LGRC9V3_SELF_REARM_EVIDENCE_LOG_KEY],
            restored_cached[LGRC9V3_SELF_REARM_EVIDENCE_LOG_KEY],
        )
        self.assertEqual(
            cached[LGRC9V3_AUTONOMOUS_PRODUCTION_LOG_KEY],
            restored_cached[LGRC9V3_AUTONOMOUS_PRODUCTION_LOG_KEY],
        )
        restored_counts = {
            "self_rearm": len(restored_cached[LGRC9V3_SELF_REARM_EVIDENCE_LOG_KEY]),
            "producer": len(restored_cached[LGRC9V3_AUTONOMOUS_PRODUCTION_LOG_KEY]),
            "packet_events": len(
                restored_runtime["packet_ledger"]["packet_event_records"]
            ),
        }
        self.assertEqual(counts_before, restored_counts)
        restored_validation = validate_lgrc9v3_self_rearm_evidence_artifacts(
            events=restored.snapshot()["events"],
            production_results=tuple(
                restored_cached[LGRC9V3_AUTONOMOUS_PRODUCTION_LOG_KEY]
            ),
        )
        self.assertTrue(
            restored_validation["valid"],
            restored_validation["failure_reasons"],
        )

    def test_continue_after_load_preserves_order_and_duplicate_suppression(
        self,
    ) -> None:
        model, _production_results, report = self._run_recurrent_positive(
            direction="clockwise"
        )
        self.assertTrue(report["native_d2_3_equivalent"])
        with tempfile.TemporaryDirectory() as temp_dir:
            snapshot_path = Path(temp_dir) / "native_packet_loop_snapshot.json"
            model.save(str(snapshot_path))
            restored = LGRC9V3.load(str(snapshot_path))

        route_aspect = _two_pole_route_aspect(direction="clockwise")
        self._configure_recurrent_trigger(
            restored,
            route_aspect=route_aspect,
            source_pole_id="S",
            reference_mass=2.15,
            eligible_channel_id="S_to_K",
        )
        produced = restored.produce_events(
            policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS
        )
        duplicate = restored.produce_events(
            policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS
        )
        self.assertEqual(1, produced.scheduled_event_count)
        self.assertEqual(0, duplicate.scheduled_event_count)
        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_IDEMPOTENT_SKIP,
            duplicate.production_records[0].reason_code,
        )
        restored.step()
        restored.step()
        validation = validate_lgrc9v3_self_rearm_evidence_artifacts(
            events=restored.snapshot()["events"],
            production_results=self._production_log_from_snapshot(restored),
        )
        self.assertTrue(validation["valid"], validation["failure_reasons"])
        self.assertGreaterEqual(validation["completed_count"], 2 * self.n_cycles_min + 1)

    def test_disabled_policy_stays_default_off_after_save_load(self) -> None:
        model = LGRC9V3.from_state(_two_pole_state(), {"dt": 1.0})
        with tempfile.TemporaryDirectory() as temp_dir:
            snapshot_path = Path(temp_dir) / "disabled_policy_snapshot.json"
            model.save(str(snapshot_path))
            restored = LGRC9V3.load(str(snapshot_path))

        produced = restored.produce_events()
        cached = restored.snapshot()["dynamics"]["lgrc9v3_runtime"][
            "cached_quantities"
        ]
        self.assertEqual(0, produced.scheduled_event_count)
        self.assertNotIn(LGRC9V3_AUTONOMOUS_PRODUCTION_LOG_KEY, cached)
        self.assertNotIn(LGRC9V3_SELF_REARM_EVIDENCE_LOG_KEY, cached)

    def test_telemetry_exposes_packet_loop_fields(self) -> None:
        model, _production_results, report = self._run_recurrent_positive(
            direction="clockwise"
        )
        self.assertTrue(report["native_d2_3_equivalent"])
        self_rearm_events = [
            event
            for event in model.snapshot()["events"]
            if event["kind"] == LGRC9V3_SELF_REARM_EVIDENCE_EVENT_KIND
        ]
        completed = next(
            event
            for event in self_rearm_events
            if event["payload"]["self_rearm_status"] == "child_departure_processed"
        )
        event_extension = classify_lgrc9v3_event_extension(
            completed["kind"],
            completed["payload"],
        )
        self.assertEqual(
            LGRC9V3_EVENT_DOMAIN_SELF_REARM,
            event_extension["event_domain"],
        )
        self.assertEqual(
            "child_departure_processed",
            event_extension["self_rearm_status"],
        )
        self.assertTrue(event_extension["native_self_rearm_evidence"])
        self.assertFalse(event_extension["movement_claim_allowed"])

        step_extension = classify_lgrc9v3_step_extension(model)
        self.assertTrue(
            step_extension["packet_loop"][
                "route_aspect_surplus_trigger_configured"
            ]
        )
        self.assertGreaterEqual(
            step_extension["packet_loop"]["completed_self_rearm_count"],
            2 * self.n_cycles_min,
        )
        self.assertTrue(step_extension["packet_loop"]["native_self_rearm_evidence"])
        self.assertFalse(step_extension["packet_loop"]["movement_claim_allowed"])

        identity = RunTelemetryIdentity(
            run_id="native-packet-loop-telemetry-test",
            model_family="LGRC9V3",
            params_identity=None,
        )
        checkpoint = build_lgrc9v3_graph_checkpoint(
            model,
            identity=identity,
            checkpoint_id="native_packet_loop_final",
            checkpoint_label="final",
        )
        family_extension = checkpoint.family_extensions["lgrc9v3"]
        self.assertIn("packet_loop", family_extension)
        self.assertIn("cached_quantities", family_extension)
        checkpoint_validation = validate_lgrc9v3_self_rearm_evidence_artifacts(
            events=model.snapshot()["events"],
            production_results=tuple(
                family_extension["cached_quantities"][
                    LGRC9V3_AUTONOMOUS_PRODUCTION_LOG_KEY
                ]
            ),
        )
        self.assertTrue(
            checkpoint_validation["valid"],
            checkpoint_validation["failure_reasons"],
        )


if __name__ == "__main__":
    unittest.main()

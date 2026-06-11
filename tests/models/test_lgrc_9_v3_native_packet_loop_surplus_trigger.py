"""Tests for native LGRC9V3 route-aspect surplus trigger producer."""

from __future__ import annotations

import unittest

from pygrc.core import InvalidStateTransitionError, PortGraphBackend
from pygrc.models import (
    GRC9V3NodeState,
    GRC9V3State,
    LGRC9V3,
    LGRC9V3RouteAspect,
    LGRC9V3RouteAspectChannel,
    LGRC9V3RouteAspectHop,
    LGRC9V3_SELF_REARM_EVIDENCE_EVENT_KIND,
    PortEdge,
    validate_lgrc9v3_self_rearm_evidence_artifacts,
)
from pygrc.models.lgrc_9_v3_contract import (
    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_DISABLED,
    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_IDEMPOTENT_SKIP,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_NO_ELIGIBLE_WORK,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_SURPLUS_TRIGGER_SCHEDULED,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_SURPLUS_TRIGGER_SUBTHRESHOLD,
)
from pygrc.models.lgrc_9_v3_packets import LGRC9V3_PACKET_EVENT_KIND_DEPARTURE


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


def _two_pole_route_aspect() -> LGRC9V3RouteAspect:
    return LGRC9V3RouteAspect(
        route_aspect_id="two_pole_surplus_loop",
        direction="clockwise",
        pole_regions={"S": (0,), "K": (1,)},
        channels=(
            LGRC9V3RouteAspectChannel(
                channel_id="S_to_K",
                source_pole_id="S",
                target_pole_id="K",
                expected_next_channel_id="K_to_S",
                route_hops=(
                    LGRC9V3RouteAspectHop(
                        source_node_id=0,
                        target_node_id=1,
                        edge_id=0,
                    ),
                ),
            ),
            LGRC9V3RouteAspectChannel(
                channel_id="K_to_S",
                source_pole_id="K",
                target_pole_id="S",
                expected_next_channel_id="S_to_K",
                route_hops=(
                    LGRC9V3RouteAspectHop(
                        source_node_id=1,
                        target_node_id=0,
                        edge_id=1,
                    ),
                ),
            ),
        ),
        channel_sequence=("S_to_K", "K_to_S"),
    )


class LGRC9V3RouteAspectSurplusTriggerTest(unittest.TestCase):
    """Validate Iteration 45 native surplus-trigger producer behavior."""

    def _process_parent_arrival_into_source_pole(self, model: LGRC9V3) -> None:
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=0,
            edge_id=1,
            amount=0.25,
            departure_event_time_key=0.0,
            scheduler_event_index=1,
        )
        results = model.run_event_queue(max_events=2)
        self.assertEqual(
            [
                LGRC9V3_PACKET_EVENT_KIND_DEPARTURE,
                "lgrc9v3_packet_arrival",
            ],
            [result.bookkeeping["processed_event_kind"] for result in results],
        )

    def _configure_positive_source_trigger(self, model: LGRC9V3) -> None:
        model.set_route_aspect_surplus_trigger(
            route_aspect=_two_pole_route_aspect(),
            source_pole_id="S",
            reference_mass=1.0,
            trigger_threshold=0.2,
            packet_amount=0.1,
        )

    def _completed_self_rearm_artifacts(
        self,
    ) -> tuple[list[dict[str, object]], tuple[dict[str, object], ...]]:
        model = LGRC9V3.from_state(_two_pole_state(), {"dt": 1.0})
        self._process_parent_arrival_into_source_pole(model)
        self._configure_positive_source_trigger(model)
        produced = model.produce_events(
            policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS
        )
        model.step()
        return model.snapshot()["events"], (produced.to_artifact(),)

    def test_disabled_policy_remains_noop_with_surplus_config(self) -> None:
        model = LGRC9V3.from_state(_two_pole_state(), {"dt": 1.0})
        before = model.snapshot()["dynamics"]["lgrc9v3_runtime"]
        model.set_route_aspect_surplus_trigger(
            route_aspect=_two_pole_route_aspect(),
            source_pole_id="S",
            reference_mass=1.0,
            trigger_threshold=0.5,
            packet_amount=0.25,
        )

        produced = model.produce_events(policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_DISABLED)

        self.assertEqual(0, produced.scheduled_event_count)
        self.assertEqual((), model.get_state().packet_ledger.event_queue_records)
        self.assertEqual(
            before["packet_ledger"],
            model.snapshot()["dynamics"]["lgrc9v3_runtime"]["packet_ledger"],
        )

    def test_missing_surplus_config_reports_no_eligible_work(self) -> None:
        model = LGRC9V3.from_state(_two_pole_state(), {"dt": 1.0})

        produced = model.produce_events(
            policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS
        )
        record = produced.production_records[0]

        self.assertEqual(0, produced.scheduled_event_count)
        self.assertFalse(produced.state_mutated)
        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_NO_ELIGIBLE_WORK,
            record.reason_code,
        )
        self.assertFalse(
            record.observed_evidence["route_aspect_surplus_trigger_configured"]
        )

    def test_surplus_trigger_schedules_departure_without_debiting_source(self) -> None:
        model = LGRC9V3.from_state(_two_pole_state(), {"dt": 1.0})
        model.set_route_aspect_surplus_trigger(
            route_aspect=_two_pole_route_aspect(),
            source_pole_id="S",
            reference_mass=1.0,
            trigger_threshold=0.5,
            packet_amount=0.25,
        )

        produced = model.produce_events(
            policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS
        )
        record = produced.production_records[0]
        queued_event = model.get_state().packet_ledger.event_queue_records[0]

        self.assertTrue(produced.state_mutated)
        self.assertEqual(1, produced.scheduled_event_count)
        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_SURPLUS_TRIGGER_SCHEDULED,
            record.reason_code,
        )
        self.assertEqual(LGRC9V3_PACKET_EVENT_KIND_DEPARTURE, record.scheduled_event_kind)
        self.assertEqual(queued_event.event_id, record.scheduled_event_id)
        self.assertEqual(0, record.trigger_node_id)
        self.assertEqual(0, record.trigger_edge_id)
        self.assertAlmostEqual(2.0, record.observed_evidence["observed_mass"])
        self.assertAlmostEqual(1.0, record.observed_evidence["reference_mass"])
        self.assertAlmostEqual(1.0, record.observed_evidence["surplus"])
        self.assertEqual("S_to_K", record.observed_evidence["eligible_channel_id"])
        self.assertEqual("K_to_S", record.observed_evidence["expected_next_channel_id"])
        self.assertEqual(queued_event.packet_id, record.observed_evidence["scheduled_packet_id"])
        self.assertAlmostEqual(
            0.0,
            record.observed_evidence["producer_event_time_key"],
        )
        self.assertAlmostEqual(
            0.0,
            record.observed_evidence["source_node_proper_time_at_evaluation"],
        )
        self.assertAlmostEqual(
            0.0,
            record.observed_evidence[
                "source_node_last_update_event_time_key_at_evaluation"
            ],
        )
        self.assertEqual(
            "step_processes_packet_departure",
            record.observed_evidence["producer_mutation_ownership"],
        )
        self.assertAlmostEqual(2.0, model.get_state().base_state.nodes[0].coherence)

        step = model.step()

        self.assertEqual(LGRC9V3_PACKET_EVENT_KIND_DEPARTURE, step.events[0].kind)
        self.assertAlmostEqual(1.75, model.get_state().base_state.nodes[0].coherence)
        self.assertAlmostEqual(
            0.25,
            model.get_state().packet_ledger.in_flight_packet_total,
        )

    def test_subthreshold_surplus_schedules_no_packet(self) -> None:
        model = LGRC9V3.from_state(_two_pole_state(source_coherence=1.25), {"dt": 1.0})
        model.set_route_aspect_surplus_trigger(
            route_aspect=_two_pole_route_aspect(),
            source_pole_id="S",
            reference_mass=1.0,
            trigger_threshold=0.5,
            packet_amount=0.25,
        )

        produced = model.produce_events(
            policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS
        )
        record = produced.production_records[0]

        self.assertFalse(produced.state_mutated)
        self.assertEqual(0, produced.scheduled_event_count)
        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_SURPLUS_TRIGGER_SUBTHRESHOLD,
            record.reason_code,
        )
        self.assertAlmostEqual(0.25, record.observed_evidence["surplus"])
        self.assertEqual((), model.get_state().packet_ledger.event_queue_records)

    def test_no_surplus_fixture_schedules_no_packet(self) -> None:
        model = LGRC9V3.from_state(_two_pole_state(source_coherence=1.0), {"dt": 1.0})
        model.set_route_aspect_surplus_trigger(
            route_aspect=_two_pole_route_aspect(),
            source_pole_id="S",
            reference_mass=1.0,
            trigger_threshold=0.5,
            packet_amount=0.25,
        )

        produced = model.produce_events(
            policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS
        )
        record = produced.production_records[0]

        self.assertFalse(produced.state_mutated)
        self.assertEqual(0, produced.scheduled_event_count)
        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_SURPLUS_TRIGGER_SUBTHRESHOLD,
            record.reason_code,
        )
        self.assertAlmostEqual(0.0, record.observed_evidence["surplus"])
        self.assertEqual((), model.get_state().packet_ledger.event_queue_records)

    def test_surplus_trigger_is_idempotent_in_same_eligibility_window(self) -> None:
        model = LGRC9V3.from_state(_two_pole_state(), {"dt": 1.0})
        model.set_route_aspect_surplus_trigger(
            route_aspect=_two_pole_route_aspect(),
            source_pole_id="S",
            reference_mass=1.0,
            trigger_threshold=0.5,
            packet_amount=0.25,
        )

        first = model.produce_events(
            policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS
        )
        second = model.produce_events(
            policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS
        )

        self.assertEqual(1, first.scheduled_event_count)
        self.assertEqual(0, second.scheduled_event_count)
        self.assertFalse(second.state_mutated)
        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_IDEMPOTENT_SKIP,
            second.production_records[0].reason_code,
        )
        self.assertEqual(1, len(model.get_state().packet_ledger.event_queue_records))

    def test_wrong_channel_direction_is_rejected_at_configuration(self) -> None:
        model = LGRC9V3.from_state(_two_pole_state(), {"dt": 1.0})

        with self.assertRaises(ValueError):
            model.set_route_aspect_surplus_trigger(
                route_aspect=_two_pole_route_aspect(),
                source_pole_id="K",
                reference_mass=1.0,
                trigger_threshold=0.5,
                packet_amount=0.25,
                eligible_channel_id="S_to_K",
            )

    def test_surplus_trigger_rejects_source_node_overdraw(self) -> None:
        model = LGRC9V3.from_state(_two_pole_state(), {"dt": 1.0})
        model.set_route_aspect_surplus_trigger(
            route_aspect=_two_pole_route_aspect(),
            source_pole_id="S",
            reference_mass=1.0,
            trigger_threshold=0.5,
            packet_amount=3.0,
        )

        with self.assertRaises(InvalidStateTransitionError):
            model.produce_events(
                policy=(
                    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS
                )
            )

    def test_self_rearm_candidate_requires_prior_parent_arrival(self) -> None:
        model = LGRC9V3.from_state(_two_pole_state(), {"dt": 1.0})
        self._configure_positive_source_trigger(model)

        produced = model.produce_events(
            policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS
        )

        self.assertEqual(1, produced.scheduled_event_count)
        self.assertNotIn(
            "native_self_rearm_evidence",
            produced.production_records[0].observed_evidence,
        )
        self.assertEqual(
            [],
            [
                event
                for event in model.snapshot()["events"]
                if event["kind"] == LGRC9V3_SELF_REARM_EVIDENCE_EVENT_KIND
            ],
        )

    def test_self_rearm_candidate_and_completion_chain_are_native_artifacts(
        self,
    ) -> None:
        model = LGRC9V3.from_state(_two_pole_state(), {"dt": 1.0})
        self._process_parent_arrival_into_source_pole(model)
        self._configure_positive_source_trigger(model)

        produced = model.produce_events(
            policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS
        )
        record = produced.production_records[0]
        candidate = record.observed_evidence["self_rearm_evidence"]
        candidate_events = [
            event
            for event in model.snapshot()["events"]
            if event["kind"] == LGRC9V3_SELF_REARM_EVIDENCE_EVENT_KIND
        ]

        self.assertTrue(record.observed_evidence["native_self_rearm_evidence"])
        self.assertEqual("scheduled_child_pending_departure", candidate["self_rearm_status"])
        self.assertEqual(record.record_id, candidate["producer_record_id"])
        self.assertEqual(
            record.observed_evidence["scheduled_packet_id"],
            candidate["child_packet_id"],
        )
        self.assertEqual(1, len(candidate_events))
        self.assertEqual(
            candidate["self_rearm_evidence_id"],
            candidate_events[0]["payload"]["self_rearm_evidence_id"],
        )
        self.assertTrue(candidate["event_time_ordering"]["arrival_before_or_at_producer"])
        self.assertTrue(
            candidate["event_time_ordering"]["producer_before_or_at_child_departure"]
        )
        self.assertAlmostEqual(2.25, candidate["observed_mass_after_arrival"])
        self.assertTrue(candidate["threshold_crossed"])
        self.assertEqual("S", candidate["source_pole_id"])
        self.assertEqual(0, candidate["parent_arrival_target_node_id"])
        self.assertEqual("K_to_S", candidate["parent_arrival_channel_id"])
        self.assertEqual("K_to_S", candidate["expected_previous_channel_id"])
        self.assertEqual("S_to_K", candidate["trigger_channel_id"])

        pending_log = model.get_state().cached_quantities[
            "lgrc9v3_self_rearm_evidence_log"
        ]
        self.assertEqual("scheduled_child_pending_departure", pending_log[0]["self_rearm_status"])
        pending_validation = validate_lgrc9v3_self_rearm_evidence_artifacts(
            events=model.snapshot()["events"],
            production_results=(produced.to_artifact(),),
        )
        self.assertFalse(pending_validation["valid"])
        self.assertIn(
            "no_completed_self_rearm_evidence",
            pending_validation["failure_reasons"],
        )

        step = model.step()
        completion_events = [
            event
            for event in step.events
            if event.kind == LGRC9V3_SELF_REARM_EVIDENCE_EVENT_KIND
        ]
        snapshot_events = [
            event
            for event in model.snapshot()["events"]
            if event["kind"] == LGRC9V3_SELF_REARM_EVIDENCE_EVENT_KIND
        ]

        self.assertEqual(LGRC9V3_PACKET_EVENT_KIND_DEPARTURE, step.events[0].kind)
        self.assertEqual(1, len(completion_events))
        completion = completion_events[0].payload
        self.assertEqual("child_departure_processed", completion["self_rearm_status"])
        self.assertEqual(
            candidate["self_rearm_evidence_id"],
            completion["candidate_self_rearm_evidence_id"],
        )
        self.assertEqual(
            candidate["child_departure_event_id"],
            completion["child_departure_processed_event_id"],
        )
        self.assertTrue(
            completion["event_time_ordering"]["arrival_before_or_at_child_departure"]
        )
        self.assertAlmostEqual(0.0, completion["child_departure_budget_error"])
        validation = validate_lgrc9v3_self_rearm_evidence_artifacts(
            events=model.snapshot()["events"],
            production_results=(produced.to_artifact(),),
        )
        self.assertTrue(validation["valid"], validation["failure_reasons"])
        self.assertEqual(1, validation["candidate_count"])
        self.assertEqual(1, validation["completed_count"])
        self.assertEqual(
            [completion["self_rearm_evidence_id"]],
            validation["validated_self_rearm_evidence_ids"],
        )
        self.assertEqual(2, len(snapshot_events))
        self.assertEqual(
            "child_departure_processed",
            model.get_state().cached_quantities[
                "lgrc9v3_self_rearm_evidence_log"
            ][0]["self_rearm_status"],
        )

    def test_subthreshold_trigger_emits_no_self_rearm_evidence(self) -> None:
        model = LGRC9V3.from_state(_two_pole_state(), {"dt": 1.0})
        self._process_parent_arrival_into_source_pole(model)
        model.set_route_aspect_surplus_trigger(
            route_aspect=_two_pole_route_aspect(),
            source_pole_id="S",
            reference_mass=1.0,
            trigger_threshold=2.0,
            packet_amount=0.1,
        )

        produced = model.produce_events(
            policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS
        )

        self.assertEqual(0, produced.scheduled_event_count)
        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_SURPLUS_TRIGGER_SUBTHRESHOLD,
            produced.production_records[0].reason_code,
        )
        self.assertEqual(
            [],
            [
                event
                for event in model.snapshot()["events"]
                if event["kind"] == LGRC9V3_SELF_REARM_EVIDENCE_EVENT_KIND
            ],
        )

    def test_scheduled_child_without_departure_remains_incomplete(self) -> None:
        model = LGRC9V3.from_state(_two_pole_state(), {"dt": 1.0})
        self._process_parent_arrival_into_source_pole(model)
        self._configure_positive_source_trigger(model)

        model.produce_events(
            policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS
        )

        self.assertEqual(
            [
                "scheduled_child_pending_departure",
            ],
            [
                record["self_rearm_status"]
                for record in model.get_state().cached_quantities[
                    "lgrc9v3_self_rearm_evidence_log"
                ]
            ],
        )

    def test_artifact_validator_rejects_missing_producer_record(self) -> None:
        events, _production_results = self._completed_self_rearm_artifacts()

        validation = validate_lgrc9v3_self_rearm_evidence_artifacts(
            events=events,
            production_results=(),
        )

        self.assertFalse(validation["valid"])
        self.assertTrue(
            any(
                reason.startswith("missing_producer_record:")
                for reason in validation["failure_reasons"]
            )
        )

    def test_artifact_validator_rejects_missing_parent_arrival(self) -> None:
        events, production_results = self._completed_self_rearm_artifacts()
        filtered_events = [
            event
            for event in events
            if event["kind"] != "lgrc9v3_packet_arrival"
        ]

        validation = validate_lgrc9v3_self_rearm_evidence_artifacts(
            events=filtered_events,
            production_results=production_results,
        )

        self.assertFalse(validation["valid"])
        self.assertTrue(
            any(
                reason.startswith("missing_parent_arrival_event:")
                for reason in validation["failure_reasons"]
            )
        )

    def test_artifact_validator_rejects_route_digest_mismatch(self) -> None:
        events, production_results = self._completed_self_rearm_artifacts()
        mutated_events: list[dict[str, object]] = []
        for event in events:
            cloned_event = dict(event)
            payload = dict(cloned_event["payload"])
            if payload.get("self_rearm_status") == "child_departure_processed":
                payload["route_aspect_digest"] = "wrong-digest"
            cloned_event["payload"] = payload
            mutated_events.append(cloned_event)

        validation = validate_lgrc9v3_self_rearm_evidence_artifacts(
            events=mutated_events,
            production_results=production_results,
        )

        self.assertFalse(validation["valid"])
        self.assertTrue(
            any(
                reason.startswith("route_digest_mismatch:")
                for reason in validation["failure_reasons"]
            )
        )

    def test_artifact_validator_rejects_wrong_channel_order(self) -> None:
        events, production_results = self._completed_self_rearm_artifacts()
        mutated_events: list[dict[str, object]] = []
        for event in events:
            cloned_event = dict(event)
            payload = dict(cloned_event["payload"])
            if payload.get("self_rearm_status") == "child_departure_processed":
                payload["parent_arrival_channel_id"] = "S_to_K"
            cloned_event["payload"] = payload
            mutated_events.append(cloned_event)

        validation = validate_lgrc9v3_self_rearm_evidence_artifacts(
            events=mutated_events,
            production_results=production_results,
        )

        self.assertFalse(validation["valid"])
        self.assertTrue(
            any(
                reason.startswith("route_order_mismatch:")
                for reason in validation["failure_reasons"]
            )
        )


if __name__ == "__main__":
    unittest.main()

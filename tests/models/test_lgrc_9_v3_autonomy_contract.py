"""Tests for LGRC9V3 autonomous producer contracts."""

from __future__ import annotations

import json
import math
from pathlib import Path
import tempfile
import unittest

from pygrc.core import InvalidStateTransitionError, PortGraphBackend
from pygrc.models import (
    CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY,
    EDGE_DELAY_POLICY_CONSTANT_DELAY,
    GRC9V3NodeState,
    GRC9V3State,
    LAPSE_POLICY_UNIT,
    LGRC_RUNTIME_LEVEL_LGRC3,
    LGRC9V3,
    LGRC9V3_CAUSAL_BOUNDARY_BIRTH_EVENT_KIND,
    LGRC9V3_CAUSAL_BOUNDARY_BIRTH_PARENT_ELIGIBILITY_GRCL9V3_FRONT_CAPACITY,
    LGRC9V3_CAUSAL_BOUNDARY_BIRTH_POLICY_GRC9V3_OUTWARD_FLUX,
    PortEdge,
)
from pygrc.models.lgrc_9_v3_contract import (
    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_BOUNDARY_BIRTH_TRIAL,
    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_DISABLED,
    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FLUX_ROUTE,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_BOUNDARY_BIRTH_TRIAL_SCHEDULED,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_DISABLED_POLICY,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_IDEMPOTENT_SKIP,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_NO_ELIGIBLE_WORK,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PACKET_DEPARTURE_SCHEDULED,
    LGRC9V3_AUTONOMOUS_PRODUCER_REQUIRED_FIELDS,
    LGRC9V3_AUTONOMOUS_RUN_POLICY_BOUNDED_V1,
    build_lgrc9v3_autonomous_surface_digest,
    build_lgrc9v3_disabled_autonomous_production_result,
    restore_lgrc9v3_autonomous_production_result_artifact,
)
from pygrc.models.lgrc_9_v3_packets import LGRC9V3_PACKET_EVENT_KIND_DEPARTURE


def _three_node_state() -> GRC9V3State:
    graph = PortGraphBackend()
    node_0 = graph.add_node({"label": "source"})
    node_1 = graph.add_node({"label": "middle"})
    node_2 = graph.add_node({"label": "target"})
    edge_01 = graph.connect_ports(node_0, 0, node_1, 0, {"kind": "01"})
    edge_12 = graph.connect_ports(node_1, 1, node_2, 0, {"kind": "12"})
    return GRC9V3State(
        topology=graph,
        nodes={
            node_0: GRC9V3NodeState(coherence=1.0),
            node_1: GRC9V3NodeState(coherence=2.0),
            node_2: GRC9V3NodeState(coherence=3.0),
        },
        port_edges={
            edge_01: PortEdge(node_0, 1, node_1, 1, conductance=1.0, flux_uv=0.0),
            edge_12: PortEdge(node_1, 2, node_2, 1, conductance=1.0, flux_uv=0.0),
        },
        base_conductance={edge_01: 1.0, edge_12: 1.0},
        geometric_length={edge_01: 1.0, edge_12: 1.0},
        temporal_delay={edge_01: 1.0, edge_12: 1.0},
        flux_coupling={edge_01: 0.0, edge_12: 0.0},
    )


def _boundary_birth_state() -> GRC9V3State:
    state = _three_node_state()
    state.nodes[0] = GRC9V3NodeState(coherence=4.0)
    state.port_edges[0] = PortEdge(
        0,
        1,
        1,
        1,
        conductance=1.0,
        flux_uv=2.0,
    )
    return state


def _boundary_birth_params(*, enabled: bool = True) -> dict[str, object]:
    params: dict[str, object] = {
        "dt": 1.0,
        "evolution": {
            "lambda_birth": 1.0,
            "alpha_seed": 0.25,
            "w_bond": 1.5,
            "rng_seed": 0,
        },
    }
    if enabled:
        params["causal_modes"] = {
            "causal_layer_mode": CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY,
            "lgrc_runtime_level": LGRC_RUNTIME_LEVEL_LGRC3,
            "lapse_policy": LAPSE_POLICY_UNIT,
            "edge_delay_policy": EDGE_DELAY_POLICY_CONSTANT_DELAY,
            "event_time_policy": "explicit_event_time_key",
            "proper_time_accumulation_policy": "local_event_frontier",
            "causal_boundary_birth_allowed": True,
            "causal_boundary_birth_policy": (
                LGRC9V3_CAUSAL_BOUNDARY_BIRTH_POLICY_GRC9V3_OUTWARD_FLUX
            ),
        }
    return params


def _front_capacity_boundary_birth_params() -> dict[str, object]:
    params = _boundary_birth_params()
    causal_modes = dict(params["causal_modes"])  # type: ignore[index]
    causal_modes["causal_boundary_birth_parent_eligibility"] = (
        LGRC9V3_CAUSAL_BOUNDARY_BIRTH_PARENT_ELIGIBILITY_GRCL9V3_FRONT_CAPACITY
    )
    params["causal_modes"] = causal_modes
    return params


def _front_capacity_boundary_birth_state() -> GRC9V3State:
    state = _boundary_birth_state()
    state.cached_quantities["grcl9v3_front_growth_eligible_ports"] = {"0": [3]}
    state.cached_quantities["grcl9v3_growth_parent_capacity_sources"] = {
        "0": {
            "construct_id": "test-front-capacity-construct",
            "growth_semantics": "front_capacity",
            "front_capacity_source": "spark_expansion_front",
            "inactive_parent_port": 3,
        }
    }
    return state


def _front_capacity_boundary_birth_state_without_source() -> GRC9V3State:
    state = _boundary_birth_state()
    state.cached_quantities["grcl9v3_front_growth_eligible_ports"] = {"0": [3]}
    return state


class LGRC9V3AutonomyContractTest(unittest.TestCase):
    """Validate autonomous producer contracts and active producer behavior."""

    def test_disabled_producer_contract_json_round_trips(self) -> None:
        digest = build_lgrc9v3_autonomous_surface_digest(
            {
                "scheduler_event_index": 0,
                "event_queue_records": [],
                "boundary_birth_trial_queue": [],
            }
        )
        result = build_lgrc9v3_disabled_autonomous_production_result(
            scheduler_event_index=0,
            checkpoint_index=0,
            event_time_key=0.0,
            causal_surface_digest=digest,
        )

        artifact = json.loads(json.dumps(result.to_artifact(), sort_keys=True))
        restored = restore_lgrc9v3_autonomous_production_result_artifact(artifact)
        record = artifact["production_records"][0]

        self.assertEqual(artifact, restored.to_artifact())
        self.assertEqual(0, artifact["scheduled_event_count"])
        self.assertFalse(artifact["queued_work_consumed"])
        self.assertFalse(artifact["topology_mutated"])
        self.assertFalse(artifact["collapse_reabsorption_emitted"])
        self.assertFalse(artifact["identity_acceptance_emitted"])
        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_DISABLED_POLICY,
            record["reason_code"],
        )
        self.assertTrue(LGRC9V3_AUTONOMOUS_PRODUCER_REQUIRED_FIELDS.issubset(record))

    def test_disabled_model_producer_is_noop_and_idempotent(self) -> None:
        model = LGRC9V3.from_state(_three_node_state(), {"dt": 1.0})
        before_runtime = model.snapshot()["dynamics"]["lgrc9v3_runtime"]
        before_nodes = tuple(model.get_state().base_state.topology.iter_live_node_ids())
        before_edges = tuple(model.get_state().base_state.topology.iter_live_edge_ids())

        first = model.produce_events()
        second = model.produce_events(policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_DISABLED)
        after_runtime = model.snapshot()["dynamics"]["lgrc9v3_runtime"]

        self.assertEqual(before_runtime, after_runtime)
        self.assertEqual(first.to_artifact(), second.to_artifact())
        self.assertEqual(0, first.scheduled_event_count)
        self.assertEqual((), model.get_state().packet_ledger.event_queue_records)
        self.assertEqual([], model.get_state().boundary_birth_trial_queue)
        self.assertEqual(
            before_nodes,
            tuple(model.get_state().base_state.topology.iter_live_node_ids()),
        )
        self.assertEqual(
            before_edges,
            tuple(model.get_state().base_state.topology.iter_live_edge_ids()),
        )

    def test_disabled_producer_does_not_change_step_behavior(self) -> None:
        control = LGRC9V3.from_state(_three_node_state(), {"dt": 1.0})
        produced = LGRC9V3.from_state(_three_node_state(), {"dt": 1.0})
        produced.produce_events()

        control_step = control.step()
        produced_step = produced.step()

        self.assertEqual(control_step.events, produced_step.events)
        self.assertEqual(control_step.observables, produced_step.observables)
        self.assertEqual(control_step.bookkeeping, produced_step.bookkeeping)

    def test_packet_departure_producer_schedules_from_route_policy(self) -> None:
        model = LGRC9V3.from_state(_three_node_state(), {"dt": 1.0})
        model.set_causal_flux_routes(
            {0: [{"target_node_id": 1, "edge_id": 0, "amount": 0.25}]}
        )

        produced = model.produce_events(
            policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FLUX_ROUTE
        )
        record = produced.production_records[0]

        self.assertTrue(produced.state_mutated)
        self.assertEqual(1, produced.scheduled_event_count)
        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PACKET_DEPARTURE_SCHEDULED,
            record.reason_code,
        )
        self.assertEqual(LGRC9V3_PACKET_EVENT_KIND_DEPARTURE, record.scheduled_event_kind)
        self.assertEqual(0, record.trigger_node_id)
        self.assertEqual(0, record.trigger_edge_id)
        self.assertEqual(1, record.observed_evidence["target_node_id"])
        self.assertAlmostEqual(0.25, record.observed_evidence["amount"])
        self.assertEqual(
            [record.scheduled_event_id],
            [event.event_id for event in model.get_state().packet_ledger.event_queue_records],
        )

        step = model.step()

        self.assertEqual(LGRC9V3_PACKET_EVENT_KIND_DEPARTURE, step.events[0].kind)
        self.assertAlmostEqual(0.75, model.get_state().base_state.nodes[0].coherence)
        self.assertAlmostEqual(
            0.25,
            model.get_state().packet_ledger.in_flight_packet_total,
        )

    def test_packet_departure_producer_schedules_fractional_route(self) -> None:
        model = LGRC9V3.from_state(_three_node_state(), {"dt": 1.0})
        model.set_causal_flux_routes(
            {1: [{"target_node_id": 2, "edge_id": 1, "amount_fraction": 0.1}]}
        )

        produced = model.produce_events(
            policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FLUX_ROUTE
        )
        record = produced.production_records[0]

        self.assertEqual(1, produced.scheduled_event_count)
        self.assertAlmostEqual(0.2, record.observed_evidence["amount"])
        self.assertEqual(
            "source_coherence_fraction",
            record.observed_evidence["amount_source"],
        )

    def test_packet_departure_producer_reports_no_eligible_routes(self) -> None:
        model = LGRC9V3.from_state(_three_node_state(), {"dt": 1.0})

        produced = model.produce_events(
            policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FLUX_ROUTE
        )
        record = produced.production_records[0]

        self.assertFalse(produced.state_mutated)
        self.assertEqual(0, produced.scheduled_event_count)
        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_NO_ELIGIBLE_WORK,
            record.reason_code,
        )
        self.assertEqual((), model.get_state().packet_ledger.event_queue_records)

    def test_packet_departure_producer_is_idempotent_on_same_surface(self) -> None:
        model = LGRC9V3.from_state(_three_node_state(), {"dt": 1.0})
        model.set_causal_flux_routes(
            {0: [{"target_node_id": 1, "edge_id": 0, "amount": 0.25}]}
        )

        first = model.produce_events(
            policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FLUX_ROUTE
        )
        second = model.produce_events(
            policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FLUX_ROUTE
        )

        self.assertEqual(1, first.scheduled_event_count)
        self.assertEqual(0, second.scheduled_event_count)
        self.assertFalse(second.state_mutated)
        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_IDEMPOTENT_SKIP,
            second.production_records[0].reason_code,
        )
        self.assertEqual(1, len(model.get_state().packet_ledger.event_queue_records))

    def test_packet_departure_producer_rejects_malformed_route(self) -> None:
        model = LGRC9V3.from_state(_three_node_state(), {"dt": 1.0})
        model.get_state().causal_flux_routes = {
            0: [{"target_node_id": 99, "edge_id": 0, "amount": 0.25}]
        }

        with self.assertRaises(InvalidStateTransitionError):
            model.produce_events(
                policy=(
                    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FLUX_ROUTE
                )
            )

    def test_packet_departure_producer_rejects_route_overdraw(self) -> None:
        model = LGRC9V3.from_state(_three_node_state(), {"dt": 1.0})
        model.set_causal_flux_routes(
            {
                0: [
                    {"target_node_id": 1, "edge_id": 0, "amount": 0.75},
                    {"target_node_id": 1, "edge_id": 0, "amount": 0.75},
                ]
            }
        )

        with self.assertRaises(InvalidStateTransitionError):
            model.produce_events(
                policy=(
                    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FLUX_ROUTE
                )
            )

    def test_boundary_birth_producer_is_noop_when_policy_disabled(self) -> None:
        model = LGRC9V3.from_state(
            _boundary_birth_state(),
            _boundary_birth_params(enabled=False),
        )

        produced = model.produce_events(
            policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_BOUNDARY_BIRTH_TRIAL
        )
        record = produced.production_records[0]

        self.assertFalse(produced.state_mutated)
        self.assertEqual(0, produced.scheduled_event_count)
        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_NO_ELIGIBLE_WORK,
            record.reason_code,
        )
        self.assertEqual([], model.get_state().boundary_birth_trial_queue)

    def test_boundary_birth_producer_schedules_trial_with_probability_evidence(self) -> None:
        model = LGRC9V3.from_state(
            _boundary_birth_state(),
            _boundary_birth_params(),
        )

        produced = model.produce_events(
            policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_BOUNDARY_BIRTH_TRIAL
        )
        record = produced.production_records[0]
        trial = model.get_state().boundary_birth_trial_queue[0]

        self.assertTrue(produced.state_mutated)
        self.assertEqual(1, produced.scheduled_event_count)
        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_BOUNDARY_BIRTH_TRIAL_SCHEDULED,
            record.reason_code,
        )
        self.assertEqual("lgrc9v3_causal_boundary_birth_trial", record.scheduled_event_kind)
        self.assertEqual(trial["trial_event_id"], record.scheduled_event_id)
        self.assertEqual(0, record.trigger_node_id)
        self.assertAlmostEqual(2.0, record.observed_evidence["outward_flux_pressure"])
        self.assertAlmostEqual(1.0 - math.exp(-2.0), record.thresholds["birth_probability"])
        self.assertEqual(record.thresholds["rng_sample"], trial["rng_sample"])
        self.assertTrue(record.observed_evidence["birth_acceptance_deferred_to_step"])

    def test_boundary_birth_producer_uses_front_capacity_eligibility(self) -> None:
        model = LGRC9V3.from_state(
            _front_capacity_boundary_birth_state(),
            _front_capacity_boundary_birth_params(),
        )

        produced = model.produce_events(
            policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_BOUNDARY_BIRTH_TRIAL
        )
        record = produced.production_records[0]
        trial = model.get_state().boundary_birth_trial_queue[0]

        self.assertTrue(produced.state_mutated)
        self.assertEqual(1, produced.scheduled_event_count)
        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_BOUNDARY_BIRTH_TRIAL_SCHEDULED,
            record.reason_code,
        )
        self.assertEqual(0, record.trigger_node_id)
        self.assertEqual(3, record.observed_evidence["parent_port_id"])
        self.assertEqual(
            LGRC9V3_CAUSAL_BOUNDARY_BIRTH_PARENT_ELIGIBILITY_GRCL9V3_FRONT_CAPACITY,
            record.observed_evidence["parent_eligibility_mode"],
        )
        self.assertEqual(
            "spark_expansion_front",
            record.observed_evidence["front_capacity_source"],
        )
        self.assertEqual(3, trial["parent_port_id"])

    def test_boundary_birth_producer_front_capacity_missing_metadata_fails_closed(
        self,
    ) -> None:
        model = LGRC9V3.from_state(
            _boundary_birth_state(),
            _front_capacity_boundary_birth_params(),
        )

        produced = model.produce_events(
            policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_BOUNDARY_BIRTH_TRIAL
        )
        record = produced.production_records[0]

        self.assertFalse(produced.state_mutated)
        self.assertEqual(0, produced.scheduled_event_count)
        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_NO_ELIGIBLE_WORK,
            record.reason_code,
        )
        self.assertEqual(
            LGRC9V3_CAUSAL_BOUNDARY_BIRTH_PARENT_ELIGIBILITY_GRCL9V3_FRONT_CAPACITY,
            record.observed_evidence["parent_eligibility_mode"],
        )
        self.assertEqual([], model.get_state().boundary_birth_trial_queue)

    def test_boundary_birth_producer_front_capacity_partial_metadata_fails_closed(
        self,
    ) -> None:
        model = LGRC9V3.from_state(
            _front_capacity_boundary_birth_state_without_source(),
            _front_capacity_boundary_birth_params(),
        )

        produced = model.produce_events(
            policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_BOUNDARY_BIRTH_TRIAL
        )
        record = produced.production_records[0]

        self.assertFalse(produced.state_mutated)
        self.assertEqual(0, produced.scheduled_event_count)
        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_NO_ELIGIBLE_WORK,
            record.reason_code,
        )
        self.assertEqual(
            LGRC9V3_CAUSAL_BOUNDARY_BIRTH_PARENT_ELIGIBILITY_GRCL9V3_FRONT_CAPACITY,
            record.observed_evidence["parent_eligibility_mode"],
        )
        self.assertEqual([], model.get_state().boundary_birth_trial_queue)

    def test_boundary_birth_producer_is_idempotent_on_same_surface(self) -> None:
        model = LGRC9V3.from_state(
            _boundary_birth_state(),
            _boundary_birth_params(),
        )

        first = model.produce_events(
            policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_BOUNDARY_BIRTH_TRIAL
        )
        second = model.produce_events(
            policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_BOUNDARY_BIRTH_TRIAL
        )

        self.assertEqual(1, first.scheduled_event_count)
        self.assertEqual(0, second.scheduled_event_count)
        self.assertFalse(second.state_mutated)
        self.assertEqual(
            LGRC9V3_AUTONOMOUS_PRODUCER_REASON_IDEMPOTENT_SKIP,
            second.production_records[0].reason_code,
        )
        self.assertEqual(1, len(model.get_state().boundary_birth_trial_queue))

    def test_boundary_birth_producer_trial_routes_through_step(self) -> None:
        model = LGRC9V3.from_state(
            _boundary_birth_state(),
            _boundary_birth_params(),
        )
        produced = model.produce_events(
            policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_BOUNDARY_BIRTH_TRIAL
        )
        record = produced.production_records[0]
        budget_before = sum(
            node.coherence for node in model.get_state().base_state.nodes.values()
        )

        result = model.step()

        self.assertEqual(1, produced.scheduled_event_count)
        self.assertEqual(1, len(result.events))
        self.assertEqual(LGRC9V3_CAUSAL_BOUNDARY_BIRTH_EVENT_KIND, result.events[0].kind)
        self.assertEqual(0, result.bookkeeping["boundary_birth_trial_queue_after"])
        self.assertAlmostEqual(
            record.thresholds["birth_probability"],
            result.events[0].payload["birth_probability"],
        )
        self.assertAlmostEqual(
            record.thresholds["rng_sample"],
            result.events[0].payload["rng_sample"],
        )
        self.assertAlmostEqual(0.0, result.events[0].payload["budget_error"])
        self.assertAlmostEqual(
            budget_before,
            sum(node.coherence for node in model.get_state().base_state.nodes.values()),
        )

    def test_autonomous_run_reproduces_manual_packet_route_fixture(self) -> None:
        manual = LGRC9V3.from_state(_three_node_state(), {"dt": 1.0})
        manual.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=0.0,
            scheduler_event_index=1,
        )
        automatic = LGRC9V3.from_state(_three_node_state(), {"dt": 1.0})
        automatic.set_causal_flux_routes(
            {0: [{"target_node_id": 1, "edge_id": 0, "amount": 0.25}]}
        )

        manual_results = manual.run_event_queue(max_events=2)
        automatic_results = automatic.run_autonomous(
            max_events=2,
            producer_policies=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FLUX_ROUTE,
            ),
        )
        summary = automatic.get_state().cached_quantities[
            "last_lgrc9v3_autonomous_run"
        ]

        self.assertEqual(
            [[event.kind for event in result.events] for result in manual_results],
            [[event.kind for event in result.events] for result in automatic_results],
        )
        self.assertAlmostEqual(
            manual.get_state().base_state.nodes[0].coherence,
            automatic.get_state().base_state.nodes[0].coherence,
        )
        self.assertAlmostEqual(
            manual.get_state().base_state.nodes[1].coherence,
            automatic.get_state().base_state.nodes[1].coherence,
        )
        self.assertEqual(1, summary["producer_scheduled_event_count"])
        self.assertEqual(2, summary["consumed_step_count"])
        self.assertEqual("max_events_reached", summary["stop_condition"])
        self.assertEqual(summary, automatic_results[-1].bookkeeping["autonomous_run"])

    def test_autonomous_run_schedules_and_consumes_boundary_birth_trial(self) -> None:
        model = LGRC9V3.from_state(
            _boundary_birth_state(),
            _boundary_birth_params(),
        )

        results = model.run_autonomous(
            max_events=1,
            producer_policies=(LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_BOUNDARY_BIRTH_TRIAL,),
        )
        summary = model.get_state().cached_quantities["last_lgrc9v3_autonomous_run"]

        self.assertEqual(1, len(results))
        self.assertEqual(LGRC9V3_CAUSAL_BOUNDARY_BIRTH_EVENT_KIND, results[0].events[0].kind)
        self.assertEqual(1, summary["producer_scheduled_event_count"])
        self.assertEqual(1, summary["consumed_step_count"])
        self.assertEqual("max_events_reached", summary["stop_condition"])
        self.assertEqual(0, len(model.get_state().boundary_birth_trial_queue))

    def test_autonomous_run_max_events_zero_is_noop(self) -> None:
        model = LGRC9V3.from_state(_three_node_state(), {"dt": 1.0})
        model.set_causal_flux_routes(
            {0: [{"target_node_id": 1, "edge_id": 0, "amount": 0.25}]}
        )

        results = model.run_autonomous(max_events=0)
        summary = model.get_state().cached_quantities["last_lgrc9v3_autonomous_run"]

        self.assertEqual([], results)
        self.assertEqual(0, summary["producer_invocation_count"])
        self.assertEqual(0, summary["consumed_step_count"])
        self.assertEqual("max_events_reached", summary["stop_condition"])
        self.assertEqual((), model.get_state().packet_ledger.event_queue_records)

    def test_autonomous_run_empty_no_producer_work_stops_cleanly(self) -> None:
        model = LGRC9V3.from_state(_three_node_state(), {"dt": 1.0})

        results = model.run_autonomous(
            max_events=5,
            policy=LGRC9V3_AUTONOMOUS_RUN_POLICY_BOUNDED_V1,
            producer_policies=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FLUX_ROUTE,
            ),
        )
        summary = model.get_state().cached_quantities["last_lgrc9v3_autonomous_run"]

        self.assertEqual([], results)
        self.assertEqual(1, summary["producer_invocation_count"])
        self.assertEqual(1, summary["producer_no_eligible_work_count"])
        self.assertEqual(0, summary["producer_scheduled_event_count"])
        self.assertEqual("no_autonomous_work_available", summary["stop_condition"])

    def test_autonomous_run_snapshot_round_trips_after_execution(self) -> None:
        model = LGRC9V3.from_state(_three_node_state(), {"dt": 1.0})
        model.set_causal_flux_routes(
            {0: [{"target_node_id": 1, "edge_id": 0, "amount": 0.25}]}
        )
        model.run_autonomous(
            max_events=2,
            producer_policies=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FLUX_ROUTE,
            ),
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "lgrc9v3-autonomous.json"
            model.save(str(path))
            loaded = LGRC9V3.load(str(path))

        self.assertEqual(
            model.snapshot()["dynamics"]["lgrc9v3_runtime"],
            loaded.snapshot()["dynamics"]["lgrc9v3_runtime"],
        )


if __name__ == "__main__":
    unittest.main()

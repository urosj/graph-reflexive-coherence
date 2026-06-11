"""Contract tests for shared state and step-result datatypes."""

from __future__ import annotations

import unittest

from pygrc.core import GRCState, StepResult


class TypesContractTest(unittest.TestCase):
    """Validate the Phase 1 state/result contract surface."""

    def test_state_exposes_required_shared_fields(self) -> None:
        state = GRCState()

        self.assertEqual(0, state.step_index)
        self.assertEqual(0.0, state.time)
        self.assertEqual(0.0, state.budget_target)
        self.assertEqual(0.0, state.remainder)
        self.assertEqual({}, state.cached_quantities)
        self.assertEqual([], state.event_log)
        self.assertEqual({}, state.observables)
        self.assertIsNone(state.rng_state)
        self.assertIsNone(state.params_identity)

    def test_state_keeps_generic_topology_payloads(self) -> None:
        state = GRCState(topology={"kind": "graph"}, node_values={"n0": 1.0})

        self.assertEqual({"kind": "graph"}, state.topology)
        self.assertEqual({"n0": 1.0}, state.node_values)

    def test_step_result_exposes_required_spec_fields(self) -> None:
        result = StepResult(
            step_index=7,
            time=1.5,
            events=[],
            observables={"mass": 2.0},
        )

        self.assertEqual(7, result.step_index)
        self.assertEqual(1.5, result.time)
        self.assertEqual([], result.events)
        self.assertEqual({"mass": 2.0}, result.observables)
        self.assertEqual({}, result.bookkeeping)

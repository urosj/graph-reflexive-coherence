"""Contract tests for the core model interface surface."""

from __future__ import annotations

import unittest
from collections.abc import Mapping
from typing import Any

from pygrc.core import BaseSnapshot, GRCEvent, GRCModel, GRCState, StepResult


REQUIRED_ABSTRACT_METHODS = {
    "from_config",
    "from_state",
    "load",
    "get_state",
    "set_state",
    "get_params",
    "list_capabilities",
    "compute_observables",
    "step",
    "reset",
    "snapshot",
    "save",
}


class DummyModel(GRCModel):
    """Minimal concrete implementation for exercising the base contract."""

    def __init__(self) -> None:
        self._state = GRCState(step_index=0, time=0.0)
        self._initial_state = GRCState(step_index=0, time=0.0)
        self._params: dict[str, Any] = {"dt": 1.0}

    @classmethod
    def from_config(cls, config: Mapping[str, Any]) -> "DummyModel":
        model = cls()
        model._params = dict(config)
        return model

    @classmethod
    def from_state(
        cls, state: Mapping[str, Any], params: Mapping[str, Any]
    ) -> "DummyModel":
        model = cls()
        model._state = GRCState(**dict(state))
        model._params = dict(params)
        return model

    @classmethod
    def load(cls, path: str) -> "DummyModel":
        del path
        return cls()

    def get_state(self) -> GRCState:
        return self._state

    def set_state(self, state: GRCState) -> None:
        self._state = state

    def get_params(self) -> dict[str, Any]:
        return self._params

    def list_capabilities(self) -> set[str]:
        return {"dummy_capability"}

    def compute_observables(self) -> dict[str, Any]:
        return {"step_index": self._state.step_index}

    def step(self) -> StepResult:
        self._state.step_index += 1
        self._state.time += 1.0
        return StepResult(
            step_index=self._state.step_index,
            time=self._state.time,
            events=[GRCEvent(kind="dummy_step", step_index=self._state.step_index)],
            observables=self.compute_observables(),
        )

    def reset(self) -> None:
        self._state = GRCState(
            step_index=self._initial_state.step_index,
            time=self._initial_state.time,
        )

    def rebase_reset_baseline(self) -> None:
        self._initial_state = GRCState(
            step_index=self._state.step_index,
            time=self._state.time,
        )

    def snapshot(self) -> BaseSnapshot:
        return {
            "metadata": {
                "snapshot_schema": "pygrc.snapshot",
                "snapshot_version": 1,
                "model_family": "DummyModel",
                "step_index": self._state.step_index,
                "params": dict(self._params),
                "resolved_params": dict(self._params),
                "params_hash": "dummy",
                "capabilities": sorted(self.list_capabilities()),
            },
            "topology": {},
            "dynamics": {
                "state": {
                    "step_index": self._state.step_index,
                    "time": self._state.time,
                }
            },
        }

    def save(self, path: str) -> None:
        del path


class InterfaceContractTest(unittest.TestCase):
    """Validate the public model interface contract shape."""

    def test_abstract_surface_matches_required_methods(self) -> None:
        self.assertTrue(REQUIRED_ABSTRACT_METHODS.issubset(GRCModel.__abstractmethods__))

    def test_rebase_reset_baseline_is_additive_common_surface(self) -> None:
        self.assertTrue(callable(GRCModel.rebase_reset_baseline))

    def test_run_uses_step_exactly_num_steps_times(self) -> None:
        model = DummyModel()

        results = model.run(3)

        self.assertEqual(3, len(results))
        self.assertEqual(3, model.get_state().step_index)
        self.assertEqual(3.0, model.get_state().time)

    def test_run_rejects_negative_step_counts(self) -> None:
        model = DummyModel()

        with self.assertRaises(ValueError):
            model.run(-1)

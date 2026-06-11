"""Common model interface contracts for PyGRC.

This module defines the family-neutral public model surface required by the
common-interface spec. Concrete parameter, state, event, and step-result types
are introduced in later Phase 1 iterations; for now the interface keeps those
positions deliberately lightweight so the public method surface can be fixed
without forcing the rest of the contract layer to exist early.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any, Self, TypeAlias

from .observables import ObservableMap
from .serialization import BaseSnapshot
from .types import GRCState, StepResult


ModelConfig: TypeAlias = Mapping[str, Any]
SerializedState: TypeAlias = Mapping[str, Any]
SerializedParams: TypeAlias = Mapping[str, Any]


class GRCModel(ABC):
    """Abstract base class for all concrete GRC model families."""

    @classmethod
    @abstractmethod
    def from_config(cls, config: ModelConfig) -> Self:
        """Create a model from a JSON/YAML-friendly configuration mapping."""

    @classmethod
    @abstractmethod
    def from_state(cls, state: SerializedState, params: SerializedParams) -> Self:
        """Restore a model from serialized state and parameters."""

    @classmethod
    @abstractmethod
    def load(cls, path: str) -> Self:
        """Load a serialized model from persistent storage."""

    @abstractmethod
    def get_state(self) -> GRCState:
        """Return the current model state."""

    @abstractmethod
    def set_state(self, state: GRCState) -> None:
        """Replace the current model state after validating compatibility."""

    @abstractmethod
    def get_params(self) -> Any:
        """Return the resolved parameter object governing the current model."""

    @abstractmethod
    def list_capabilities(self) -> set[str]:
        """Return the capability flags advertised by this model."""

    @abstractmethod
    def compute_observables(self) -> ObservableMap:
        """Compute the model observables for the current state."""

    @abstractmethod
    def step(self) -> StepResult:
        """Advance exactly one simulation step and return the step result."""

    def run(self, num_steps: int) -> list[StepResult]:
        """Run `step()` repeatedly and collect the produced step results."""
        if num_steps < 0:
            raise ValueError("num_steps must be non-negative")
        return [self.step() for _ in range(num_steps)]

    @abstractmethod
    def reset(self) -> None:
        """Restore the initial state used at construction time."""

    @abstractmethod
    def snapshot(self) -> BaseSnapshot:
        """Return a serialization-safe deep representation of the model."""

    @abstractmethod
    def save(self, path: str) -> None:
        """Persist the model to implementation-defined storage."""

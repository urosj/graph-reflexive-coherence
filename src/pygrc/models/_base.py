"""Internal base class for Phase 1 family stubs."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from pygrc.core import (
    BaseSnapshot,
    CapabilityProfile,
    GRCModel,
    GRCParams,
    GRCState,
    ObservableMap,
    SnapshotCompatibilityError,
    build_dynamics_group,
    build_event_records,
    build_snapshot_metadata,
    build_standard_snapshot,
    build_state_payload,
    build_topology_snapshot,
    load_snapshot,
    require_snapshot_family,
    restore_state_payload,
    save_snapshot,
)


class BaseFamilyStub(GRCModel):
    """Common implementation for non-executable Phase 1 family stubs."""

    MODEL_FAMILY = "BASE"
    CAPABILITY_PROFILE: CapabilityProfile

    def __init__(self, params: GRCParams, state: GRCState | None = None) -> None:
        self._params = params
        self._state = deepcopy(state) if state is not None else GRCState()
        self._initial_state = deepcopy(self._state)

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "BaseFamilyStub":
        params_input = dict(config.get("params", config))
        params = GRCParams.from_mapping(params_input)
        state_input = dict(config.get("state", {}))
        state = GRCState(**state_input)
        return cls(params=params, state=state)

    @classmethod
    def from_state(cls, state: dict[str, Any], params: dict[str, Any]) -> "BaseFamilyStub":
        return cls(params=GRCParams.from_mapping(dict(params)), state=GRCState(**state))

    @classmethod
    def load(cls, path: str) -> "BaseFamilyStub":
        snapshot = load_snapshot(path)
        require_snapshot_family(snapshot, expected_family=cls.MODEL_FAMILY)
        dynamics = snapshot.get("dynamics", {})
        state_payload = dynamics.get("state", {})
        if not isinstance(state_payload, dict):
            raise SnapshotCompatibilityError("snapshot dynamics.state must be a mapping")
        restored_state = restore_state_payload(state_payload)
        params_payload = snapshot["metadata"]["params"]
        if not isinstance(params_payload, dict):
            raise SnapshotCompatibilityError("snapshot metadata.params must be a mapping")
        return cls(params=GRCParams.from_mapping(dict(params_payload)), state=restored_state)

    def get_state(self) -> GRCState:
        return self._state

    def set_state(self, state: GRCState) -> None:
        if not isinstance(state, GRCState):
            raise SnapshotCompatibilityError("state must be a GRCState instance")
        self._state = deepcopy(state)

    def get_params(self) -> GRCParams:
        return self._params

    def list_capabilities(self) -> set[str]:
        claims = set(self.CAPABILITY_PROFILE.required)
        self.CAPABILITY_PROFILE.validate_claims(claims)
        return claims

    def compute_observables(self) -> ObservableMap:
        return dict(self._state.observables)

    def step(self) -> Any:
        raise NotImplementedError(
            f"{self.MODEL_FAMILY} is a Phase 1 contract stub and has no step logic yet"
        )

    def reset(self) -> None:
        self._state = deepcopy(self._initial_state)

    def snapshot(self) -> BaseSnapshot:
        return build_standard_snapshot(
            metadata=build_snapshot_metadata(
                model_family=self.MODEL_FAMILY,
                step_index=self._state.step_index,
                params=dict(self._params.raw_config),
                resolved_params=dict(self._params.resolved_config),
                params_hash=self._params.canonical_identity(),
                capabilities=self.list_capabilities(),
                rng_state=self._state.rng_state,
            ),
            topology=build_topology_snapshot(),
            dynamics=build_dynamics_group(state=build_state_payload(self._state)),
            observables=self.compute_observables(),
            events=build_event_records(
                [
                    {
                    "kind": event.kind,
                    "step_index": event.step_index,
                    "payload": event.payload,
                    "source_family": event.source_family,
                }
                    for event in self._state.event_log
                ]
            ),
        )

    def save(self, path: str) -> None:
        save_snapshot(path, self.snapshot())

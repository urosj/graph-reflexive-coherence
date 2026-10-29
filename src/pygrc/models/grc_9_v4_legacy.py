"""Exact GRC9V3 delegate component for selected disabled GRC9V4 profiles.

This component starts from an explicitly supplied legacy target snapshot. It
does not migrate an enabled owner or fabricate an entry/loss receipt. The
P9-9.4 crossing owner must supply that admission before publishing a disabled
scientific branch. No enabled V4 kernel runs on this surface.
"""

from copy import deepcopy
from dataclasses import dataclass
from threading import RLock
from types import MappingProxyType
import json

from pygrc.core import load_snapshot, save_snapshot
from .grc_9_v3 import GRC9V3
from .grc_9_v3_state import GRC9V3State
from .grc_9_v4_lifecycle import GRC9V4Specialization
from .grc_v4_codec import canonical_json_bytes
from .grc_v4_profile import GRCV4Profile
from .grc_v4_state import FrozenJSONMap


TARGET_VERSION = "grc9v3-spec-2026-09-v1"
FAMILIES = frozenset(("C_OS", "C_CI", "A_CI", "A_PC", "A_OS", "C_PC", "C_CI_PC"))
_COMPATIBILITY = dict(
    schema_version="grc9v4-legacy-compatibility-policy-v1",
    target_spec_version=TARGET_VERSION,
    transition_policy_id="exact_profile_scoped_delegate_v1",
    state_policy_id="exact_candidate_specific_projection_v1",
    observable_policy_id="exact_legacy_observable_set_v1",
    lifecycle_policy_id="typed_atomic_delegate_crossing_v1",
    undefined_expansion_disposition="legacy_expansion_target_undefined",
)


def _legacy_json(value):
    # Legacy caches can lawfully contain signed zero. Do not canonicalize them
    # through the stricter V4 scientific-state encoding.
    json.dumps(value, allow_nan=False)
    return value


def _frozen_legacy(value):
    if isinstance(value, dict):
        return MappingProxyType({k: _frozen_legacy(v) for k, v in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_frozen_legacy(v) for v in value)
    return value


class LegacyExpansionTargetUndefined(ValueError):
    """The requested legacy operation is outside its defined expansion domain."""

    code = "legacy_expansion_target_undefined"
    committed = False


class _DefinedLegacy(GRC9V3):
    """Native implementation, with a V4 domain guard at actual detection time.

    GRC9V3.step invokes detection after its native pre-flux/flux/identity
    stages. Inspect that result once, before the native routine can append an
    event or start conflicting rewiring. Valid-domain calculations are exactly
    the inherited methods. No module patch, replacement event or alternate port
    allocator is installed in GRC9V3.
    """

    def detect_hybrid_spark_candidates(self):
        candidates = super().detect_hybrid_spark_candidates()
        for event in candidates:
            node = int(event.payload["sink_node_id"])
            ports = set()
            for edge_id in self._state.topology.incident_edge_ids(node):
                for endpoint in self._state.topology.edge_ports(edge_id):
                    if endpoint[0] == node:
                        ports.add(endpoint[1] + 1)
            if ports == set(range(1, 10)):
                raise LegacyExpansionTargetUndefined(
                    "saturated old port 5 conflicts with inherited internal spine"
                )
        return candidates


@dataclass(frozen=True, slots=True)
class LegacyDelegateBinding:
    """Execution context; never injected into the legacy scientific projection."""

    profile: GRCV4Profile
    specialization: GRC9V4Specialization

    def __post_init__(self):
        if (
            type(self.profile) is not GRCV4Profile
            or type(self.specialization) is not GRC9V4Specialization
        ):
            raise TypeError("closed V4 profile and specialization required")
        profile = GRCV4Profile.from_canonical_bytes(self.profile.to_canonical_bytes())
        spec = GRC9V4Specialization(
            self.specialization.resolved, self.specialization.identity_payload
        )
        if profile.identity_payload.profile_family_id not in FAMILIES:
            raise ValueError("disabled delegate family is outside selected scope")
        if spec.resolved["compatibility"].to_dict() != _COMPATIBILITY:
            raise ValueError("unsupported exact legacy target/policy")
        object.__setattr__(self, "profile", profile)
        object.__setattr__(self, "specialization", spec)

    @property
    def model_identity(self):
        from .grc_9_v4_identity import model_identity

        return model_identity(self.profile.complete_profile_id, self.specialization)

    def to_payload(self):
        return dict(
            profile=self.profile.to_payload(),
            specialization=self.specialization.to_payload(),
            active_model_identity=self.model_identity,
            target_spec_version=TARGET_VERSION,
        )


class GRC9V4LegacyDelegate:
    """Private-copy transactions over the exact, unchanged legacy implementation.

    `snapshot` and observable/state projections contain only legacy fields.
    `checkpoint` adds the separate profile/version context for this component.
    The original model, supplied snapshot and returned projections never alias
    live owner state. No claim of an enabled-to-disabled crossing is made.
    """

    def __init__(self, binding, legacy_snapshot):
        if type(binding) is not LegacyDelegateBinding:
            raise TypeError("explicit legacy delegate binding required")
        self._binding = LegacyDelegateBinding(binding.profile, binding.specialization)
        self._delegate = _DefinedLegacy._from_snapshot(
            deepcopy(legacy_snapshot), restore_reset_baseline=True
        )
        # An immutable, finite JSON projection is an additional V4 ownership
        # check. Legacy deserialization still owns the target semantics.
        _legacy_json(self._delegate.snapshot())
        self._lock = RLock()

    @property
    def binding(self):
        return self._binding

    @property
    def state(self):
        with self._lock:
            return _frozen_legacy(self._delegate.snapshot())

    def get_state(self):
        """Detached exact legacy dataclass projection, never live authority."""
        with self._lock:
            return deepcopy(self._delegate.get_state())

    def get_params(self):
        with self._lock:
            return self._delegate.get_params()  # GRCParams is recursively immutable.

    @staticmethod
    def _clone(delegate):
        # Native GRCParams contains recursively frozen mapping proxies. Share
        # that immutable value while copying every mutable state/baseline field.
        params = delegate.get_params()
        return deepcopy(delegate, {id(params): params})

    def _transaction(self, method, *args):
        with self._lock:
            target = self._clone(self._delegate)
            result = getattr(target, method)(*deepcopy(args))
            target._validate_state(target.get_state())
            _legacy_json(target.snapshot())
            self._delegate = target
            return deepcopy(result)

    def step(self):
        return self._transaction("step")

    def reset(self):
        return self._transaction("reset")

    def rebase_reset_baseline(self):
        return self._transaction("rebase_reset_baseline")

    def apply_hybrid_sparks(self):
        return self._transaction("apply_hybrid_sparks")

    def set_state(self, state):
        if type(state) is not GRC9V3State:
            raise TypeError("disabled projection requires exact GRC9V3State")
        return self._transaction("set_state", state)

    def compute_observables(self):
        with self._lock:
            return deepcopy(self._delegate.compute_observables())

    def snapshot(self):
        with self._lock:
            return deepcopy(self._delegate.snapshot())

    def checkpoint(self):
        with self._lock:
            return dict(
                descriptor_version="grc9v4-legacy-delegate-checkpoint-v1",
                binding=self.binding.to_payload(),
                delegate=self.snapshot(),
            )

    @classmethod
    def from_checkpoint(cls, value):
        data = deepcopy(_legacy_json(value))
        if (
            set(data) != {"descriptor_version", "binding", "delegate"}
            or data["descriptor_version"] != "grc9v4-legacy-delegate-checkpoint-v1"
        ):
            raise ValueError("closed delegate checkpoint required")
        b = data["binding"]
        if (
            set(b)
            != {
                "profile",
                "specialization",
                "active_model_identity",
                "target_spec_version",
            }
            or b["target_spec_version"] != TARGET_VERSION
        ):
            raise ValueError("unsupported delegate binding/version")
        s = b["specialization"]
        if set(s) != {"resolved", "identity_payload"}:
            raise ValueError("closed specialization required")
        profile = GRCV4Profile.from_canonical_bytes(canonical_json_bytes(b["profile"]))
        binding = LegacyDelegateBinding(
            profile,
            GRC9V4Specialization(
                FrozenJSONMap(s["resolved"]), FrozenJSONMap(s["identity_payload"])
            ),
        )
        if b["active_model_identity"] != binding.model_identity:
            raise ValueError("delegate context identity mismatch")
        return cls(binding, data["delegate"])

    def duplicate(self):
        # Native in-memory duplicate preserves all caches and baseline values;
        # snapshot round-trip is tested separately against native load semantics.
        with self._lock:
            clone = object.__new__(type(self))
            clone._binding = self._binding
            clone._delegate = self._clone(self._delegate)
            clone._lock = RLock()
            return clone

    def save(self, path):
        save_snapshot(str(path), self.snapshot())

    @classmethod
    def load(cls, binding, path):
        return cls(binding, load_snapshot(str(path)))

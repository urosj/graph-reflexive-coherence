"""Explicit v3 exact-resource configuration and native lifecycle value records."""

from dataclasses import dataclass

from .grc_9_v4_completion_codec import CompletionPolicy, digest, validate
from .grc_9_v4_identity import model_identity
from .grc_9_v4_lifecycle import GRC9V4Specialization
from .grc_v4_geometry import GRCV4Graph
from .grc_v4_spark import quartic_kernel, quartic_profile
from .grc_v4_spark_carrier import ExactCarrierState, exact_state
from .grc_v4_spark_state import (
    ExactResources,
    QuarticCOSProfile,
    rational,
)
from .grc_v4_state import FrozenJSONMap


@dataclass(frozen=True, slots=True)
class SparkReference:
    graph: GRCV4Graph
    profile: QuarticCOSProfile

    def __post_init__(self):
        quartic_kernel(self.graph, self.profile)
        # Explicit optional asset admission; .2 legacy spelling stays readable
        # only at its numerical boundary, never silently promoted to v3.
        validate(self.profile.site.to_payload())

    def to_payload(self):
        return {
            "schema_version": "grc9v4-exact-spark-reference-v1",
            "graph": self.graph.to_payload(),
            "profile": self.profile.to_payload(),
            "context": "constant_zero_context_v1",
            "K_4": "zero",
            "H_ref": "identity",
            "W": "unit",
        }

    @classmethod
    def from_payload(cls, value):
        result = cls(
            GRCV4Graph.from_payload(value["graph"]),
            quartic_profile(value["profile"]),
        )
        if result.to_payload() != value:
            raise ValueError("closed supported exact reference required")
        return result


@dataclass(frozen=True, slots=True)
class GRC9V4SparkConfiguration:
    reference: SparkReference
    specialization: GRC9V4Specialization
    current: ExactResources
    reset: ExactResources
    step_index: int = 0
    time: str = "0"

    def __post_init__(self):
        if (
            type(self.reference) is not SparkReference
            or type(self.specialization) is not GRC9V4Specialization
        ):
            raise TypeError("typed v3 reference/specialization required")
        if (
            self.specialization.resolved["schema_version"]
            != "grc9v4-resolved-specialization-v3"
        ):
            raise ValueError("explicit v3 completion policy or null required")
        if (
            type(self.step_index) is not int
            or not 0 <= self.step_index <= 2**53 - 1
            or rational(self.time) < 0
        ):
            raise ValueError("exact nonnegative clock required")
        if (
            any(
                type(x) is not (ExactCarrierState if self.reference.profile.FAMILY == "C_PC" else ExactResources) or x.graph != self.reference.graph
                for x in (self.current, self.reset)
            )
            or self.current.charge != self.reset.charge
        ):
            raise ValueError("both exact roles must share graph and charge")
        if self.specialization.resolved["spark"]["child_stabilization"] is not None:
            raise ValueError("legacy untyped stabilization cannot enable completion")
        if (
            self.policy is not None
            and self.policy.landscape_sign
            != self.specialization.identity_payload["hessian_sign"]
        ):
            raise ValueError("completion landscape sign differs from specialization")

        if self.policy is not None and self.policy.numerical_policy_id != self.reference.profile.NUMERICS:
            raise ValueError("completion numerical policy differs from profile family")

    @property
    def policy(self):
        data = self.specialization.resolved["completion_policy"]
        return None if data is None else CompletionPolicy.from_payload(data)

    @property
    def model_identity(self):
        return model_identity(
            self.reference.profile.complete_profile_id, self.specialization
        )

    @property
    def scientific_digest(self):
        return "grcv4-state-sha256:" + digest(self.to_payload())

    @property
    def budget_target(self):
        return self.current.charge

    @property
    def targets(self):
        return ()

    def to_payload(self):
        return {
            "schema_version": "grc9v4-configuration-v3",
            "reference": self.reference.to_payload(),
            "specialization": self.specialization.to_payload(),
            "current": self.current.to_payload(),
            "reset": self.reset.to_payload(),
            "step_index": self.step_index,
            "time": self.time,
            "execution": {
                "exact_backend": "flint",
                "numerical_policy": self.reference.profile.NUMERICS,
            },
        }

    @classmethod
    def from_payload(cls, value):
        spec = value["specialization"]
        result = cls(
            SparkReference.from_payload(value["reference"]),
            GRC9V4Specialization(
                FrozenJSONMap(spec["resolved"]), FrozenJSONMap(spec["identity_payload"])
            ),
            exact_state(value["current"]),
            exact_state(value["reset"]),
            value["step_index"],
            value["time"],
        )
        if result.to_payload() != value:
            raise ValueError("closed explicit v3 configuration required")
        return result


@dataclass(frozen=True, slots=True)
class SparkReceipt:
    identity_payload: FrozenJSONMap

    @property
    def receipt_id(self):
        return "grc9v4-native-receipt-sha256:" + digest(self.identity_payload.to_dict())

    def to_payload(self):
        return {
            "receipt_id": self.receipt_id,
            "identity_payload": self.identity_payload.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class SparkResult:
    committed: bool
    emitted_receipts: tuple = ()
    reason: str | None = None
    local_gain: int = 0

    @property
    def disposition(self):
        return "committed" if self.committed else "rejected"

    @property
    def commit_id(self):
        return (
            None
            if not self.committed
            else "grc9v4-native-commit-sha256:"
            + digest([r.receipt_id for r in self.emitted_receipts])
        )

    def to_payload(self):
        return {
            "schema_version": "grc9v4-native-spark-result-v1",
            "committed": self.committed,
            "disposition": self.disposition,
            "commit_id": self.commit_id,
            "emitted_receipts": [r.to_payload() for r in self.emitted_receipts],
            "reason": self.reason,
            "local_gain": self.local_gain,
        }


@dataclass(frozen=True, slots=True)
class SparkStateView:
    configuration: GRC9V4SparkConfiguration
    completion: FrozenJSONMap
    lifecycle_digest: str
    receipts: tuple
    compatibility_branch: str = "enabled_spark_v4"

    @property
    def branch(self):
        return self.compatibility_branch

    @property
    def scientific_state_digest(self):
        return self.configuration.scientific_digest

    @property
    def active_model_identity(self):
        return self.configuration.model_identity

    @property
    def step_index(self):
        return self.configuration.step_index

    @property
    def time(self):
        return self.configuration.time

    @property
    def budget_target(self):
        return self.configuration.budget_target

    @property
    def current(self):
        return self.configuration.current

    @property
    def reset(self):
        return self.configuration.reset

    @property
    def model_identity(self):
        return self.configuration.model_identity

    @property
    def scientific_digest(self):
        return self.configuration.scientific_digest

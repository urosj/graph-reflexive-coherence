"""Exact C/W/Z state and explicit quartic A_PC declaration."""

from dataclasses import dataclass
from typing import ClassVar

from .grc_v4_codec import decode_canonical_json
from .grc_v4_geometry import GRCV4Graph
from .grc_v4_spark_carrier import ExactCarrierState
from .grc_v4_spark_conductance import ExactConductanceState, QuarticAOSProfile
from .grc_v4_spark_state import ExactResources, flint_operation

APC_NUMERICAL_POLICY = "spark_apc_arb256_flux128_conductance192_carrier192_v1"


@dataclass(frozen=True, slots=True, eq=False)
class QuarticAPCProfile(QuarticAOSProfile):
    FAMILY: ClassVar[str] = "A_PC"
    NUMERICS: ClassVar[str] = APC_NUMERICAL_POLICY


ACIPC_NUMERICAL_POLICY = "spark_acipc_arb256_flux128_conductance192_carrier192_v1"


@dataclass(frozen=True, slots=True, eq=False)
class QuarticACIPCProfile(QuarticAOSProfile):
    FAMILY: ClassVar[str] = "A_CI_PC"
    NUMERICS: ClassVar[str] = ACIPC_NUMERICAL_POLICY


@dataclass(frozen=True, slots=True)
class ExactAdaptiveCarrierState(ExactConductanceState):
    Z_4: tuple[tuple[str, ...], ...]

    @flint_operation
    def __post_init__(self):
        ExactConductanceState.__post_init__(self)
        # Reuse the exact signed-star validation, including the Frobenius ball.
        carrier = ExactCarrierState(self.graph, self.C, self.charge, self.Z_4)
        object.__setattr__(self, "Z_4", carrier.Z_4)

    def to_payload(self):
        return dict(
            ExactConductanceState.to_payload(self),
            schema_version="grcv4-exact-adaptive-carrier-state-v1",
            Z_4=[list(row) for row in self.Z_4],
        )

    @classmethod
    def from_canonical_bytes(cls, raw):
        value = decode_canonical_json(raw)
        if (
            set(value) != {"schema_version", "graph", "C", "charge", "W_A", "Z_4"}
            or value["schema_version"] != "grcv4-exact-adaptive-carrier-state-v1"
        ):
            raise ValueError("closed full C/W/Z state required")
        return cls(
            GRCV4Graph.from_payload(value["graph"]),
            value["C"],
            value["charge"],
            value["W_A"],
            value["Z_4"],
        )

    def advance(self, flux, duration):
        raise ValueError("A_PC requires one atomic C/W/Z publication")

    def advance_conductance(self, flux, duration, W):
        raise ValueError("A_PC cannot publish a partial W update")

    def advance_carrier(self, flux, duration, Z):
        raise ValueError("A_PC cannot publish a partial Z update")

    def advance_histories(self, flux, duration, W, Z):
        resources = ExactResources.advance(self, flux, duration)
        return type(self)(self.graph, resources.C, self.charge, W, Z)

    def transfer(self, target, matrix):
        raise ValueError("A_PC history transfer needs both explicit channel policies")

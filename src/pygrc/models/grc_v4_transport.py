"""Candidate mobility, provisional continuity, and the unit-measure charge gate.

A mobility reads supplied retained W_A. C mobility reads only resolved W_C_tr
and eta_C; it has no selector or geometry input. E_H and E_M are sibling
constructors with distinct types and authorities, including at eta_C=1.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import ClassVar

from .grc_v4_codec import canonical_json_bytes
from .grc_v4_geometry import (
    GRCV4Differential,
    GRCV4Graph,
    GeometryDomainError,
    NonfiniteGeometryError,
    Matrix,
    OneForm,
    OneFormHodge,
    PhysicalFlux,
    VertexScalar,
    _computed,
    _diagonal,
    _identity,
    _require_coordinates,
)
from .grc_v4_profile import CandidateAParams, CandidateCParams, GRCV4Profile
from .grc_v4_state import _number, _vector


def _positive_products(eta: float, weights: tuple[float, ...]) -> tuple[float, ...]:
    gain = _number(eta)
    if gain <= 0:
        raise ValueError("mobility gain must be strictly positive")
    # Reject underflow to zero as well as overflow. No floor or fallback.
    products = tuple(_computed(gain * w) for w in weights)
    if any(x <= 0 for x in products):
        raise GeometryDomainError("computed mobility must be strictly positive")
    return _vector(products, positive=True)


def _c_reference(graph: GRCV4Graph, params: CandidateCParams) -> tuple[float, ...]:
    if type(graph) is not GRCV4Graph or type(params) is not CandidateCParams:
        raise TypeError("C reference requires graph and resolved C parameters")
    if set(params.W_C_tr) != set(graph.live_edge_ids):
        raise ValueError("C transport reference must cover exactly the live edge IDs")
    return _vector(tuple(params.W_C_tr[e] for e in graph.live_edge_ids), positive=True)


@dataclass(frozen=True, slots=True)
class _Mobility:
    graph: GRCV4Graph
    diagonal: tuple[float, ...] = field(init=False)
    SOURCE: ClassVar[str]

    @property
    def matrix(self) -> Matrix:
        return _diagonal(self.diagonal)

    def apply(self, driving_form: OneForm) -> PhysicalFlux:
        _require_coordinates(driving_form, OneForm, self.graph)
        return PhysicalFlux(
            self.graph,
            tuple(
                _computed(m * x)
                for m, x in zip(self.diagonal, driving_form.values, strict=True)
            ),
        )


@dataclass(frozen=True, slots=True)
class CandidateAMobility(_Mobility):
    params: CandidateAParams
    retained_W_A: tuple[float, ...]
    SOURCE: ClassVar[str] = "candidate_A_retained_W_A"

    def __post_init__(self) -> None:
        if (
            type(self.graph) is not GRCV4Graph
            or type(self.params) is not CandidateAParams
        ):
            raise TypeError("A mobility requires graph and resolved A parameters")
        weights = _vector(self.retained_W_A, positive=True)
        if len(weights) != len(self.graph.oriented_edges):
            raise ValueError("retained W_A must follow live edge order")
        object.__setattr__(self, "retained_W_A", weights)
        object.__setattr__(
            self, "diagonal", _positive_products(self.params.eta, weights)
        )

    @property
    def identity(self) -> str:
        return _identity(
            "grcv4-mobility-sha256",
            {
                "descriptor_version": "grcv4-candidate-mobility-factor-v1",
                "source": self.SOURCE,
                "graph_digest": self.graph.graph_digest,
                "orientation_identity": self.graph.orientation_identity,
                "params": self.params.to_payload(),
                "retained_W_A": self.retained_W_A,
            },
        )


@dataclass(frozen=True, slots=True)
class CandidateCMobility(_Mobility):
    params: CandidateCParams
    SOURCE: ClassVar[str] = "candidate_C_profile_W_C_tr"

    def __post_init__(self) -> None:
        weights = _c_reference(self.graph, self.params)
        object.__setattr__(
            self, "diagonal", _positive_products(self.params.eta_C, weights)
        )

    @property
    def identity(self) -> str:
        return _identity(
            "grcv4-mobility-sha256",
            {
                "descriptor_version": "grcv4-candidate-mobility-factor-v1",
                "source": self.SOURCE,
                "graph_digest": self.graph.graph_digest,
                "orientation_identity": self.graph.orientation_identity,
                "params": self.params.to_payload(),
            },
        )


def candidate_c_structural_hodge(
    graph: GRCV4Graph, params: CandidateCParams
) -> OneFormHodge:
    """E_H(W_C_tr)=diag(W_C_tr), independently of E_M=eta_C diag(W_C_tr)."""
    return OneFormHodge(graph, _diagonal(_c_reference(graph, params)))


class ChargeDomainError(ValueError):
    """Finite resource outside the nonnegative charge domain."""


def unit_charge(resource: VertexScalar) -> float:
    """Adjacent balanced binary64 tree in the graph's live-vertex order.

    Carry an unmatched last leaf unchanged to the next level. This is the
    admitted unit-measure primitive; neither Hodge nor mobility contributes.
    Each addition rounds separately. No sorting, fsum or resource repair.
    """
    if type(resource) is not VertexScalar:
        raise TypeError("charge requires a typed vertex resource")
    if any(value < 0 for value in resource.values):
        raise ChargeDomainError("charge resource must be nonnegative")
    values = _vector(resource.values, nonnegative=True)
    while len(values) > 1:
        values = tuple(
            _computed(values[i] + values[i + 1]) if i + 1 < len(values) else values[i]
            for i in range(0, len(values), 2)
        )
    return values[0] if values else 0.0


@dataclass(frozen=True, slots=True)
class ChargeEvaluation:
    """Evaluate the frozen inequality without modifying the supplied resource.

    Q_actual is the prescribed binary64 tree result. Compare the stated
    inequality exactly on its binary64 inputs: a rounded tolerance product
    must not enlarge or shrink the admitted interval. The diagnostic residual
    is rounded once to binary64 for the frozen receipt/observable fields.
    Zero residual does not imply exact conservation of the stored coordinate
    sum: the continuity updates and Q_actual reduction have already rounded.
    This value does not authenticate a lifecycle or a successful commit.
    """

    resource: VertexScalar
    target: float
    profile: GRCV4Profile
    actual: float = field(init=False)
    residual: float = field(init=False)
    admitted: bool = field(init=False)

    def __post_init__(self) -> None:
        if type(self.profile) is not GRCV4Profile:
            raise TypeError("charge requires a complete resolved profile")
        profile = GRCV4Profile.from_canonical_bytes(
            canonical_json_bytes(self.profile.to_payload())
        )
        if (
            profile.identity_payload.charge_profile_id != "unit_vertex_measure_v1"
            or profile.params_resolved.common.measure_profile_id
            != "unit_vertex_measure_v1"
        ):
            raise ValueError("unimplemented charge/measure profile")
        if type(self.resource) is not VertexScalar:
            raise TypeError("charge requires a typed vertex resource")
        resource = VertexScalar(self.resource.graph, self.resource.values)
        target = _number(self.target)
        actual = unit_charge(resource)
        delta = Fraction(actual) - Fraction(target)
        policy = profile.params_resolved.charge
        bound = Fraction(policy.absolute_tolerance) + Fraction(
            policy.relative_tolerance
        ) * max(abs(Fraction(target)), Fraction(1))
        try:
            residual = _computed(float(delta))
        except OverflowError:
            raise NonfiniteGeometryError("nonfinite charge residual") from None
        for name, value in (
            ("profile", profile),
            ("resource", resource),
            ("target", target),
            ("actual", actual),
            ("residual", residual),
            ("admitted", abs(delta) <= bound),
        ):
            object.__setattr__(self, name, value)

    @property
    def remainder(self) -> None:
        return None

    def receipt_values(self) -> dict[str, float]:
        """Computed charge fields; the later commit owner supplies ReceiptCore."""
        return {
            "target_charge": self.target,
            "admitted_charge": self.actual,
            "residual": self.residual,
        }


def provisional_continuity(
    resource: VertexScalar,
    current: PhysicalFlux,
    dt: float,
    *,
    differential: GRCV4Differential,
) -> VertexScalar:
    """One closed-internal C - dt * B J evaluation, with no authoritative write.

    The supplied current must already have been selected by its stage owner.
    Use the actual declared differential, then one binary64 multiplication
    and subtraction per vertex. The caller must admit the resulting resource
    and charge before exposing it to a writer. Underflow can round a transfer
    away; no hidden remainder is retained. External exchanges are typed events.
    """
    if type(differential) is not GRCV4Differential:
        raise TypeError("continuity requires the declared graph differential")
    _require_coordinates(resource, VertexScalar, differential.graph)
    _require_coordinates(current, PhysicalFlux, differential.graph)
    _vector(resource.values, nonnegative=True)
    duration = _number(dt)
    if duration < 0:
        raise ValueError("negative continuity duration")
    if duration == 0:
        return VertexScalar(resource.graph, resource.values)
    divergence = differential.divergence(current)
    return VertexScalar(
        resource.graph,
        tuple(
            _computed(c - _computed(duration * rate))
            for c, rate in zip(resource.values, divergence.values, strict=True)
        ),
    )

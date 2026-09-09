"""Candidate A history-free construction and retained authority (P9-5.1).

The graph-generic G_W law consumes a freshly rebuilt GRC differential and an
explicit target reference-stage flux. No seed, source W_A, geometry-derived
mobility, ordinary writer, current solve, migration or commit is inferred.
See specs/grc-v4-spec.md, Candidate A and lifecycle contracts, and the GRCV3
specification's Appendix A.2 for the host-frame WLS differential used here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
import math
from typing import cast

from .grc_v4_codec import JSONValue, canonical_json_bytes, json_value
from .grc_v4_geometry import (
    GRCV4Graph,
    GRCV4ReferenceGeometry,
    Matrix,
    NonfiniteGeometryError,
    PhysicalFlux,
    VertexScalar,
    _computed,
    _identity,
    _local_payload,
    _require_coordinates,
)
from .grc_v4_profile import CandidateAParams, GRCV4Profile
from .grc_v4_state import FrozenJSONMap, GRCV4AuthoritativeState, _number, _vector
from .grc_v4_transport import CandidateAMobility


HISTORY_POLICY = "candidate_a_explicit_reference_initialization_log_history_v1"
BACKEND = "grcv3_host_frame_reference_weighted_gradient_v1"


def _finite_fraction(value: Fraction) -> float:
    try:
        return _computed(float(value))
    except OverflowError as exc:
        raise NonfiniteGeometryError("A differential is not representable") from exc


def _solve_spd(a: list[list[Fraction]], b: list[Fraction]) -> tuple[float, ...]:
    # The declared positive ridge makes these exact normal equations SPD,
    # including disconnected/isolated nodes and rank-deficient host positions.
    # Rational elimination avoids intermediate overflow and pivot tolerances.
    n = len(b)
    rows = [row[:] + [rhs] for row, rhs in zip(a, b, strict=True)]
    for k in range(n):
        pivot = rows[k][k]
        if pivot <= 0:
            raise ValueError("A differential normal equations are not positive")
        for i in range(k + 1, n):
            gain = rows[i][k] / pivot
            for j in range(k + 1, n + 1):
                rows[i][j] -= gain * rows[k][j]
    answer = [Fraction(0) for _ in range(n)]
    for i in reversed(range(n)):
        answer[i] = (
            rows[i][n] - sum(rows[i][j] * answer[j] for j in range(i + 1, n))
        ) / rows[i][i]
    return tuple(_finite_fraction(x) for x in answer)


@dataclass(frozen=True, slots=True)
class CandidateADifferentialReference:
    """Explicit host-frame GRC WLS gradient; no GRC9 chart or source history.

    Positions follow live vertex order in one shared Euclidean host frame.
    Reference weights cover stable live edges exactly. Dimension, regularization,
    rounding and all reference preimages enter the profile's backend identity.
    This computes the gradient needed by G_W, not Hessian/basin conformance.
    """

    graph: GRCV4Graph
    dimension: int
    positions: Matrix
    reference_weights: FrozenJSONMap
    regularization: float

    def __post_init__(self) -> None:
        if type(self.graph) is not GRCV4Graph:
            raise TypeError("A differential requires a typed graph")
        if type(self.dimension) is not int or not 1 <= self.dimension <= 2**53 - 1:
            raise ValueError("host dimension must be a positive safe integer")
        # _vector rejects unordered/coercible/bool/nonfinite coordinate inputs.
        if type(self.positions) not in (tuple, list):
            raise TypeError("host positions require ordered rows")
        positions = tuple(_vector(row) for row in self.positions)
        if len(positions) != len(self.graph.live_node_ids) or any(
            len(row) != self.dimension for row in positions
        ):
            raise ValueError(
                "host positions must follow the complete live vertex order"
            )
        weights = FrozenJSONMap(self.reference_weights)
        if set(weights) != set(self.graph.live_edge_ids):
            raise ValueError("A differential weights must cover exactly the live edges")
        _vector(tuple(weights[e] for e in self.graph.live_edge_ids), positive=True)
        ridge = _number(self.regularization)
        if ridge <= 0:
            raise ValueError("A differential regularization must be positive")
        object.__setattr__(self, "positions", positions)
        object.__setattr__(self, "reference_weights", weights)
        object.__setattr__(self, "regularization", ridge)

    def to_payload(self) -> dict[str, JSONValue]:
        return {
            "backend": BACKEND,
            "graph": self.graph.to_payload(),
            "dimension": self.dimension,
            "positions": [list(row) for row in self.positions],
            "reference_weights": json_value(self.reference_weights),
            "regularization": self.regularization,
            "rounding": "exact_binary64_input_normal_equations_then_binary64_gradient_v1",
        }

    @property
    def identity(self) -> str:
        return _identity("grcv4-a-descriptor-sha256", self.to_payload())

    @classmethod
    def from_payload(cls, value: object) -> CandidateADifferentialReference:
        data = _local_payload(
            value,
            {
                "backend",
                "graph",
                "dimension",
                "positions",
                "reference_weights",
                "regularization",
                "rounding",
            },
        )
        result = cls(
            GRCV4Graph.from_payload(data["graph"]),
            cast(int, data["dimension"]),
            cast(Matrix, data["positions"]),
            cast(FrozenJSONMap, data["reference_weights"]),
            cast(float, data["regularization"]),
        )
        if canonical_json_bytes(result.to_payload()) != canonical_json_bytes(data):
            raise ValueError(
                "unsupported A differential recipe or noncanonical preimage"
            )
        return result

    def rebuild(self, C: VertexScalar) -> Matrix:
        _require_coordinates(C, VertexScalar, self.graph)
        _vector(C.values, nonnegative=True)
        dimension = self.dimension
        result = []
        for node in self.graph.live_node_ids:
            i = self.graph.node_index(node)
            a = [
                [
                    Fraction(self.regularization if k == j else 0)
                    for j in range(dimension)
                ]
                for k in range(dimension)
            ]
            b = [Fraction(0) for _ in range(dimension)]
            for edge in self.graph.oriented_edges:
                if node not in (edge.tail_node_id, edge.head_node_id):
                    continue
                neighbor = (
                    edge.head_node_id
                    if edge.tail_node_id == node
                    else edge.tail_node_id
                )
                j = self.graph.node_index(neighbor)
                delta = [
                    Fraction(y) - Fraction(x)
                    for x, y in zip(self.positions[i], self.positions[j], strict=True)
                ]
                weight = Fraction(_number(self.reference_weights[edge.edge_id]))
                dc = Fraction(C.values[j]) - Fraction(C.values[i])
                for k in range(dimension):
                    b[k] += weight * delta[k] * dc
                    for column in range(dimension):
                        a[k][column] += weight * delta[k] * delta[column]
            result.append(_solve_spd(a, b))
        return tuple(result)


def _conductance(
    graph: GRCV4Graph,
    params: CandidateAParams,
    C: VertexScalar,
    descriptors: Matrix,
    reference_current: PhysicalFlux,
) -> tuple[float, ...]:
    values = []
    for edge, current in zip(
        graph.oriented_edges, reference_current.values, strict=True
    ):
        u, v = graph.node_index(edge.tail_node_id), graph.node_index(edge.head_node_id)
        # Coefficients may be signed. Sum the entire exponent before rounding;
        # 0 * an overflowing square and cancelling large channels stay defined.
        contrast = sum(
            (Fraction(x) - Fraction(y)) ** 2
            for x, y in zip(descriptors[u], descriptors[v], strict=True)
        )
        exponent = (
            -(
                Fraction(params.alpha) * (Fraction(C.values[u]) + Fraction(C.values[v]))
                + Fraction(params.beta) * contrast
                + Fraction(params.gamma) * Fraction(current) ** 2
            )
            / 2
        )
        # These conservative bounds are outside the whole binary64 exp range.
        # Below -1000 the normative positive floor wins, even if subnormal.
        if exponent < -1000:
            value = params.W_floor
        elif exponent > 1000:
            raise NonfiniteGeometryError("A conductance exponential overflows")
        else:
            try:
                value = max(params.W_floor, math.exp(float(exponent)))
            except OverflowError as exc:
                raise NonfiniteGeometryError(
                    "A conductance exponential overflows"
                ) from exc
        values.append(_computed(value))
    return _vector(values, positive=True)


@dataclass(frozen=True, slots=True)
class CandidateARetainedAuthority:
    """Bind supplied positive A_OS state to its sole retained mobility input.

    W_floor is a G_W floor, not a license to clamp supplied positive history.
    Construction validates local state/mobility, not a current root or lifecycle.
    """

    graph: GRCV4Graph
    profile: GRCV4Profile
    state: GRCV4AuthoritativeState
    mobility: CandidateAMobility = field(init=False)

    def __post_init__(self) -> None:
        if type(self.graph) is not GRCV4Graph or type(self.profile) is not GRCV4Profile:
            raise TypeError("A retained authority requires graph and complete profile")
        if type(self.profile.params_resolved.candidate) is not CandidateAParams:
            raise TypeError("A retained authority requires Candidate A")
        if self.profile.identity_payload.realization != "OS":
            raise ValueError("P9-5.1 admits only the A_OS local construction surface")
        if type(self.state) is not GRCV4AuthoritativeState:
            raise TypeError("A retained authority requires typed state")
        state = GRCV4AuthoritativeState(self.state.C, self.state.W_A, self.state.Z_4)
        if (
            len(state.C) != len(self.graph.live_node_ids)
            or state.W_A is None
            or state.Z_4 is not None
        ):
            raise ValueError(
                "A_OS authority requires graph-sized C, W_A and no carrier"
            )
        mobility = CandidateAMobility(
            self.graph, self.profile.params_resolved.candidate, state.W_A
        )
        object.__setattr__(self, "state", state)
        object.__setattr__(self, "mobility", mobility)


@dataclass(frozen=True, slots=True)
class CandidateAInitializationStage:
    """Reconstructible target stage; the reference flux is mandatory input.

    Its value and role are declared, never obtained from old A mobility or a
    fabricated zero seed. This is an initializer operand, not a certificate that
    a candidate current solver produced the supplied flux or that its causal
    origin is history-free. Crossings still own source-history disposition and
    whole-target readmission. No caller-supplied differential cache is consumed.
    """

    reference: GRCV4ReferenceGeometry
    differential_reference: CandidateADifferentialReference
    C: VertexScalar
    reference_current: PhysicalFlux
    descriptors: Matrix = field(init=False)
    authority: CandidateARetainedAuthority = field(init=False)

    def __post_init__(self) -> None:
        if type(self.reference) is not GRCV4ReferenceGeometry:
            raise TypeError("A initialization requires a typed target reference")
        if type(self.differential_reference) is not CandidateADifferentialReference:
            raise TypeError(
                "A initialization requires the declared differential recipe"
            )
        graph, profile = self.reference.graph, self.reference.profile
        params = profile.params_resolved.candidate
        if type(params) is not CandidateAParams:
            raise TypeError("A initialization requires Candidate A")
        if profile.identity_payload.realization != "OS":
            raise ValueError("P9-5.1 admits only the A_OS local construction surface")
        if profile.params_resolved.lifecycle.history_policy_id != HISTORY_POLICY:
            raise ValueError("unimplemented A initializer/history policy")
        if (
            self.differential_reference.graph != graph
            or params.descriptor_backend_id != self.differential_reference.identity
            or canonical_json_bytes(self.differential_reference.reference_weights)
            != canonical_json_bytes(self.reference.edge_weights)
        ):
            raise ValueError("A target differential reference/profile mismatch")
        _require_coordinates(self.C, VertexScalar, graph)
        _require_coordinates(self.reference_current, PhysicalFlux, graph)
        descriptors = self.differential_reference.rebuild(self.C)
        weights = _conductance(
            graph, params, self.C, descriptors, self.reference_current
        )
        authority = CandidateARetainedAuthority(
            graph, profile, GRCV4AuthoritativeState(self.C.values, weights, None)
        )
        object.__setattr__(self, "descriptors", descriptors)
        object.__setattr__(self, "authority", authority)

    def to_payload(self) -> dict[str, JSONValue]:
        return {
            "schema_version": "grcv4-a-history-free-stage-v1",
            "reference": self.reference.to_payload(),
            "differential_reference": self.differential_reference.to_payload(),
            "C": list(self.C.values),
            "reference_current": list(self.reference_current.values),
            "reference_current_role": "explicit_target_reference_stage_flux_v1",
        }

    @property
    def identity(self) -> str:
        return _identity("grcv4-a-initialization-stage-sha256", self.to_payload())

    @classmethod
    def from_payload(cls, value: object) -> CandidateAInitializationStage:
        data = _local_payload(
            value,
            {
                "schema_version",
                "reference",
                "differential_reference",
                "C",
                "reference_current",
                "reference_current_role",
            },
        )
        reference = GRCV4ReferenceGeometry.from_payload(data["reference"])
        result = cls(
            reference,
            CandidateADifferentialReference.from_payload(
                data["differential_reference"]
            ),
            VertexScalar(reference.graph, cast(tuple[float, ...], data["C"])),
            PhysicalFlux(
                reference.graph, cast(tuple[float, ...], data["reference_current"])
            ),
        )
        if canonical_json_bytes(result.to_payload()) != canonical_json_bytes(data):
            raise ValueError("unsupported A initializer stage recipe")
        return result


@dataclass(frozen=True, slots=True)
class CandidateAInitialization:
    """Construct both targets before returning; no lifecycle is committed.

    The same recipe applies independently to current and reset inputs. A reset
    failure publishes no partial result. The returned states are detached values;
    later current/lifecycle admission and direction-specific receipts remain
    with their owning leaves. Initialized state proves neither formation nor
    preservation of source history.
    """

    current: CandidateAInitializationStage
    reset: CandidateAInitializationStage

    def __post_init__(self) -> None:
        if (
            type(self.current) is not CandidateAInitializationStage
            or type(self.reset) is not CandidateAInitializationStage
        ):
            raise TypeError("A initialization requires current and reset target stages")
        if (
            self.current.reference.identity != self.reset.reference.identity
            or self.current.differential_reference.identity
            != self.reset.differential_reference.identity
        ):
            raise ValueError("current/reset must use the same declared target recipe")

    @classmethod
    def construct(
        cls,
        reference: GRCV4ReferenceGeometry,
        differential_reference: CandidateADifferentialReference,
        *,
        current_C: VertexScalar,
        current_reference_current: PhysicalFlux,
        reset_C: VertexScalar,
        reset_reference_current: PhysicalFlux,
    ) -> CandidateAInitialization:
        return cls(
            CandidateAInitializationStage(
                reference, differential_reference, current_C, current_reference_current
            ),
            CandidateAInitializationStage(
                reference, differential_reference, reset_C, reset_reference_current
            ),
        )

    @property
    def identity(self) -> str:
        return _identity("grcv4-a-initialization-sha256", self.to_payload())

    def to_payload(self) -> dict[str, JSONValue]:
        return {
            "schema_version": "grcv4-a-history-free-construction-v1",
            "current": self.current.to_payload(),
            "reset": self.reset.to_payload(),
            "construction": "history_free_target_initialization",
            "source_history_preserved": False,
            "native_formation_claimed": False,
            "whole_target_readmission": "pending_current_and_lifecycle_implementation",
            "lifecycle_committed": False,
        }

    @classmethod
    def from_payload(cls, value: object) -> CandidateAInitialization:
        data = _local_payload(
            value,
            {
                "schema_version",
                "current",
                "reset",
                "construction",
                "source_history_preserved",
                "native_formation_claimed",
                "whole_target_readmission",
                "lifecycle_committed",
            },
        )
        result = cls(
            CandidateAInitializationStage.from_payload(data["current"]),
            CandidateAInitializationStage.from_payload(data["reset"]),
        )
        if canonical_json_bytes(result.to_payload()) != canonical_json_bytes(data):
            raise ValueError(
                "A initializer cannot claim formation, history preservation or commit"
            )
        return result

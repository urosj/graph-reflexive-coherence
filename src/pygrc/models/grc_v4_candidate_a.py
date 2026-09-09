"""Candidate A construction, fixed-stage current and log writer (P9-5.1/5.2).

The graph-generic G_W law consumes a freshly rebuilt GRC differential and an
explicit target reference-stage flux. Ordinary current reads incoming retained
W_A; its separate writer consumes admitted final C and the selected current.
These provisional primitives do not execute a full OS pass or lifecycle commit.
See specs/grc-v4-spec.md, Candidate A and lifecycle contracts, and the GRCV3
specification's Appendix A.2 for the host-frame WLS differential used here.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from decimal import (
    Context,
    Decimal,
    DivisionByZero,
    InvalidOperation,
    Overflow,
    ROUND_HALF_EVEN,
    localcontext,
)
from fractions import Fraction
import math
from typing import TYPE_CHECKING, cast

from .grc_v4_candidate_c import CandidateCStageError, _c_residual_pass, _c_solve

from .grc_v4_codec import JSONValue, canonical_json_bytes, json_value
from .grc_v4_geometry import (
    GRCV4Graph,
    GRCV4ReferenceGeometry,
    GeometryStageInputs,
    K4Tensor,
    Matrix,
    NonfiniteGeometryError,
    OneForm,
    PhysicalFlux,
    StarAssembly,
    VertexScalar,
    _computed,
    _identity,
    _local_payload,
    _require_coordinates,
)
from .grc_v4_profile import CandidateAParams, GRCV4Profile
from .grc_v4_state import (
    FrozenJSONMap,
    GRCV4AuthoritativeState,
    SolverDisposition,
    _number,
    _vector,
)
from .grc_v4_transport import CandidateAMobility

if TYPE_CHECKING:
    from .grc_v4_step import ProvisionalResourceStep


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


A_CURRENT_NUMERICS = "grcv4-a-exact-contrast-diagonal-current-v1"
A_WRITER_NUMERICS = "grcv4-a-log-interpolation-decimal120-binary64-v1"
A_SITE_POTENTIAL = "quadratic_site_potential_zero_derivative_v1"


class CandidateAStageError(ValueError):
    """Local numerical failure; the operation owner supplies stage/receipt."""

    def __init__(self, disposition: SolverDisposition, message: str) -> None:
        if disposition not in (
            "domain_failure",
            "singular",
            "conditioning_failure",
            "nonfinite",
            "no_admitted_root",
            "multiple_admitted_roots",
        ):
            raise ValueError("expected a failed A stage disposition")
        super().__init__(message)
        self.disposition = disposition


def _a_float(value: Fraction) -> float:
    try:
        return _computed(float(value))
    except (OverflowError, NonfiniteGeometryError) as exc:
        raise CandidateAStageError(
            "nonfinite", "A stage output is not finite binary64"
        ) from exc


@dataclass(frozen=True, slots=True)
class CandidateAReadBack:
    source_identity: str
    current: PhysicalFlux
    flux: PhysicalFlux
    causal_flat: OneForm


@dataclass(frozen=True, slots=True)
class CandidateACurrent:
    """Fresh fixed-geometry A_OS current from incoming retained authority.

    This stage primitive is not an OS pass or lifecycle admission. Only the
    declared zero-derivative site potential is implemented. The contrast stays
    rational through the diagonal solve: its displayed binary64 value may
    round to +/-1 without making the exact denominator singular.
    Potential decomposition diagnostics are exact rationals in the input
    graph's live-node order. Only their consumed sum must fit binary64;
    individually overflowing components may cancel to a finite potential.
    """

    inputs: GeometryStageInputs
    differential_reference: CandidateADifferentialReference
    authority: CandidateARetainedAuthority = field(init=False)
    descriptors: Matrix = field(init=False)
    reference_potential_exact: tuple[Fraction, ...] = field(init=False)
    geometry_potential_increment_exact: tuple[Fraction, ...] = field(init=False)
    potential: VertexScalar = field(init=False)
    baseline: PhysicalFlux = field(init=False)
    W_hat_A: tuple[float, ...] = field(init=False)
    contrast: tuple[float, ...] = field(init=False)
    contrast_exact: tuple[Fraction, ...] = field(init=False)
    denominator_exact: tuple[Fraction, ...] = field(init=False)
    current: PhysicalFlux = field(init=False)
    read: CandidateAReadBack = field(init=False)
    closure_residual_squared: str = field(init=False)

    def __post_init__(self) -> None:
        if type(self.inputs) is not GeometryStageInputs:
            raise TypeError("A current requires exact typed stage inputs")
        if type(self.differential_reference) is not CandidateADifferentialReference:
            raise TypeError("A current requires a declared differential recipe")
        ref = self.inputs.geometry.reference
        profile, graph = ref.profile, ref.graph
        params, common, policy = (
            profile.params_resolved.candidate,
            profile.params_resolved.common,
            profile.params_resolved.solver,
        )
        authority = CandidateARetainedAuthority(graph, profile, self.inputs.current)
        assert isinstance(params, CandidateAParams)
        if (
            params.site_potential_id != A_SITE_POTENTIAL
            or common.domain_id != "fixed_graph_strict_gap_spd_v1"
            or common.gauge_id != "component_zero_mean_potential_v1"
            or common.normalization_id != "unnormalized_vertex_stiffness_v1"
            or profile.identity_payload.solver_id != "direct_unique_root_v1"
            or policy.solver_kind != "direct"
            or policy.residual_norm_id != "edge_l2_v1"
        ):
            raise ValueError("unimplemented A current/profile declaration")
        if self.inputs.trial_current is not None:
            raise ValueError("fixed A_OS stage does not consume a trial-current cache")
        backend = self.differential_reference
        if (
            backend.graph != graph
            or backend.identity != params.descriptor_backend_id
            or canonical_json_bytes(backend.reference_weights)
            != canonical_json_bytes(ref.edge_weights)
        ):
            raise ValueError("A stage differential reference/profile mismatch")
        C = VertexScalar(graph, authority.state.C)
        try:
            descriptors = backend.rebuild(C)
        except NonfiniteGeometryError as exc:
            raise CandidateAStageError("nonfinite", str(exc)) from exc
        B = tuple(tuple(Fraction(x) for x in row) for row in graph.incidence)
        dC = tuple(
            sum((B[i][e] * Fraction(c) for i, c in enumerate(C.values)), Fraction())
            for e in range(len(graph.live_edge_ids))
        )
        assert authority.state.W_A is not None
        phi0 = tuple(
            Fraction(params.kappa_c)
            * sum(
                (
                    B[i][e] * Fraction(w) * dC[e]
                    for e, w in enumerate(authority.state.W_A)
                ),
                Fraction(),
            )
            for i in range(len(C.values))
        )
        h, h_ref = (
            self.inputs.geometry.one_form_hodge.matrix,
            ref.pairings.one_form.matrix,
        )
        # H0_ref is the separately admitted unit-vertex pairing. Sum the full
        # reference-relative increment before rounding, including dense H1.
        delta_edge = tuple(
            sum(
                (
                    (Fraction(x) - Fraction(y)) * dc
                    for x, y, dc in zip(row, reference_row, dC, strict=True)
                ),
                Fraction(),
            )
            for row, reference_row in zip(h, h_ref, strict=True)
        )
        delta_phi = tuple(
            Fraction(params.kappa_Ah)
            * sum((x * y for x, y in zip(row, delta_edge, strict=True)), Fraction())
            for row in B
        )
        phi = VertexScalar(
            graph, tuple(_a_float(x + y) for x, y in zip(phi0, delta_phi, strict=True))
        )
        baseline = PhysicalFlux(
            graph,
            tuple(
                _a_float(
                    -Fraction(m)
                    * sum(
                        (B[i][e] * Fraction(c) for i, c in enumerate(phi.values)),
                        Fraction(),
                    )
                )
                for e, m in enumerate(authority.mobility.diagonal)
            ),
        )
        try:
            w_hat = _conductance(graph, params, C, descriptors, baseline)
        except NonfiniteGeometryError as exc:
            raise CandidateAStageError("nonfinite", str(exc)) from exc
        q = tuple(
            (Fraction(w) - Fraction(target)) / (Fraction(w) + Fraction(target))
            for w, target in zip(authority.state.W_A, w_hat, strict=True)
        )
        denominator = tuple(
            1 - Fraction(params.zeta_A) * Fraction(params.chi_A) * x for x in q
        )
        if any(x == 0 for x in denominator):
            raise CandidateAStageError(
                "singular", "singular A physical current block; no fallback"
            )
        if denominator and max(map(abs, denominator)) > Fraction(
            policy.conditioning_limit
        ) * min(map(abs, denominator)):
            raise CandidateAStageError(
                "conditioning_failure",
                "A physical current block exceeds conditioning limit",
            )
        current = PhysicalFlux(
            graph,
            tuple(
                _a_float(Fraction(j) / d)
                for j, d in zip(baseline.values, denominator, strict=True)
            ),
        )
        for name, value in (
            ("authority", authority),
            ("descriptors", descriptors),
            ("reference_potential_exact", phi0),
            ("geometry_potential_increment_exact", delta_phi),
            ("potential", phi),
            ("baseline", baseline),
            ("W_hat_A", w_hat),
            ("contrast", tuple(map(float, q))),
            ("contrast_exact", q),
            ("denominator_exact", denominator),
            ("current", current),
        ):
            object.__setattr__(self, name, value)
        read = self.read_back(current)
        residual = tuple(
            Fraction(j) - Fraction(j0) - Fraction(params.zeta_A) * Fraction(r)
            for j, j0, r in zip(
                current.values, baseline.values, read.flux.values, strict=True
            )
        )
        block_residual = tuple(
            d * Fraction(j) - Fraction(j0)
            for d, j, j0 in zip(
                denominator, current.values, baseline.values, strict=True
            )
        )
        rhs = tuple(map(Fraction, baseline.values))
        if not all(
            _c_residual_pass(r, rhs, policy) for r in (residual, block_residual)
        ):
            raise CandidateAStageError(
                "no_admitted_root", "A physical read-back closure residual failed"
            )
        object.__setattr__(self, "read", read)
        object.__setattr__(
            self,
            "closure_residual_squared",
            str(sum((x * x for x in residual), Fraction())),
        )

    @property
    def identity(self) -> str:
        return _identity("grcv4-a-fixed-stage-sha256", self.to_payload())

    def read_back(self, current: PhysicalFlux) -> CandidateAReadBack:
        ref = self.inputs.geometry.reference
        _require_coordinates(current, PhysicalFlux, ref.graph)
        params = ref.profile.params_resolved.candidate
        assert isinstance(params, CandidateAParams)
        flux = PhysicalFlux(
            ref.graph,
            tuple(
                _a_float(Fraction(params.chi_A) * q * Fraction(j))
                for q, j in zip(self.contrast_exact, current.values, strict=True)
            ),
        )
        # Reuse only the existing certified matrix solve/residual arithmetic;
        # no C selector, potential, current or mobility participates in A.
        try:
            flat = _c_solve(
                self.inputs.geometry.one_form_hodge.matrix,
                tuple((x,) for x in flux.values),
                ref.profile.params_resolved.solver,
                "A structural flat map",
                [],
            )
        except CandidateCStageError as exc:
            raise CandidateAStageError(exc.disposition, str(exc)) from exc
        return CandidateAReadBack(
            self.identity,
            current,
            flux,
            OneForm(ref.graph, tuple(row[0] for row in flat)),
        )

    def structural_source(self) -> K4Tensor:
        ref = self.inputs.geometry.reference
        params = ref.profile.params_resolved.candidate
        assert isinstance(params, CandidateAParams)
        n = len(ref.graph.live_edge_ids)
        increment = (
            tuple((0.0,) * n for _ in range(n))
            if params.zeta_A == 0
            else tuple(
                tuple(_a_float(Fraction(params.zeta_A) * Fraction(x)) for x in row)
                for row in StarAssembly(self.read.causal_flat).matrix
            )
        )
        return K4Tensor(ref.graph, ref.K4_base, increment)

    def to_payload(self) -> dict[str, JSONValue]:
        return {
            "schema_version": "grcv4-a-fixed-stage-v1",
            "numerics": A_CURRENT_NUMERICS,
            "inputs": self.inputs.to_payload(),
            "differential_reference": self.differential_reference.to_payload(),
        }

    @classmethod
    def from_payload(cls, value: object) -> CandidateACurrent:
        data = _local_payload(
            value,
            {"schema_version", "numerics", "inputs", "differential_reference"},
            "schema_version",
            "grcv4-a-fixed-stage-v1",
        )
        if data["numerics"] != A_CURRENT_NUMERICS:
            raise ValueError("unsupported A current numerical recipe")
        return cls(
            GeometryStageInputs.from_payload(data["inputs"]),
            CandidateADifferentialReference.from_payload(
                data["differential_reference"]
            ),
        )


def candidate_a_log_interpolation(
    old: tuple[float, ...],
    target: tuple[float, ...],
    dt: float,
    tau: float,
) -> tuple[float, ...]:
    """One declared log-space interpolation, without resource/commit authority.

    Exact binary64 inputs, 120-digit half-even Decimal log/exp, then one
    binary64 rounding. The ratio is not first divided in binary64. Branching
    around the nearer endpoint avoids subtracting nearly equal decay weights.
    Beyond dt/tau=1000 the residual is below half an ULP at either positive
    binary64 endpoint (|log(target/old)| < 1455); return the exact target.
    """
    old, target = _vector(old, positive=True), _vector(target, positive=True)
    dt, tau = _number(dt), _number(tau)
    if len(old) != len(target) or dt < 0 or tau <= 0:
        raise ValueError(
            "A log writer requires matching positive fields, dt>=0 and tau>0"
        )
    if dt == 0:
        return old
    if Fraction(dt) >= 1000 * Fraction(tau):
        return target
    with localcontext(
        # Context otherwise inherits unspecified fields from mutable
        # DefaultContext, including traps for expected inexact arithmetic.
        Context(
            prec=120,
            rounding=ROUND_HALF_EVEN,
            Emin=-999999,
            Emax=999999,
            capitals=1,
            clamp=0,
            flags=[],
            traps=[InvalidOperation, DivisionByZero, Overflow],
        )
    ):
        ratio = Decimal.from_float(dt) / Decimal.from_float(tau)
        decay = (-ratio).exp()
        advance = 1 - decay
        result = []
        for w, drive in zip(old, target, strict=True):
            if w == drive:
                result.append(w)
                continue
            lw, ld = Decimal.from_float(w).ln(), Decimal.from_float(drive).ln()
            log_next = (
                lw + advance * (ld - lw) if ratio <= 1 else ld + decay * (lw - ld)
            )
            result.append(float(log_next.exp()))
    return _vector(result, positive=True)


@dataclass(frozen=True, slots=True)
class CandidateAWriter:
    """Consume admitted final C and the actual fixed-stage corrector current.

    This writes a detached candidate value once. The complete OS/step and
    lifecycle owners still supply the genuine corrector geometry, authenticate
    state/ledger, and commit atomically. New W_A never feeds this beat's current.
    """

    point: CandidateACurrent
    resource: ProvisionalResourceStep
    descriptors: Matrix = field(init=False)
    W_drv_A: tuple[float, ...] = field(init=False)
    authority: CandidateARetainedAuthority = field(init=False)

    def __post_init__(self) -> None:
        from .grc_v4_step import CurrentSelection, ProvisionalResourceStep

        if (
            type(self.point) is not CandidateACurrent
            or type(self.resource) is not ProvisionalResourceStep
        ):
            raise TypeError(
                "A writer requires the current owner and admitted resource boundary"
            )
        inputs = self.point.inputs
        if inputs.stage != "os_corrector" or inputs.dt <= 0:
            raise ValueError("A writer requires a positive-duration OS corrector")
        ref = inputs.geometry.reference
        if ref.profile.params_resolved.lifecycle.history_policy_id != HISTORY_POLICY:
            raise ValueError("unimplemented A retained-history writer policy")
        expected_before = replace(inputs, geometry=ref.geometry(), stage="pre_read")
        final = self.resource.consume(
            expected_prestate=expected_before,
            expected_selection=CurrentSelection(
                inputs, "valid_root", self.point.current
            ),
        )
        C = VertexScalar(ref.graph, final.C)
        params = ref.profile.params_resolved.candidate
        assert isinstance(params, CandidateAParams)
        try:
            descriptors = self.point.differential_reference.rebuild(C)
            target = _conductance(ref.graph, params, C, descriptors, self.point.current)
            assert inputs.current.W_A is not None
            weights = candidate_a_log_interpolation(
                inputs.current.W_A, target, inputs.dt, params.tau_A
            )
            authority = CandidateARetainedAuthority(
                ref.graph, ref.profile, GRCV4AuthoritativeState(final.C, weights, None)
            )
        except NonfiniteGeometryError as exc:
            raise CandidateAStageError("nonfinite", str(exc)) from exc
        object.__setattr__(self, "descriptors", descriptors)
        object.__setattr__(self, "W_drv_A", target)
        object.__setattr__(self, "authority", authority)

    @property
    def identity(self) -> str:
        return _identity("grcv4-a-provisional-writer-sha256", self.to_payload())

    def to_payload(self) -> dict[str, JSONValue]:
        return {
            "schema_version": "grcv4-a-provisional-writer-v1",
            "numerics": A_WRITER_NUMERICS,
            "current": self.point.to_payload(),
            "resource_prestate": self.resource.prestate.to_payload(),
        }

    @classmethod
    def from_payload(cls, value: object) -> CandidateAWriter:
        from .grc_v4_step import CurrentSelection, ProvisionalResourceStep

        data = _local_payload(
            value,
            {"schema_version", "numerics", "current", "resource_prestate"},
            "schema_version",
            "grcv4-a-provisional-writer-v1",
        )
        if data["numerics"] != A_WRITER_NUMERICS:
            raise ValueError("unsupported A writer numerical recipe")
        point = CandidateACurrent.from_payload(data["current"])
        resource = ProvisionalResourceStep(
            GeometryStageInputs.from_payload(data["resource_prestate"]),
            CurrentSelection(point.inputs, "valid_root", point.current),
        )
        return cls(point, resource)

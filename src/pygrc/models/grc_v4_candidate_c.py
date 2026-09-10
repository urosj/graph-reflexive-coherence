"""Candidate C reference transport and fixed-stage current (P9-4.1/P9-4.2).

The complete profile owns W_C_tr. E_H and E_M independently consume that
map; neither a live geometry nor a retained Hodge can supply mobility.
The stage evaluator rederives the selector, retained Hodge and physical current.
It does not write resource, execute a complete realization, or admit a lifecycle.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
import math
from typing import TypeAlias

from .grc_v4_codec import (
    JSONValue,
    V4SchemaError,
    canonical_json_bytes,
    decode_canonical_json,
    json_value,
    payload_identity,
)
from .grc_v4_geometry import (
    GRCV4Graph,
    GRCV4Pairings,
    GeometryStageInputs,
    Matrix,
    OneForm,
    OneFormHodge,
    PhysicalFlux,
    VertexScalar,
    _computed,
    _identity,
    _require_coordinates,
)
from .grc_v4_codec import _dependency
from .grc_v4_profile import CandidateCParams, GRCV4Profile, SolverPolicy
from .grc_v4_state import FrozenJSONMap, SolverDisposition, _number, _vector
from .grc_v4_transport import CandidateCMobility, candidate_c_structural_hodge


@dataclass(frozen=True, slots=True)
class CandidateCTransport:
    """Fixed-graph/profile sibling constructors, with reconstructible inputs.

    Constructor identities name the typed recipe and its exact inputs. They
    differ from operator identities and the complete binding identity: eta
    changes only E_M; selector/geometry controls change the complete profile
    binding without changing either reference constructor. The Hodge output
    is the reference Hodge, never the generated or retained stage Hodge.
    """

    graph: GRCV4Graph
    profile: GRCV4Profile
    structural_hodge: OneFormHodge = field(init=False)
    mobility: CandidateCMobility = field(init=False)

    def __post_init__(self) -> None:
        if type(self.graph) is not GRCV4Graph or type(self.profile) is not GRCV4Profile:
            raise TypeError("C transport requires a typed graph and complete profile")
        params = self.profile.params_resolved.candidate
        if type(params) is not CandidateCParams:
            raise TypeError("C transport requires a Candidate C complete profile")
        # Both constructors enforce exact live-edge coverage. Check the declared
        # structural reference preimage too: matching dimensions is insufficient.
        hodge = candidate_c_structural_hodge(self.graph, params)
        payload_identity(
            "reference_hodge_identity_payload",
            {
                "schema_version": "grcv4-reference-hodge-identity-v1",
                "edge_weights": params.W_C_tr,
            },
            expected=self.profile.params_resolved.geometry.reference_hodge_digest,
        )
        mobility = CandidateCMobility(self.graph, params)
        object.__setattr__(self, "structural_hodge", hodge)
        object.__setattr__(self, "mobility", mobility)

    @property
    def params(self) -> CandidateCParams:
        params = self.profile.params_resolved.candidate
        assert isinstance(params, CandidateCParams)
        return params

    def _constructor_payload(self, *, mobility: bool) -> dict[str, JSONValue]:
        params = self.params
        payload: dict[str, JSONValue] = {
            "descriptor": "grcv4-c-reference-constructor-v1",
            "transport_id": params.transport_id,
            "constructor_id": params.E_M_policy_id
            if mobility
            else params.E_H_policy_id,
            "output_type": "physical_flux_mobility" if mobility else "one_form_hodge",
            "units_id": self.profile.params_resolved.common.units_id,
            "graph_digest": self.graph.graph_digest,
            "orientation_identity": self.graph.orientation_identity,
            "W_C_tr_content_digest": params.W_C_tr_content_digest,
        }
        if mobility:
            payload["eta_C"] = params.eta_C
        return payload

    @property
    def structural_hodge_constructor_payload(self) -> dict[str, JSONValue]:
        return self._constructor_payload(mobility=False)

    @property
    def mobility_constructor_payload(self) -> dict[str, JSONValue]:
        return self._constructor_payload(mobility=True)

    @property
    def structural_hodge_constructor_identity(self) -> str:
        return _identity(
            "grcv4-c-reference-constructor-sha256",
            self.structural_hodge_constructor_payload,
        )

    @property
    def mobility_constructor_identity(self) -> str:
        return _identity(
            "grcv4-c-reference-constructor-sha256", self.mobility_constructor_payload
        )

    @property
    def identity(self) -> str:
        return _identity("grcv4-c-reference-binding-sha256", self.to_payload())

    def to_payload(self) -> dict[str, JSONValue]:
        """Internal reconstruction record of source inputs, not a snapshot."""
        return {
            "schema_version": "grcv4-c-reference-binding-v1",
            "graph": self.graph.to_payload(),
            "profile": self.profile.to_payload(),
        }

    @classmethod
    def from_payload(cls, value: object) -> CandidateCTransport:
        payload = json_value(value)
        if (
            not isinstance(payload, dict)
            or set(payload) != {"schema_version", "graph", "profile"}
            or payload["schema_version"] != "grcv4-c-reference-binding-v1"
        ):
            raise V4SchemaError("expected exact Candidate C reference binding inputs")
        return cls(
            GRCV4Graph.from_payload(payload["graph"]),
            GRCV4Profile.from_canonical_bytes(canonical_json_bytes(payload["profile"])),
        )

    def to_canonical_bytes(self) -> bytes:
        return canonical_json_bytes(self.to_payload())

    @classmethod
    def from_canonical_bytes(cls, data: bytes | str) -> CandidateCTransport:
        return cls.from_payload(decode_canonical_json(data))


_CExact: TypeAlias = tuple[tuple[Fraction, ...], ...]
C_STAGE_NUMERICS = "grcv4-c-stage-exact-linear-binary64-v1"


def _fixed_current_policy(profile: GRCV4Profile) -> bool:
    """The CI algorithm eliminates its current block by the same direct solve.

    The outer fixed-point algorithm is declared explicitly; this is not a
    solver fallback or an admission of an arbitrary CI domain.
    """
    identity, policy = profile.identity_payload, profile.params_resolved.solver
    return policy.residual_norm_id == "edge_l2_v1" and (
        (identity.solver_id == "direct_unique_root_v1" and policy.solver_kind == "direct")
        or (
            identity.realization in {"CI", "CI+PC"}
            and identity.solver_id == "ci_reduced_fixed_point_v1"
            and policy.solver_kind == "fixed_point"
        )
    )


class CandidateCStageError(ValueError):
    """Observed numeric failure; the operation owner supplies stage and receipt.

    Residual rejection means no numerically admitted root was produced, not
    proof that the underlying exact constitutive equation lacks a solution.
    """

    def __init__(self, disposition: SolverDisposition, message: str) -> None:
        if disposition not in (
            "domain_failure",
            "singular",
            "conditioning_failure",
            "nonfinite",
            "no_admitted_root",
            "multiple_admitted_roots",
        ):
            raise ValueError("expected a failed C stage disposition")
        super().__init__(message)
        self.disposition = disposition


def _c_exact(matrix: Matrix) -> _CExact:
    return tuple(tuple(Fraction(x) for x in row) for row in matrix)


def _c_float(matrix: _CExact) -> Matrix:
    try:
        return tuple(tuple(_computed(float(x)) for x in row) for row in matrix)
    except OverflowError as exc:
        raise CandidateCStageError(
            "nonfinite", "C stage result is not finite binary64"
        ) from exc


def _c_transpose(matrix: _CExact) -> _CExact:
    return tuple(zip(*matrix, strict=True))


def _c_mm(left: _CExact, right: _CExact) -> _CExact:
    return tuple(
        tuple(
            sum((a * b for a, b in zip(row, col, strict=True)), Fraction())
            for col in _c_transpose(right)
        )
        for row in left
    )


def _c_product(left: Matrix, right: Matrix) -> Matrix:
    return _c_float(_c_mm(_c_exact(left), _c_exact(right)))


def _c_eye(size: int) -> Matrix:
    return tuple(tuple(float(i == j) for j in range(size)) for i in range(size))


def _c_apply(matrix: Matrix, values: tuple[float, ...]) -> tuple[float, ...]:
    result = _c_float(_c_mm(_c_exact(matrix), tuple((Fraction(x),) for x in values)))
    return tuple(row[0] for row in result)


def _c_inverse(matrix: _CExact) -> _CExact:
    """Exact elimination of the supplied coefficients; never a pseudoinverse."""
    n = len(matrix)
    rows = [
        list(row) + [Fraction(i == j) for j in range(n)] for i, row in enumerate(matrix)
    ]
    for j in range(n):
        pivot = next((i for i in range(j, n) if rows[i][j]), None)
        if pivot is None:
            raise CandidateCStageError(
                "singular", "singular C stage block; no fallback"
            )
        rows[j], rows[pivot] = rows[pivot], rows[j]
        divisor = rows[j][j]
        rows[j] = [x / divisor for x in rows[j]]
        for i in range(n):
            if i != j:
                factor = rows[i][j]
                rows[i] = [
                    a - factor * b for a, b in zip(rows[i], rows[j], strict=True)
                ]
    return tuple(tuple(row[n:]) for row in rows)


def _c_inertia(matrix: _CExact) -> tuple[int, int, int]:
    """Exact symmetric congruences, including a 2x2 pivot when diagonals vanish.

    Returns negative, zero, positive counts. No eigensolver tolerance decides
    whether the declared cutoff is exactly on the supplied mathematical spectrum.
    """
    rows = [list(row) for row in matrix]
    negative = positive = 0
    while rows:
        n = len(rows)
        pivot = next((i for i in range(n) if rows[i][i]), None)
        if pivot is not None:
            order = [pivot] + [i for i in range(n) if i != pivot]
            rows = [[rows[i][j] for j in order] for i in order]
            d = rows[0][0]
            negative += int(d < 0)
            positive += int(d > 0)
            rows = [
                [rows[i][j] - rows[i][0] * rows[0][j] / d for j in range(1, n)]
                for i in range(1, n)
            ]
        else:
            pair = next(
                ((i, j) for i in range(n) for j in range(i + 1, n) if rows[i][j]), None
            )
            if pair is None:
                return negative, n, positive
            i, j = pair
            order = [i, j] + [k for k in range(n) if k not in pair]
            rows = [[rows[i][j] for j in order] for i in order]
            b = rows[0][1]
            rows = [
                [
                    rows[i][j] - (rows[i][0] * rows[1][j] + rows[i][1] * rows[0][j]) / b
                    for j in range(2, n)
                ]
                for i in range(2, n)
            ]
            negative += 1
            positive += 1
    return negative, 0, positive


def _c_condition(matrix: Matrix, limit: float, label: str) -> FrozenJSONMap:
    """Certify a Euclidean 2-norm condition bound on these coordinates.

    SVD proposes endpoints only. Exact PSD tests on the normalized Gram matrix
    certify the endpoints, including equality. Unresolved bounds fail closed.
    """
    exact = _c_exact(matrix)
    scale = max(abs(x) for row in exact for x in row)
    if not scale:
        raise CandidateCStageError("singular", "singular " + label)
    normalized = tuple(tuple(x / scale for x in row) for row in exact)
    gram = _c_mm(_c_transpose(normalized), normalized)
    n = len(gram)
    if not any(gram[i][j] for i in range(n) for j in range(n) if i != j):
        lower, upper = (
            min(gram[i][i] for i in range(n)),
            max(gram[i][i] for i in range(n)),
        )
        if lower <= 0:
            raise CandidateCStageError("singular", "singular " + label)
    elif n == 2:
        # Squaring the exact 2x2 Gram eigenvalue ratio inequality avoids
        # deciding an equality from rounded singular-value endpoints.
        a, b, d = gram[0][0], gram[0][1], gram[1][1]
        if a * d <= b * b:
            raise CandidateCStageError("singular", "singular " + label)
        trace, discriminant = a + d, (a - d) ** 2 + 4 * b * b
        k2 = Fraction(limit) ** 2
        if k2 < 1 or (k2 - 1) ** 2 * trace**2 < (k2 + 1) ** 2 * discriminant:
            raise CandidateCStageError(
                "conditioning_failure", "conditioning limit exceeded: " + label
            )
        numerator = math.isqrt(discriminant.numerator)
        denominator = math.isqrt(discriminant.denominator)
        if (
            numerator**2 == discriminant.numerator
            and denominator**2 == discriminant.denominator
        ):
            root = Fraction(numerator, denominator)
            lower, upper = trace - root, trace + root
        else:
            lower, upper = Fraction(1), k2
    else:
        np = _dependency("numpy")
        try:
            singular = np.linalg.svd(np.array(_c_float(normalized)), compute_uv=False)
        except np.linalg.LinAlgError as exc:
            raise CandidateCStageError(
                "conditioning_failure", "conditioning decomposition failed: " + label
            ) from exc
        if not np.all(np.isfinite(singular)):
            raise CandidateCStageError(
                "nonfinite", "nonfinite conditioning decomposition: " + label
            )
        if min(singular) <= 0:
            raise CandidateCStageError(
                "conditioning_failure", "conditioning cannot resolve " + label
            )
        small, large = float(min(singular)), float(max(singular))
        for attempt in range(32):
            if attempt:
                error = math.ldexp(large, attempt - 52)
                small_bound, large_bound = small - error, large + error
            else:
                small_bound, large_bound = small, large
            if small_bound <= 0 or not math.isfinite(large_bound):
                raise CandidateCStageError(
                    "conditioning_failure", "conditioning cannot resolve " + label
                )
            lower, upper = Fraction(small_bound) ** 2, Fraction(large_bound) ** 2
            low_test = tuple(
                tuple(x - (lower if i == j else 0) for j, x in enumerate(row))
                for i, row in enumerate(gram)
            )
            high_test = tuple(
                tuple((upper if i == j else 0) - x for j, x in enumerate(row))
                for i, row in enumerate(gram)
            )
            if _c_inertia(low_test)[0] == 0 and _c_inertia(high_test)[0] == 0:
                break
        else:
            raise CandidateCStageError(
                "conditioning_failure", "conditioning certificate unresolved: " + label
            )
    bound = upper / lower
    if bound > Fraction(limit) ** 2:
        raise CandidateCStageError(
            "conditioning_failure", "conditioning limit exceeded: " + label
        )
    return FrozenJSONMap(
        {
            "block": label,
            "norm": "euclidean_2",
            "condition_upper_squared": str(bound),
            "limit": limit,
        }
    )


def _c_residual_pass(
    residual: tuple[Fraction, ...], rhs: tuple[Fraction, ...], policy: SolverPolicy
) -> bool:
    """||r||2 <= atol + rtol max(1,||rhs||2), compared without underflow."""
    r2 = sum((x * x for x in residual), Fraction())
    b2 = max(Fraction(1), sum((x * x for x in rhs), Fraction()))
    a, b = Fraction(policy.absolute_tolerance), Fraction(policy.relative_tolerance)
    excess = r2 - a * a - b * b * b2
    return excess <= 0 or excess * excess <= 4 * a * a * b * b * b2


def _c_solve(
    matrix: Matrix,
    rhs: Matrix,
    policy: SolverPolicy,
    label: str,
    certificates: list[FrozenJSONMap],
) -> Matrix:
    inverse = _c_inverse(_c_exact(matrix))
    certificates.append(_c_condition(matrix, policy.conditioning_limit, label))
    result = _c_float(_c_mm(inverse, _c_exact(rhs)))
    observed = _c_mm(_c_exact(matrix), _c_exact(result))
    for residual, target in zip(
        _c_transpose(
            tuple(
                tuple(a - b for a, b in zip(left, right, strict=True))
                for left, right in zip(observed, _c_exact(rhs), strict=True)
            )
        ),
        _c_transpose(_c_exact(rhs)),
        strict=True,
    ):
        if not _c_residual_pass(residual, target, policy):
            raise CandidateCStageError(
                "no_admitted_root", "declared residual tolerance failed: " + label
            )
    return result


def _c_components(graph: GRCV4Graph) -> tuple[tuple[int, ...], ...]:
    remaining = set(range(len(graph.live_node_ids)))
    neighbors: dict[int, set[int]] = {i: set() for i in remaining}
    for edge in graph.oriented_edges:
        i, j = graph.node_index(edge.tail_node_id), graph.node_index(edge.head_node_id)
        neighbors[i].add(j)
        neighbors[j].add(i)
    groups = []
    while remaining:
        group, queue = set(), [min(remaining)]
        while queue:
            i = queue.pop()
            if i not in group:
                group.add(i)
                queue.extend(neighbors[i] - group)
        remaining -= group
        groups.append(tuple(sorted(group)))
    return tuple(groups)


@dataclass(frozen=True, slots=True)
class CandidateCSelector:
    """Local spectral algebra for positive diagonal vertex measures.

    The shipped stage admits unit measures. Nonunit diagonal measures serve
    the frozen algebra witness; this primitive does not admit a full profile.
    """

    resource: VertexScalar
    pairings: GRCV4Pairings
    cutoff: float
    projector: Matrix = field(init=False)
    selected: VertexScalar = field(init=False)
    rank: int = field(init=False)
    certificate: FrozenJSONMap = field(init=False)

    def __post_init__(self) -> None:
        if type(self.pairings) is not GRCV4Pairings:
            raise TypeError("selector requires typed pairings")
        graph = self.pairings.vertex.graph
        _require_coordinates(self.resource, VertexScalar, graph)
        cutoff = _number(self.cutoff)
        object.__setattr__(self, "cutoff", cutoff)
        h0, h1 = self.pairings.vertex.matrix, self.pairings.one_form.matrix
        n = len(h0)
        if not n or any(h0[i][j] for i in range(n) for j in range(n) if i != j):
            raise ValueError("local C selector requires nonempty diagonal vertex Hodge")
        mu = tuple(Fraction(h0[i][i]) for i in range(n))
        incidence = _c_exact(graph.incidence)
        stiffness = _c_mm(_c_mm(incidence, _c_exact(h1)), _c_transpose(incidence))
        shifted = tuple(
            tuple(
                x - (Fraction(cutoff) * mu[i] if i == j else 0)
                for j, x in enumerate(row)
            )
            for i, row in enumerate(stiffness)
        )
        rank, zeros, _ = _c_inertia(shifted)
        if zeros:
            raise CandidateCStageError(
                "domain_failure", "selector cutoff lies on the exact spectrum"
            )
        components = _c_components(graph)
        certificate: dict[str, object] = {
            "method": "exact_generalized_shift_inertia",
            "rank": rank,
            "cutoff": cutoff,
        }
        if rank in (0, n):
            projection = tuple(
                tuple(Fraction(rank == n and i == j) for j in range(n))
                for i in range(n)
            )
        elif rank == len(components):
            # The exact weighted kernel projector avoids eigenbasis noise on
            # disconnected graphs and retains every component's zero mode.
            projection_rows = [[Fraction() for _ in range(n)] for _ in range(n)]
            for group in components:
                total = sum((mu[i] for i in group), Fraction())
                for i in group:
                    for j in group:
                        projection_rows[i][j] = mu[j] / total
            projection = tuple(tuple(row) for row in projection_rows)
        else:
            np = _dependency("numpy")
            roots = tuple(math.sqrt(float(m)) for m in mu)
            whitened = [[0.0] * n for _ in range(n)]
            for i in range(n):
                for j in range(i, n):
                    value = _computed(
                        float(stiffness[i][j] / Fraction(roots[i]) / Fraction(roots[j]))
                    )
                    whitened[i][j] = whitened[j][i] = value
            try:
                values, vectors = np.linalg.eigh(np.array(whitened))
            except np.linalg.LinAlgError as exc:
                raise CandidateCStageError(
                    "domain_failure", "selector decomposition failed"
                ) from exc
            if not np.all(np.isfinite(values)) or not np.all(np.isfinite(vectors)):
                raise CandidateCStageError(
                    "nonfinite", "nonfinite selector decomposition"
                )
            physical = tuple(
                tuple(
                    Fraction(_computed(float(vectors[i, j]) / roots[i]))
                    for j in range(n)
                )
                for i in range(n)
            )
            weighted = tuple(
                tuple(mu[i] * x for x in row) for i, row in enumerate(physical)
            )
            gram = _c_mm(_c_transpose(physical), weighted)
            defect = max(
                sum((abs(x - int(i == j)) for j, x in enumerate(row)), Fraction())
                for i, row in enumerate(gram)
            )
            residual = _c_mm(stiffness, physical)
            residual_l1 = sum(
                (
                    abs(
                        residual[i][j]
                        - mu[i] * physical[i][j] * Fraction(float(values[j]))
                    )
                    for i in range(n)
                    for j in range(n)
                ),
                Fraction(),
            )
            lower_root = math.nextafter(min(roots), 0.0)
            if defect >= 1 or lower_root <= 0 or Fraction(lower_root) ** 2 > min(mu):
                raise CandidateCStageError(
                    "domain_failure", "selector metric certificate failed"
                )
            # Polar orthonormalization bounds the difference to an orthogonal
            # diagonalization: ||R||/(1-delta) + 4||D||delta/(1-delta).
            error = (
                residual_l1 / Fraction(lower_root)
                + 4 * max(abs(Fraction(float(v))) for v in values) * defect
            ) / (1 - defect)
            gap = min(abs(Fraction(float(v)) - Fraction(cutoff)) for v in values)
            if gap <= error or sum(float(v) < cutoff for v in values) != rank:
                raise CandidateCStageError(
                    "domain_failure", "selector gap is numerically unresolved"
                )
            selected_indices = [
                j for j, value in enumerate(values) if float(value) < cutoff
            ]
            chosen = tuple(tuple(row[j] for j in selected_indices) for row in physical)
            weighted_chosen = tuple(
                tuple(mu[i] * x for x in row) for i, row in enumerate(chosen)
            )
            chosen_gram = _c_mm(_c_transpose(chosen), weighted_chosen)
            projection = _c_mm(
                _c_mm(chosen, _c_inverse(chosen_gram)), _c_transpose(weighted_chosen)
            )
            certificate.update(
                method="exact_inertia_and_generalized_eigen_residual",
                eigen_error_upper=str(error),
                gap_lower=str(gap - error),
            )
        selected = _c_float(
            _c_mm(projection, tuple((Fraction(x),) for x in self.resource.values))
        )
        object.__setattr__(self, "projector", _c_float(projection))
        object.__setattr__(
            self, "selected", VertexScalar(graph, tuple(row[0] for row in selected))
        )
        object.__setattr__(self, "rank", rank)
        object.__setattr__(self, "certificate", FrozenJSONMap(certificate))


@dataclass(frozen=True, slots=True)
class CandidateCSelectedForm:
    """Selected/retained coordinates are distinct from structural OneForm."""

    hodge: OneFormHodge
    values: tuple[float, ...]

    def __post_init__(self) -> None:
        if type(self.hodge) is not OneFormHodge:
            raise TypeError("selected form requires its typed retained Hodge")
        values = _vector(self.values)
        if len(values) != len(self.hodge.graph.live_edge_ids):
            raise ValueError("selected form coordinate count mismatch")
        object.__setattr__(self, "values", values)


@dataclass(frozen=True, slots=True)
class CandidateCReadBack:
    source_identity: str
    current: PhysicalFlux
    structural_flat: OneForm
    selected_input: CandidateCSelectedForm
    selected_response: CandidateCSelectedForm
    ungated_flat: OneForm
    causal_flat: OneForm
    flux: PhysicalFlux


@dataclass(frozen=True, slots=True)
class _CandidateCAlgebra:
    """Typed finite algebra, including the nonunit-H0 frozen witness.

    CandidateCCurrent owns complete-profile/stage admission. No candidate or
    realization authority follows from constructing this private algebra object.
    """

    transport: CandidateCTransport
    resource: VertexScalar
    pairings: GRCV4Pairings
    selector: CandidateCSelector = field(init=False)
    retained_hodge: OneFormHodge = field(init=False)
    deformation: tuple[float, ...] = field(init=False)
    potential: VertexScalar = field(init=False)
    generated_potential: VertexScalar = field(init=False)
    retained_potential_increment: VertexScalar = field(init=False)
    baseline: PhysicalFlux = field(init=False)
    identification: Matrix = field(init=False)
    inverse_identification: Matrix = field(init=False)
    flat_matrix: Matrix = field(init=False)
    physical_identification: Matrix = field(init=False)
    laplacian: Matrix = field(init=False)
    response: Matrix = field(init=False)
    flux_response: Matrix = field(init=False)
    current_block: Matrix = field(init=False)
    certificates: tuple[FrozenJSONMap, ...] = field(init=False)

    def __post_init__(self) -> None:
        if (
            type(self.transport) is not CandidateCTransport
            or type(self.pairings) is not GRCV4Pairings
        ):
            raise TypeError("C algebra requires bound transport and typed pairings")
        graph = self.transport.graph
        _require_coordinates(self.resource, VertexScalar, graph)
        if graph != self.pairings.vertex.graph:
            raise ValueError("C algebra uses foreign Hodge coordinates")
        params, policy = (
            self.transport.params,
            self.transport.profile.params_resolved.solver,
        )
        if (
            params.potential_evaluator_id
            != "quadratic_site_potential_zero_derivative_v1"
        ):
            raise ValueError("unimplemented C site potential evaluator")
        if (
            params.current_conditioning_policy_id
            != "strict_invertible_current_block_v1"
        ):
            raise ValueError("unimplemented C current conditioning policy")
        if not _fixed_current_policy(self.transport.profile):
            raise ValueError("unimplemented C fixed-geometry solver policy")
        selector = CandidateCSelector(self.resource, self.pairings, params.Lambda_C)
        # tanh of an overflowed finite-input quotient is its correctly rounded
        # saturation value; no resource clipping or retained-Hodge floor occurs.
        rho = tuple(math.tanh(t / params.C_ref) for t in selector.selected.values)
        try:
            deformation = tuple(
                math.exp(
                    _computed(0.5 * params.kappa_M_C)
                    * (
                        0.5
                        * (
                            rho[graph.node_index(e.tail_node_id)]
                            + rho[graph.node_index(e.head_node_id)]
                        )
                    )
                )
                for e in graph.oriented_edges
            )
        except OverflowError as exc:
            raise CandidateCStageError(
                "nonfinite", "nonfinite C Hodge deformation"
            ) from exc
        if any(x <= 0 for x in deformation):
            raise CandidateCStageError(
                "domain_failure", "computed C deformation must be positive"
            )
        deformation = _vector(deformation, positive=True)
        pre = self.pairings.one_form.matrix
        retained = OneFormHodge(
            graph,
            _c_float(
                tuple(
                    tuple(
                        Fraction(deformation[i])
                        * Fraction(x)
                        * Fraction(deformation[j])
                        for j, x in enumerate(row)
                    )
                    for i, row in enumerate(pre)
                )
            ),
        )
        b = _c_exact(graph.incidence)
        bt = _c_transpose(b)
        # Mathematical regularity precedes binary64 resolvent construction.
        # L is singular iff ((1-zeta*chi) I + tau Delta) is singular; a
        # rounded inverse may otherwise turn an exact zero mode into a tiny
        # nonzero one, even in a one-dimensional (condition-number-one) block.
        exact_laplacian = _c_mm(
            _c_mm(_c_mm(bt, _c_inverse(_c_exact(self.pairings.vertex.matrix))), b),
            _c_exact(retained.matrix),
        )
        beta = Fraction(params.zeta_C) * Fraction(params.chi_C)
        regularity_block = tuple(
            tuple(
                (1 - beta) * int(i == j) + Fraction(params.tau_C) * x
                for j, x in enumerate(row)
            )
            for i, row in enumerate(exact_laplacian)
        )
        _c_inverse(regularity_block)
        gradient = _c_mm(bt, tuple((Fraction(c),) for c in self.resource.values))

        def potential(hodge: Matrix) -> _CExact:
            return tuple(
                tuple(Fraction(params.kappa_Phi_C) * x for x in row)
                for row in _c_mm(_c_mm(b, _c_exact(hodge)), gradient)
            )

        phi, generated = potential(retained.matrix), potential(pre)
        phi_values = tuple(row[0] for row in _c_float(phi))
        baseline = _c_float(
            tuple(
                tuple(-Fraction(m) * x for x in row)
                for m, row in zip(
                    self.transport.mobility.diagonal,
                    _c_mm(bt, tuple((Fraction(x),) for x in phi_values)),
                    strict=True,
                )
            )
        )
        certificates: list[FrozenJSONMap] = []
        eye = _c_eye(len(pre))
        flat = _c_solve(pre, eye, policy, "structural flat map", certificates)
        ident = tuple(
            zip(
                *_c_solve(
                    pre,
                    tuple(zip(*retained.matrix, strict=True)),
                    policy,
                    "pre-to-retained identification",
                    certificates,
                ),
                strict=True,
            )
        )
        inverse_ident = _c_solve(
            ident, eye, policy, "inverse retained identification", certificates
        )
        q = _c_product(ident, flat)
        h0_inverse_b = _c_solve(
            self.pairings.vertex.matrix,
            graph.incidence,
            policy,
            "vertex Hodge inverse",
            certificates,
        )
        laplacian = _c_product(
            tuple(zip(*graph.incidence, strict=True)),
            _c_product(h0_inverse_b, retained.matrix),
        )
        resolvent_block = _c_float(
            tuple(
                tuple(
                    Fraction(i == j) + Fraction(params.tau_C) * Fraction(x)
                    for j, x in enumerate(row)
                )
                for i, row in enumerate(laplacian)
            )
        )
        response = _c_solve(
            resolvent_block, eye, policy, "retained resolvent", certificates
        )
        flux_response = (
            eye
            if params.tau_C == 0
            else _c_solve(
                q,
                _c_product(response, q),
                policy,
                "physical Q_C similarity",
                certificates,
            )
        )
        if params.tau_C == 0:
            certificates.append(
                _c_condition(
                    q, policy.conditioning_limit, "physical Q_C identification"
                )
            )
        current_block = _c_float(
            tuple(
                tuple(
                    Fraction(i == j)
                    - Fraction(params.zeta_C) * Fraction(params.chi_C) * Fraction(x)
                    for j, x in enumerate(row)
                )
                for i, row in enumerate(flux_response)
            )
        )
        # Condition the actual physical block, never a retained-space margin.
        _c_inverse(_c_exact(current_block))
        certificates.append(
            _c_condition(
                current_block, policy.conditioning_limit, "physical total-current block"
            )
        )
        for name, value in {
            "selector": selector,
            "retained_hodge": retained,
            "deformation": deformation,
            "potential": VertexScalar(graph, phi_values),
            "generated_potential": VertexScalar(
                graph, tuple(row[0] for row in _c_float(generated))
            ),
            "retained_potential_increment": VertexScalar(
                graph,
                tuple(
                    row[0]
                    for row in _c_float(
                        tuple(
                            tuple(a - b for a, b in zip(left, right, strict=True))
                            for left, right in zip(phi, generated, strict=True)
                        )
                    )
                ),
            ),
            "baseline": PhysicalFlux(graph, tuple(row[0] for row in baseline)),
            "identification": ident,
            "inverse_identification": inverse_ident,
            "flat_matrix": flat,
            "physical_identification": q,
            "laplacian": laplacian,
            "response": response,
            "flux_response": flux_response,
            "current_block": current_block,
            "certificates": tuple(certificates),
        }.items():
            object.__setattr__(self, name, value)

    def read_back(
        self, current: PhysicalFlux, source_identity: str
    ) -> CandidateCReadBack:
        graph, params = self.transport.graph, self.transport.params
        _require_coordinates(current, PhysicalFlux, graph)
        flat = OneForm(graph, _c_apply(self.flat_matrix, current.values))
        selected = CandidateCSelectedForm(
            self.retained_hodge, _c_apply(self.identification, flat.values)
        )
        response = CandidateCSelectedForm(
            self.retained_hodge, _c_apply(self.response, selected.values)
        )
        ungated = (
            flat
            if params.tau_C == 0
            else OneForm(graph, _c_apply(self.inverse_identification, response.values))
        )
        causal = OneForm(
            graph, tuple(_computed(params.chi_C * x) for x in ungated.values)
        )
        flux = (
            PhysicalFlux(
                graph, tuple(_computed(params.chi_C * x) for x in current.values)
            )
            if params.tau_C == 0
            else PhysicalFlux(
                graph, _c_apply(self.pairings.one_form.matrix, causal.values)
            )
        )
        return CandidateCReadBack(
            source_identity, current, flat, selected, response, ungated, causal, flux
        )


@dataclass(frozen=True, slots=True)
class CandidateCCurrent:
    """Fresh fixed-h current at a declared stage; no continuity or commit.

    The full inputs bind current/reset, geometry, profile, context, stage and
    iteration. Trial J is a residual operand, never a baseline/selector input.
    """

    inputs: GeometryStageInputs
    algebra: _CandidateCAlgebra = field(init=False)
    current: PhysicalFlux = field(init=False)
    read: CandidateCReadBack = field(init=False)
    closure_residual_squared: str = field(init=False)

    def __post_init__(self) -> None:
        if type(self.inputs) is not GeometryStageInputs:
            raise TypeError("C current requires exact typed stage inputs")
        ref = self.inputs.geometry.reference
        profile = ref.profile
        common = profile.params_resolved.common
        if (
            profile.identity_payload.candidate != "C"
            or common.domain_id != "fixed_graph_strict_gap_spd_v1"
            or common.gauge_id != "component_zero_mean_potential_v1"
            or common.normalization_id != "unnormalized_vertex_stiffness_v1"
            or not _fixed_current_policy(profile)
        ):
            raise ValueError("unimplemented C current/profile declaration")
        transport = CandidateCTransport(ref.graph, profile)
        algebra = _CandidateCAlgebra(
            transport,
            VertexScalar(ref.graph, self.inputs.current.C),
            self.inputs.geometry.pairings,
        )
        policy = profile.params_resolved.solver
        result = _c_solve(
            algebra.current_block,
            tuple((x,) for x in algebra.baseline.values),
            policy,
            "physical current solve",
            [],
        )
        current = PhysicalFlux(ref.graph, tuple(row[0] for row in result))
        read = algebra.read_back(current, self.identity)
        residual = tuple(
            Fraction(j) - Fraction(j0) - Fraction(transport.params.zeta_C) * Fraction(r)
            for j, j0, r in zip(
                current.values, algebra.baseline.values, read.flux.values, strict=True
            )
        )
        if not _c_residual_pass(
            residual, tuple(Fraction(x) for x in algebra.baseline.values), policy
        ):
            raise CandidateCStageError(
                "no_admitted_root", "physical read-back closure residual failed"
            )
        object.__setattr__(self, "algebra", algebra)
        object.__setattr__(self, "current", current)
        object.__setattr__(self, "read", read)
        object.__setattr__(
            self,
            "closure_residual_squared",
            str(sum((x * x for x in residual), Fraction())),
        )

    @property
    def identity(self) -> str:
        return _identity("grcv4-c-fixed-stage-sha256", self.to_payload())

    def read_back(self, current: PhysicalFlux) -> CandidateCReadBack:
        return self.algebra.read_back(current, self.identity)

    def to_payload(self) -> dict[str, JSONValue]:
        return {
            "descriptor_version": "grcv4-c-fixed-stage-v1",
            "numerics": C_STAGE_NUMERICS,
            "inputs": self.inputs.to_payload(),
        }

    def to_canonical_bytes(self) -> bytes:
        return canonical_json_bytes(self.to_payload())

    @classmethod
    def from_payload(cls, value: object) -> CandidateCCurrent:
        data = json_value(value)
        if (
            not isinstance(data, dict)
            or set(data) != {"descriptor_version", "numerics", "inputs"}
            or data["descriptor_version"] != "grcv4-c-fixed-stage-v1"
            or data["numerics"] != C_STAGE_NUMERICS
        ):
            raise V4SchemaError("expected exact C current reconstruction inputs")
        return cls(GeometryStageInputs.from_payload(data["inputs"]))

    @classmethod
    def from_canonical_bytes(cls, data: bytes | str) -> CandidateCCurrent:
        return cls.from_payload(decode_canonical_json(data))

"""Native exact-rational C_OS quartic map with conservative represented output.

This bounded numerical kernel is not a completion detector or lifecycle owner.
It uses production typed graphs/profile identities and contains no research imports.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache

from .grc_v4_codec import canonical_json_bytes
from .grc_v4_geometry import GRCV4Graph
from .grc_v4_exact import exact_number, _flint_module
from . import grc_v4_numerics as numerics
from .grc_v4_certification import CertificationInconclusive
from .grc_v4_spark_state import (
    ExactResources, QuarticCOSProfile, FLUX_BITS, NUMERICAL_POLICY,
    rational, round_flux, flint_operation,
)


def _matrix(rows):
    return _flint_module().fmpq_mat([[rational(x) for x in row] for row in rows])


def _inverse(matrix):
    """Use the shared exact inverse boundary, including operation-owned reuse."""
    return _flint_module().fmpq_mat(numerics.inverse(numerics.exact_matrix(matrix.tolist())))


def _rows(matrix):
    return tuple(tuple(str(matrix[i, j]) for j in range(matrix.ncols())) for i in range(matrix.nrows()))


def _norm_inf(matrix):
    return max((sum(abs(matrix[i, j]) for j in range(matrix.ncols())) for i in range(matrix.nrows())), default=0)


def _binary64(value):
    """The exact declared binary64 operand, not its decimal approximation."""
    return exact_number(value)


@lru_cache(maxsize=16)
@flint_operation
def _reference_facts(graph_bytes):
    fmpq, fmpq_mat = exact_number, _flint_module().fmpq_mat
    from .grc_v4_codec import decode_canonical_json

    graph = GRCV4Graph.from_payload(decode_canonical_json(graph_bytes))
    n, m = len(graph.live_node_ids), len(graph.oriented_edges)
    if not 2 <= n <= 32 or not 1 <= m <= 64:
        raise ValueError("bounded spark graph size exceeded")
    B = fmpq_mat([[int(edge.tail_node_id == node)-int(edge.head_node_id == node)
                   for edge in graph.oriented_edges] for node in graph.live_node_ids])
    adjacency = [set() for _ in range(n)]
    for edge in graph.oriented_edges:
        i, j = graph.node_index(edge.tail_node_id), graph.node_index(edge.head_node_id)
        if i == j:
            raise ValueError("loop-free spark graph required")
        adjacency[i].add(j); adjacency[j].add(i)
    diameter = 0
    for start in range(n):
        distance, todo = {start: 0}, [start]
        for i in todo:
            for j in sorted(adjacency[i] - distance.keys()):
                distance[j] = distance[i]+1; todo.append(j)
        if len(distance) != n:
            raise ValueError("connected spark graph required")
        diameter = max(diameter, max(distance.values()))
    gap = fmpq(2, (n-1)*diameter)
    if gap <= fmpq(1, 64):
        raise CertificationInconclusive("constant-selector separation unproved")
    I = fmpq_mat([[int(i == j) for j in range(m)] for i in range(m)])
    L = B.transpose()*B
    A = 3*I/4+L
    inverse = _inverse(A)
    if A*inverse != I:
        raise ArithmeticError("reference inverse identity failed")
    O = fmpq_mat([[sum(abs(B[k, i]*B[k, j]) for k in range(n)) for j in range(m)] for i in range(m)])
    # Cache immutable rational tuples only; no current/state/admission cache.
    return _rows(B), _rows(I), _rows(L), _rows(O), _rows(inverse), str(gap)


@dataclass(frozen=True, slots=True)
class SparkCOSStep:
    before: ExactResources
    after: ExactResources
    profile_id: str
    duration: str
    flux: tuple[str, ...]
    exact_current: tuple[str, ...]
    componentwise_error_bounds: tuple[str, ...]
    split_frobenius_squared: str
    predictor_flat: tuple[str, ...]
    selected_geometry: tuple[tuple[str, ...], ...]
    final_current: tuple[str, ...]
    reference_current: tuple[str, ...]
    numerical_policy_id: str = field(default=NUMERICAL_POLICY, init=False)


@dataclass(frozen=True, slots=True)
class SparkCOSKernel:
    """A bounded, explicit equation/representation binding, no hidden fallback."""
    graph: GRCV4Graph
    profile: QuarticCOSProfile
    _B: tuple = field(init=False, repr=False)
    _I: tuple = field(init=False, repr=False)
    _L: tuple = field(init=False, repr=False)
    _O: tuple = field(init=False, repr=False)
    _inverse: tuple = field(init=False, repr=False)
    selector_gap_lower: str = field(init=False)

    @flint_operation
    def __post_init__(self):
        from .grc_v4_geometry import GRCV4ReferenceGeometry, GRCV4Context
        from .grc_v4_state import FrozenJSONMap
        from .grc_v4_candidate_c import CandidateCTransport

        graph, profile = self.graph, self.profile
        if type(graph) is not GRCV4Graph or type(profile) is not QuarticCOSProfile:
            raise TypeError("typed graph and quartic C_OS profile required")
        if not 2 <= len(graph.live_node_ids) <= 32 or not 1 <= len(graph.oriented_edges) <= 64:
            raise ValueError("bounded spark graph size exceeded")
        if (profile.site.c0, profile.site.a, profile.site.mu) != ("2", "1", "1"):
            raise ValueError("kernel supports the declared c0=2, a=mu=1 slice")
        p = profile.baseline.params_resolved
        expected = dict(Lambda_C=1/64, kappa_M_C=0, kappa_Phi_C=1/64, eta_C=1/1024,
                        tau_C=1, chi_C=1/2, zeta_C=1/2)
        if any(getattr(p.candidate, k) != v for k, v in expected.items()):
            raise ValueError("unsupported quartic C_OS parameters")
        if set(p.candidate.W_C_tr) != set(graph.live_edge_ids) or any(x != 1 for x in p.candidate.W_C_tr.values()):
            raise ValueError("unit transport weights on the actual graph required")
        if p.geometry.kappa_H != 1/2 or p.realization.tolerance != 1e-11:
            raise ValueError("unsupported geometry gain or OS split tolerance")
        common = p.common
        if (common.domain_id != "fixed_graph_strict_gap_spd_v1" or
                common.gauge_id != "component_zero_mean_potential_v1" or
                common.normalization_id != "unnormalized_vertex_stiffness_v1" or
                p.realization.split_residual_norm_id != "edge_l2_v1" or
                profile.baseline.identity_payload.solver_id != "direct_unique_root_v1" or
                p.solver.solver_kind != "direct" or
                p.solver.residual_norm_id != "edge_l2_v1"):
            raise ValueError("unsupported domain, gauge, split norm or solve policy")
        # Reuse the native reference/transport owners to validate all recipe IDs,
        # actual graph coverage, zero K4 and both unit-Hodge content bindings.
        # These constructors do not execute the predecessor's site or charge law.
        m = len(graph.oriented_edges)
        GRCV4ReferenceGeometry(graph, profile.baseline,
            GRCV4Context("constant_zero_context_v1", FrozenJSONMap({})),
            tuple((0.0,)*m for _ in range(m)),
            FrozenJSONMap({e: 1 for e in graph.live_edge_ids}))
        CandidateCTransport(graph, profile.baseline)
        facts = _reference_facts(canonical_json_bytes(graph.to_payload()))
        for key, value in zip(("_B", "_I", "_L", "_O", "_inverse", "selector_gap_lower"), facts, strict=True):
            object.__setattr__(self, key, value)

    @staticmethod
    def cache_info():
        return _reference_facts.cache_info()._asdict()

    def _operators(self, H, reference=False):
        I, L = _matrix(self._I), _matrix(self._L)
        A = 3*I/4+H*L
        inverse = _matrix(self._inverse) if reference else _inverse(A)
        if A*inverse != I:
            raise ArithmeticError("current inverse certificate failed")
        # ||A||2 ||A^-1||2 <= sqrt(m)||A||inf sqrt(m)||A^-1||inf.
        condition_bound = A.nrows()*_norm_inf(A)*_norm_inf(inverse)
        limit = _binary64(self.profile.baseline.params_resolved.solver.conditioning_limit)
        if condition_bound > limit or H.nrows()*_norm_inf(H) > limit:
            raise CertificationInconclusive("declared current conditioning limit not certified")
        flat_inverse = I if reference else _inverse(H)
        if H*flat_inverse != I:
            raise ArithmeticError("flat inverse certificate failed")
        return A, inverse, flat_inverse

    def _read(self, C, H, operators):
        fmpq_mat = _flint_module().fmpq_mat

        B = _matrix(self._B)
        derivative = fmpq_mat([[self.profile.site.evaluate(str(C[i, 0]))[1]] for i in range(C.nrows())])
        potential = B*H*B.transpose()*C/64-derivative
        j0 = -B.transpose()*potential/1024
        A, inverse, flat_inverse = operators
        y = inverse*j0
        if A*y != j0:
            raise ArithmeticError("exact current residual failed")
        flat = flat_inverse*y/2
        if 2*H*flat != y:
            raise ArithmeticError("exact flat residual failed")
        return j0+y/4, flat

    @flint_operation
    @numerics.matrix_operation()
    def reference_read(self, state: ExactResources):
        """A fresh fixed-reference read, including unchanged reset-role inputs."""
        fmpq_mat = _flint_module().fmpq_mat
        if type(state) is not ExactResources or state.graph != self.graph:
            raise ValueError("actual graph-bound exact resources required")
        I = _matrix(self._I)
        current, flat = self._read(fmpq_mat([[rational(x)] for x in state.C]), I,
                                   self._operators(I, reference=True))
        return tuple(map(str, current.entries())), tuple(map(str, flat.entries()))

    def _geometry(self, flat):
        fmpq_mat = _flint_module().fmpq_mat

        I, O = _matrix(self._I), _matrix(self._O)
        m = flat.nrows()
        return I+fmpq_mat([[flat[i, 0]*O[i, j]*flat[j, 0]/8 for j in range(m)] for i in range(m)])

    def _selected_stage(self, state):
        fmpq_mat = _flint_module().fmpq_mat
        if type(state) is not ExactResources or state.graph != self.graph:
            raise ValueError("actual graph-bound exact resources required")
        C = fmpq_mat([[rational(x)] for x in state.C])
        I = _matrix(self._I)
        reference_operators = self._operators(I, reference=True)
        _, predictor = self._read(C, I, reference_operators)
        H = self._geometry(predictor)
        selected_operators = self._operators(H)
        current, corrector = self._read(C, H, selected_operators)
        defect = H-self._geometry(corrector)
        split = sum(x*x for x in defect.entries())
        # Frobenius is a sufficient upper bound on the selected operator norm.
        if split > _binary64(self.profile.baseline.params_resolved.realization.tolerance)**2:
            raise CertificationInconclusive("OS split not certified at unchanged tolerance")
        return C, I, reference_operators, predictor, H, selected_operators, current, split

    @flint_operation
    @numerics.matrix_operation()
    def readmission(self, state: ExactResources):
        """Fresh predictor/corrector/domain/split admission without continuity."""
        _, _, _, _, _, _, current, split = self._selected_stage(state)
        return tuple(map(str, current.entries())), str(split)

    @flint_operation
    @numerics.matrix_operation()
    def step(self, state: ExactResources, duration: str = "32"):
        fmpq, fmpq_mat = exact_number, _flint_module().fmpq_mat
        if rational(duration) != 32:
            raise ValueError("this numerical binding selects duration 32")
        C, I, reference_operators, predictor, H, selected_operators, current, split = self._selected_stage(state)
        flux = tuple(str(round_flux(x)) for x in current.entries())
        after = state.advance(flux, duration)
        B = _matrix(self._B)
        bounds = tuple(str(32*sum(abs(B[i, j]) for j in range(B.ncols())) / fmpq(1 << (FLUX_BITS+1))) for i in range(B.nrows()))
        ideal = C-32*B*current
        for i, (value, bound) in enumerate(zip(after.C, bounds, strict=True)):
            if abs(rational(value)-ideal[i, 0]) > rational(bound):
                raise ArithmeticError("full-step error certificate failed")
        # Reuse only this step's already verified operator inverses. Read the
        # new resource state freshly in consumed and restart geometries.
        C_after = fmpq_mat([[rational(x)] for x in after.C])
        final, _ = self._read(C_after, H, selected_operators)
        restart, _ = self._read(C_after, I, reference_operators)
        return SparkCOSStep(state, after, self.profile.complete_profile_id, duration, flux,
                            tuple(map(str, current.entries())), bounds, str(split),
                            tuple(map(str, predictor.entries())), _rows(H),
                            tuple(map(str, final.entries())), tuple(map(str, restart.entries())))

    @flint_operation
    def uniform_rounding_bound(self, charge_chart, margin: str):
        """Numerical bound only; the caller must admit the actual trap/metric.

For every exact admitted input, all read arithmetic is rational. Only final
flux rounding contributes: ||U(T_hat-T)||inf <= h ||UB||inf 2^-129.
"""
        fmpq = exact_number

        U, B = _matrix(charge_chart), _matrix(self._B)
        if U.ncols() != B.nrows() or U.nrows() != B.nrows()-1:
            raise ValueError("complete charge-tangent chart dimensions required")
        error = 32*_norm_inf(U*B)/fmpq(1 << (FLUX_BITS+1))
        if not 0 < error < rational(margin):
            raise CertificationInconclusive("uniform represented error must be below strict image margin")
        return dict(numerical_policy_id=NUMERICAL_POLICY, full_step_error=str(error),
                    image_margin=margin, exact_charge_preserved=True,
                    condition="exact equation/stage admission and independently validated trap/chart",
                    completion_admitted=False)

"""Native A_OS: exact C/W, certified OS reads and an atomic log-law writer."""

from dataclasses import dataclass, field
from hashlib import sha256

from .grc_v4_certification import _ARB_CONTEXT_LOCK
from .grc_v4_codec import canonical_json_bytes
from .grc_v4_exact import _flint_module, exact_number
from .grc_v4_geometry import GRCV4Context, GRCV4Graph, GRCV4ReferenceGeometry
from .grc_v4_spark_aos_math import AOSMath
from .grc_v4_spark_conductance import (
    AOS_NUMERICAL_POLICY,
    ExactConductanceState,
    QuarticAOSProfile,
    _fixed_rows,
    descriptor_identity,
)
from .grc_v4_spark_cos import _matrix, _reference_facts
from .grc_v4_spark_cpc import _decay, interval, intervals, need, norm
from .grc_v4_spark_state import ExactResources, flint_operation, rational, round_flux
from .grc_v4_state import FrozenJSONMap

PRECISION = 256
CURRENT_BITS = 192
CONDUCTANCE_BITS = 192
WRITER_BITS = 224


def _vector(values):
    return _flint_module().arb_mat([[rational(x)] for x in values])


def _midpoints(values, bits, label):
    epsilon = exact_number(1, 1 << bits)
    result = []
    for x in values.entries():
        mid = x.mid().fmpq()
        need(
            max(mid - x.lower().fmpq(), x.upper().fmpq() - mid) <= epsilon,
            label + " enclosure exceeds midpoint budget",
        )
        result.append(str(mid))
    return tuple(result)


@dataclass(frozen=True, slots=True)
class SparkAOSStep:
    before: ExactConductanceState
    after: ExactConductanceState
    profile_id: str
    duration: str
    flux: tuple[str, ...]
    componentwise_error_bounds: tuple[str, ...]
    log_conductance_component_error: str
    consumed_read: FrozenJSONMap
    writer: FrozenJSONMap
    restart_read: FrozenJSONMap
    final_current: tuple
    reference_current: tuple
    numerical_policy_id: str = field(default=AOS_NUMERICAL_POLICY, init=False)


@dataclass(frozen=True, slots=True)
class SparkAOSKernel:
    graph: GRCV4Graph
    profile: QuarticAOSProfile
    _B: tuple = field(init=False, repr=False)
    selector_gap_lower: str = field(init=False)

    @flint_operation
    def __post_init__(self):
        if (
            type(self.graph) is not GRCV4Graph
            or type(self.profile) is not QuarticAOSProfile
        ):
            raise TypeError("typed graph and explicit quartic A_OS profile required")
        if (self.profile.site.c0, self.profile.site.a, self.profile.site.mu) != (
            "2",
            "1",
            "1",
        ):
            raise ValueError("declared quartic coefficients required")
        p = self.profile.baseline.params_resolved
        expected = {
            "eta": 1 / 1024,
            "kappa_c": 1 / 64,
            "kappa_Ah": 1 / 64,
            "chi_A": 1 / 2,
            "zeta_A": 1 / 2,
            "alpha": 1 / 32768,
            "beta": 1 / 32768,
            "gamma": 1 / 32768,
            "W_floor": 1 / 2,
            "tau_A": 32,
        }
        if any(getattr(p.candidate, k) != v for k, v in expected.items()):
            raise ValueError("unsupported A_OS coefficients")
        if (
            p.candidate.descriptor_backend_id != descriptor_identity(self.graph)
            or p.candidate.conductance_evaluator_id != "curvature_disabled_G_W_v1"
            or p.geometry.kappa_H != 1 / 2
            or p.realization.tolerance != 1e-11
            or p.realization.predictor_policy_id != "reference_geometry_predictor_v1"
            or p.realization.corrector_policy_id != "one_fresh_geometry_corrector_v1"
            or p.realization.split_residual_norm_id != "edge_l2_v1"
            or p.solver.solver_kind != "direct"
            or p.solver.root_selector_id != "unique_admitted_root_v1"
            or p.solver.residual_norm_id != "edge_l2_v1"
            or p.solver.failure_policy_id != "fail_closed_no_fallback_v1"
            or self.profile.baseline.identity_payload.solver_id
            != "direct_unique_root_v1"
            or p.common.domain_id != "fixed_graph_strict_gap_spd_v1"
            or p.common.gauge_id != "component_zero_mean_potential_v1"
            or p.common.normalization_id != "unnormalized_vertex_stiffness_v1"
        ):
            raise ValueError("unsupported A_OS descriptor, domain or solve policy")
        m = len(self.graph.oriented_edges)
        GRCV4ReferenceGeometry(
            self.graph,
            self.profile.baseline,
            GRCV4Context("constant_zero_context_v1", FrozenJSONMap({})),
            tuple((0.0,) * m for _ in range(m)),
            FrozenJSONMap({e: 1 for e in self.graph.live_edge_ids}),
        )
        facts = _reference_facts(canonical_json_bytes(self.graph.to_payload()))
        object.__setattr__(self, "_B", facts[0])
        object.__setattr__(self, "selector_gap_lower", facts[-1])

    @property
    def precision_bits(self):
        return PRECISION

    @staticmethod
    def cache_info():
        return {
            "graph": _reference_facts.cache_info()._asdict(),
            "rows": _fixed_rows.cache_info()._asdict(),
            "decay": _decay.cache_info()._asdict(),
        }

    def _subject(self, state):
        need(
            type(state) is ExactConductanceState and state.graph == self.graph,
            "complete actual C/W subject required",
        )
        need(all(0 <= rational(x) <= 4 for x in state.C), "A_OS resource box")
        need(
            all(
                rational("99/100") < rational(w) < rational("101/100")
                for w in state.W_A
            ),
            "A_OS conductance box",
        )
        need(
            rational(self.selector_gap_lower) * min(map(rational, state.W_A))
            > rational("1/64"),
            "weighted selector separation unresolved",
        )

    def _admitted_read(self, state):
        self._subject(state)
        math = AOSMath(self.graph)
        C, W = _vector(state.C), _vector(state.W_A)
        L = _flint_module().arb_mat([[x.log()] for x in W.entries()])
        read = math.os_read(C, L, W)
        need(
            read["split_upper"]
            < _flint_module().arb(
                exact_number(
                    self.profile.baseline.params_resolved.realization.tolerance
                )
            ),
            "unchanged OS split tolerance",
        )
        H = read["geometry"]
        condition = math.m * norm(H) * norm(H.inv())
        need(
            condition
            < exact_number(
                self.profile.baseline.params_resolved.solver.conditioning_limit
            ),
            "A_OS flat conditioning unresolved",
        )
        read.update(
            subject_digest=sha256(state.to_canonical_bytes()).hexdigest(),
            current_midpoint=_midpoints(
                read["corrector"]["current"], CURRENT_BITS, "A_OS current"
            ),
            conditioning_upper=condition,
        )
        need(
            all(abs(x) < 1 for x in read["corrector"]["current"].entries()),
            "A_OS current envelope",
        )
        return read

    def read_payload(self, read):
        return FrozenJSONMap(
            {
                "numerical_policy_id": AOS_NUMERICAL_POLICY,
                "precision_bits": PRECISION,
                "subject_digest": read["subject_digest"],
                "current_midpoint": list(read["current_midpoint"]),
                "H": intervals(read["geometry"]),
                "predictor": {k: intervals(v) for k, v in read["predictor"].items()},
                "corrector": {k: intervals(v) for k, v in read["corrector"].items()},
                "split_upper": str(read["split_upper"].upper().fmpq()),
                "conditioning_upper": str(read["conditioning_upper"].upper().fmpq()),
            }
        )

    @flint_operation
    def readmission(self, state):
        with _ARB_CONTEXT_LOCK, _flint_module().ctx.workprec(PRECISION):
            return self.read_payload(self._admitted_read(state))

    def _writer(self, state, after_resources, read):
        need(
            read["subject_digest"] == sha256(state.to_canonical_bytes()).hexdigest(),
            "stale A_OS writer subject",
        )
        need(
            after_resources.graph == self.graph
            and after_resources.charge == state.charge,
            "writer final resource subject",
        )
        math = AOSMath(self.graph)
        C = _vector(after_resources.C)
        need(all(0 <= x <= 4 for x in C.entries()), "writer final resource box")
        exponent, _ = math.exponent(C, read["_W"], read["corrector"]["current"])
        L = math.decay * read["_L"] + (1 - math.decay) * exponent
        ideal = math.exp(L)
        midpoint = _midpoints(ideal, WRITER_BITS, "A_OS conductance writer")
        weights = tuple(str(round_flux(rational(x) * 2**64) / 2**64) for x in midpoint)
        need(
            all(math.q(99, 100) < x < math.q(101, 100) for x in ideal.entries()),
            "ideal writer conductance box",
        )
        return weights, FrozenJSONMap(
            {
                "consumed_state_digest": read["subject_digest"],
                "final_resource_digest": sha256(
                    after_resources.to_canonical_bytes()
                ).hexdigest(),
                "incoming_W": list(state.W_A),
                "selected_current": intervals(read["corrector"]["current"]),
                "exponent": intervals(exponent),
                "decay": interval(math.decay),
                "ideal": intervals(ideal),
                "midpoint": list(midpoint),
            }
        )

    @flint_operation
    def step(self, state, duration="32"):
        if rational(duration) != 32:
            raise ValueError("A_OS requires duration 32")
        f = _flint_module()
        with _ARB_CONTEXT_LOCK, f.ctx.workprec(PRECISION):
            read = self._admitted_read(state)
            flux = tuple(str(round_flux(rational(x))) for x in read["current_midpoint"])
            resources = ExactResources.advance(state, flux, duration)
            ideal_C = (
                _vector(state.C)
                - 32 * f.arb_mat(_matrix(self._B)) * read["corrector"]["current"]
            )
            need(
                all(0 <= x <= 4 for x in ideal_C.entries()),
                "ideal resource endpoint box",
            )
            weights, writer = self._writer(state, resources, read)
            after = state.advance_conductance(flux, duration, weights)
            need(after.C == resources.C, "atomic C/W resource mismatch")
            restart = self._admitted_read(after)
            math = AOSMath(self.graph)
            final = math.read(_vector(after.C), _vector(state.W_A), read["geometry"])
            reference = math.read(_vector(after.C), _vector(after.W_A), math.I)
            errors, log_error = self.coordinate_error_bounds()
            return SparkAOSStep(
                state,
                after,
                self.profile.complete_profile_id,
                duration,
                flux,
                tuple(map(str, errors)),
                str(log_error),
                self.read_payload(read),
                writer,
                self.read_payload(restart),
                tuple(tuple(interval(x)) for x in final["current"].entries()),
                tuple(tuple(interval(x)) for x in reference["current"].entries()),
            )

    @flint_operation
    def coordinate_error_bounds(self):
        B = _matrix(self._B)
        epsilon = exact_number(1, 1 << 129) + exact_number(1, 1 << CURRENT_BITS)
        resource = tuple(
            32 * sum(abs(B[i, j]) for j in range(B.ncols())) * epsilon
            for i in range(B.nrows())
        )
        # In [0,4], each weighted row has range [-4,4] and C-derivative
        # l1 norm <=2. A row difference has norm <=4 and magnitude <=8.
        # Thus ||d_C log G||_1 <= (2+3*2*8*4)/65536 = 194/65536.
        # Use (1-exp(-1)) < 1; the writer consumes represented final C.
        propagated = exact_number(194, 65536) * max(resource)
        rounded = exact_number(100, 99) * (
            exact_number(1, 1 << 193) + exact_number(1, 1 << WRITER_BITS)
        )
        return resource, propagated + rounded

    @flint_operation
    def uniform_rounding_bound(self, chart, margin):
        U = _matrix(chart)
        n, m = len(self.graph.live_node_ids), len(self.graph.live_edge_ids)
        if (U.nrows(), U.ncols()) != (n - 1 + m, n + m):
            raise ValueError("complete C/logW chart required")
        resource, history = self.coordinate_error_bounds()
        errors = (*resource, *((history,) * m))
        bound = max(
            sum(abs(U[i, j]) * errors[j] for j in range(n + m))
            for i in range(n - 1 + m)
        )
        need(0 < bound < rational(margin), "full C/logW error exceeds image margin")
        return {
            "full_step_error": str(bound),
            "resource_component_errors": list(map(str, resource)),
            "log_conductance_component_error": str(history),
            "writer_resource_propagation_included": True,
            "exact_charge_preserved": True,
            "numerical_policy_id": AOS_NUMERICAL_POLICY,
        }

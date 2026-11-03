"""Native exact C/W A_RG2b steps; the joint invariant section has no history."""

from dataclasses import dataclass, field
from functools import lru_cache
from hashlib import sha256

from flint import arb, arb_mat, ctx, fmpq

from .grc_v4_certification import _ARB_CONTEXT_LOCK
from .grc_v4_codec import canonical_json_bytes, decode_canonical_json
from .grc_v4_geometry import GRCV4Context, GRCV4Graph, GRCV4ReferenceGeometry
from .grc_v4_spark_aos import SparkAOSKernel, _midpoints
from .grc_v4_spark_arg2b_math import (
    APPROXIMATION_ID,
    COMPLETION_ID,
    DOMAIN_ID,
    ERROR_NORM,
    LIP,
    PRECISION,
    PROPOSAL_BITS,
    RHO,
    SCALE,
    ARG2bMath,
    global_domain,
)
from .grc_v4_spark_conductance import (
    ARG2B_NUMERICAL_POLICY,
    ExactConductanceState,
    QuarticARG2bProfile,
    _fixed_rows,
    descriptor_identity,
)
from .grc_v4_spark_cos import _matrix, _reference_facts
from .grc_v4_spark_crg2b import intervals, matrix_ball
from .grc_v4_spark_crg2b_math import ball, exact_bounds, maxnorm, need
from .grc_v4_spark_state import ExactResources, flint_operation, rational, round_flux
from .grc_v4_state import FrozenJSONMap

CURRENT_BITS = 192
WRITER_BITS = 224


def vector(values):
    return arb_mat([[fmpq(x)] for x in values])


@lru_cache(maxsize=8)
def _section_witness(graph_bytes, profile_bytes, state_bytes, precision):
    with _ARB_CONTEXT_LOCK, ctx.workprec(precision):
        graph = GRCV4Graph.from_payload(decode_canonical_json(graph_bytes))
        state = ExactConductanceState.from_canonical_bytes(state_bytes)
        m = ARG2bMath(graph)
        C, W = vector(state.C), vector(state.W_A)
        L = arb_mat([[x.log()] for x in W.entries()])
        X = m.pack(C, L)
        need(m.in_agreement(X), "full exact C/logW subject outside agreement")
        scale = 2**PROPOSAL_BITS
        qs = [x.mid().fmpq() for x in X.entries()]
        point = arb_mat(
            [[fmpq((q.numerator * scale) // q.denominator, scale)] for q in qs]
        )
        selected = m.section(point, retain_chain=True)
        shift = maxnorm(X - point)
        error = (selected["error"] + ball(LIP) * shift).upper()
        H = arb_mat(m.m, m.m)
        for i in range(m.m):
            for j in range(i, m.m):
                if m.overlap[i][j]:
                    H[i, j] = H[j, i] = arb(
                        selected["proposal"][i, j].fmpq(), error.fmpq()
                    )
        need(maxnorm(H - m.I) < ball(RHO), "full-input H ball")
        read = m.read(C, W, H)
        need(
            all(
                x.is_finite() and x.rad() < arb(fmpq(1, 2**CURRENT_BITS))
                for x in read["current"].entries()
            ),
            "section current exceeds fixed error policy",
        )
        return FrozenJSONMap(
            {
                "numerical_policy_id": ARG2B_NUMERICAL_POLICY,
                "precision_bits": precision,
                "graph": graph.to_payload(),
                "profile": decode_canonical_json(profile_bytes),
                "state": state.to_payload(),
                "completion": m.domain,
                "query_proposal": [str(x.fmpq()) for x in point.entries()],
                "query_shift": exact_bounds(shift),
                "section_error": exact_bounds(error),
                "section_tail": exact_bounds(selected["tail"]),
                "residual_error": exact_bounds(selected["residual_error"]),
                "state_residual": exact_bounds(selected["state_residual"]),
                "geometry_residual": exact_bounds(selected["geometry_residual"]),
                "proposal": intervals(selected["proposal"]),
                "geometry": intervals(H),
                "selected": {k: intervals(v) for k, v in read.items()},
                "chain": selected["chain"],
                "proposal_sweeps": m.proposal_sweeps,
                "newton_iterations": m.newton_iterations,
                "physical_state": ["C", "W_A"],
                "section_coordinates": "C_then_64_logW",
                "writer_in_inverse": True,
                "section_C1_claimed": False,
            }
        )


@dataclass(frozen=True, slots=True)
class SparkARG2bStep:
    before: ExactConductanceState
    after: ExactConductanceState
    profile_id: str
    duration: str
    flux: tuple[str, ...]
    componentwise_error_bounds: tuple[str, ...]
    log_conductance_component_error: str
    section: FrozenJSONMap
    writer: FrozenJSONMap
    restart_section: FrozenJSONMap
    final_current: tuple
    reference_current: tuple
    numerical_policy_id: str = field(default=ARG2B_NUMERICAL_POLICY, init=False)


@dataclass(frozen=True, slots=True)
class SparkARG2bKernel(SparkAOSKernel):
    profile: QuarticARG2bProfile

    @flint_operation
    def __post_init__(self):
        if (
            type(self.graph) is not GRCV4Graph
            or type(self.profile) is not QuarticARG2bProfile
        ):
            raise TypeError("typed graph and explicit quartic A_RG2b profile required")
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
            raise ValueError("unsupported A_RG2b coefficients")
        if (
            p.candidate.descriptor_backend_id != descriptor_identity(self.graph)
            or p.candidate.conductance_evaluator_id != "curvature_disabled_G_W_v1"
            or p.geometry.kappa_H != 1 / 2
            or p.realization.extension_evaluator_id != COMPLETION_ID
            or p.realization.approximation_policy_id != APPROXIMATION_ID
            or p.realization.containment_certificate_id != DOMAIN_ID
            or p.realization.error_norm_id != ERROR_NORM
            or p.realization.error_tolerance != 1e-11
            or p.realization.iteration_limit != 16
            or p.realization.failure_policy_id
            != "fail_closed_on_uncertified_section_v1"
            or p.solver.solver_kind != "direct"
            or p.solver.iteration_limit != 1
            or p.solver.absolute_tolerance != 1e-11
            or p.solver.relative_tolerance != 1e-11
            or p.solver.conditioning_limit != 10**12
            or p.solver.root_selector_id != "unique_admitted_root_v1"
            or p.solver.residual_norm_id != "edge_l2_v1"
            or p.solver.failure_policy_id != "fail_closed_no_fallback_v1"
            or self.profile.baseline.identity_payload.solver_id
            != "direct_unique_root_v1"
            or p.common.domain_id != "fixed_graph_strict_gap_spd_v1"
            or p.common.gauge_id != "component_zero_mean_potential_v1"
            or p.common.normalization_id != "unnormalized_vertex_stiffness_v1"
        ):
            raise ValueError("unsupported A_RG2b descriptor, domain or solve policy")
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

        with _ARB_CONTEXT_LOCK, ctx.workprec(PRECISION):
            self.section_math()

    @property
    def precision_bits(self):
        return PRECISION

    def section_math(self):
        return ARG2bMath(self.graph)

    @staticmethod
    def cache_info():
        return {
            "graph": _reference_facts.cache_info()._asdict(),
            "rows": _fixed_rows.cache_info()._asdict(),
            "domain": global_domain.cache_info()._asdict(),
            "section": _section_witness.cache_info()._asdict(),
        }

    def _admitted_section(self, state):
        need(
            type(state) is ExactConductanceState and state.graph == self.graph,
            "complete actual C/W subject required",
        )
        need(
            min(map(rational, state.W_A))
            * rational(self.selector_gap_lower)
            * (1 - RHO)
            > fmpq(1, 64),
            "weighted selector separation",
        )
        result = _section_witness(
            canonical_json_bytes(self.graph.to_payload()),
            self.profile.to_canonical_bytes(),
            state.to_canonical_bytes(),
            self.precision_bits,
        )
        H = matrix_ball(result["geometry"])
        need(
            H.nrows() * maxnorm(H) * maxnorm(H.inv()) < 10**12,
            "section lowering conditioning",
        )
        return result

    @flint_operation
    def readmission(self, state):
        with _ARB_CONTEXT_LOCK, ctx.workprec(self.precision_bits):
            return self._admitted_section(state)

    def _writer(self, state, resources, witness):
        need(witness["state"].to_dict() == state.to_payload(), "joint writer subject")
        m = self.section_math()
        W = vector(state.W_A)
        L = arb_mat([[x.log()] for x in W.entries()])
        J = matrix_ball(witness["selected"]["current"])
        exponent, _ = m.exponent(vector(resources.C), W, J)
        nextL = m.decay * L + (1 - m.decay) * exponent
        ideal = m.exp(nextL)
        mids = _midpoints(ideal, WRITER_BITS, "A_RG2b writer")
        weights = tuple(str(round_flux(rational(x) * 2**64) / 2**64) for x in mids)
        return weights, FrozenJSONMap(
            {
                "consumed_state_digest": sha256(state.to_canonical_bytes()).hexdigest(),
                "final_resource_digest": sha256(
                    resources.to_canonical_bytes()
                ).hexdigest(),
                "incoming_W": list(state.W_A),
                "selected_current": intervals(J),
                "exponent": intervals(exponent),
                "decay": exact_bounds(m.decay),
                "ideal": intervals(ideal),
                "midpoint": list(mids),
            }
        )

    @flint_operation
    def step(self, state, duration="16"):
        if rational(duration) != 16:
            raise ValueError("A_RG2b requires duration 16")
        with _ARB_CONTEXT_LOCK, ctx.workprec(self.precision_bits):
            witness = self._admitted_section(state)
            J = matrix_ball(witness["selected"]["current"])
            flux = []
            for x in J.entries():
                lower, upper = (
                    round_flux(x.lower().fmpq()),
                    round_flux(x.upper().fmpq()),
                )
                need(
                    lower == upper, "section does not determine unique represented flux"
                )
                flux.append(str(lower))
            flux = tuple(flux)
            resources = ExactResources.advance(state, flux, duration)
            weights, writer = self._writer(state, resources, witness)
            after = state.advance_conductance(flux, duration, weights)
            restart = self._admitted_section(after)
            m = self.section_math()
            H = matrix_ball(witness["geometry"])
            final = m.read(vector(after.C), vector(state.W_A), H)
            reference = m.read(vector(after.C), vector(after.W_A), m.I)
            errors, history = self.coordinate_error_bounds()
            return SparkARG2bStep(
                state,
                after,
                self.profile.complete_profile_id,
                duration,
                flux,
                tuple(map(str, errors)),
                str(history),
                witness,
                writer,
                restart,
                tuple(tuple(exact_bounds(x)) for x in final["current"].entries()),
                tuple(tuple(exact_bounds(x)) for x in reference["current"].entries()),
            )

    @flint_operation
    def coordinate_error_bounds(self):
        B = _matrix(self._B)
        epsilon = fmpq(1, 2**129) + fmpq(1, 2**CURRENT_BITS)
        resource = tuple(
            16 * sum(abs(B[i, j]) for j in range(B.ncols())) * epsilon
            for i in range(B.nrows())
        )
        # The writer uses represented final C. In [0,4], its resource
        # derivative l1 bound is 194/65536; (1-exp(-1/2)) < 1.
        propagated = fmpq(194, 65536) * max(resource)
        rounded = fmpq(100, 99) * (fmpq(1, 2**193) + fmpq(1, 2**WRITER_BITS))
        return resource, propagated + rounded

    @flint_operation
    def uniform_metric_error(self, P, margin):
        with _ARB_CONTEXT_LOCK, ctx.workprec(self.precision_bits):
            B = _matrix(self._B)
            e = fmpq(1, 2**129) + fmpq(1, 2**CURRENT_BITS)
            resource = (
                16
                * e
                * sum(
                    arb((B.transpose() * P * B)[j, j]).sqrt() for j in range(B.ncols())
                )
            )
            _, history = self.coordinate_error_bounds()
            conductance = SCALE * arb(len(self.graph.live_edge_ids)).sqrt() * history
            error = max(resource, conductance).upper()
            need(
                0 < error < ball(margin),
                "full C/64logW represented error exceeds image margin",
            )
            return str(error.fmpq())

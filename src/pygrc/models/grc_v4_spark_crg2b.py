"""Exact C_RG2b physical steps with fresh, certified invariant-section reads.

C is the only physical state. A bounded cache memoizes deterministic complete
section witnesses for identical exact subjects; no geometry history crosses an
event and no approximate previous section chooses a future physical output.
"""

from dataclasses import dataclass, field
from functools import lru_cache

from flint import arb, arb_mat, ctx, fmpq

from .grc_v4_certification import _ARB_CONTEXT_LOCK
from .grc_v4_codec import canonical_json_bytes, decode_canonical_json
from .grc_v4_geometry import GRCV4Context, GRCV4Graph, GRCV4ReferenceGeometry
from .grc_v4_spark_cos import SparkCOSKernel, _matrix, _reference_facts
from .grc_v4_spark_crg2b_math import (
    APPROXIMATION_ID,
    COMPLETION_ID,
    DOMAIN_ID,
    ERROR_NORM,
    LIP,
    PRECISION,
    PROPOSAL_BITS,
    RHO,
    SectionMath,
    _algebra_facts,
    _matrix_facts,
    ball,
    exact_bounds,
    global_domain,
    maxnorm,
    need,
)
from .grc_v4_spark_state import (
    CRG2B_NUMERICAL_POLICY,
    ExactResources,
    QuarticCRG2bProfile,
    flint_operation,
    rational,
    round_flux,
)
from .grc_v4_state import FrozenJSONMap

CURRENT_BITS = 160


def intervals(M):
    return [[exact_bounds(M[i, j]) for j in range(M.ncols())] for i in range(M.nrows())]


def matrix_ball(rows):
    return arb_mat(
        [
            [arb((fmpq(a) + fmpq(b)) / 2, (fmpq(b) - fmpq(a)) / 2) for a, b in row]
            for row in rows
        ]
    )


@lru_cache(maxsize=8)
def _section_witness(graph_bytes, profile_bytes, state_bytes, precision):
    """Immutable witness, keyed by all declarations, exact input and precision."""
    graph = decode_canonical_json(graph_bytes)
    state = decode_canonical_json(state_bytes)
    with _ARB_CONTEXT_LOCK, ctx.workprec(precision):
        m = SectionMath(graph)
        C = arb_mat([[fmpq(x)] for x in state["C"]])
        km = list(map(ball, m.domain["K_minus"]))
        need(
            all(km[0] < x < km[1] for x in C.entries()),
            "section query outside physical K-minus",
        )
        scale = 2**PROPOSAL_BITS

        def quantized(x):
            q = x.mid().fmpq()
            return arb(fmpq((q.numerator * scale) // q.denominator, scale))

        proposal = arb_mat([[quantized(x)] for x in C.entries()])
        selected = m.section(proposal, retain_chain=True)
        shift = maxnorm(C - proposal)
        error = (selected["error"] + ball(LIP) * shift).upper()
        H = arb_mat(m.m, m.m)
        for i in range(m.m):
            for j in range(i, m.m):
                if m.overlap[i][j]:
                    H[i, j] = arb(selected["proposal"][i, j].fmpq(), error.fmpq())
                    H[j, i] = H[i, j]
        need(maxnorm(H - m.I) < ball(RHO), "full-input section leaves geometry ball")
        read = m.lag(C, m.operators(H))
        epsilon = arb(fmpq(1, 2**CURRENT_BITS))
        need(
            all(x.is_finite() and x.rad() < epsilon for x in read["current"].entries()),
            "full section-current enclosure exceeds policy",
        )
        return FrozenJSONMap(
            {
                "numerical_policy_id": CRG2B_NUMERICAL_POLICY,
                "precision_bits": precision,
                "graph": graph,
                "profile": decode_canonical_json(profile_bytes),
                "state": state,
                "completion": m.domain.to_dict(),
                "query_proposal": [str(x.fmpq()) for x in proposal.entries()],
                "query_shift": exact_bounds(shift),
                "section_error": exact_bounds(error),
                "section_tail": exact_bounds(selected["tail"]),
                "residual_error": exact_bounds(selected["residual_error"]),
                "state_residual": exact_bounds(selected["state_residual"]),
                "geometry_residual": exact_bounds(selected["geometry_residual"]),
                "proposal": intervals(selected["proposal"]),
                "geometry": intervals(H),
                "current": intervals(read["current"]),
                "flat": intervals(read["causal_flat"]),
                "baseline": intervals(read["baseline"]),
                "chain": selected["chain"],
                "proposal_sweeps": m.proposal_sweeps,
                "newton_iterations": m.newton_iterations,
                "physical_state": ["C"],
                "section_C1_claimed": False,
            }
        )


@dataclass(frozen=True, slots=True)
class SparkCRG2bStep:
    before: ExactResources
    after: ExactResources
    profile_id: str
    duration: str
    flux: tuple[str, ...]
    componentwise_error_bounds: tuple[str, ...]
    section: FrozenJSONMap
    restart_section: FrozenJSONMap
    final_current: tuple
    reference_current: tuple[str, ...]
    numerical_policy_id: str = field(default=CRG2B_NUMERICAL_POLICY, init=False)


@dataclass(frozen=True, slots=True)
class SparkCRG2bKernel(SparkCOSKernel):
    profile: QuarticCRG2bProfile

    @flint_operation
    def __post_init__(self):
        from .grc_v4_candidate_c import CandidateCTransport

        if (
            type(self.graph) is not GRCV4Graph
            or type(self.profile) is not QuarticCRG2bProfile
        ):
            raise TypeError("explicit typed quartic C_RG2b graph/profile required")
        if (self.profile.site.c0, self.profile.site.a, self.profile.site.mu) != (
            "2",
            "1",
            "1",
        ):
            raise ValueError("declared quartic site required")
        p = self.profile.baseline.params_resolved
        expected = {
            "Lambda_C": 1 / 64,
            "kappa_M_C": 0,
            "kappa_Phi_C": 1 / 64,
            "eta_C": 1 / 1024,
            "tau_C": 1,
            "chi_C": 1 / 2,
            "zeta_C": 1 / 2,
        }
        if any(getattr(p.candidate, k) != v for k, v in expected.items()):
            raise ValueError("unsupported quartic C_RG2b coefficients")
        if set(p.candidate.W_C_tr) != set(self.graph.live_edge_ids) or any(
            x != 1 for x in p.candidate.W_C_tr.values()
        ):
            raise ValueError("actual-graph unit transport required")
        r = p.realization
        s = p.solver
        if (
            r.extension_evaluator_id != COMPLETION_ID
            or r.approximation_policy_id != APPROXIMATION_ID
            or r.containment_certificate_id != DOMAIN_ID
            or r.error_norm_id != ERROR_NORM
            or r.error_tolerance != 1e-11
            or r.iteration_limit != 12
            or r.failure_policy_id != "fail_closed_on_uncertified_section_v1"
            or p.geometry.kappa_H != 1 / 2
            or s.solver_kind != "direct"
            or s.iteration_limit != 1
            or s.root_selector_id != "unique_admitted_root_v1"
            or s.residual_norm_id != "edge_l2_v1"
            or s.absolute_tolerance != 1e-11
            or s.relative_tolerance != 1e-11
            or s.conditioning_limit != 10**12
            or s.failure_policy_id != "fail_closed_no_fallback_v1"
            or self.profile.baseline.identity_payload.solver_id
            != "direct_unique_root_v1"
            or p.common.domain_id != "fixed_graph_strict_gap_spd_v1"
            or p.common.gauge_id != "component_zero_mean_potential_v1"
            or p.common.normalization_id != "unnormalized_vertex_stiffness_v1"
        ):
            raise ValueError("unsupported frozen completion, section or solver policy")
        m = len(self.graph.oriented_edges)
        GRCV4ReferenceGeometry(
            self.graph,
            self.profile.baseline,
            GRCV4Context("constant_zero_context_v1", FrozenJSONMap({})),
            tuple((0.0,) * m for _ in range(m)),
            FrozenJSONMap({e: 1 for e in self.graph.live_edge_ids}),
        )
        CandidateCTransport(self.graph, self.profile.baseline)
        facts = _reference_facts(canonical_json_bytes(self.graph.to_payload()))
        for key, value in zip(
            ("_B", "_I", "_L", "_O", "_inverse", "selector_gap_lower"),
            facts,
            strict=True,
        ):
            object.__setattr__(self, key, value)
        with _ARB_CONTEXT_LOCK, ctx.workprec(self.precision_bits):
            self.section_math()

    @property
    def precision_bits(self):
        return PRECISION

    def section_math(self):
        return SectionMath(self.graph.to_payload())

    @staticmethod
    def cache_info():
        return {
            "graph": _reference_facts.cache_info()._asdict(),
            "algebra": _algebra_facts.cache_info()._asdict(),
            "exact_matrix_scalars": _matrix_facts.cache_info()._asdict(),
            "domain": global_domain.cache_info()._asdict(),
            "section": _section_witness.cache_info()._asdict(),
        }

    def _admitted_section(self, state):
        if type(state) is not ExactResources or state.graph != self.graph:
            raise ValueError("actual graph-bound exact resources required")
        result = _section_witness(
            canonical_json_bytes(self.graph.to_payload()),
            self.profile.to_canonical_bytes(),
            state.to_canonical_bytes(),
            self.precision_bits,
        )
        H = matrix_ball(result["geometry"])
        J = matrix_ball(result["current"])
        m = self.section_math()
        operators = m.operators(H)
        need(
            m.m * maxnorm(3 * m.I / 4 + H * m.Le) * maxnorm(operators["M"]) < 10**12
            and m.m * maxnorm(H) * maxnorm(operators["Hi"]) < 10**12,
            "section physical solve conditioning unresolved",
        )
        need(
            all(x.rad() < arb(fmpq(1, 2**CURRENT_BITS)) for x in J.entries()),
            "decoded section-current error exceeds policy",
        )
        return result

    @flint_operation
    def readmission(self, state):
        with _ARB_CONTEXT_LOCK, ctx.workprec(self.precision_bits):
            return self._admitted_section(state)

    @flint_operation
    def step(self, state, duration="8"):
        if rational(duration) != 8:
            raise ValueError("C_RG2b numerical binding requires duration 8")
        with _ARB_CONTEXT_LOCK, ctx.workprec(self.precision_bits):
            selected = self._admitted_section(state)
            J = matrix_ball(selected["current"])
            flux = []
            for x in J.entries():
                lower, upper = (
                    round_flux(x.lower().fmpq()),
                    round_flux(x.upper().fmpq()),
                )
                need(
                    lower == upper,
                    "section enclosure does not select a unique rounded flux",
                )
                flux.append(str(lower))
            flux = tuple(flux)
            after = state.advance(flux, duration)
            epsilon = fmpq(1, 2**129) + fmpq(1, 2**CURRENT_BITS)
            need(
                all(
                    max(
                        abs(fmpq(v) - x.lower().fmpq()), abs(fmpq(v) - x.upper().fmpq())
                    )
                    <= epsilon
                    for v, x in zip(flux, J.entries(), strict=True)
                ),
                "represented section current exceeds full error budget",
            )
            B = _matrix(self._B)
            errors = tuple(
                str(8 * sum(abs(B[i, j]) for j in range(B.ncols())) * epsilon)
                for i in range(B.nrows())
            )
            m = self.section_math()
            post = arb_mat([[fmpq(x)] for x in after.C])
            H = matrix_ball(selected["geometry"])
            final = m.lag(post, m.operators(H))
            restart = self._admitted_section(after)
            reference, _ = self.reference_read(after)
            return SparkCRG2bStep(
                state,
                after,
                self.profile.complete_profile_id,
                duration,
                flux,
                errors,
                selected,
                restart,
                tuple(tuple(exact_bounds(x)) for x in final["current"].entries()),
                reference,
            )

    @flint_operation
    def uniform_metric_error(self, margin):
        with _ARB_CONTEXT_LOCK, ctx.workprec(self.precision_bits):
            m = self.section_math()
            B = m.algebra["B"]
            P = m.algebra["P"]
            norm = sum(
                arb((B.transpose() * P * B)[j, j]).sqrt() for j in range(B.ncols())
            )
            error = (8 * norm * arb(fmpq(1, 2**129) + fmpq(1, 2**CURRENT_BITS))).upper()
            need(
                0 < error < ball(margin),
                "full charge-tangent represented error exceeds image margin",
            )
            return str(error.fmpq())

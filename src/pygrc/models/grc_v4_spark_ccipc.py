"""Native composite C_CI_PC: selected full-state roots and same-source writing.

Only immutable graph/domain facts are cached. Root proposals start at zero;
whole-input Banach bounds supply authority before a single exact C/Z write.
"""

from dataclasses import dataclass, field
from functools import lru_cache
from hashlib import sha256
from math import isqrt

from .grc_v4_certification import _ARB_CONTEXT_LOCK, CertificationInconclusive
from .grc_v4_codec import canonical_json_bytes
from .grc_v4_exact import _flint_module, exact_number
from .grc_v4_geometry import GRCV4Context, GRCV4Graph, GRCV4ReferenceGeometry
from .grc_v4_spark_carrier import ExactCarrierState
from .grc_v4_spark_cci import SparkCCIKernel
from .grc_v4_spark_cos import _matrix, _norm_inf, _reference_facts
from .grc_v4_spark_cpc import (
    SOURCE_ENVELOPE,
    SparkCPCKernel,
    SparkCPCStep,
    frobenius,
    interval,
    intervals,
    need,
    norm,
)
from .grc_v4_spark_state import (
    CIPC_NUMERICAL_POLICY,
    QuarticCCIPCProfile,
    flint_operation,
    rational,
    round_flux,
)
from .grc_v4_state import FrozenJSONMap

PRECISION = 256
CURRENT_BITS = 192
WRITER_BITS = 224
PROPOSAL_BITS = 224
ROOT_DOMAIN = "cipc_quartic_flat_inf_ball_1_over_32_carrier_1_over_128_v1"


@lru_cache(maxsize=16)
@flint_operation
def _domain(encoded):
    facts = _reference_facts(encoded)
    B, L, O, inverse = (_matrix(facts[i]) for i in (0, 2, 3, 4))
    q = exact_number
    ell, b, a, s = _norm_inf(L), _norm_inf(B), _norm_inf(inverse), _norm_inf(O) / 8
    r, R = q(1, 32), q(1, 128)
    m = L.nrows()
    z = (isqrt(m - 1) + 1) * R / 2
    h = z + s * r * r
    need(h < 1 and a * h * ell < 1, "CI+PC inverse premises unresolved")
    u, v = 1 / (1 - h), a / (1 - a * h * ell)
    j = q(2, 1024) * (b * q(4, 64) + 6) + q(1, 1024 * 64) * ell * h * 4
    y = v * j
    image = u * y / 2
    lip = u * (v * (q(1, 1024 * 64) * ell * 4 + ell * y) / 2 + image)
    contraction = lip * 2 * s * r
    source = q(m, 2) * image * image
    need(
        image < r and contraction < 1 and source < R,
        "CI+PC root/source domain unresolved",
    )
    lower = 1 - R / 2  # S(f) is PSD; signed Z is bounded in Frobenius norm.
    need(lower * rational(facts[5]) > q(1, 64), "CI+PC selector separation unresolved")
    return FrozenJSONMap(
        {
            "domain_id": ROOT_DOMAIN,
            "resource_box": ["0", "4"],
            "carrier_radius": str(R),
            "carrier_norm": "symmetric_star_frobenius_v1",
            "flat_radius": str(r),
            "overlap_row_sum": str(s),
            "edge_laplacian_norm": str(ell),
            "incidence_norm": str(b),
            "reference_inverse_norm": str(a),
            "carrier_hodge_deviation": str(z),
            "hodge_deviation": str(h),
            "hodge_inverse_norm": str(u),
            "current_inverse_norm": str(v),
            "image_bound": str(image),
            "geometry_to_flat_lipschitz": str(lip),
            "contraction": str(contraction),
            "source_norm_upper": str(source),
            "H_eigenvalue_lower": str(lower),
            "H_eigenvalue_upper": str(1 + R / 2 + q(m, 4) * r * r),
            "invariant_carrier_ball": True,
            "resource_box_invariance_claimed": False,
            "uniqueness": "one root in the declared flat ball",
            "stationary_composite_gain": 2,
        }
    )


@dataclass(frozen=True, slots=True)
class SparkCCIPCStep(SparkCPCStep):
    numerical_policy_id: str = field(default=CIPC_NUMERICAL_POLICY, init=False)


@dataclass(frozen=True, slots=True)
class SparkCCIPCKernel(SparkCPCKernel):
    profile: QuarticCCIPCProfile

    @flint_operation
    def __post_init__(self):
        from .grc_v4_candidate_c import CandidateCTransport

        if (
            type(self.graph) is not GRCV4Graph
            or type(self.profile) is not QuarticCCIPCProfile
        ):
            raise TypeError("explicit quartic C_CI_PC graph/profile required")
        if (self.profile.site.c0, self.profile.site.a, self.profile.site.mu) != (
            "2",
            "1",
            "1",
        ):
            raise ValueError("declared quartic coefficients required")
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
            raise ValueError("unsupported PC coefficients")
        if set(p.candidate.W_C_tr) != set(self.graph.live_edge_ids) or any(
            x != 1 for x in p.candidate.W_C_tr.values()
        ):
            raise ValueError("unit actual-graph transport required")
        if (
            p.geometry.kappa_H != 1 / 2
            or p.realization.rho_inst != 1
            or p.realization.contraction_domain_id != ROOT_DOMAIN
            or p.realization.tolerance != 1e-11
            or p.realization.root_selector_id != "unique_admitted_root_v1"
            or p.realization.residual_norm_id != "joint_current_geometry_l2_v1"
            or not 1 <= p.realization.iteration_limit <= 60
            or p.solver.iteration_limit != p.realization.iteration_limit
            or p.realization.tau_PC != 32
            or p.realization.radius != 1 / 128
            or p.realization.carrier_norm_id != "symmetric_star_frobenius_v1"
            or p.realization.source_envelope_id != SOURCE_ENVELOPE
            or p.realization.writer_id != "zero_order_hold_exponential_v1"
            or p.solver.solver_kind != "fixed_point"
            or p.solver.root_selector_id != "unique_admitted_root_v1"
            or p.solver.absolute_tolerance != 1e-11
            or p.solver.relative_tolerance != 1e-11
            or p.solver.residual_norm_id != "edge_l2_v1"
            or p.solver.failure_policy_id != "fail_closed_no_fallback_v1"
            or self.profile.baseline.identity_payload.solver_id
            != "ci_reduced_fixed_point_v1"
            or p.common.domain_id != "fixed_graph_strict_gap_spd_v1"
            or p.common.gauge_id != "component_zero_mean_potential_v1"
            or p.common.normalization_id != "unnormalized_vertex_stiffness_v1"
        ):
            raise ValueError("unsupported PC domain, writer or solver policy")
        m = len(self.graph.oriented_edges)
        GRCV4ReferenceGeometry(
            self.graph,
            self.profile.baseline,
            GRCV4Context("constant_zero_context_v1", FrozenJSONMap({})),
            tuple((0.0,) * m for _ in range(m)),
            FrozenJSONMap({e: 1 for e in self.graph.live_edge_ids}),
        )
        CandidateCTransport(self.graph, self.profile.baseline)
        encoded = canonical_json_bytes(self.graph.to_payload())
        for key, value in zip(
            ("_B", "_I", "_L", "_O", "_inverse", "selector_gap_lower"),
            _reference_facts(encoded),
            strict=True,
        ):
            object.__setattr__(self, key, value)
        object.__setattr__(self, "domain", _domain(encoded))

    @property
    def precision_bits(self):
        return PRECISION

    @staticmethod
    def domain_cache_info():
        return _domain.cache_info()._asdict()

    def _geometry_ball(self, flat, Z):
        return SparkCCIKernel._geometry_ball(self, flat) + Z / 2

    _read_ball = SparkCCIKernel._read_ball

    def _root(self, C, Z):
        """Proposal-only fixed point followed by a whole-input Banach enclosure."""
        f = _flint_module()
        need(all(x >= 0 and x <= 4 for x in C.entries()), "C outside CI resource box")
        M, ball = f.arb_mat, f.arb
        need(frobenius(Z) <= ball(rational("1/128")), "CI+PC carrier ball unresolved")
        proposal_Z = M(
            [[Z[i, j].mid() for j in range(Z.ncols())] for i in range(Z.nrows())]
        )
        proposal_C = M([[x.mid()] for x in C.entries()])
        flat = M(len(self.graph.oriented_edges), 1)
        threshold = ball(2) ** (-PROPOSAL_BITS)
        for iteration in range(
            self.profile.baseline.params_resolved.realization.iteration_limit
        ):
            read = self._read_ball(proposal_C, self._geometry_ball(flat, proposal_Z))
            residual = norm(read["F"] - flat)
            if residual < threshold:
                break
            flat = M([[x.mid()] for x in read["F"].entries()])
            need(norm(flat) < ball(1) / 32, "CI proposal outside selected root ball")
        else:
            raise CertificationInconclusive(
                "CI proposal limit reached without enclosure"
            )
        actual = self._read_ball(C, self._geometry_ball(flat, Z))
        residual = norm(actual["F"] - flat)
        error = (residual / (1 - ball(rational(self.domain["contraction"])))).upper()
        need(
            norm(flat) + error < ball(1) / 32, "CI enclosure leaves selected root ball"
        )
        enclosed = M([[ball(x.fmpq(), error.fmpq())] for x in flat.entries()])
        selected = self._read_ball(C, self._geometry_ball(enclosed, Z))
        O = _matrix(self._O)
        coefficient = ball(sum((x / 8) ** 2 for x in O.entries())).sqrt()
        joint = coefficient * (2 * norm(flat) * residual + residual**2)
        selected.update(
            flat=enclosed,
            proposal=flat,
            error=error,
            proposal_residual=residual,
            joint_residual_upper=joint,
            iterations=iteration + 1,
        )
        source = M(
            [
                [
                    f.arb(O[i, j]) * enclosed[i, 0] * enclosed[j, 0] / 4
                    for j in range(O.ncols())
                ]
                for i in range(O.nrows())
            ]
        )
        need(
            frobenius(source) < ball(rational("1/128")),
            "CI+PC source envelope unresolved",
        )
        selected.update(S=source, residual=joint)
        return selected

    @flint_operation
    def read_ball(self, C, Z):
        return self._root(C, Z)

    @flint_operation
    def _admitted_read(self, state):
        f = _flint_module()
        if type(state) is not ExactCarrierState or state.graph != self.graph:
            raise ValueError("complete actual C/Z subject required")
        read = self.read_ball(
            f.arb_mat([[rational(x)] for x in state.C]), f.arb_mat(_matrix(state.Z_4))
        )
        need(
            read["residual"]
            < f.arb(
                exact_number(
                    self.profile.baseline.params_resolved.solver.absolute_tolerance
                )
            ),
            "PC read residual unresolved",
        )
        eps = exact_number(1, 1 << CURRENT_BITS)
        for x in read["J"].entries():
            q = x.mid().fmpq()
            need(
                max(q - x.lower().fmpq(), x.upper().fmpq() - q) <= eps,
                "PC current enclosure exceeds numerical budget",
            )
        read["subject_digest"] = sha256(state.to_canonical_bytes()).hexdigest()
        return read

    def read_payload(self, read):
        return FrozenJSONMap(
            dict(
                numerical_policy_id=CIPC_NUMERICAL_POLICY,
                precision_bits=PRECISION,
                subject_digest=read["subject_digest"],
                current_midpoint=[str(x.mid().fmpq()) for x in read["J"].entries()],
                **{k: intervals(read[k]) for k in ("H", "J", "flat", "S")},
                residual_upper=str(read["residual"].upper().fmpq()),
                root_domain=self.domain.to_dict(),
                proposal=intervals(read["proposal"]),
                root_error=interval(read["error"]),
                proposal_residual=interval(read["proposal_residual"]),
                iterations=read["iterations"],
                conditioning_upper=str(read["condition"].upper().fmpq()),
            )
        )

    @flint_operation
    def readmission(self, state):
        f = _flint_module()
        with _ARB_CONTEXT_LOCK, f.ctx.workprec(PRECISION):
            return self.read_payload(self._admitted_read(state))

    @flint_operation
    def step(self, state, duration="32"):
        f = _flint_module()
        if rational(duration) != 32:
            raise ValueError("PC requires duration 32")
        with _ARB_CONTEXT_LOCK, f.ctx.workprec(PRECISION):
            read = self._admitted_read(state)
            flux = tuple(str(round_flux(x.mid().fmpq())) for x in read["J"].entries())
            edge_error = exact_number(1, 1 << 129) + exact_number(1, 1 << CURRENT_BITS)
            for q, x in zip(flux, read["J"].entries(), strict=True):
                need(
                    max(
                        abs(rational(q) - x.lower().fmpq()),
                        abs(rational(q) - x.upper().fmpq()),
                    )
                    <= edge_error,
                    "PC flux error exceeds budget",
                )
            Z, writer = self._writer(state, read)
            after = state.advance_carrier(flux, duration, Z)
            restart = self._admitted_read(after)
            B = _matrix(self._B)
            bounds = tuple(
                str(32 * sum(abs(B[i, j]) for j in range(B.ncols())) * edge_error)
                for i in range(B.nrows())
            )
            # Diagnostic only: hold the incoming root geometry after continuity.
            final = self._read_ball(
                f.arb_mat([[rational(x)] for x in after.C]), read["H"]
            )
            reference, _ = self.reference_read(after)
            return SparkCCIPCStep(
                state,
                after,
                self.profile.complete_profile_id,
                duration,
                flux,
                bounds,
                str(exact_number(1, 1 << 193) + exact_number(1, 1 << WRITER_BITS)),
                self.read_payload(read),
                writer,
                self.read_payload(restart),
                tuple(tuple(interval(x)) for x in final["J"].entries()),
                reference,
            )

    @flint_operation
    def uniform_rounding_bound(self, chart, margin, carrier_radius="1/100000000"):
        result = SparkCPCKernel.uniform_rounding_bound(
            self, chart, margin, carrier_radius
        )
        result["numerical_policy_id"] = CIPC_NUMERICAL_POLICY
        return result

    @flint_operation
    def partials(self, C, Z):
        """Full implicit C/Z derivative; immediate geometry and held source couple."""
        f = _flint_module()
        M = f.arb_mat
        B, L, O, I = (M(_matrix(x)) for x in (self._B, self._L, self._O, self._I))
        n, m = B.nrows(), B.ncols()
        root = self.read_ball(C, Z)
        flat = root["flat"]
        read = self._read_ball(C, self._geometry_ball(flat, Z))
        H, y, inv, hi = (read[k] for k in ("H", "y", "inverse", "h_inverse"))
        curvature = M(
            [
                [(3 * (C[i, 0] - 2) ** 2 - 1) if i == j else 0 for j in range(n)]
                for i in range(n)
            ]
        )
        jC = -B.transpose() * (B * H * B.transpose() / 64 - curvature) / 1024
        yC = inv * jC
        FC, JC = hi * yC / 2, jC + yC / 4
        variations = [
            M(
                [
                    [
                        O[i, j]
                        * (
                            (flat[j, 0] if i == k else 0)
                            + (flat[i, 0] if j == k else 0)
                        )
                        / 8
                        for j in range(m)
                    ]
                    for i in range(m)
                ]
            )
            for k in range(m)
        ]
        for i, j in self.pairs:
            dH = M(m, m)
            dH[i, j] = f.arb(1) / 2 if i == j else 1 / (2 * f.arb(2).sqrt())
            dH[j, i] = dH[i, j]
            variations.append(dH)
        pack = lambda cols: M([[col[i, 0] for col in cols] for i in range(m)])
        dj = [-L * dH * B.transpose() * C / (1024 * 64) for dH in variations]
        dy = inv * pack([j - dH * L * y for j, dH in zip(dj, variations, strict=True)])
        dF = hi * (dy / 2 - pack([dH * read["F"] for dH in variations]))
        dJ = pack(dj) + dy / 4
        block = lambda A, start, count: M(
            [[A[i, j] for j in range(start, start + count)] for i in range(m)]
        )
        Ff, FZ = block(dF, 0, m), block(dF, m, len(self.pairs))
        Jf, JZ = block(dJ, 0, m), block(dJ, m, len(self.pairs))
        need(
            norm(Ff) < f.arb(rational(self.domain["contraction"])),
            "implicit root bound unresolved",
        )
        rhs = M(
            [
                [FC[i, j] for j in range(n)]
                + [FZ[i, j] for j in range(len(self.pairs))]
                for i in range(m)
            ]
        )
        implicit = (I - Ff).solve(rhs)
        fC, fZ = block(implicit, 0, n), block(implicit, n, len(self.pairs))
        JC, JZ = JC + Jf * fC, JZ + Jf * fZ

        def source_derivative(df):
            return M(
                [
                    [
                        (1 if i == j else f.arb(2).sqrt())
                        * O[i, j]
                        / 4
                        * (flat[i, 0] * df[j, k] + flat[j, 0] * df[i, k])
                        for k in range(df.ncols())
                    ]
                    for i, j in self.pairs
                ]
            )

        In = M([[int(i == j) for j in range(n)] for i in range(n)])
        return {
            "CC": In - 32 * B * JC,
            "CZ": -32 * B * JZ,
            "SC": source_derivative(fC),
            "SZ": source_derivative(fZ),
            "read": root,
            "root_derivative": norm(Ff),
        }

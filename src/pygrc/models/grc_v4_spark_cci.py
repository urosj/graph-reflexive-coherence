"""Certified quartic C_CI joint roots and conservative represented steps.

Only resources are physical state. Every solve starts at zero; proposals gain
authority only through a fresh Banach enclosure on the actual input. Geometry
and current use that same root. No research evaluator or saved root is used.
"""

from dataclasses import dataclass, field
from functools import lru_cache

from .grc_v4_certification import _ARB_CONTEXT_LOCK, CertificationInconclusive
from .grc_v4_codec import canonical_json_bytes
from .grc_v4_exact import _flint_module, exact_number
from .grc_v4_geometry import GRCV4Context, GRCV4Graph, GRCV4ReferenceGeometry
from .grc_v4_spark_cos import SparkCOSKernel, _matrix, _norm_inf, _reference_facts
from .grc_v4_spark_state import (
    CI_NUMERICAL_POLICY,
    ExactResources,
    QuarticCCIProfile,
    flint_operation,
    rational,
    round_flux,
)
from .grc_v4_state import FrozenJSONMap

ROOT_DOMAIN = "ci_quartic_flat_inf_ball_1_over_32_v1"
PRECISION = 256
ROOT_CURRENT_BITS = 192
PROPOSAL_BITS = 224


def _need(ok, message):
    if not ok:
        raise CertificationInconclusive(message)


def _norm(A):
    f = _flint_module()
    return f.arb(
        max(
            sum(abs(A[i, j]).upper().fmpq() for j in range(A.ncols()))
            for i in range(A.nrows())
        )
    )


def _interval(x):
    return [str(x.lower().fmpq()), str(x.upper().fmpq())]


def _intervals(A):
    return [[_interval(A[i, j]) for j in range(A.ncols())] for i in range(A.nrows())]


@lru_cache(maxsize=16)
@flint_operation
def _root_domain(graph_bytes):
    """Exact graph-bound Banach inequalities for every C in [0,4]^V."""
    facts = _reference_facts(graph_bytes)
    B, L, O, inverse = (_matrix(facts[i]) for i in (0, 2, 3, 4))
    q = exact_number
    ell, b, a, S = _norm_inf(L), _norm_inf(B), _norm_inf(inverse), _norm_inf(O) / 8
    r = q(1, 32)
    h = S * r * r
    _need(h < 1 and a * h * ell < 1, "CI root inverse premises unresolved")
    u, v = 1 / (1 - h), a / (1 - a * h * ell)
    j0 = q(2, 1024) * (b * q(4, 64) + 6) + q(1, 1024 * 64) * ell * h * 4
    y = v * j0
    image = u * y / 2
    lip = u * (v * (q(1, 1024 * 64) * ell * 4 + ell * y) / 2 + image)
    contraction = lip * 2 * S * r
    _need(image < r and contraction < 1, "CI root self-map/contraction unresolved")
    return FrozenJSONMap(
        {
            "domain_id": ROOT_DOMAIN,
            "resource_box": ["0", "4"],
            "flat_radius": str(r),
            "overlap_row_sum": str(S),
            "edge_laplacian_norm": str(ell),
            "incidence_norm": str(b),
            "reference_inverse_norm": str(a),
            "hodge_deviation": str(h),
            "hodge_inverse_norm": str(u),
            "current_inverse_norm": str(v),
            "current_baseline_bound": str(j0),
            "y_bound": str(y),
            "image_bound": str(image),
            "geometry_to_flat_lipschitz": str(lip),
            "contraction": str(contraction),
            "uniqueness": "one root in the declared flat ball",
        }
    )


@dataclass(frozen=True, slots=True)
class SparkCCIStep:
    before: ExactResources
    after: ExactResources
    profile_id: str
    duration: str
    flux: tuple[str, ...]
    componentwise_error_bounds: tuple[str, ...]
    root: FrozenJSONMap
    restart_root: FrozenJSONMap
    final_current: tuple
    reference_current: tuple[str, ...]
    numerical_policy_id: str = field(default=CI_NUMERICAL_POLICY, init=False)


@dataclass(frozen=True, slots=True)
class SparkCCIKernel(SparkCOSKernel):
    profile: QuarticCCIProfile
    root_domain: FrozenJSONMap = field(init=False)

    @flint_operation
    def __post_init__(self):
        from .grc_v4_candidate_c import CandidateCTransport

        if (
            type(self.graph) is not GRCV4Graph
            or type(self.profile) is not QuarticCCIProfile
        ):
            raise TypeError("typed graph and explicit quartic C_CI profile required")
        if (self.profile.site.c0, self.profile.site.a, self.profile.site.mu) != (
            "2",
            "1",
            "1",
        ):
            raise ValueError("declared c0=2, a=mu=1 slice required")
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
            raise ValueError("unsupported quartic CI coefficients")
        if set(p.candidate.W_C_tr) != set(self.graph.live_edge_ids) or any(
            x != 1 for x in p.candidate.W_C_tr.values()
        ):
            raise ValueError("unit actual-graph transport required")
        if (
            p.geometry.kappa_H != 1 / 2
            or p.realization.contraction_domain_id != ROOT_DOMAIN
            or p.realization.tolerance != 1e-11
            or p.realization.root_selector_id != "unique_admitted_root_v1"
            or p.realization.residual_norm_id != "joint_current_geometry_l2_v1"
            or not 1 <= p.realization.iteration_limit <= 60
            or p.solver.solver_kind != "fixed_point"
            or p.solver.root_selector_id != "unique_admitted_root_v1"
            or p.solver.iteration_limit != p.realization.iteration_limit
            or p.solver.residual_norm_id != "edge_l2_v1"
            or p.solver.absolute_tolerance != 1e-11
            or p.solver.relative_tolerance != 1e-11
            or p.solver.failure_policy_id != "fail_closed_no_fallback_v1"
            or self.profile.baseline.identity_payload.solver_id
            != "ci_reduced_fixed_point_v1"
            or p.common.domain_id != "fixed_graph_strict_gap_spd_v1"
            or p.common.gauge_id != "component_zero_mean_potential_v1"
            or p.common.normalization_id != "unnormalized_vertex_stiffness_v1"
        ):
            raise ValueError("unsupported CI root, tolerance or solve policy")
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
        facts = _reference_facts(encoded)
        for key, value in zip(
            ("_B", "_I", "_L", "_O", "_inverse", "selector_gap_lower"),
            facts,
            strict=True,
        ):
            object.__setattr__(self, key, value)
        object.__setattr__(self, "root_domain", _root_domain(encoded))

    @staticmethod
    def root_cache_info():
        return _root_domain.cache_info()._asdict()

    @property
    def precision_bits(self):
        return PRECISION

    def _geometry_ball(self, flat):
        f = _flint_module()
        O, I = f.arb_mat(_matrix(self._O)), f.arb_mat(_matrix(self._I))
        return I + f.arb_mat(
            [
                [O[i, j] * flat[i, 0] * flat[j, 0] / 8 for j in range(I.ncols())]
                for i in range(I.nrows())
            ]
        )

    def _read_ball(self, C, H):
        f = _flint_module()
        B, I, L = (f.arb_mat(_matrix(x)) for x in (self._B, self._I, self._L))
        site = f.arb_mat([[(x - 2) ** 3 - (x - 2)] for x in C.entries()])
        j0 = -B.transpose() * (B * H * B.transpose() * C / 64 - site) / 1024
        A = 3 * I / 4 + H * L
        inverse, h_inverse = A.inv(), H.inv()
        _need(
            all(x.is_finite() for M in (inverse, h_inverse) for x in M.entries()),
            "CI inverse enclosure unresolved",
        )
        condition = H.nrows() * _norm(A) * _norm(inverse)
        h_condition = H.nrows() * _norm(H) * _norm(h_inverse)
        limit = f.arb(
            exact_number(
                self.profile.baseline.params_resolved.solver.conditioning_limit
            )
        )
        _need(
            condition < limit and h_condition < limit,
            "CI conditioning limit unresolved",
        )
        y = inverse * j0
        return {
            "H": H,
            "j0": j0,
            "y": y,
            "J": j0 + y / 4,
            "F": h_inverse * y / 2,
            "inverse": inverse,
            "h_inverse": h_inverse,
            "condition": condition,
        }

    def _root(self, C):
        """Proposal-only fixed point followed by a whole-input Banach enclosure."""
        f = _flint_module()
        _need(all(x >= 0 and x <= 4 for x in C.entries()), "C outside CI resource box")
        M, ball = f.arb_mat, f.arb
        proposal_C = M([[x.mid()] for x in C.entries()])
        flat = M(len(self.graph.oriented_edges), 1)
        threshold = ball(2) ** (-PROPOSAL_BITS)
        for iteration in range(
            self.profile.baseline.params_resolved.realization.iteration_limit
        ):
            read = self._read_ball(proposal_C, self._geometry_ball(flat))
            residual = _norm(read["F"] - flat)
            if residual < threshold:
                break
            flat = M([[x.mid()] for x in read["F"].entries()])
            _need(_norm(flat) < ball(1) / 32, "CI proposal outside selected root ball")
        else:
            raise CertificationInconclusive(
                "CI proposal limit reached without enclosure"
            )
        actual = self._read_ball(C, self._geometry_ball(flat))
        residual = _norm(actual["F"] - flat)
        error = (
            residual / (1 - ball(rational(self.root_domain["contraction"])))
        ).upper()
        _need(
            _norm(flat) + error < ball(1) / 32, "CI enclosure leaves selected root ball"
        )
        enclosed = M([[ball(x.fmpq(), error.fmpq())] for x in flat.entries()])
        selected = self._read_ball(C, self._geometry_ball(enclosed))
        O = _matrix(self._O)
        coefficient = ball(sum((x / 8) ** 2 for x in O.entries())).sqrt()
        joint = coefficient * (2 * _norm(flat) * residual + residual**2)
        selected.update(
            flat=enclosed,
            proposal=flat,
            error=error,
            proposal_residual=residual,
            joint_residual_upper=joint,
            iterations=iteration + 1,
        )
        return selected

    def _root_payload(self, root):
        return FrozenJSONMap(
            {
                "numerical_policy_id": CI_NUMERICAL_POLICY,
                "domain": self.root_domain.to_dict(),
                "precision_bits": PRECISION,
                "iterations": root["iterations"],
                "flat": _intervals(root["flat"]),
                "geometry": _intervals(root["H"]),
                "current": _intervals(root["J"]),
                "proposal": _intervals(root["proposal"]),
                "root_error": _interval(root["error"]),
                "proposal_residual": _interval(root["proposal_residual"]),
                "joint_residual_upper": _interval(root["joint_residual_upper"]),
                "conditioning_upper": _interval(root["condition"]),
            }
        )

    def _admitted_root(self, state):
        f = _flint_module()
        if type(state) is not ExactResources or state.graph != self.graph:
            raise ValueError("actual graph-bound exact resources required")
        root = self._root(f.arb_mat([[rational(x)] for x in state.C]))
        tolerance = f.arb(
            exact_number(self.profile.baseline.params_resolved.realization.tolerance)
        )
        _need(
            root["joint_residual_upper"] < tolerance,
            "CI joint residual tolerance unresolved",
        )
        epsilon = exact_number(1, 1 << ROOT_CURRENT_BITS)
        for x in root["J"].entries():
            mid = x.mid().fmpq()
            _need(
                max(mid - x.lower().fmpq(), x.upper().fmpq() - mid) <= epsilon,
                "CI entire-current enclosure exceeds numerical policy",
            )
        return root

    @flint_operation
    def readmission(self, state):
        f = _flint_module()
        with _ARB_CONTEXT_LOCK, f.ctx.workprec(PRECISION):
            return self._root_payload(self._admitted_root(state))

    @flint_operation
    def step(self, state, duration="32"):
        f = _flint_module()
        if rational(duration) != 32:
            raise ValueError("CI numerical binding requires duration 32")
        with _ARB_CONTEXT_LOCK, f.ctx.workprec(PRECISION):
            root = self._admitted_root(state)
            flux = tuple(str(round_flux(x.mid().fmpq())) for x in root["J"].entries())
            edge_error = exact_number(1, 1 << 129) + exact_number(
                1, 1 << ROOT_CURRENT_BITS
            )
            for value, interval in zip(flux, root["J"].entries(), strict=True):
                _need(
                    max(
                        abs(rational(value) - interval.lower().fmpq()),
                        abs(rational(value) - interval.upper().fmpq()),
                    )
                    <= edge_error,
                    "CI represented current error exceeds policy",
                )
            after = state.advance(flux, duration)
            B = _matrix(self._B)
            bounds = tuple(
                str(32 * sum(abs(B[i, j]) for j in range(B.ncols())) * edge_error)
                for i in range(B.nrows())
            )
            # Both final reads consume the new C; only the incoming joint root
            # supplies continuity. Restart has a separately certified joint root.
            post = f.arb_mat([[rational(x)] for x in after.C])
            final = self._read_ball(post, root["H"])
            restart = self._admitted_root(after)
            reference, _ = self.reference_read(after)
            return SparkCCIStep(
                state,
                after,
                self.profile.complete_profile_id,
                duration,
                flux,
                bounds,
                self._root_payload(root),
                self._root_payload(restart),
                tuple(tuple(_interval(x)) for x in final["J"].entries()),
                reference,
            )

    @flint_operation
    def uniform_rounding_bound(self, charge_chart, margin):
        U, B = _matrix(charge_chart), _matrix(self._B)
        if U.ncols() != B.nrows() or U.nrows() != B.nrows() - 1:
            raise ValueError("complete charge-tangent chart required")
        epsilon = exact_number(1, 1 << 129) + exact_number(1, 1 << ROOT_CURRENT_BITS)
        error = 32 * _norm_inf(U * B) * epsilon
        _need(
            0 < error < rational(margin),
            "CI full-step error exceeds strict image margin",
        )
        return {
            "numerical_policy_id": CI_NUMERICAL_POLICY,
            "full_step_error": str(error),
            "image_margin": margin,
            "exact_charge_preserved": True,
            "condition": "fresh whole-root/current enclosure and admitted full-domain chart",
            "completion_admitted": False,
        }

    @flint_operation
    def partials(self, C, flat):
        """Full C/f partials, including both consumers of generated geometry."""
        f = _flint_module()
        M = f.arb_mat
        B, L, O = (M(_matrix(x)) for x in (self._B, self._L, self._O))
        n, m = B.nrows(), B.ncols()
        read = self._read_ball(C, self._geometry_ball(flat))
        H, y, inv, hi = read["H"], read["y"], read["inverse"], read["h_inverse"]
        curvature = M(
            [
                [(3 * (C[i, 0] - 2) ** 2 - 1) if i == j else 0 for j in range(n)]
                for i in range(n)
            ]
        )
        jC = -B.transpose() * (B * H * B.transpose() / 64 - curvature) / 1024
        yC = inv * jC
        FC, JC = hi * yC / 2, jC + yC / 4
        ds, djs, rhs = [], [], []
        for k in range(m):
            dH = M(
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
            dj = -L * dH * B.transpose() * C / (1024 * 64)
            ds.append(dH)
            djs.append(dj)
            rhs.append(dj - dH * L * y)
        pack = lambda columns: M(
            [[columns[j][i, 0] for j in range(m)] for i in range(m)]
        )
        dy = inv * pack(rhs)
        Ff = hi * (dy / 2 - pack([dH * read["F"] for dH in ds]))
        Jf = pack(djs) + dy / 4
        return read, Ff, FC, Jf, JC

    @flint_operation
    def analytic(self, C):
        """Whole-input root enclosure and full implicit physical derivative."""
        f = _flint_module()
        M = f.arb_mat
        B, I = M(_matrix(self._B)), M(_matrix(self._I))
        root = self._root(C)
        _, Ff, FC, Jf, JC = self.partials(C, root["flat"])
        _need(
            _norm(Ff) < f.arb(rational(self.root_domain["contraction"])),
            "CI implicit derivative exceeds certified root bound",
        )
        df = (I - Ff).solve(FC)
        In = M([[int(i == j) for j in range(B.nrows())] for i in range(B.nrows())])
        J = In - 32 * B * (JC + Jf * df)
        _need(
            all(
                sum(J[i, j] for i in range(B.nrows())).contains(1)
                for j in range(B.nrows())
            ),
            "CI derivative charge identity failed",
        )
        return C - 32 * B * root["J"], J, _norm(Ff), root["condition"]

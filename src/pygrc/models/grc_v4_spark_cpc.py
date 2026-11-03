"""Native full C/Z quartic PC map, outward Arb reads and exact represented writes."""

from dataclasses import dataclass, field
from functools import lru_cache
from hashlib import sha256

from .grc_v4_certification import _ARB_CONTEXT_LOCK, CertificationInconclusive
from .grc_v4_codec import canonical_json_bytes
from .grc_v4_exact import _flint_module, exact_number
from .grc_v4_geometry import GRCV4Context, GRCV4Graph, GRCV4ReferenceGeometry
from .grc_v4_spark_carrier import ExactCarrierState, carrier_pairs
from .grc_v4_spark_cos import SparkCOSKernel, _matrix, _norm_inf, _reference_facts
from .grc_v4_spark_state import (
    PC_NUMERICAL_POLICY,
    ExactResources,
    QuarticCPCProfile,
    flint_operation,
    rational,
    round_flux,
)
from .grc_v4_state import FrozenJSONMap

PRECISION = 256
CURRENT_BITS = 192
CARRIER_BITS = 192
WRITER_BITS = 224
SOURCE_ENVELOPE = "pc_compact_base_chart_v1:0x1.0000000000000p+2:0x1.0000000000000p+0:0x1.0000000000000p+0"


def need(ok, message):
    if not ok:
        raise CertificationInconclusive(message)


def interval(x):
    return [str(x.lower().fmpq()), str(x.upper().fmpq())]


def intervals(A):
    return [[interval(A[i, j]) for j in range(A.ncols())] for i in range(A.nrows())]


def norm(A):
    f = _flint_module()
    return f.arb(
        max(
            sum(abs(A[i, j]).upper().fmpq() for j in range(A.ncols()))
            for i in range(A.nrows())
        )
    )


def frobenius(A):
    return sum(abs(x).upper() ** 2 for x in A.entries()).sqrt().upper()


@lru_cache(maxsize=4)
def _decay(precision):
    f = _flint_module()
    with _ARB_CONTEXT_LOCK, f.ctx.workprec(precision):
        return tuple(interval((-f.arb(1)).exp()))


def decay():
    f = _flint_module()
    a, b = map(rational, _decay(f.ctx.prec))
    return f.arb((a + b) / 2, (b - a) / 2)


@lru_cache(maxsize=16)
@flint_operation
def _domain(encoded):
    f = _flint_module()
    facts = _reference_facts(encoded)
    L = _matrix(facts[2])
    m = L.nrows()
    with _ARB_CONTEXT_LOCK, f.ctx.workprec(PRECISION):
        R = f.arb(rational("1/64"))
        lo, hi = 1 - R / 2, 1 + R / 2
        j = f.arb(m).sqrt() * (_norm_inf(L) * hi / 16 + 12) / 1024
        inverse = (hi / lo).sqrt() * 4 / 3
        flat = inverse * j / (2 * lo)
        source = flat**2 / 2
        need(source < R, "uniform PC source ball unresolved")
        need(
            lo * f.arb(rational(facts[5])) > f.arb(rational("1/64")),
            "PC selector separation unresolved",
        )
        return FrozenJSONMap(
            {
                "resource_box": ["0", "4"],
                "carrier_radius": "1/64",
                "carrier_norm": "symmetric_star_frobenius_v1",
                "H_eigenvalue_lower": str(lo.lower().fmpq()),
                "H_eigenvalue_upper": str(hi.upper().fmpq()),
                "source_norm_upper": str(source.upper().fmpq()),
                "flat_norm_upper": str(flat.upper().fmpq()),
                "current_inverse_norm_upper": str(inverse.upper().fmpq()),
                "resource_box_invariance_claimed": False,
            }
        )


@dataclass(frozen=True, slots=True)
class SparkCPCStep:
    before: ExactCarrierState
    after: ExactCarrierState
    profile_id: str
    duration: str
    flux: tuple
    componentwise_error_bounds: tuple
    carrier_component_error: str
    consumed_read: FrozenJSONMap
    writer: FrozenJSONMap
    restart_read: FrozenJSONMap
    final_current: tuple
    reference_current: tuple
    numerical_policy_id: str = field(default=PC_NUMERICAL_POLICY, init=False)


@dataclass(frozen=True, slots=True)
class SparkCPCKernel(SparkCOSKernel):
    profile: QuarticCPCProfile
    domain: FrozenJSONMap = field(init=False)

    @flint_operation
    def __post_init__(self):
        from .grc_v4_candidate_c import CandidateCTransport

        if (
            type(self.graph) is not GRCV4Graph
            or type(self.profile) is not QuarticCPCProfile
        ):
            raise TypeError("explicit quartic C_PC graph/profile required")
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
            or p.realization.tau_PC != 32
            or p.realization.radius != 1 / 64
            or p.realization.carrier_norm_id != "symmetric_star_frobenius_v1"
            or p.realization.source_envelope_id != SOURCE_ENVELOPE
            or p.realization.writer_id != "zero_order_hold_exponential_v1"
            or p.solver.solver_kind != "direct"
            or p.solver.root_selector_id != "unique_admitted_root_v1"
            or p.solver.absolute_tolerance != 1e-11
            or p.solver.relative_tolerance != 1e-11
            or p.solver.residual_norm_id != "edge_l2_v1"
            or p.solver.failure_policy_id != "fail_closed_no_fallback_v1"
            or self.profile.baseline.identity_payload.solver_id
            != "direct_unique_root_v1"
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
    def pairs(self):
        return carrier_pairs(self.graph)

    @property
    def precision_bits(self):
        return PRECISION

    @staticmethod
    def domain_cache_info():
        return _domain.cache_info()._asdict()

    @staticmethod
    def decay_cache_info():
        return _decay.cache_info()._asdict()

    @flint_operation
    def read_ball(self, C, Z):
        f = _flint_module()
        M = f.arb_mat
        B, I, L, O = (M(_matrix(x)) for x in (self._B, self._I, self._L, self._O))
        need(all(x >= 0 and x <= 4 for x in C.entries()), "PC resource box unresolved")
        need(frobenius(Z) <= f.arb(rational("1/64")), "PC carrier ball unresolved")
        H = I + Z / 2
        A = 3 * I / 4 + H * L
        inverse = A.inv()
        hi = H.inv()
        site = M([[(x - 2) ** 3 - (x - 2)] for x in C.entries()])
        j0 = -B.transpose() * (B * H * B.transpose() * C / 64 - site) / 1024
        y = inverse * j0
        flat = hi * y / 2
        J = j0 + y / 4
        S = M(I.nrows(), I.nrows())
        for i, j in self.pairs:
            S[i, j] = O[i, j] * flat[i, 0] * flat[j, 0] / 4
            S[j, i] = S[i, j]
        residual = max(frobenius(A * y - j0), frobenius(2 * H * flat - y))
        condition = max(
            A.nrows() * norm(A) * norm(inverse), H.nrows() * norm(H) * norm(hi)
        )
        # Interval boxes describe many correlated solves; subtracting their
        # hulls is not a solver residual. Pointwise admission checks the fresh
        # represented-input residual separately below.
        need(
            all(x.contains(0) for x in (A * y - j0).entries())
            and all(x.contains(0) for x in (2 * H * flat - y).entries()),
            "PC interval solve identity unresolved",
        )
        need(
            condition
            < f.arb(
                exact_number(
                    self.profile.baseline.params_resolved.solver.conditioning_limit
                )
            ),
            "PC conditioning unresolved",
        )
        need(frobenius(S) < f.arb(rational("1/64")), "PC source ball unresolved")
        return {
            "H": H,
            "J": J,
            "flat": flat,
            "S": S,
            "y": y,
            "inverse": inverse,
            "h_inverse": hi,
            "residual": residual,
            "condition": condition,
        }

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

    def reference_read(self, state):
        if type(state) is not ExactCarrierState or state.graph != self.graph:
            raise ValueError("full PC state required")
        return SparkCOSKernel.reference_read(
            self, ExactResources(state.graph, state.C, state.charge)
        )

    def read_payload(self, read):
        return FrozenJSONMap(
            dict(
                numerical_policy_id=PC_NUMERICAL_POLICY,
                precision_bits=PRECISION,
                subject_digest=read["subject_digest"],
                current_midpoint=[str(x.mid().fmpq()) for x in read["J"].entries()],
                **{k: intervals(read[k]) for k in ("H", "J", "flat", "S")},
                residual_upper=str(read["residual"].upper().fmpq()),
                conditioning_upper=str(read["condition"].upper().fmpq()),
            )
        )

    @flint_operation
    def readmission(self, state):
        f = _flint_module()
        with _ARB_CONTEXT_LOCK, f.ctx.workprec(PRECISION):
            return self.read_payload(self._admitted_read(state))

    def _writer(self, state, read):
        need(
            read["subject_digest"] == sha256(state.to_canonical_bytes()).hexdigest(),
            "stale PC writer subject",
        )
        f = _flint_module()
        d = decay()
        ideal = d * f.arb_mat(_matrix(state.Z_4)) + (1 - d) * read["S"]
        m = ideal.nrows()
        Z = [["0"] * m for _ in range(m)]
        epsilon = exact_number(1, 1 << WRITER_BITS)
        for i, j in self.pairs:
            x = ideal[i, j]
            mid = x.mid().fmpq()
            need(
                max(mid - x.lower().fmpq(), x.upper().fmpq() - mid) <= epsilon,
                "PC writer enclosure exceeds budget",
            )
            rounded = round_flux(mid * 2**64) / 2**64
            Z[i][j] = Z[j][i] = str(rounded)
            need(
                max(abs(rounded - x.lower().fmpq()), abs(rounded - x.upper().fmpq()))
                <= exact_number(1, 1 << 193) + epsilon,
                "PC represented writer error exceeds budget",
            )
        return tuple(tuple(row) for row in Z), FrozenJSONMap(
            {
                "decay": interval(d),
                "ideal": intervals(ideal),
                "midpoint": [
                    [str(ideal[i, j].mid().fmpq()) for j in range(m)] for i in range(m)
                ],
                "consumed_state_digest": read["subject_digest"],
                "source": intervals(read["S"]),
            }
        )

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
            final = self._admitted_read(
                ExactCarrierState(self.graph, after.C, after.charge, state.Z_4)
            )
            reference, _ = self.reference_read(after)
            return SparkCPCStep(
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
        need(rational(carrier_radius) > 0, "positive carrier radius required")
        U, B = _matrix(chart), _matrix(self._B)
        if U.ncols() != B.nrows() or U.nrows() != B.nrows() - 1:
            raise ValueError("complete charge chart required")
        resource = (
            32
            * _norm_inf(U * B)
            * (exact_number(1, 1 << 129) + exact_number(1, 1 << CURRENT_BITS))
        )
        carrier = (
            B.ncols()
            * (exact_number(1, 1 << 193) + exact_number(1, 1 << WRITER_BITS))
            / rational(carrier_radius)
        )
        bound = max(resource, carrier)
        need(0 < bound < rational(margin), "full C/Z error exceeds image margin")
        return {
            "full_step_error": str(bound),
            "resource_error": str(resource),
            "scaled_carrier_error": str(carrier),
            "exact_charge_preserved": True,
            "numerical_policy_id": PC_NUMERICAL_POLICY,
        }

    def partials(self, C, Z):
        """All C and Frobenius-orthonormal signed symmetric-star Z directions."""
        f = _flint_module()
        M = f.arb_mat
        read = self.read_ball(C, Z)
        B, L, O = (M(_matrix(x)) for x in (self._B, self._L, self._O))
        n, m = B.nrows(), B.ncols()
        H, flat, y, inv, hi = (
            read[k] for k in ("H", "flat", "y", "inverse", "h_inverse")
        )
        curvature = M(
            [
                [(3 * (C[i, 0] - 2) ** 2 - 1) if i == j else 0 for j in range(n)]
                for i in range(n)
            ]
        )
        jC = -B.transpose() * (B * H * B.transpose() / 64 - curvature) / 1024
        yC = inv * jC
        fC = hi * yC / 2
        JC = jC + yC / 4
        variations = []
        for i, j in self.pairs:
            dH = M(m, m)
            dH[i, j] = f.arb(1) / 2 if i == j else 1 / (2 * f.arb(2).sqrt())
            dH[j, i] = dH[i, j]
            variations.append(dH)
        pack = lambda cols: M([[col[i, 0] for col in cols] for i in range(m)])
        jZ = [-L * dH * B.transpose() * C / (1024 * 64) for dH in variations]
        yZ = inv * pack([j - dH * L * y for j, dH in zip(jZ, variations, strict=True)])
        fZ = hi * (yZ / 2 - pack([dH * flat for dH in variations]))
        JZ = pack(jZ) + yZ / 4

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
            "read": read,
        }

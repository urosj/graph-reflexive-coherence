"""Independent A_CI_PC root, two-history and complete represented-map oracle.

Fixed-H equations are assembled edge by edge by the independent A reference.
Carrier sources are literal star sums; no production writer or derivative is used.
"""

from hashlib import sha256
from math import isqrt

from aos_native_spark_oracle import Reference as FixedHReference
from aos_native_spark_oracle import classify as classify  # noqa: PLC0414
from aos_native_spark_oracle import contains, need, upper
from cos_native_spark_oracle import incidence, matrix, vector
from cpc_native_spark_pressure_oracle import round_even
from flint import arb, arb_mat, ctx
from flint import fmpq as Q


def frobenius(A):
    return sum(abs(x).upper() ** 2 for x in A.entries()).sqrt().upper().fmpq()


class Reference(FixedHReference):
    def __init__(self, graph):
        super().__init__(graph)
        self.carrier_pairs = [
            (i, j)
            for i, a in enumerate(self.pairs)
            for j, b in enumerate(self.pairs)
            if i <= j and set(a) & set(b)
        ]

        E = incidence(graph).transpose() * incidence(graph)
        ell = max(sum(abs(E[i, j]) for j in range(self.m)) for i in range(self.m))
        self.overlap = [[len(set(a) & set(b)) for b in self.pairs] for a in self.pairs]
        S, r, R = Q(max(map(sum, self.overlap)), 8), Q(1, 32), Q(1, 64)
        z = Q(isqrt(self.m - 1) + 1) * R / 2
        h = z + S * r * r
        u = 1 / (1 - h)
        wl, wh = Q(99, 100), Q(101, 100)
        j = wh * (12 + ell * wh / 16 + ell * h / 16) / 1024
        g = 1 - (200 + j * j) / 65536
        a = max(wh - g, 1 - wl) / (wl + g)
        den = 1 - a / 4
        J = j / den
        M = u * a * J / 2
        jH = wh * ell / 16384
        qj = wh * j / (16384 * (wl + g) ** 2)
        Jj = 1 / den + j * qj / (4 * den**2)
        FH = u * ((a * Jj + J * qj) * jH / 2 + M)
        self.rate = 2 * S * r * FH
        self.image = M
        self.constants = {
            "flat_radius": r,
            "carrier_radius": R,
            "overlap_row_sum": S,
            "edge_laplacian_norm": ell,
            "carrier_H_deviation": z,
            "H_deviation": h,
            "H_inverse": u,
            "H_eigenvalue_lower": 1 - R / 2,
            "H_eigenvalue_upper": 1 + R / 2 + Q(self.m, 4) * r * r,
            "baseline_current": j,
            "drive_lower": g,
            "q_absolute": a,
            "closure_denominator_lower": den,
            "selected_current": J,
            "image_bound": M,
            "baseline_H_lipschitz": jH,
            "q_baseline_lipschitz": qj,
            "current_baseline_lipschitz": Jj,
            "flat_H_lipschitz": FH,
            "contraction": self.rate,
            "source_norm_upper": Q(self.m, 2) * M * M,
            "writer_drive_lower": 1 - (200 + J * J) / 65536,
        }
        need(
            h < 1
            and g > Q(1, 2)
            and M < r
            and self.rate < 1
            and self.constants["source_norm_upper"] < R
            and self.constants["writer_drive_lower"] > wl,
            "independent composite root/history envelope",
        )

    def log_drive(self, C, W, J):
        # Explicit polynomial multiplication admits zero-crossing intervals.
        # Keep the original preflight evaluator and its recorded sources frozen.
        D = self.rows(C, W)
        values = []
        for k, (i, j) in enumerate(self.pairs):
            squared = sum(
                ((D[i][a] - D[j][a]) * (D[i][a] - D[j][a]) for a in range(3)), arb(0)
            )
            value = -(C[i, 0] + C[j, 0] + squared + J[k, 0] * J[k, 0]) / 65536
            need(value > -arb(2).log(), "independent inactive floor")
            values.append([value])
        return arb_mat(values)

    def source(self, flat):
        S = arb_mat(self.m, self.m)
        for node in range(self.n):
            active = [k for k, pair in enumerate(self.pairs) if node in pair]
            for i in active:
                for j in active:
                    S[i, j] += flat[i, 0] * flat[j, 0] / 4
        return S

    def composite_geometry(self, f, Z):
        return self.I + (Z + self.source(f)) / 2

    def selected(self, C, W, Z):
        cp = arb_mat([[x.mid()] for x in C.entries()])
        wp = arb_mat([[x.mid()] for x in W.entries()])
        zp = arb_mat([[x.mid() for x in row] for row in Z.tolist()])
        f = arb_mat(self.m, 1)
        for _ in range(60):
            F = self.read(cp, wp, self.composite_geometry(f, zp))["causal_flat"]
            if upper(F - f) < Q(1, 2**640):
                break
            f = arb_mat([[x.mid()] for x in F.entries()])
        else:
            raise AssertionError("independent composite root iteration limit")
        rho = upper(
            self.read(C, W, self.composite_geometry(f, Z))["causal_flat"] - f
        ) / (1 - self.rate)
        need(upper(f) + rho < Q(1, 32), "independent composite root ball")
        enclosed = arb_mat([[arb(x.fmpq(), rho)] for x in f.entries()])
        H = self.composite_geometry(enclosed, Z)
        return {
            "H": H,
            "selected": self.read(C, W, H),
            "source": self.source(enclosed),
            "flat": enclosed,
        }

    def map(self, C, L, Z):
        W = arb_mat([[x.exp()] for x in L.entries()])
        r = self.selected(C, W, Z)
        J = r["selected"]["current"]
        after = C - 32 * self.B * J
        d = (-arb(1)).exp()
        ln = d * L + (1 - d) * self.log_drive(after, W, J)
        zn = d * Z + (1 - d) * r["source"]
        return arb_mat(
            after.tolist()
            + ln.tolist()
            + [
                [zn[i, j] * (1 if i == j else arb(2).sqrt())]
                for i, j in self.carrier_pairs
            ]
        )


def audit_read(reference, state, payload, *, compact=False):
    need(
        payload["subject_digest"] == sha256(state.to_canonical_bytes()).hexdigest(),
        "complete C/W/Z read subject",
    )
    C, W, Z = (
        arb_mat(vector(state.C)),
        arb_mat(vector(state.W_A)),
        arb_mat(matrix(state.Z_4)),
    )
    need(all(0 <= Q(x) <= 4 for x in state.C), "conditional resource box")
    need(all(Q(99, 100) < Q(x) < Q(101, 100) for x in state.W_A), "conductance box")
    need(
        sum(Q(x) ** 2 for row in state.Z_4 for x in row) <= Q(1, 4096),
        "signed carrier ball",
    )
    r = reference.selected(C, W, Z)
    if not compact:
        need(contains(payload["H"], r["H"]), "incoming-carrier geometry")
        need(set(payload["selected"]) == set(r["selected"]), "complete selected read")
        for name, value in r["selected"].items():
            need(contains(payload["selected"][name], value), "selected " + name)
        need(contains(payload["source"], r["source"]), "same selected star source")
    need(
        all(
            Q(payload["domain"][key]) == value
            for key, value in reference.constants.items()
        ),
        "complete independent root constants",
    )
    need(
        payload["domain"]["domain_id"]
        == "acipc_quartic_C_W_Z_flat_inf_ball_1_over_32_carrier_1_over_64_v1",
        "composite domain identity",
    )
    need(
        tuple(payload["domain"]["resource_box"]) == ("0", "4")
        and tuple(payload["domain"]["conductance_box"]) == ("99/100", "101/100")
        and payload["domain"]["carrier_norm"] == "symmetric_star_frobenius_v1",
        "conditional composite input domain",
    )
    need(
        payload["domain"]["invariant_carrier_ball"] is True
        and payload["domain"]["resource_box_invariance_claimed"] is False
        and payload["domain"]["stationary_composite_gain"] == 2,
        "composite domain scope",
    )
    proposal = arb_mat([[Q(row[0][0])] for row in payload["proposal"]])
    need(
        all(row[0][0] == row[0][1] for row in payload["proposal"]),
        "exact root proposal",
    )
    residual = upper(
        reference.read(C, W, reference.composite_geometry(proposal, Z))["causal_flat"]
        - proposal
    )
    need(
        residual <= Q(payload["proposal_residual"][1]),
        "actual full-input root residual",
    )
    need(
        residual / (1 - reference.rate) <= Q(payload["root_error"][1]),
        "composite Banach radius",
    )
    need(
        upper(proposal) + Q(payload["root_error"][1]) < Q(1, 32),
        "strict selected root ball",
    )
    if not compact:
        need(contains(payload["flat"], r["flat"]), "independent selected root")
        for i, row in enumerate(payload["flat"]):
            need(
                Q(row[0][0]) <= proposal[i, 0].fmpq() - Q(payload["root_error"][1])
                and Q(row[0][1]) >= proposal[i, 0].fmpq() + Q(payload["root_error"][1]),
                "declared root radius",
            )
    coefficient = arb(
        sum(Q(x, 8) ** 2 for row in reference.overlap for x in row)
    ).sqrt()
    joint = coefficient * (2 * upper(proposal) * residual + residual**2)
    need(
        joint.upper().fmpq()
        <= Q(payload["joint_residual_upper"])
        < Q(*(1e-11).as_integer_ratio()),
        "composite joint residual",
    )
    need(1 <= payload["iterations"] <= 60, "bounded root proposal count")
    s = r["selected"]
    need(
        upper(arb_mat(vector(payload["current_midpoint"])) - s["current"])
        <= Q(1, 2**192),
        "current midpoint budget",
    )
    residual = max(
        frobenius(
            r["H"] * s["causal_flat"]
            - arb_mat(
                [[s["q"][i, 0] * s["current"][i, 0] / 2] for i in range(reference.m)]
            )
        ),
        frobenius(
            arb_mat(
                [
                    [(1 - s["q"][i, 0] / 4) * s["current"][i, 0] - s["baseline"][i, 0]]
                    for i in range(reference.m)
                ]
            )
        ),
    )
    need(
        residual <= Q(payload["residual_upper"]) < Q(*(1e-11).as_integer_ratio()),
        "selected-read residual",
    )
    inf = lambda A: max(
        sum(abs(A[i, j]).upper() for j in range(A.ncols())).upper().fmpq()
        for i in range(A.nrows())
    )
    need(
        reference.m * inf(r["H"]) * inf(r["H"].inv())
        <= Q(payload["conditioning_upper"])
        < 10**12,
        "conditioning bound",
    )
    need(
        payload["numerical_policy_id"]
        == "spark_acipc_arb256_flux128_conductance192_carrier192_v1",
        "A_CI_PC numerical policy",
    )
    return r


def verify_step(step, certificate=None, role="current", *, compact=False):
    from pygrc.models.grc_v4_certification import _ARB_CONTEXT_LOCK
    from pygrc.models.grc_v4_spark_state import ExactResources

    with _ARB_CONTEXT_LOCK, ctx.workprec(768):
        r = Reference(step.before.graph.to_payload())
        before, after = step.before, step.after
        C, W, C1, W1 = (
            arb_mat(vector(x)) for x in (before.C, before.W_A, after.C, after.W_A)
        )
        need(
            step.duration == "32" and before.graph == after.graph,
            "step subject and duration",
        )
        incoming = audit_read(r, before, step.consumed_read, compact=compact)
        audit_read(r, after, step.restart_read, compact=compact)
        J = incoming["selected"]["current"]
        need(
            tuple(
                str(round_even(x, 128)) for x in step.consumed_read["current_midpoint"]
            )
            == step.flux,
            "nearest-even flux",
        )
        B = incidence(before.graph.to_payload())
        need(
            vector(after.C) == vector(before.C) - 32 * B * vector(step.flux),
            "exact incidence",
        )
        need(
            sum(map(Q, before.C))
            == sum(map(Q, after.C))
            == Q(before.charge)
            == Q(after.charge),
            "exact charge",
        )
        writer = step.writer
        need(
            writer["consumed_state_digest"] == step.consumed_read["subject_digest"]
            and list(writer["incoming_W"]) == list(before.W_A),
            "writer incoming history",
        )
        resources = ExactResources(after.graph, after.C, after.charge)
        need(
            writer["final_resource_digest"]
            == sha256(resources.to_canonical_bytes()).hexdigest(),
            "writer actual final resources",
        )
        if not compact:
            need(
                contains(writer["selected_current"], J), "same selected writer current"
            )
        exponent = r.log_drive(C1, W, J)
        d = (-arb(1)).exp()
        L = arb_mat([[w.log()] for w in W.entries()])
        ideal_at_native_C = arb_mat(
            [[x.exp()] for x in (d * L + (1 - d) * exponent).entries()]
        )
        if not compact:
            need(
                contains(writer["exponent"], exponent)
                and contains(writer["ideal"], ideal_at_native_C),
                "final-C incoming-W writer",
            )
        need(
            Q(writer["decay"][0])
            <= d.lower().fmpq()
            <= d.upper().fmpq()
            <= Q(writer["decay"][1]),
            "writer decay",
        )
        need(
            upper(arb_mat(vector(writer["midpoint"])) - ideal_at_native_C)
            <= Q(1, 2**224),
            "writer midpoint budget",
        )
        need(
            tuple(str(round_even(x, 192)) for x in writer["midpoint"]) == after.W_A,
            "nearest-even conductance",
        )
        ideal_C = C - 32 * r.B * J
        ideal_L = d * L + (1 - d) * r.log_drive(ideal_C, W, J)
        error_C = C1 - ideal_C
        error_L = arb_mat([[w.log()] for w in W1.entries()]) - ideal_L
        eps = Q(1, 2**129) + Q(1, 2**192)
        eb = [32 * sum(abs(B[i, j]) for j in range(r.m)) * eps for i in range(r.n)]
        el = Q(194, 65536) * max(eb) + Q(100, 99) * (Q(1, 2**193) + Q(1, 2**224))
        need(
            list(map(str, eb)) == list(step.componentwise_error_bounds)
            and str(el) == step.log_conductance_component_error,
            "complete coordinate error bounds",
        )
        need(
            all(abs(error_C[i, 0]).upper().fmpq() <= eb[i] for i in range(r.n))
            and upper(error_L) <= el,
            "complete C/logW error",
        )
        Z, Z1 = arb_mat(matrix(before.Z_4)), arb_mat(matrix(after.Z_4))
        ideal_Z = d * Z + (1 - d) * incoming["source"]
        zw = step.carrier_writer
        need(
            zw["consumed_state_digest"] == step.consumed_read["subject_digest"],
            "same complete carrier-writer input",
        )
        if not compact:
            need(
                contains(zw["source"], incoming["source"])
                and contains(zw["ideal"], ideal_Z),
                "old-state carrier source and exact exponential writer",
            )
        need(
            Q(zw["decay"][0])
            <= d.lower().fmpq()
            <= d.upper().fmpq()
            <= Q(zw["decay"][1]),
            "independent carrier decay",
        )
        ez = Q(1, 2**193) + Q(1, 2**224)
        pairs = set(r.carrier_pairs)
        for i in range(r.m):
            for j in range(r.m):
                if (min(i, j), max(i, j)) in pairs:
                    need(
                        abs(arb(Q(zw["midpoint"][i][j])) - ideal_Z[i, j]).upper().fmpq()
                        <= Q(1, 2**224),
                        "carrier midpoint budget",
                    )
                    need(
                        Q(after.Z_4[i][j]) == round_even(zw["midpoint"][i][j], 192),
                        "nearest-even signed carrier",
                    )
                else:
                    need(Q(after.Z_4[i][j]) == 0, "canonical off-star zero")
        error_Z = Z1 - ideal_Z
        need(
            step.carrier_component_error == str(ez) and upper(error_Z) <= ez,
            "complete carrier coordinate error",
        )
        held = r.read(C1, W, incoming["H"])["current"]
        restart_reference = r.read(C1, W1, r.I)["current"]
        need(
            all(
                Q(lo) <= x.lower().fmpq() <= x.upper().fmpq() <= Q(hi)
                for (lo, hi), x in zip(step.final_current, held.entries(), strict=True)
            ),
            "held geometry diagnostic",
        )
        need(
            all(
                Q(lo) <= x.lower().fmpq() <= x.upper().fmpq() <= Q(hi)
                for (lo, hi), x in zip(
                    step.reference_current, restart_reference.entries(), strict=True
                )
            ),
            "fresh reference diagnostic",
        )
        bound = None
        if certificate:
            need(certificate.operands["binding"]["role"] == role, "certificate role")
            U = matrix(certificate.operands["U"])
            components = eb + [el] * r.m
            uniform = max(
                sum(abs(U[i, j]) * components[j] for j in range(r.n + r.m))
                for i in range(U.nrows())
            )
            rho = Q(certificate.operands["carrier_radius"])
            uniform = max(uniform, r.m * ez / rho)
            actual = max(
                upper(arb_mat(U) * arb_mat(error_C.tolist() + error_L.tolist())),
                frobenius(error_Z) / rho,
            )
            need(
                actual
                <= uniform
                == Q(certificate.proof["full_step_error"])
                < Q(certificate.proof["image_margin"]),
                "independent full chart error",
            )
            bound = str(actual)
        return {
            "independent_precision_bits": 768,
            "exact_charge": True,
            "old_W_Z_selected_read": True,
            "joint_root_with_both_geometry_consumers": True,
            "same_root_for_geometry_and_carrier_writer": True,
            "same_selected_carrier_writer": True,
            "carrier_error_frobenius_upper": str(frobenius(error_Z)),
            "final_C_incoming_W_writer": True,
            "full_diagnostics_checked": not compact,
            "returned_full_read": True,
            "resource_error_upper": str(upper(error_C)),
            "log_conductance_error_upper": str(upper(error_L)),
            "full_chart_error_upper": bound,
        }

"""Independent A_PC pressure oracle, including zero-crossing polynomial intervals.

Fixed-H equations are assembled edge by edge by the independent A reference.
Carrier sources are literal star sums; no production writer or derivative is used.
"""

from hashlib import sha256

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

    def selected(self, C, W, Z):
        H = self.I + Z / 2
        read = self.read(C, W, H)
        return {"H": H, "selected": read, "source": self.source(read["causal_flat"])}

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
        == "spark_apc_arb256_flux128_conductance192_carrier192_v1",
        "A_PC numerical policy",
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
            "same_selected_carrier_writer": True,
            "carrier_error_frobenius_upper": str(frobenius(error_Z)),
            "final_C_incoming_W_writer": True,
            "full_diagnostics_checked": not compact,
            "returned_full_read": True,
            "resource_error_upper": str(upper(error_C)),
            "log_conductance_error_upper": str(upper(error_L)),
            "full_chart_error_upper": bound,
        }

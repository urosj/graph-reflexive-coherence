"""Independent A_CI selected-root, writer and complete C/logW error audit.

The shared reference assembles fixed-H equations edge by edge. This module
independently reconstructs the uniform Banach constants and selected root;
no production/research root, derivative or writer supplies expected values.
"""

from hashlib import sha256

from aos_native_spark_oracle import Reference as FixedHReference
from aos_native_spark_oracle import (
    classify as classify,  # noqa: PLC0414 - public exact predicate oracle
)
from aos_native_spark_oracle import contains, need, upper
from cos_native_spark_oracle import incidence, matrix, vector
from cpc_native_spark_pressure_oracle import round_even
from flint import arb, arb_mat, ctx
from flint import fmpq as Q


class Reference(FixedHReference):
    def __init__(self, graph):
        super().__init__(graph)
        B = incidence(graph)
        E = B.transpose() * B
        ell = max(sum(abs(E[i, j]) for j in range(self.m)) for i in range(self.m))
        self.overlap = [[len(set(a) & set(b)) for b in self.pairs] for a in self.pairs]
        S = Q(max(map(sum, self.overlap)), 8)
        r = Q(1, 32)
        h = S * r * r
        u = 1 / (1 - h)
        wl = Q(99, 100)
        wh = Q(101, 100)
        j = wh * (12 + ell * wh / 16 + ell * h / 16) / 1024
        g = 1 - (200 + j * j) / 65536
        a = max(wh - g, 1 - wl) / (wl + g)
        den = 1 - a / 4
        J = j / den
        M = u * a * J / 2
        jH = wh * ell / 16384
        qj = wh * j / (16384 * (wl + g) ** 2)
        Jj = 1 / den + j * qj / (4 * den**2)
        self.rate = 2 * S * r * u * ((a * Jj + J * qj) * jH / 2 + M)
        need(
            g > Q(1, 2) and M < r and self.rate < Q(1, 100000),
            "independent uniform root domain",
        )
        self.image = M

    def selected(self, C, W):
        # Separately implemented, high-precision root, with actual-input residual.
        cp = arb_mat([[x.mid()] for x in C.entries()])
        wp = arb_mat([[x.mid()] for x in W.entries()])
        f = arb_mat(self.m, 1)
        for _ in range(60):
            F = self.read(cp, wp, self.geometry(f))["causal_flat"]
            if upper(F - f) < Q(1, 2**640):
                break
            f = arb_mat([[x.mid()] for x in F.entries()])
        else:
            raise AssertionError("independent root iteration limit")
        rho = upper(self.read(C, W, self.geometry(f))["causal_flat"] - f) / (
            1 - self.rate
        )
        need(upper(f) + rho < Q(1, 32), "independent root ball")
        enclosed = arb_mat([[arb(x.fmpq(), rho)] for x in f.entries()])
        H = self.geometry(enclosed)
        return {"selected": self.read(C, W, H), "H": H, "flat": enclosed}

    def map(self, C, L):
        W = arb_mat([[x.exp()] for x in L.entries()])
        result = self.selected(C, W)
        J = result["selected"]["current"]
        after = C - 32 * self.B * J
        decay = (-arb(1)).exp()
        return arb_mat(
            after.tolist()
            + (decay * L + (1 - decay) * self.log_drive(after, W, J)).tolist()
        )


def audit_read(reference, state, payload, *, compact=False):
    need(
        payload["subject_digest"] == sha256(state.to_canonical_bytes()).hexdigest(),
        "complete C/W root subject",
    )
    C, W = arb_mat(vector(state.C)), arb_mat(vector(state.W_A))
    result = reference.selected(C, W)
    if not compact:
        need(
            contains(payload["H"], result["H"])
            and contains(payload["flat"], result["flat"]),
            "selected root and geometry",
        )
        need(
            set(payload["selected"]) == set(result["selected"]),
            "complete selected read",
        )
        for name, value in result["selected"].items():
            need(contains(payload["selected"][name], value), "selected " + name)
    need(
        Q(payload["domain"]["contraction"]) == reference.rate
        and Q(payload["domain"]["image_bound"]) == reference.image,
        "exact uniform root constants",
    )
    need(
        payload["domain"]["domain_id"] == "aci_quartic_C_W_flat_inf_ball_1_over_32_v1",
        "declared root domain",
    )
    proposal = arb_mat([[Q(row[0][0])] for row in payload["proposal"]])
    need(all(row[0][0] == row[0][1] for row in payload["proposal"]), "exact proposal")
    residual = upper(
        reference.read(C, W, reference.geometry(proposal))["causal_flat"] - proposal
    )
    need(
        residual <= Q(payload["proposal_residual"][1]), "actual-input proposal residual"
    )
    need(
        residual / (1 - reference.rate) <= Q(payload["root_error"][1]),
        "Banach root error",
    )
    need(
        upper(proposal) + Q(payload["root_error"][1]) < Q(1, 32),
        "root enclosure containment",
    )
    # The recorded enclosure must use exactly its declared radius.
    if not compact:
        for i, row in enumerate(payload["flat"]):
            need(
                Q(row[0][0]) <= proposal[i, 0].fmpq() - Q(payload["root_error"][1])
                and Q(row[0][1]) >= proposal[i, 0].fmpq() + Q(payload["root_error"][1]),
                "declared flat radius",
            )
    coefficient = arb(
        sum(Q(x, 8) ** 2 for row in reference.overlap for x in row)
    ).sqrt()
    joint = coefficient * (2 * upper(proposal) * residual + residual**2)
    need(
        joint.upper().fmpq()
        <= Q(payload["joint_residual_upper"])
        < Q(*(1e-11).as_integer_ratio()),
        "joint residual bound",
    )
    need(1 <= payload["iterations"] <= 60, "root proposal count")
    J = result["selected"]["current"]
    need(
        upper(arb_mat(vector(payload["current_midpoint"])) - J) <= Q(1, 2**192),
        "selected current midpoint",
    )
    inf = lambda A: max(
        sum(abs(A[i, j]).upper() for j in range(A.ncols())).upper().fmpq()
        for i in range(A.nrows())
    )
    need(
        reference.m * inf(result["H"]) * inf(result["H"].inv())
        <= Q(payload["conditioning_upper"])
        < 10**12,
        "root conditioning",
    )
    need(
        payload["numerical_policy_id"] == "spark_aci_arb256_flux128_conductance192_v1",
        "ACI numerical policy",
    )
    return result


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
            actual = upper(arb_mat(U) * arb_mat(error_C.tolist() + error_L.tolist()))
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
            "joint_root_complete": True,
            "final_C_incoming_W_writer": True,
            "full_diagnostics_checked": not compact,
            "returned_full_read": True,
            "resource_error_upper": str(upper(error_C)),
            "log_conductance_error_upper": str(upper(error_L)),
            "full_chart_error_upper": bound,
        }

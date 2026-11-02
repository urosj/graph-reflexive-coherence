"""Independent PC pressure algebra: exact fixed-H solves and Arb768 writer.

Only literal graph/state operands enter expectations. No native read, writer,
derivative, classifier or research PC evaluator supplies an expected result.
"""

import json
from hashlib import sha256

from flint import arb, arb_mat, ctx
from flint import fmpq as Q
from flint import fmpq_mat as M

from pygrc.models.grc_v4_certification import _ARB_CONTEXT_LOCK

POLICY = "spark_cpc_arb256_flux128_carrier192_v1"


def need(ok, message):
    if not ok:
        raise AssertionError(message)


def matrix(rows):
    return M([[Q(str(x)) for x in row] for row in rows])


def vector(values):
    return matrix([[x] for x in values])


def pack(A):
    return [[str(A[i, j]) for j in range(A.ncols())] for i in range(A.nrows())]


def intervals(A):
    return [
        [
            [str(A[i, j].lower().fmpq()), str(A[i, j].upper().fmpq())]
            for j in range(A.ncols())
        ]
        for i in range(A.nrows())
    ]


def decode(rows):
    def ball(p):
        lo, hi = map(Q, p)
        need(lo <= hi, "ordered finite interval")
        return arb((lo + hi) / 2, (hi - lo) / 2)

    return arb_mat([[ball(p) for p in row] for row in rows])


def encloses(rows, A):
    need(
        len(rows) == A.nrows() and all(len(row) == A.ncols() for row in rows),
        "complete coordinate coverage",
    )
    return all(
        Q(rows[i][j][0]) <= A[i, j] <= Q(rows[i][j][1])
        for i in range(A.nrows())
        for j in range(A.ncols())
    )


def contains_ball(rows, A):
    return encloses(
        rows,
        matrix(
            [
                [str(A[i, j].lower().fmpq()) for j in range(A.ncols())]
                for i in range(A.nrows())
            ]
        ),
    ) and encloses(
        rows,
        matrix(
            [
                [str(A[i, j].upper().fmpq()) for j in range(A.ncols())]
                for i in range(A.nrows())
            ]
        ),
    )


def norm2(A):
    return sum(x * x for x in A.entries())


def upper(A):
    return max(
        sum(abs(A[i, j]).upper().fmpq() for j in range(A.ncols()))
        for i in range(A.nrows())
    )


def frobenius(A):
    return sum(abs(x).upper() ** 2 for x in A.entries()).sqrt().upper()


class Equations:
    def __init__(self, graph):
        self.graph = graph
        nodes = graph["live_node_ids"]
        edges = graph.get("edges", graph.get("oriented_edges"))
        endpoints = [
            (e["tail"]["node_id"], e["head"]["node_id"])
            if "tail" in e
            else (e["tail_node_id"], e["head_node_id"])
            for e in edges
        ]
        self.B = M([[int(a == n) - int(b == n) for a, b in endpoints] for n in nodes])
        self.I = M(
            [[int(i == j) for j in range(len(edges))] for i in range(len(edges))]
        )
        A = M(
            [
                [abs(self.B[i, j]) for j in range(self.B.ncols())]
                for i in range(self.B.nrows())
            ]
        )
        self.L = self.B.transpose() * self.B
        self.O = A.transpose() * A
        self.pairs = tuple(
            (i, j)
            for i in range(len(edges))
            for j in range(i, len(edges))
            if self.O[i, j]
        )

    def read(self, C, Z):
        H = self.I + Z / 2
        return self.fixed(C, H)

    def fixed(self, C, H):
        site = M([[(x - 2) ** 3 - (x - 2)] for x in C.entries()])
        j0 = (
            -self.B.transpose()
            * (self.B * H * self.B.transpose() * C / 64 - site)
            / 1024
        )
        y = (3 * self.I / 4 + H * self.L).solve(j0)
        J = j0 + y / 4
        f = H.solve(y) / 2
        S = M(
            [
                [self.O[i, j] * f[i, 0] * f[j, 0] / 4 for j in range(self.I.nrows())]
                for i in range(self.I.nrows())
            ]
        )
        return {"H": H, "J": J, "flat": f, "S": S}

    def audit_read(self, state, payload):
        need(
            payload["subject_digest"] == sha256(state.to_canonical_bytes()).hexdigest(),
            "whole C/Z read identity",
        )
        need(
            payload["precision_bits"] == 256
            and payload["numerical_policy_id"] == POLICY,
            "fixed-H numerical policy",
        )
        exact = self.read(vector(state.C), matrix(state.Z_4))
        for key in ("H", "J", "flat", "S"):
            need(encloses(payload[key], exact[key]), "exact old-carrier read: " + key)
        for i, p in enumerate(payload["J"]):
            q = Q(payload["current_midpoint"][i])
            lo, hi = map(Q, p[0])
            need(
                lo <= q <= hi and max(q - lo, hi - q) <= Q(1, 2**192),
                "whole current midpoint budget",
            )
        H, J, f = (decode(payload[k]) for k in ("H", "J", "flat"))
        C = arb_mat(vector(state.C))
        B = arb_mat(self.B)
        site = arb_mat([[(x - 2) ** 3 - (x - 2)] for x in C.entries()])
        j0 = -B.transpose() * (B * H * B.transpose() * C / 64 - site) / 1024
        y = 2 * H * f
        defects = (
            (3 * arb_mat(self.I) / 4 + H * arb_mat(self.L)) * y - j0,
            J - j0 - y / 4,
        )
        need(
            all(frobenius(x) < arb(Q(1, 10**11)) for x in defects),
            "fixed-H equation residual",
        )
        need(
            0 <= Q(payload["residual_upper"]) < Q(1, 10**11),
            "declared residual admission",
        )
        need(
            0 < Q(payload["conditioning_upper"]) < 10**12,
            "declared conditioning admission",
        )

        def infnorm(A):
            return max(
                sum(abs(A[i, j]) for j in range(A.ncols())) for i in range(A.nrows())
            )

        h = exact["H"]
        a = 3 * self.I / 4 + h * self.L
        conditioning = self.I.nrows() * max(
            infnorm(a) * infnorm(a.inv()), infnorm(h) * infnorm(h.inv())
        )
        need(
            conditioning <= Q(payload["conditioning_upper"]),
            "independent conditioning bound",
        )
        need(norm2(exact["S"]) < Q(1, 64) ** 2, "independent source domain")
        return exact


def round_even(q, bits):
    q = Q(q) * 2**bits
    a, r = divmod(q.numerator, q.denominator)
    if 2 * r > q.denominator or (2 * r == q.denominator and a % 2):
        a += 1
    return Q(a, 2**bits)


def audit_writer(state, source, writer, after):
    Z = matrix(state.Z_4)
    a = (-arb(1)).exp()
    b = 1 - a
    expected = a * arb_mat(Z) + b * arb_mat(source)
    need(encloses(writer["source"], source), "same incoming held source")
    need(
        Q(writer["decay"][0]) <= a.lower().fmpq()
        and a.upper().fmpq() <= Q(writer["decay"][1]),
        "tau_PC exponential coefficient",
    )
    need(contains_ball(writer["ideal"], expected), "complete exponential writer")
    need(
        writer["consumed_state_digest"]
        == sha256(state.to_canonical_bytes()).hexdigest(),
        "held source subject identity",
    )
    for i, row in enumerate(writer["midpoint"]):
        for j, mid in enumerate(row):
            q = Q(mid)
            lo, hi = map(Q, writer["ideal"][i][j])
            need(
                lo <= q <= hi and max(q - lo, hi - q) <= Q(1, 2**224),
                "whole writer midpoint budget",
            )
            need(
                Q(after.Z_4[i][j]) == round_even(q, 192),
                "single represented carrier write",
            )
    error = arb_mat(matrix(after.Z_4)) - expected
    bound = Q(1, 2**193) + Q(1, 2**224)
    need(
        all(abs(x).upper().fmpq() <= bound for x in error.entries()),
        "complete carrier publication error",
    )
    return error


def audit_step(config, captured, step, certificate=None, role="current"):
    with _ARB_CONTEXT_LOCK, ctx.workprec(768):
        need(
            step.before == captured
            and captured.graph == config.reference.graph
            and step.after.graph == captured.graph,
            "immutable input and graph binding",
        )
        need(
            config.reference.profile.FAMILY == "C_PC"
            and step.profile_id == config.reference.profile.complete_profile_id,
            "explicit PC profile binding",
        )
        need(
            step.duration == "32"
            and step.numerical_policy_id == config.policy.numerical_policy_id == POLICY,
            "fixed duration and policy binding",
        )
        params = config.reference.profile.baseline.params_resolved
        need(
            params.realization.tau_PC == 32 and params.candidate.tau_C == 1,
            "separate PC and resolvent time constants",
        )
        eq = Equations(captured.graph.to_payload())
        exact = eq.audit_read(captured, step.consumed_read)
        eq.audit_read(step.after, step.restart_read)
        errZ = audit_writer(captured, exact["S"], step.writer, step.after)
        need(
            encloses(
                [[x] for x in step.final_current],
                eq.read(vector(step.after.C), matrix(captured.Z_4))["J"],
            ),
            "consumed-H diagnostic label",
        )
        need(
            vector(step.reference_current)
            == eq.read(vector(step.after.C), M(eq.I.nrows(), eq.I.ncols()))["J"],
            "exact reference diagnostic",
        )
        C, C1 = vector(captured.C), vector(step.after.C)
        need(
            all(
                Q(q) == round_even(mid, 128)
                for q, mid in zip(
                    step.flux, step.consumed_read["current_midpoint"], strict=True
                )
            ),
            "nearest-even conservative flux",
        )
        need(C1 == C - 32 * eq.B * vector(step.flux), "one conservative resource write")
        need(
            sum(C.entries())
            == sum(C1.entries())
            == Q(step.after.charge)
            == Q(captured.charge),
            "exact resource-only charge",
        )
        errC = C1 - (C - 32 * eq.B * exact["J"])
        need(
            all(
                abs(x) <= Q(b)
                for x, b in zip(
                    errC.entries(), step.componentwise_error_bounds, strict=True
                )
            ),
            "complete resource error",
        )
        need(
            Q(step.carrier_component_error) == Q(1, 2**193) + Q(1, 2**224),
            "carrier numerical budget",
        )
        result = {
            "exact_fixed_H_equations": True,
            "whole_writer": True,
            "full_returned_state": True,
            "carrier_coordinates": len(eq.pairs),
            "charge": captured.charge,
            "resource_error_max": str(max(map(abs, errC.entries()))),
            "carrier_error_F_upper": str(frobenius(errZ).upper().fmpq()),
        }
        if certificate:
            b = certificate.operands["binding"]
            need(
                b["role"] == role
                and b["profile"].to_dict() == config.reference.profile.to_payload()
                and b["policy"].to_dict() == config.policy.to_payload()
                and b["graph"].to_dict() == captured.graph.to_payload()
                and b["charge"] == captured.charge
                and b["state_channels"] == ("C", "Z_4"),
                "full-state certificate binding",
            )
            U = matrix(certificate.operands["U"])
            r = Q(certificate.operands["carrier_radius"])
            ec = max(map(abs, (U * errC).entries()))
            ez = (frobenius(errZ) / r).upper().fmpq()
            uniform = max(
                32
                * max(
                    sum(abs((U * eq.B)[i, j]) for j in range(eq.B.ncols()))
                    for i in range(U.nrows())
                )
                * (Q(1, 2**129) + Q(1, 2**192)),
                eq.B.ncols() * (Q(1, 2**193) + Q(1, 2**224)) / r,
            )
            need(
                max(ec, ez)
                <= uniform
                == Q(certificate.proof["full_step_error"])
                < Q(certificate.proof["image_margin"]),
                "independent joint uniform error budget",
            )
            result.update(
                resource_chart_error=str(ec),
                scaled_carrier_error=str(ez),
                uniform_error=str(uniform),
            )
        return result


def audit_event(source_config, target_config, event):
    archive = event["carrier_history"]["source_archive"]
    need(
        event["carrier_history"]["native_release"] is False,
        "event loss differs from release",
    )
    need(
        event["carrier_history"]["policy_id"] == "event_loss_and_zero_target_carrier_v1"
        and event["carrier_history"]["information_loss"] == "carrier_history_loss",
        "explicit event loss policy",
    )
    nodes = target_config.reference.graph.live_node_ids
    module = tuple(event["module"])
    for role in ("current", "reset"):
        before = getattr(source_config, role)
        after = getattr(target_config, role)
        need(
            archive[role] == before.to_payload(), "whole actual source archive: " + role
        )
        need(
            all(Q(x) == 0 for row in after.Z_4 for x in row),
            "whole target carrier zero: " + role,
        )
        values = dict(zip(before.graph.live_node_ids, map(Q, before.C), strict=True))
        resource = values["v"]
        expected = [0, resource / 64, 31 * resource / 32, resource / 64]
        for n, x in zip(nodes, map(Q, after.C), strict=True):
            need(
                x == (expected[module.index(n)] if n in module else values[n]),
                "literal role-specific allocation: " + role,
            )
        need(sum(map(Q, after.C)) == sum(values.values()), "event charge")
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            Equations(before.graph.to_payload()).audit_read(
                before, event["carrier_history"]["fresh_source_reads"][role]
            )
    content = {
        "schema_version": "grcv4-exact-carrier-history-v1",
        "subject": "carrier",
        "content": archive,
    }
    history_digest = (
        "grcv4-history-content-sha256:"
        + sha256(
            json.dumps(
                content, sort_keys=True, separators=(",", ":"), ensure_ascii=False
            ).encode()
        ).hexdigest()
    )
    need(
        event["carrier_history"]["history_policy"]["carrier"]["source_history_digest"]
        == history_digest,
        "retrievable whole-history digest",
    )
    return {
        "source_coordinates": len(
            Equations(source_config.reference.graph.to_payload()).pairs
        ),
        "target_coordinates": len(
            Equations(target_config.reference.graph.to_payload()).pairs
        ),
        "whole_archives": True,
        "whole_target_zero": True,
        "allocation": True,
    }

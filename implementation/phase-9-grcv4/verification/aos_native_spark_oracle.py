"""Independent A_OS equations, exact weighted predicates and full-map errors.

No production or research evaluator, writer, classifier or derivative supplies
expected values. The typed native step is only the evidence being checked.
"""

from hashlib import sha256

from cos_native_spark_oracle import incidence, matrix, vector
from cpc_native_spark_pressure_oracle import round_even
from flint import arb, arb_mat, ctx
from flint import fmpq as Q


def need(ok, message):
    if not ok:
        raise AssertionError(message)


def upper(A):
    return max(abs(x).upper().fmpq() for x in A.entries())


def contains(rows, A):
    return (
        len(rows) == A.nrows()
        and all(len(row) == A.ncols() for row in rows)
        and all(
            Q(rows[i][j][0])
            <= A[i, j].lower().fmpq()
            <= A[i, j].upper().fmpq()
            <= Q(rows[i][j][1])
            for i in range(A.nrows())
            for j in range(A.ncols())
        )
    )


class Reference:
    def __init__(self, graph):
        self.graph = graph
        self.nodes = graph["live_node_ids"]
        self.edges = graph["edges"]
        self.n, self.m = len(self.nodes), len(self.edges)
        self.B = arb_mat(incidence(graph))
        self.I = arb_mat([[int(i == j) for j in range(self.m)] for i in range(self.m)])
        self.pairs = [
            (
                self.nodes.index(e["tail"]["node_id"]),
                self.nodes.index(e["head"]["node_id"]),
            )
            for e in self.edges
        ]
        self.terms = [[[] for _ in range(3)] for _ in self.nodes]
        for k, e in enumerate(self.edges):
            for a, b in ((e["tail"], e["head"]), (e["head"], e["tail"])):
                self.terms[self.nodes.index(a["node_id"])][(a["port"] - 1) // 3].append(
                    (k, self.nodes.index(b["node_id"]))
                )

    def rows(self, C, W):
        return [
            [
                sum((W[k, 0] * (C[j, 0] - C[i, 0]) for k, j in row), arb(0))
                / sum((W[k, 0] for k, j in row), arb(0))
                if row
                else arb(0)
                for row in terms
            ]
            for i, terms in enumerate(self.terms)
        ]

    def log_drive(self, C, W, J):
        D = self.rows(C, W)
        values = []
        for k, (i, j) in enumerate(self.pairs):
            value = (
                -(
                    C[i, 0]
                    + C[j, 0]
                    + sum((D[i][a] - D[j][a]) ** 2 for a in range(3))
                    + J[k, 0] ** 2
                )
                / 65536
            )
            need(value > -arb(2).log(), "independent inactive floor")
            values.append([value])
        return arb_mat(values)

    def read(self, C, W, H):
        # Assemble the two Laplacian contributions edge by edge, separately
        # from production's matrix expression; transport uses incoming W.
        delta = self.B.transpose() * C
        p = arb_mat([[-((C[i, 0] - 2) ** 3 - (C[i, 0] - 2))] for i in range(self.n)])
        for k, (i, j) in enumerate(self.pairs):
            transfer = W[k, 0] * delta[k, 0] / 64
            p[i, 0] += transfer
            p[j, 0] -= transfer
        geometry = (H - self.I) * delta / 64
        p += self.B * geometry
        base = arb_mat(
            [
                [-W[k, 0] * (p[i, 0] - p[j, 0]) / 1024]
                for k, (i, j) in enumerate(self.pairs)
            ]
        )
        logs = self.log_drive(C, W, base)
        G = arb_mat([[x.exp()] for x in logs.entries()])
        q = arb_mat(
            [[(W[k, 0] - G[k, 0]) / (W[k, 0] + G[k, 0])] for k in range(self.m)]
        )
        # Equivalent closure J = 4 (W+G) j0 / (3W+5G).
        J = arb_mat(
            [
                [4 * (W[k, 0] + G[k, 0]) * base[k, 0] / (3 * W[k, 0] + 5 * G[k, 0])]
                for k in range(self.m)
            ]
        )
        flat = H.inv() * arb_mat([[q[k, 0] * J[k, 0] / 2] for k in range(self.m)])
        return {
            "potential": p,
            "baseline": base,
            "drive": G,
            "q": q,
            "current": J,
            "causal_flat": flat,
        }

    def geometry(self, flat):
        H = arb_mat(self.I)
        # Literal sum of vertex-star rank-one contributions.
        for node in range(self.n):
            active = [k for k, pair in enumerate(self.pairs) if node in pair]
            for i in active:
                for j in active:
                    H[i, j] += flat[i, 0] * flat[j, 0] / 8
        return H

    def selected(self, C, W):
        pred = self.read(C, W, self.I)
        H = self.geometry(pred["causal_flat"])
        corr = self.read(C, W, H)
        return {"predictor": pred, "corrector": corr, "H": H}

    def map(self, C, L):
        W = arb_mat([[x.exp()] for x in L.entries()])
        selected = self.selected(C, W)
        J = selected["corrector"]["current"]
        after = C - 32 * self.B * J
        d = (-arb(1)).exp()
        log_after = d * L + (1 - d) * self.log_drive(after, W, J)
        return arb_mat(after.tolist() + log_after.tolist())


def audit_read(reference, state, payload):
    need(
        payload["subject_digest"] == sha256(state.to_canonical_bytes()).hexdigest(),
        "complete C/W read subject",
    )
    C, W = arb_mat(vector(state.C)), arb_mat(vector(state.W_A))
    result = reference.selected(C, W)
    need(contains(payload["H"], result["H"]), "literal star geometry")
    for stage in ("predictor", "corrector"):
        need(set(payload[stage]) == set(result[stage]), "complete read tuple")
        for name, value in result[stage].items():
            need(contains(payload[stage][name], value), stage + " " + name)
    J = result["corrector"]["current"]
    need(
        upper(arb_mat(vector(payload["current_midpoint"])) - J) <= Q(1, 2**192),
        "current midpoint budget",
    )
    split = (
        sum(
            abs(x).upper() ** 2
            for x in (
                result["H"] - reference.geometry(result["corrector"]["causal_flat"])
            ).entries()
        )
    ).sqrt()
    need(
        split.upper().fmpq()
        <= Q(payload["split_upper"])
        < Q(*(1e-11).as_integer_ratio()),
        "split bound",
    )
    H = result["H"]
    hi = H.inv()
    inf = lambda A: max(
        sum(abs(A[i, j]).upper() for j in range(A.ncols())).upper().fmpq()
        for i in range(A.nrows())
    )
    need(
        reference.m * inf(H) * inf(hi) <= Q(payload["conditioning_upper"]) < 10**12,
        "conditioning bound",
    )
    need(
        payload["numerical_policy_id"] == "spark_aos_arb256_flux128_conductance192_v1",
        "numerical policy",
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
        if compact:
            reads = []
            for state, payload in (
                (before, step.consumed_read),
                (after, step.restart_read),
            ):
                need(
                    payload["subject_digest"]
                    == sha256(state.to_canonical_bytes()).hexdigest(),
                    "complete compact C/W subject",
                )
                value = r.selected(arb_mat(vector(state.C)), arb_mat(vector(state.W_A)))
                need(
                    upper(
                        arb_mat(vector(payload["current_midpoint"]))
                        - value["corrector"]["current"]
                    )
                    <= Q(1, 2**192),
                    "compact current midpoint",
                )
                reads.append(value)
            incoming = reads[0]
        else:
            incoming = audit_read(r, before, step.consumed_read)
            audit_read(r, after, step.restart_read)
        J = incoming["corrector"]["current"]
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
            "predictor_corrector_complete": True,
            "final_C_incoming_W_writer": True,
            "full_diagnostics_checked": not compact,
            "returned_full_read": True,
            "resource_error_upper": str(upper(error_C)),
            "log_conductance_error_upper": str(upper(error_L)),
            "full_chart_error_upper": bound,
        }


def classify(graph, values, weights, policy):
    """Exhaustive reachability, including unqualified terminals, then domains."""
    nodes = graph["live_node_ids"]
    C = dict(zip(nodes, map(Q, values), strict=True))
    sign = policy["landscape_sign"]
    adjacency = {n: set() for n in nodes}
    terms = {n: [[], [], []] for n in nodes}
    for edge, weight in zip(graph["edges"], map(Q, weights), strict=True):
        a, b = edge["tail"], edge["head"]
        for here, there in ((a, b), (b, a)):
            x, y = here["node_id"], there["node_id"]
            adjacency[x].add(y)
            terms[x][(here["port"] - 1) // 3].append((weight, C[y] - C[x]))
    down = {x: {y for y in adjacency[x] if sign * (C[y] - C[x]) < 0} for x in nodes}
    terminals = {}
    for start in nodes:
        pending, seen, ends = [start], set(), set()
        while pending:
            x = pending.pop()
            if x in seen:
                continue
            seen.add(x)
            if down[x]:
                pending.extend(down[x])
            else:
                ends.add(x)
        terminals[start] = tuple(x for x in nodes if x in ends)
    rows, anchors = [], set()
    for x in nodes:
        means = [
            sum(w * v for w, v in row) / sum(w for w, v in row) if row else Q(0)
            for row in terms[x]
        ]
        squared, minimum = sum(g * g for g in means), min(sign * g for g in means)
        seed = squared < Q(policy["epsilon_gradient"]) ** 2 and minimum > Q(
            policy["epsilon_Hessian"]
        )
        anchor = (
            seed
            and bool(adjacency[x])
            and C[x] > Q(policy["minimum_resource"])
            and all(sign * (C[y] - C[x]) > Q(policy["contrast"]) for y in adjacency[x])
        )
        rows.append(
            {
                "node_id": x,
                "gradient": list(map(str, means)),
                "gradient_squared": str(squared),
                "minimum_signed_gradient": str(minimum),
                "seed": seed,
                "anchor": anchor,
                "evaluation_error": "0",
            }
        )
        if anchor:
            anchors.add(x)
    domains = [
        (a, tuple(x for x in nodes if terminals[x] == (a,)))
        for a in nodes
        if a in anchors
    ]
    return (
        tuple((a, members) for a, members in domains if len(members) > 1),
        tuple(terminals.items()),
        rows,
    )

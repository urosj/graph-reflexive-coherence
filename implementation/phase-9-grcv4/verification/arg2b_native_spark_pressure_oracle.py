"""Independent joint-map pressure arithmetic; no native increment/writer helpers.

Manufactured finite chains contain outward transcendental enclosures. They are
Gamma_N controls, not exact rational solutions or replacements for the tail.
"""

from functools import lru_cache
from hashlib import sha256

from arg2b_native_spark_oracle import model, proof_read
from crg2b_native_spark_oracle import decoded, encoded, need, norm, vector
from flint import arb, arb_mat, ctx
from flint import fmpq as Q
from flint import fmpq_mat as M

from pygrc.models.grc_v4_codec import canonical_json_bytes
from pygrc.models.grc_v4_state import FrozenJSONMap


def algebra(graph):
    nodes = graph["live_node_ids"]
    edges = {e["edge_id"]: e for e in graph["edges"]}
    ordered = [edges[e] for e in [e["edge_id"] for e in graph["edges"]]]
    B = M(
        [
            [
                int(e["tail"]["node_id"] == n) - int(e["head"]["node_id"] == n)
                for e in ordered
            ]
            for n in nodes
        ]
    )
    I = M([[int(i == j) for j in range(B.ncols())] for i in range(B.ncols())])
    absolute = M([[abs(x) for x in r] for r in B.tolist()])
    A = B * B.transpose()
    P = (A + M([[Q(1, len(nodes))] * len(nodes) for _ in nodes])).inv()
    return B, I, absolute.transpose() * absolute, P


def clip(graph, X):
    charts = model(graph).domain["resource_agreement"]
    n = len(graph["live_node_ids"])
    values = []
    for i, x in enumerate(X.entries()):
        lo, hi = (
            map(Q, charts[graph["live_node_ids"][i]])
            if i < n
            else (Q(-1, 16), Q(1, 16))
        )
        a, b = max(lo, min(hi, x.lower().fmpq())), max(lo, min(hi, x.upper().fmpq()))
        values.append([arb((a + b) / 2, (b - a) / 2)])
    return arb_mat(values)


def fixed(
    graph,
    X,
    H,
    *,
    retract=True,
    duration=16,
    decay=None,
    post_clip=False,
    writer_baseline=False,
    freeze_history=False,
    potential_H=True,
    lowering_H=True,
):
    """Literal endpoints/ports equations, including both distinct writer stages."""
    Bq, Iq, Oq, _ = algebra(graph)
    B, I, O = arb_mat(Bq), arb_mat(Iq), arb_mat(Oq)
    n, m = B.nrows(), B.ncols()
    x = clip(graph, X) if retract else X
    C = arb_mat([[x[i, 0]] for i in range(n)])
    Y = arb_mat([[x[n + i, 0]] for i in range(m)])
    W = arb_mat([[(v / 64).exp()] for v in Y.entries()])
    nodes = graph["live_node_ids"]
    index = {v: i for i, v in enumerate(nodes)}
    byid = {e["edge_id"]: e for e in graph["edges"]}
    edges = [byid[e] for e in [e["edge_id"] for e in graph["edges"]]]
    pairs = [(index[e["tail"]["node_id"]], index[e["head"]["node_id"]]) for e in edges]
    terms = [[[] for _ in range(3)] for _ in nodes]
    for k, e in enumerate(edges):
        for a, b in ((e["tail"], e["head"]), (e["head"], e["tail"])):
            terms[index[a["node_id"]]][(a["port"] - 1) // 3].append(
                (k, index[b["node_id"]])
            )

    def rows(c):
        return [
            [
                sum((W[k, 0] * (c[j, 0] - c[i, 0]) for k, j in r), arb(0))
                / sum((W[k, 0] for k, j in r), arb(0))
                if r
                else arb(0)
                for r in node
            ]
            for i, node in enumerate(terms)
        ]

    def writer(c, j):
        D = rows(c)
        ex = arb_mat(
            [
                [
                    -(
                        c[u, 0]
                        + c[v, 0]
                        + sum((D[u][r] - D[v][r]) ** 2 for r in range(3))
                        + j[k, 0] ** 2
                    )
                    / 65536
                ]
                for k, (u, v) in enumerate(pairs)
            ]
        )
        need(
            all(e > -arb(2).log() for e in ex.entries()),
            "independent inactive floor branch",
        )
        return ex, arb_mat([[e.exp()] for e in ex.entries()]), D

    lap = (
        B
        * arb_mat([[W[i, 0] if i == j else 0 for j in range(m)] for i in range(m)])
        * B.transpose()
        * C
    )
    if potential_H:
        lap += B * (H - I) * B.transpose() * C
    phi = lap / 64 - arb_mat([[(c - 2) ** 3 - (c - 2)] for c in C.entries()])
    baseline = arb_mat(
        [[-W[k, 0] * (phi[u, 0] - phi[v, 0]) / 1024] for k, (u, v) in enumerate(pairs)]
    )
    read_exponent, G, D = writer(C, baseline)
    theta = arb_mat([[(W[k, 0] - G[k, 0]) / (W[k, 0] + G[k, 0])] for k in range(m)])
    J = arb_mat([[baseline[k, 0] / (1 - theta[k, 0] / 4)] for k in range(m)])
    rhs = arb_mat([[theta[k, 0] * J[k, 0] / 2] for k in range(m)])
    flat = H.solve(rhs) if lowering_H else rhs
    generated = I + arb_mat(
        [[O[i, j] * flat[i, 0] * flat[j, 0] / 8 for j in range(m)] for i in range(m)]
    )
    finalC = C - duration * B * J
    writerC = finalC
    if post_clip:
        cl = clip(graph, arb_mat(finalC.tolist() + Y.tolist()))
        writerC = arb_mat([[cl[i, 0]] for i in range(n)])
    exponent, drive, finalD = writer(writerC, baseline if writer_baseline else J)
    a = (-arb(Q(duration, 32))).exp() if decay is None else decay
    incrementY = (1 - a) * (64 * exponent - Y)
    if freeze_history:
        incrementY = arb_mat(m, 1)
    increment = arb_mat((-duration * B * J).tolist() + incrementY.tolist())
    return {
        "X": X + increment,
        "increment": increment,
        "H": generated,
        "J": J,
        "flat": flat,
        "baseline": baseline,
        "potential": phi,
        "read_drive": G,
        "read_exponent": read_exponent,
        "theta": theta,
        "writer_exponent": exponent,
        "writer_drive": drive,
        "writer_C": writerC,
        "writer_W": W,
        "C": C,
        "Y": Y,
        "W": W,
        "rows": D,
        "writer_rows": finalD,
    }


def block_norm(X, start, end):
    return norm(arb_mat([[X[i, 0]] for i in range(start, end)]))


def chain_residuals(graph, rows):
    n = len(graph["live_node_ids"])
    d = n + len([e["edge_id"] for e in graph["edges"]])
    rc, ry, rh = arb(0), arb(0), arb(0)
    detail = []
    for i in range(1, len(rows)):
        X, H = decoded(rows[i]["X"]), decoded(rows[i]["H"])
        value = fixed(graph, X, H)
        difference = value["X"] - decoded(rows[i - 1]["X"])
        a, b, c = (
            block_norm(difference, 0, n),
            block_norm(difference, n, d),
            norm(value["H"] - decoded(rows[i - 1]["H"])),
        )
        rc, ry, rh = max(rc, a), max(ry, b), max(rh, c)
        detail.append([str(z.upper().fmpq()) for z in (a, b, c)])
    return rc, ry, rh, detail


def manufactured(graph, depth):
    m = model(graph)
    chart = m.domain["resource_agreement"]
    C = [(Q(chart[v][0]) + Q(chart[v][1])) / 2 for v in graph["live_node_ids"]]
    X = arb_mat([[c] for c in C] + [[Q((-1) ** i, 128)] for i in range(m.m)])
    H = arb_mat(algebra(graph)[1])
    rows = [{"X": encoded(X), "H": encoded(H)}]
    for _ in range(depth):
        f = fixed(graph, X, H)
        X, H = f["X"], f["H"]
        rows.append({"X": encoded(X), "H": encoded(H)})
    value = {
        "depth": depth,
        "precision_bits": ctx.prec,
        "finite_only": True,
        "rows": list(reversed(rows)),
        "residual_allowance": str(Q(1, 2**650)),
        "conversion": "outward_Arb_intervals_no_exact_solution_claim",
    }
    return sealed(value)


def sealed(value):
    body = {k: v for k, v in value.items() if k != "record_digest"}
    return dict(body, record_digest=sha256(canonical_json_bytes(body)).hexdigest())


def manufactured_check(graph, value):
    need(value == sealed(value), "manufactured seal")
    need(
        value["depth"] in (1, 2) and len(value["rows"]) == value["depth"] + 1,
        "finite depth",
    )
    need(
        value["finite_only"] is True and value["precision_bits"] == 768,
        "finite enclosure scope",
    )
    B, I, _O, _ = algebra(graph)
    n, m = B.nrows(), B.ncols()
    allowance = arb(Q(1, 2**650))
    need(Q(value["residual_allowance"]) == Q(1, 2**650), "fixed fixture allowance")
    for row in value["rows"]:
        X, H = decoded(row["X"]), decoded(row["H"])
        need(
            (X.nrows(), X.ncols(), H.nrows(), H.ncols()) == (n + m, 1, m, m),
            "complete joint fixture",
        )
        need(norm(H - arb_mat(I)) < arb(Q(1, 1024)), "fixture H ball")
        need(all(x.is_finite() for x in X.entries()), "finite fixture coordinates")
    need(decoded(value["rows"][-1]["H"]) == arb_mat(I), "fixture terminal I")
    rc, ry, rh, detail = chain_residuals(graph, value["rows"])
    need(rc < allowance, "manufactured resource residual")
    need(ry < allowance, "manufactured history residual")
    need(rh < allowance, "manufactured geometry residual")
    return {
        "depth": value["depth"],
        "residual_blocks": detail,
        "infinite_section_claimed": False,
    }


def audit_read(graph, profile, state, witness):
    """Own every inverse C/Y residual; common checker supplies global theorem bounds."""
    len(graph["live_node_ids"])
    _B, I, O, _ = algebra(graph)
    m = I.nrows()
    need(
        witness["graph"].to_dict() == graph
        and witness["profile"].to_dict() == profile
        and witness["state"].to_dict() == state.to_payload(),
        "external full C/W binding",
    )
    H = decoded(witness["proposal"])
    need(all(x.rad() == 0 and x.is_finite() for x in H.entries()), "exact proposal H")
    need(
        all(H[i, j] == 0 for i in range(m) for j in range(m) if not O[i, j]),
        "query star support",
    )
    rows = [{"X": encoded(vector(witness["query_proposal"])), "H": encoded(H)}]
    pairs = [(i, j) for i in range(m) for j in range(i, m) if O[i, j]]
    for item in witness["chain"]:
        H = arb_mat(m, m)
        for (i, j), x in zip(pairs, item["H"], strict=True):
            H[i, j] = H[j, i] = arb(Q(x))
        rows.append({"X": encoded(vector(item["X"])), "H": encoded(H)})
    need(len(rows) == 17, "sixteen joint inverse levels")
    rc, ry, rh, detail = chain_residuals(graph, rows)
    for item, values in zip(witness["chain"], detail, strict=True):
        need(
            max(Q(values[0]), Q(values[1])) <= Q(item["state_residual"][1]),
            "independent C/Y inverse residual",
        )
        need(
            Q(values[2]) <= Q(item["geometry_residual"][1]),
            "independent geometry residual",
        )
    for name, actual in (("state_residual", max(rc, ry)), ("geometry_residual", rh)):
        need(actual <= arb(Q(witness[name][1])), "reported full maximum " + name)
    proof = proof_read(graph, profile, state, witness)
    X = state_X(state)
    independent = fixed(graph, X, decoded(proof["H"]), retract=False)
    keys = {
        "potential": "potential",
        "baseline": "baseline",
        "drive": "read_drive",
        "q": "theta",
        "current": "J",
        "causal_flat": "flat",
    }
    for key, other in keys.items():
        need(
            overlaps(decoded(witness["selected"][key]), independent[other]),
            "literal independent selected " + key,
        )
    return proof, {
        "resource_residual_upper": str(rc.upper().fmpq()),
        "history_residual_upper": str(ry.upper().fmpq()),
        "geometry_residual_upper": str(rh.upper().fmpq()),
        "history_coordinates_checked": 16 * m,
    }


def overlaps(A, B):
    return (
        A.nrows() == B.nrows()
        and A.ncols() == B.ncols()
        and all(a.overlaps(b) for a, b in zip(A.entries(), B.entries(), strict=True))
    )


def state_X(state):
    return arb_mat(
        [[Q(c)] for c in state.C] + [[64 * arb(Q(w)).log()] for w in state.W_A]
    )


@lru_cache(maxsize=8)
def fresh_X(graph_bytes, input_bytes):
    import json

    graph = json.loads(graph_bytes)
    X = decoded(json.loads(input_bytes))
    m = model(graph)
    scale = 2**384
    point = arb_mat(
        [
            [Q((x.mid().fmpq().numerator * scale) // x.mid().fmpq().denominator, scale)]
            for x in X.entries()
        ]
    )
    section = m.section(point)
    error = (section["error"] + arb(Q(1, 256)) * norm(X - point)).upper().fmpq()
    H = arb_mat(m.m, m.m)
    for i in range(m.m):
        for j in range(m.m):
            if m.overlap[i][j]:
                H[i, j] = arb(section["proposal"][i, j].fmpq(), error)
    return FrozenJSONMap(
        {"H": encoded(H), "input_shift": str(norm(X - point).upper().fmpq())}
    )


def fresh(graph, X):
    return decoded(
        fresh_X(canonical_json_bytes(graph), canonical_json_bytes(encoded(X)))["H"]
    )


def time_shift(graph, profile, state, witness):
    proof, _ = audit_read(graph, profile, state, witness)
    X = state_X(state)
    H = decoded(proof["H"])
    exact = fixed(graph, X, H, retract=False)
    nextH = fresh(graph, exact["X"])
    need(overlaps(nextH, exact["H"]), "joint unrounded time-shift identity")
    need(not overlaps(H, exact["H"]), "resolved consumed/generated distinction")
    n = len(state.C)
    stale = arb_mat(exact["X"].tolist()[:n] + X.tolist()[n:])
    staleH = fresh(graph, stale)
    need(not overlaps(staleH, exact["H"]), "stale-history time shift rejected")
    return {
        "unrounded_X": encoded(exact["X"]),
        "generated": encoded(exact["H"]),
        "fresh_next_H": encoded(nextH),
        "stale_history_H": encoded(staleH),
        "duration": "16",
        "full_history_query": True,
        "enclosure_comparison_not_new_theorem": True,
    }


def joint_distances(graph, curve, X, parameter):
    s = Q(parameter)
    need(0 <= s <= 1, "shared parameter range")
    Qc = M(curve)
    t = [Q(1), 2 * s - 1]
    for _ in range(2, Qc.ncols()):
        t.append(2 * t[1] * t[-1] - t[-2])
    point = arb_mat(Qc * M([[x] for x in t[: Qc.ncols()]]))
    delta = X - point
    n = len(graph["live_node_ids"])
    C = arb_mat(delta.tolist()[:n])
    Y = arb_mat(delta.tolist()[n:])
    P = arb_mat(algebra(graph)[3])
    return (C.transpose() * P * C)[0, 0], sum(y * y for y in Y.entries())


def joint_membership(graph, curve, X, parameter, radius="1/4096"):
    radius = Q(radius)
    c, y = joint_distances(graph, curve, X, parameter)
    need(
        c <= arb(radius**2) and y <= arb(radius**2),
        "shared-parameter full product norm",
    )
    return [str(z.upper().fmpq()) for z in (c, y)]


def step_error(graph, state, step, H):
    exact = fixed(graph, state_X(state), H, retract=False)
    delta = state_X(step.after) - exact["X"]
    n = len(state.C)
    dc = arb_mat(delta.tolist()[:n])
    dy = arb_mat(delta.tolist()[n:])
    c = (
        (dc.transpose() * arb_mat(algebra(graph)[3]) * dc)[0, 0]
        .nonnegative_part()
        .sqrt()
    )
    y = sum(v * v for v in dy.entries()).nonnegative_part().sqrt()
    return c, y, exact

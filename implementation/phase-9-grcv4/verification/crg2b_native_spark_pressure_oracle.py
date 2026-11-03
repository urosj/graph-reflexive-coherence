"""Independent exact finite-chain and externally bound C_RG2b pressure checks.

The manufactured chains are finite Gamma_N subjects, never substitutes for the
infinite section. Rational arithmetic is used only at depths one and two.
"""

from crg2b_native_spark_oracle import (
    decoded,
    encoded,
    model,
    need,
    norm,
    proof_read,
    reference,
    selected,
    vector,
)
from flint import arb
from flint import fmpq as Q
from flint import fmpq_mat as M

from pygrc.models.grc_v4_codec import canonical_json_bytes
from pygrc.models.grc_v4_spark_state import CRG2B_NUMERICAL_POLICY


def algebra(graph):
    B = M(
        [
            [
                int(e["tail"]["node_id"] == n) - int(e["head"]["node_id"] == n)
                for e in graph["edges"]
            ]
            for n in graph["live_node_ids"]
        ]
    )
    I = M([[int(i == j) for j in range(B.ncols())] for i in range(B.ncols())])
    absolute = M([[abs(x) for x in row] for row in B.tolist()])
    O = absolute.transpose() * absolute
    A = B * (I + (3 * I / 4 + B.transpose() * B).inv() / 4) * B.transpose()
    P = (A + M([[Q(1, B.nrows())] * B.nrows() for _ in range(B.nrows())])).inv()
    return B, I, O, A, P


def fixed(graph, X, H, *, retract=True):
    """Literal rational equations, separately assembled from oriented endpoints."""
    B, I, O, _, _ = algebra(graph)
    lo, hi = (Q(1, 2), Q(7, 2)) if B.nrows() == 12 else (Q(-1, 16), Q(65, 16))
    C = M([[max(lo, min(hi, x)) if retract else x] for x in X.entries()])
    site = M([[(x - 2) ** 3 - (x - 2)] for x in C.entries()])
    j0 = -B.transpose() * (B * H * B.transpose() * C / 64 - site) / 1024
    y = (3 * I / 4 + H * B.transpose() * B).solve(j0)
    J = j0 + y / 4
    f = H.solve(y) / 2
    generated = I + M(
        [
            [O[i, j] * f[i, 0] * f[j, 0] / 8 for j in range(I.ncols())]
            for i in range(I.nrows())
        ]
    )
    return {"X": X - 8 * B * J, "H": generated, "J": J, "flat": f, "j0": j0}


def manufactured(graph, depth):
    n = len(graph["live_node_ids"])
    X = M(
        [
            [Q(2) + (Q(1, 16) if i == 0 else -Q(1, 16) if i == 1 else 0)]
            for i in range(n)
        ]
    )
    H = algebra(graph)[1]
    rows = [{"X": X, "H": H}]
    for _ in range(depth):
        row = fixed(graph, X, H)
        X, H = row["X"], row["H"]
        rows.append({"X": X, "H": H})
    return [
        {key: [[str(x) for x in r] for r in v.tolist()] for key, v in row.items()}
        for row in reversed(rows)
    ]


def exact_chain(graph, rows):
    B, I, O, _, _ = algebra(graph)
    need(len(rows) in (2, 3), "manufactured depth one or two")
    charge = None
    for i, row in enumerate(rows):
        X, H = M(row["X"]), M(row["H"])
        need(X.nrows() == B.nrows() and X.ncols() == 1, "inverse dimension")
        need(H == H.transpose(), "manufactured symmetry")
        need(
            all(
                H[j, k] == 0
                for j in range(H.nrows())
                for k in range(H.ncols())
                if not O[j, k]
            ),
            "manufactured star support",
        )
        need(
            max(sum(abs(x) for x in r) for r in (H - I).tolist()) < Q(1, 1024),
            "manufactured induced infinity radius and SPD",
        )
        if charge is None:
            charge = sum(X.entries())
        need(sum(X.entries()) == charge, "inverse exact charge")
        if i:
            actual = fixed(graph, X, H)
            need(actual["X"] == M(rows[i - 1]["X"]), "inverse state equation")
            need(actual["H"] == M(rows[i - 1]["H"]), "inverse geometry equation")
    need(M(rows[-1]["H"]) == I, "identity terminal")
    return {
        "depth": len(rows) - 1,
        "charge": str(charge),
        "exact_residuals": True,
        "infinite_section_claimed": False,
    }


def audit_read(graph, profile, state, witness):
    """External subject and fixed declarations precede numerical chain checking."""
    need(
        witness["numerical_policy_id"] == CRG2B_NUMERICAL_POLICY,
        "duration-8 numerical policy",
    )
    m = model(graph)
    domain = witness["completion"].to_dict()
    need(domain["schema"] == "native-spark-crg2b-domain-v1", "completion schema")
    for key, value in m.domain.items():
        if key not in ("schema", "section_tail", "contained_image", "selector"):
            need(domain.get(key) == value, "completion declaration: " + key)
    # The research manifest publishes only 112-bit image endpoints. Recompute
    # its extrema before publication rounding to audit the native 256-bit ones.
    km = list(map(reference.F, domain["K_minus"]))
    if m.n == 12:
        displacement = Q(domain["global_displacement"])
        image = (arb(Q(str(km[0])) - displacement), arb(Q(str(km[1])) + displacement))
    else:
        left, right = reference.polynomial_image(m.algebra, *km)
        correction = arb(Q(domain["A_H"]) / 1024)
        image = (left - correction, right + correction)
    need(
        Q(domain["contained_image"][0]) <= image[0].lower().fmpq()
        and image[1].upper().fmpq() <= Q(domain["contained_image"][1]),
        "outward whole-image containment",
    )
    need(
        domain["selector"]
        == {
            "nonconstant_eigenvalue_lower": m.domain["selector"][
                "nonconstant_eigenvalue_lower"
            ]
        },
        "selector bound",
    )
    q, V = (
        Q(m.domain["graph_transform_contraction"]),
        Q(m.domain["section_value_radius"]),
    )
    need(Q(domain["section_tail"]) == q**32 * V, "native depth32 tail")
    H = decoded(witness["proposal"])
    need(
        all(x.is_finite() and x.rad() == 0 for x in H.entries()),
        "point geometry proposal",
    )
    need(
        H == H.transpose() and norm(H - m.I) < arb(Q(1, 1024)),
        "query geometry SPD ball",
    )
    need(
        all(
            H[i, j] == 0 for i in range(m.m) for j in range(m.m) if not m.overlap[i][j]
        ),
        "query geometry support",
    )
    for label in ("state_residual", "geometry_residual"):
        need(
            all(Q(row[label][1]) <= Q(witness[label][1]) for row in witness["chain"]),
            "reported maximum " + label,
        )
    return proof_read(graph, profile, state, witness)


def time_shift(graph, profile, state, witness):
    proved = audit_read(graph, profile, state, witness)
    m = model(graph)
    C, H, J, flat = (
        vector(state.C),
        decoded(proved["H"]),
        decoded(proved["J"]),
        decoded(proved["flat"]),
    )
    post = C - 8 * m.B * J
    # Fresh depth40 at an exact centre, extended to the entire unrounded image.
    centre = tuple(str(x.mid().fmpq()) for x in post.entries())
    fresh = selected(canonical_json_bytes(graph), centre)
    shift = (arb(Q(1, 256)) * norm(post - vector(centre))).upper().fmpq()
    next_H = decoded(fresh["H"])
    for i in range(m.m):
        for j in range(m.m):
            if m.overlap[i][j]:
                next_H[i, j] += arb(0, shift)
    generated = m.geometry(flat)
    need(
        all(
            a.overlaps(b)
            for a, b in zip(generated.entries(), next_H.entries(), strict=True)
        ),
        "time-shift section identity",
    )
    need(
        any(
            not a.overlaps(b)
            for a, b in zip(generated.entries(), H.entries(), strict=True)
        ),
        "resolved nonstationary generated/consumed distinction",
    )
    return {
        "unrounded_next_state": encoded(post),
        "generated": encoded(generated),
        "fresh_next_section": encoded(next_H),
        "input_shift": str(shift),
        "same_state_identity_rejected": True,
        "duration": "8",
    }


def membership(graph, curve, values, parameter, radius="1/4096", charge="21"):
    radius, charge = Q(radius), Q(charge)
    s = Q(parameter)
    need(0 <= s <= 1, "certified curve parameter")
    C = M([[Q(x)] for x in values])
    need(sum(C.entries()) == charge, "physical affine charge")
    Qc = M(curve)
    t = [Q(1), 2 * s - 1]
    for _ in range(2, Qc.ncols()):
        t.append(2 * t[1] * t[-1] - t[-2])
    delta = C - Qc * M([[x] for x in t[: Qc.ncols()]])
    P = algebra(graph)[4]
    squared = (delta.transpose() * P * delta)[0, 0] / radius**2
    need(0 <= squared <= 1, "complete P distance")
    return str(squared)

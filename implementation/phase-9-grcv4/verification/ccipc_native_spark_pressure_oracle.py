"""Independent composite root pressure: literal equations and fresh Newton roots.

No native root, residual, derivative or certificate evaluator supplies truth.
"""

from hashlib import sha256
from math import isqrt

from cci_native_spark_pressure_oracle import (
    decode,
    encloses,
    interval,
    need,
    read,
    upper,
)
from ccipc_native_spark_oracle import CCIPCReference, verify_step
from cos_native_spark_oracle import Equations, infinity, matrix, vector
from flint import arb, arb_mat, ctx
from flint import fmpq as Q

from pygrc.models.grc_v4_certification import _ARB_CONTEXT_LOCK


def domain(graph):
    e = Equations(graph)
    L, b, a, S = (
        infinity(e.L),
        infinity(e.B),
        infinity((3 * e.I / 4 + e.L).inv()),
        infinity(e.O) / 8,
    )
    r = Q(1, 32)
    z = Q(isqrt(e.I.nrows() - 1) + 1, 256)
    h = z + S * r * r
    need(h < 1 and a * h * L < 1, "domain inverse premises")
    u, v = 1 / (1 - h), a / (1 - a * h * L)
    j = Q(2, 1024) * (b * Q(4, 64) + 6) + Q(1, 1024 * 64) * L * h * 4
    y = v * j
    image = u * y / 2
    lip = u * (v * (Q(1, 1024 * 64) * L * 4 + L * y) / 2 + image)
    q = lip * 2 * S * r
    need(image < r and q < 1, "domain self-map/contraction")
    return {
        k: str(v)
        for k, v in {
            "flat_radius": r,
            "overlap_row_sum": S,
            "edge_laplacian_norm": L,
            "incidence_norm": b,
            "reference_inverse_norm": a,
            "hodge_deviation": h,
            "hodge_inverse_norm": u,
            "current_inverse_norm": v,
            "carrier_hodge_deviation": z,
            "source_norm_upper": Q(e.I.nrows(), 2) * image * image,
            "image_bound": image,
            "geometry_to_flat_lipschitz": lip,
            "contraction": q,
        }.items()
    }


def audit_root(state, payload):
    """Call under the shared Arb lock at 768 bits; prove, do not overlap."""
    need(
        payload["subject_digest"] == sha256(state.to_canonical_bytes()).hexdigest(),
        "full root subject binding",
    )
    graph = state.graph.to_payload()
    e = Equations(graph, outward=True)
    C = arb_mat(vector(state.C))
    Z = arb_mat(matrix(state.Z_4))
    _n, m = C.nrows(), e.I.nrows()
    d = domain(graph)
    saved = payload["root_domain"]
    need(all(saved[k] == v for k, v in d.items()), "graph-specific root-domain bounds")
    need(
        saved["domain_id"]
        == "cipc_quartic_flat_inf_ball_1_over_32_carrier_1_over_128_v1"
        and list(saved["resource_box"]) == ["0", "4"],
        "root-domain declaration",
    )
    need(
        payload["precision_bits"] == 256
        and payload["numerical_policy_id"]
        == "spark_ccipc_arb256_certified_root_flux128_carrier192_v1",
        "root numerical identity",
    )
    f, H, J = (
        decode(payload[k], *shape)
        for k, shape in [("flat", (m, 1)), ("H", (m, m)), ("J", (m, 1))]
    )
    proposal = decode(payload["proposal"], m, 1)
    need(
        all(Q(pair[0]) == Q(pair[1]) for row in payload["proposal"] for pair in row),
        "exact proposal identity",
    )
    need(all(x >= 0 and x <= 4 for x in C.entries()), "resource root chart")
    q = Q(d["contraction"])
    r = Q(1, 32)
    _, _, _, F = read(e, C, e.geometry(proposal) + Z / 2)
    residual = upper(F - proposal)
    residual_interval = interval(payload["proposal_residual"])
    need(
        residual_interval.is_finite()
        and Q(payload["proposal_residual"][1]) >= residual,
        "independent proposal residual",
    )
    error = Q(payload["root_error"][1])
    stored_residual = Q(payload["proposal_residual"][1])
    need(error >= stored_residual / (1 - q), "residual-to-root error bound")
    need(upper(proposal) + error < r and upper(f) < r, "selected root ball")
    for i in range(m):
        x = Q(payload["proposal"][i][0][0])
        need(
            Q(payload["flat"][i][0][0]) <= x - error
            and Q(payload["flat"][i][0][1]) >= x + error,
            "proposal enclosure identity",
        )
    independent = CCIPCReference(graph)
    fresh = independent.root(C, Z)
    for key, A in [
        ("flat", fresh["flat"]),
        ("H", fresh["geometry"]),
        ("J", fresh["selected"]["current"]),
    ]:
        need(encloses(payload[key], A), "fresh selected-root containment: " + key)
    A = 3 * e.I / 4 + fresh["geometry"] * e.L
    conditioning = m * upper(A) * upper(A.inv())
    need(
        conditioning <= Q(payload["conditioning_upper"]) < 10**12,
        "independent current conditioning bound",
    )
    # Independently enclosed symmetric geometry need not have byte-identical
    # transposed interval endpoints after outward arithmetic.
    need(
        all(x.contains(0) for x in (H - H.transpose()).entries()),
        "H symmetry enclosure",
    )
    need(upper(H - e.I) < 1, "whole H enclosure positive definite")
    need(
        all(H[i, j].is_zero() for i in range(m) for j in range(m) if not e.O[i, j]),
        "permitted H support",
    )
    # Derive y from the returned flat/H pair; re-evaluate all defining equations.
    j0, _, _, _ = read(e, C, H)
    y = 2 * H * f
    defects = {
        "geometry": H - e.geometry(f) - Z / 2,
        "linear_current": (3 * e.I / 4 + H * e.L) * y - j0,
        "flat": 2 * H * f - y,
        "current": J - j0 - y / 4,
    }
    for key, A in defects.items():
        need(
            all(x.is_finite() and x.contains(0) for x in A.entries()),
            "joint equation: " + key,
        )
        need(upper(A) < Q(1, 10**11), "joint residual bound: " + key)
    O = Equations(graph).O
    proposal_joint = arb(sum((x / 8) ** 2 for x in O.entries())).sqrt() * (
        2 * arb(upper(proposal)) * arb(residual) + arb(residual) ** 2
    )
    need(
        Q(payload["residual_upper"]) >= proposal_joint.upper().fmpq(),
        "joint proposal residual provenance",
    )
    need(Q(payload["residual_upper"]) < Q(1, 10**11), "joint residual tolerance")
    # A fresh validated root encloses the actual current, not just an overlapping read.
    need(
        all(
            Q(pair[1]) - Q(pair[0]) <= Q(2, 2**192)
            for row in payload["J"]
            for pair in row
        ),
        "current enclosure width",
    )
    return fresh, {
        "root_domain": d,
        "residual_upper": str(residual),
        "root_error_bound": str(error),
        "equation_residual_upper": {k: str(upper(A)) for k, A in defects.items()},
        "whole_root_containment": True,
        "reference_connected_branch": "uniform contraction in the full declared C/Z domain",
    }


def audit_step(step, certificate=None, role="current"):
    report = verify_step(step, certificate, role)
    with _ARB_CONTEXT_LOCK, ctx.workprec(768):
        for state, payload in (
            (step.before, step.consumed_read),
            (step.after, step.restart_read),
        ):
            _, checked = audit_root(state, payload)
            report["incoming_root" if state is step.before else "returned_root"] = (
                checked
            )
    return report

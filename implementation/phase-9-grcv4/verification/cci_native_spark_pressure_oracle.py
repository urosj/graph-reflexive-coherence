"""Independent CI pressure: exact decoded subjects, residuals and full-step error.

No native residual, geometry, derivative, solver or certificate evaluator is used.
Literal graph algebra is shared with the C_OS verification harness; fresh Newton
roots come from a separate research implementation and are independently checked.
"""

from cci_native_spark_oracle import CCIReference
from cos_native_spark_oracle import Equations, incidence, infinity, matrix, vector
from flint import arb, arb_mat, ctx
from flint import fmpq as Q
from flint import fmpq_mat as M

from pygrc.models.grc_v4_certification import _ARB_CONTEXT_LOCK


def need(ok, message):
    if not ok:
        raise AssertionError(message)


def upper(A):
    return max(
        sum(abs(A[i, j]).upper().fmpq() for j in range(A.ncols()))
        for i in range(A.nrows())
    )


def interval(pair):
    need(len(pair) == 2, "interval shape")
    a, b = map(Q, pair)
    need(a <= b, "interval order")
    return arb((a + b) / 2, (b - a) / 2)


def decode(rows, n, m):
    need(len(rows) == n and all(len(r) == m for r in rows), "complete root dimensions")
    return arb_mat([[interval(x) for x in row] for row in rows])


def encloses(rows, A):
    need(
        len(rows) == A.nrows() and all(len(r) == A.ncols() for r in rows),
        "complete root dimensions",
    )
    return all(
        Q(rows[i][j][0]) <= A[i, j].lower().fmpq()
        and A[i, j].upper().fmpq() <= Q(rows[i][j][1])
        for i in range(A.nrows())
        for j in range(A.ncols())
    )


def domain(graph):
    e = Equations(graph)
    L, b, a, S = (
        infinity(e.L),
        infinity(e.B),
        infinity((3 * e.I / 4 + e.L).inv()),
        infinity(e.O) / 8,
    )
    r = Q(1, 32)
    h = S * r * r
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
            "current_baseline_bound": j,
            "y_bound": y,
            "image_bound": image,
            "geometry_to_flat_lipschitz": lip,
            "contraction": q,
        }.items()
    }


def read(e, C, H):
    site = arb_mat([[(x - 2) ** 3 - (x - 2)] for x in C.entries()])
    j0 = -e.B.transpose() * (e.B * H * e.B.transpose() * C / 64 - site) / 1024
    A = 3 * e.I / 4 + H * e.L
    y = A.solve(j0)
    return j0, y, j0 + y / 4, H.solve(y) / 2


def binding(config, state):
    need(state.graph == config.reference.graph, "captured graph/ports binding")
    p = config.reference.profile.to_payload()
    base = config.reference.profile.baseline.params_resolved
    need(p["identity_payload"]["profile_family_id"] == "C_CI", "explicit CI identity")
    need(
        config.reference.profile.site.to_payload()
        == {
            "schema_version": "grcv4-homogeneous-quartic-site-v1",
            "evaluator_id": "homogeneous_quartic_site_v1",
            "c0": "2",
            "a": "1",
            "mu": "1",
            "units_id": "resource_potential_site_units_v1",
        },
        "quartic site binding",
    )
    expected = {
        "Lambda_C": Q(1, 64),
        "kappa_M_C": 0,
        "kappa_Phi_C": Q(1, 64),
        "eta_C": Q(1, 1024),
        "tau_C": 1,
        "chi_C": Q(1, 2),
        "zeta_C": Q(1, 2),
    }
    for k, v in expected.items():
        need(
            Q(*getattr(base.candidate, k).as_integer_ratio()) == v,
            "coefficient binding: " + k,
        )
    need(
        Q(*base.geometry.kappa_H.as_integer_ratio()) == Q(1, 2)
        and all(x == 1 for x in base.candidate.W_C_tr.values()),
        "unit reference stratum",
    )
    need(
        set(base.candidate.W_C_tr) == set(state.graph.live_edge_ids),
        "reference map coverage",
    )
    need(base.common.context_contract_id == "constant_zero_context_v1", "zero context")
    need(
        base.realization.contraction_domain_id
        == "ci_quartic_flat_inf_ball_1_over_32_v1",
        "root domain identity",
    )
    need(
        config.policy.numerical_policy_id
        == "spark_cci_arb256_certified_root_flux128_v1",
        "numerical policy binding",
    )
    need(sum(map(Q, state.C)) == Q(state.charge) == 21, "exact charge-21 binding")
    return p


def audit_root(state, payload):
    """Call under the shared Arb lock at 768 bits; prove, do not overlap."""
    graph = state.graph.to_payload()
    e = Equations(graph, outward=True)
    C = arb_mat(vector(state.C))
    _n, m = C.nrows(), e.I.nrows()
    d = domain(graph)
    saved = payload["domain"]
    need(all(saved[k] == v for k, v in d.items()), "graph-specific root-domain bounds")
    need(
        saved["domain_id"] == "ci_quartic_flat_inf_ball_1_over_32_v1"
        and list(saved["resource_box"]) == ["0", "4"],
        "root-domain declaration",
    )
    need(
        payload["precision_bits"] == 256
        and payload["numerical_policy_id"]
        == "spark_cci_arb256_certified_root_flux128_v1",
        "root numerical identity",
    )
    f, H, J = (
        decode(payload[k], *shape)
        for k, shape in [("flat", (m, 1)), ("geometry", (m, m)), ("current", (m, 1))]
    )
    proposal = decode(payload["proposal"], m, 1)
    need(
        all(Q(pair[0]) == Q(pair[1]) for row in payload["proposal"] for pair in row),
        "exact proposal identity",
    )
    need(all(x >= 0 and x <= 4 for x in C.entries()), "resource root chart")
    q = Q(d["contraction"])
    r = Q(1, 32)
    _, _, _, F = read(e, C, e.geometry(proposal))
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
    independent = CCIReference(graph)
    fresh = independent.root(C)
    for key, A in [
        ("flat", fresh["flat"]),
        ("geometry", fresh["geometry"]),
        ("current", fresh["selected"]["current"]),
    ]:
        need(encloses(payload[key], A), "fresh selected-root containment: " + key)
    A = 3 * e.I / 4 + fresh["geometry"] * e.L
    conditioning = m * upper(A) * upper(A.inv())
    need(
        conditioning <= Q(payload["conditioning_upper"][1]) < 10**12,
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
        "geometry": H - e.geometry(f),
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
        Q(payload["joint_residual_upper"][1]) >= proposal_joint.upper().fmpq(),
        "joint proposal residual provenance",
    )
    need(
        Q(payload["joint_residual_upper"][1]) < Q(1, 10**11), "joint residual tolerance"
    )
    # A fresh validated root encloses the actual current, not just an overlapping read.
    need(
        all(
            Q(pair[1]) - Q(pair[0]) <= Q(2, 2**192)
            for row in payload["current"]
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
        "reference_connected_branch": "uniform contraction also holds for H=I+t*diag(f)Odiag(f)/8, 0<=t<=1",
    }


def audit_step(config, captured, step, certificate=None, *, role="current"):
    with _ARB_CONTEXT_LOCK, ctx.workprec(768):
        binding(config, captured)
        need(
            step.before == captured
            and step.after.graph == captured.graph
            and step.profile_id == config.reference.profile.complete_profile_id,
            "captured input/profile binding",
        )
        need(
            step.duration == "32"
            and step.numerical_policy_id == config.policy.numerical_policy_id,
            "step policy binding",
        )
        fresh, root = audit_root(captured, step.root)
        _, restart = audit_root(step.after, step.restart_root)
        B = incidence(captured.graph.to_payload())
        C = vector(captured.C)
        actual = vector(step.after.C)
        J = vector(step.flux)
        need(J.nrows() == B.ncols(), "complete stable-edge flux")
        write = actual - (C - 32 * B * J)
        need(write == M(B.nrows(), 1), "one exact incidence write")
        need(
            sum(map(Q, step.after.C)) == Q(step.after.charge) == 21,
            "independent exact output charge",
        )
        EJ = [
            max(abs(J[i, 0] - x.lower().fmpq()), abs(J[i, 0] - x.upper().fmpq()))
            for i, x in enumerate(fresh["selected"]["current"].entries())
        ]
        epsilon = Q(1, 2**129) + Q(1, 2**192)
        need(max(EJ) <= epsilon, "selected current/flux error budget")
        report = {
            "root": root,
            "restart": restart,
            "write_error": "0",
            "edge_current_error_upper": list(map(str, EJ)),
            "exact_charge": "21",
        }
        if certificate is not None:
            b = certificate.operands["binding"]
            need(
                b["graph"].to_dict() == captured.graph.to_payload()
                and b["profile"].to_dict() == config.reference.profile.to_payload()
                and b["role"] == role
                and b["charge"] == captured.charge
                and b["policy"].to_dict() == config.policy.to_payload(),
                "complete certificate subject",
            )
            U = matrix(certificate.operands["U"])
            UB = U * B
            bound = 32 * max(
                sum(abs(UB[i, j]) * EJ[j] for j in range(UB.ncols()))
                for i in range(UB.nrows())
            )
            true_after = arb_mat(C) - 32 * arb_mat(B) * fresh["selected"]["current"]
            actual_error = upper(arb_mat(U) * (arb_mat(actual) - true_after))
            # Both calculations enclose the same exact error. Their outward
            # upper bounds need not be ordered: the direct matrix calculation
            # introduces its own Arb rounding. Check each against the unchanged
            # admitted budget; the exact incidence identity above justifies the
            # triangle bound independently, without a tolerance or slack term.
            need(
                actual_error <= Q(certificate.proof["full_step_error"]),
                "direct anisotropic full-step error exceeds certificate budget",
            )
            need(
                bound
                <= Q(certificate.proof["full_step_error"])
                < Q(certificate.proof["image_margin"]),
                "certificate-norm image margin",
            )
            report.update(
                full_step_error_upper=str(bound),
                direct_error_upper=str(actual_error),
                margin=certificate.proof["image_margin"],
            )
        return report

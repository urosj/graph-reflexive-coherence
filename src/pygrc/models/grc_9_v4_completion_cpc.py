"""Full C/Z product-domain certificate for the explicit native quartic PC map."""

from .grc_v4_certification import _ARB_CONTEXT_LOCK
from .grc_v4_exact import _flint_module
from .grc_v4_spark_carrier import ExactCarrierState
from .grc_v4_spark_cos import _matrix
from .grc_v4_spark_cpc import decay, frobenius, need
from .grc_v4_spark_state import rational
from .grc_v4_state import FrozenJSONMap


def verify(data):
    from .grc_9_v4_completion_certificate import _geometry, _lower, _upper, binding
    from .grc_9_v4_completion_codec import CompletionPolicy, digest
    from .grc_v4_geometry import GRCV4Graph
    from .grc_v4_spark import quartic_kernel, quartic_profile

    if set(data) != {
        "schema_version",
        "binding",
        "center",
        "S",
        "U",
        "carrier_center",
        "carrier_radius",
        "carrier_pairs",
    }:
        raise ValueError("closed full C/Z trap operands required")
    b = data["binding"]
    k = quartic_kernel(
        GRCV4Graph.from_payload(b["graph"]), quartic_profile(b["profile"])
    )
    policy = CompletionPolicy.from_payload(b["policy"])
    if (
        k.profile.FAMILY != "C_PC"
        or policy.numerical_policy_id != k.profile.NUMERICS
        or b != binding(k, policy, b["role"], b["charge"])
        or policy.step_duration != "32"
    ):
        raise ValueError("full C_PC certificate equation/role/policy binding required")
    center = ExactCarrierState(
        k.graph, tuple(data["center"]), b["charge"], data["carrier_center"]
    )
    if any(rational(x) != 0 for row in center.Z_4 for x in row):
        raise ValueError("declared zero-carrier trap center required")
    if data["carrier_pairs"] != [list(pair) for pair in k.pairs]:
        raise ValueError("all signed carrier directions required")
    z = rational(data["carrier_radius"])
    if not 0 < z < rational("1/128"):
        raise ValueError("strict positive carrier radius required")
    S, U = _matrix(data["S"]), _matrix(data["U"])
    n = len(center.C)
    d = n - 1
    f = _flint_module()
    M = f.arb_mat
    if (S.nrows(), S.ncols(), U.nrows(), U.ncols()) != (n, d, d, n):
        raise ValueError("full charge chart required")
    identity = f.fmpq_mat([[int(i == j) for j in range(d)] for i in range(d)])
    if U * S != identity or any(sum(S[i, j] for i in range(n)) != 0 for j in range(d)):
        raise ValueError("exact full-rank charge-tangent chart required")
    geometry = _geometry(k, policy, center, S)
    with _ARB_CONTEXT_LOCK, f.ctx.workprec(k.precision_bits):
        C = M([[rational(x)] for x in center.C])
        box = M(
            [
                [f.arb(rational(x), sum(abs(S[i, j]) for j in range(d)))]
                for i, x in enumerate(center.C)
            ]
        )
        m = len(k.graph.oriented_edges)
        Z = M(m, m)
        for i, j in k.pairs:
            Z[i, j] = f.arb(0, z)
            Z[j, i] = Z[i, j]
        p = k.partials(box, Z)
        AU, AS = M(U), M(S)
        T = AU * p["CC"] * AS
        cross = AU * p["CZ"]
        columns = p["SC"] * AS
        resource_cross = [
            z * frobenius(M([[cross[i, j] for j in range(cross.ncols())]]))
            for i in range(d)
        ]
        resource_rows = [
            sum(abs(T[i, j]).upper() for j in range(d)) + resource_cross[i]
            for i in range(d)
        ]
        release = decay()
        zc = (
            (1 - release)
            * sum(
                frobenius(M([[columns[i, j]] for i in range(columns.nrows())]))
                for j in range(d)
            )
            / z
        )
        zz = release + (1 - release) * frobenius(p["SZ"])
        history = zc + zz
        q = max([x.upper() for x in resource_rows] + [history.upper()])
        need(
            all(sum(p["CC"][i, j] for i in range(n)).contains(1) for j in range(n)),
            "PC resource derivative charge identity",
        )
        need(
            all(
                sum(p["CZ"][i, j] for i in range(n)).contains(0)
                for j in range(len(k.pairs))
            ),
            "PC carrier derivative charge identity",
        )
        read = k.read_ball(C, M(m, m))
        B = M(_matrix(k._B))
        after = C - 32 * B * read["J"]
        defect = max(
            max(abs(x).upper() for x in (AU * (after - C)).entries()),
            frobenius((1 - release) * read["S"]) / z,
        )
        margin = (1 - q - defect).lower()
        need(
            q < 1 and margin > 0, "full C/Z contraction and strict self-map unresolved"
        )
        error = k.uniform_rounding_bound(
            data["U"], _lower(margin), data["carrier_radius"]
        )
        result = {
            "q": _upper(q),
            "center_defect": _upper(defect),
            "image_margin": _lower(margin),
            "full_step_error": error["full_step_error"],
            "resource_error": error["resource_error"],
            "scaled_carrier_error": error["scaled_carrier_error"],
            "conditioning_upper": _upper(p["read"]["condition"]),
            "precision_bits": k.precision_bits,
            "exact_charge_preserved": True,
            "geometry": geometry,
            "operands_digest": digest(data),
            "domain": k.domain.to_dict(),
            "resource_dimension": d,
            "carrier_dimension": len(k.pairs),
            "full_dimension": d + len(k.pairs),
            "resource_row_bounds": [_upper(x) for x in resource_rows],
            "carrier_to_resource": [_upper(x) for x in resource_cross],
            "resource_to_carrier": _upper(zc),
            "carrier_self": _upper(zz),
            "carrier_row": _upper(history),
            "membership_measure": "squared_max_product_norm",
            "all_signed_carrier_directions": True,
        }
    return FrozenJSONMap(result)


def membership(certificate, state):
    if type(state) is not ExactCarrierState:
        raise ValueError("full C/Z membership subject required")
    b = certificate.operands["binding"]
    if state.graph.to_payload() != b["graph"].to_dict() or state.charge != b["charge"]:
        raise ValueError("membership graph/charge mismatch")
    f = _flint_module()
    c = certificate.operands["center"]
    delta = f.fmpq_mat(
        [[rational(x) - rational(y)] for x, y in zip(state.C, c, strict=True)]
    )
    a = max(abs(x) for x in (_matrix(certificate.operands["U"]) * delta).entries())
    radius = rational(certificate.operands["carrier_radius"])
    norm_squared = max(
        a * a,
        sum(rational(x) ** 2 for row in state.Z_4 for x in row) / (radius * radius),
    )
    return norm_squared <= 1, str(norm_squared)

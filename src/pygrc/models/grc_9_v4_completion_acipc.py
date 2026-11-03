"""Complete C/logW parallelotope proof and membership for native A_CI_PC."""

from .grc_9_v4_completion_aos import _geometry
from .grc_v4_certification import _ARB_CONTEXT_LOCK
from .grc_v4_exact import _flint_module, exact_number
from .grc_v4_geometry import GRCV4Graph
from .grc_v4_spark import quartic_kernel, quartic_profile
from .grc_v4_spark_acipc_math import ACIPCMath
from .grc_v4_spark_adaptive_carrier import ExactAdaptiveCarrierState
from .grc_v4_spark_cos import _matrix
from .grc_v4_spark_cpc import frobenius, need, norm
from .grc_v4_spark_state import rational
from .grc_v4_state import FrozenJSONMap


def verify(data):
    from .grc_9_v4_completion_certificate import binding
    from .grc_9_v4_completion_codec import CompletionPolicy, digest

    if (
        set(data)
        != {
            "schema_version",
            "binding",
            "center",
            "logW_center",
            "S",
            "U",
            "carrier_center",
            "carrier_radius",
            "carrier_pairs",
        }
        or data["schema_version"] != "grc9v4-native-acipc-trap-operands-v1"
    ):
        raise ValueError("closed full A_CI_PC domain operands required")
    b = data["binding"]
    kernel = quartic_kernel(
        GRCV4Graph.from_payload(b["graph"]), quartic_profile(b["profile"])
    )
    policy = CompletionPolicy.from_payload(b["policy"])
    if (
        kernel.profile.FAMILY != "A_CI_PC"
        or policy.numerical_policy_id != kernel.profile.NUMERICS
        or policy.step_duration != "32"
        or b != binding(kernel, policy, b["role"], b["charge"])
    ):
        raise ValueError("A_CI_PC certificate family/reference/policy binding")
    n, m = len(kernel.graph.live_node_ids), len(kernel.graph.live_edge_ids)
    d = n - 1 + m
    if (
        len(data["center"]) != n
        or len(data["logW_center"]) != m
        or sum(map(rational, data["center"])) != rational(b["charge"])
    ):
        raise ValueError("complete center and exact charge required")
    if data["carrier_pairs"] != [list(pair) for pair in kernel.pairs]:
        raise ValueError("every signed symmetric-star carrier direction is required")
    Z0 = _matrix(data["carrier_center"])
    if Z0.nrows() != m or Z0.ncols() != m or any(x != 0 for x in Z0.entries()):
        raise ValueError("complete zero carrier center required")
    rho = rational(data["carrier_radius"])
    if rho != rational("1/1073741824"):
        raise ValueError("declared A_CI_PC carrier radius required")
    S, U = _matrix(data["S"]), _matrix(data["U"])
    f = _flint_module()
    if (S.nrows(), S.ncols(), U.nrows(), U.ncols()) != (n + m, d, d, n + m):
        raise ValueError("all independent C/logW directions required")
    identity = f.fmpq_mat([[int(i == j) for j in range(d)] for i in range(d)])
    if U * S != identity or any(sum(S[i, j] for i in range(n)) != 0 for j in range(d)):
        raise ValueError("exact full-rank charge-tangent C/logW chart required")
    with _ARB_CONTEXT_LOCK, f.ctx.workprec(kernel.precision_bits):
        math = ACIPCMath(kernel.graph)
        values = tuple(data["center"]) + tuple(data["logW_center"])
        radii = [sum(abs(S[i, j]) for j in range(d)) for i in range(n + m)]
        point = f.arb_mat([[rational(x)] for x in values])
        box = f.arb_mat([[f.arb(rational(x), radii[i])] for i, x in enumerate(values)])
        C = f.arb_mat(point.tolist()[:n])
        L = f.arb_mat(point.tolist()[n:])
        Cbox = f.arb_mat(box.tolist()[:n])
        Lbox = f.arb_mat(box.tolist()[n:])
        geometry = _geometry(kernel, policy, data["center"], L, S, Cbox, Lbox, math)
        Z = f.arb_mat(m, m)
        Zbox = f.arb_mat(m, m)
        for i, j in kernel.pairs:
            Zbox[i, j] = Zbox[j, i] = f.arb(0, rho)
        J = math.jacobian(Cbox, Lbox, Zbox)
        nx, nz = n + m, len(kernel.pairs)
        block = lambda r0, r1, c0, c1: f.arb_mat(
            [[J[i, j] for j in range(c0, c1)] for i in range(r0, r1)]
        )
        XX = f.arb_mat(U) * block(0, nx, 0, nx) * f.arb_mat(S)
        XZ = f.arb_mat(U) * block(0, nx, nx, nx + nz)
        ZX = block(nx, nx + nz, 0, nx) * f.arb_mat(S)
        ZZ = block(nx, nx + nz, nx, nx + nz)
        a = norm(XX)
        b = rho * max(
            frobenius(f.arb_mat([[XZ[i, j] for j in range(nz)]])) for i in range(d)
        )
        c = f.arb(d).sqrt() * frobenius(ZX) / rho
        I = f.arb_mat([[int(i == j) for j in range(nz)] for i in range(nz)])
        zself = math.decay + frobenius(ZZ - math.decay * I)
        q = max((a + b).upper(), (c + zself).upper())
        need(
            all(
                sum(J[i, j] for i in range(n)).contains(int(j < n))
                for j in range(nx + nz)
            ),
            "full A_CI_PC derivative charge identity",
        )
        stage = math.step(C, L, Z)
        change = f.arb_mat(
            (stage["after"] - C).tolist() + (stage["logW_after"] - L).tolist()
        )
        defect = max(
            norm(f.arb_mat(U) * change), frobenius(stage["carrier_after"]) / rho
        )
        margin = (1 - q - defect).lower()
        need(q < 1 and margin > 0, "full C/logW invariant contraction unresolved")
        full = math.step(Cbox, Lbox, Zbox)
        need(
            all(0 < x < 4 for x in full["after"].entries()),
            "whole-domain ideal resource endpoint",
        )
        need(
            all(abs(x) < 1 for x in full["selected"]["current"].entries()),
            "whole-domain current envelope",
        )
        need(
            all(
                math.q(99, 100) < w < math.q(101, 100)
                for w in math.exp(full["logW_after"]).entries()
            ),
            "whole-domain ideal writer box",
        )
        need(
            frobenius(full["source"]) < f.arb(rational("1/64")),
            "whole-domain carrier source envelope",
        )
        condition = m * norm(full["geometry"]) * norm(full["geometry"].inv())
        need(
            condition
            < exact_number(
                kernel.profile.baseline.params_resolved.solver.conditioning_limit
            ),
            "whole-domain conditioning",
        )
        numeric = kernel.uniform_rounding_bound(
            data["U"], str(margin.fmpq()), data["carrier_radius"]
        )
        return FrozenJSONMap(
            {
                "q": str(q.upper().fmpq()),
                "center_defect": str(defect.upper().fmpq()),
                "image_margin": str(margin.fmpq()),
                "full_step_error": numeric["full_step_error"],
                "numerical_bound": numeric,
                "domain": kernel.domain.to_dict(),
                "all_signed_carrier_directions": True,
                "implicit_root_derivative": True,
                "same_selected_source": True,
                "carrier_dimension": nz,
                "full_dimension": d + nz,
                "C_logW_dimension": d,
                "C_logW_self": str(a.upper().fmpq()),
                "carrier_to_C_logW": str(b.upper().fmpq()),
                "C_logW_to_carrier": str(c.upper().fmpq()),
                "carrier_self": str(zself.upper().fmpq()),
                "membership_measure": "squared_max_C_logW_carrier_product_upper",
                "conditioning_upper": str(condition.upper().fmpq()),
                "precision_bits": kernel.precision_bits,
                "relative_dimension": d + nz,
                "resource_dimension": n - 1,
                "conductance_dimension": m,
                "state_chart": "C/logW/Frobenius_Z",
                "exact_charge_preserved": True,
                "geometry": geometry,
                "operands_digest": digest(data),
            }
        )


def membership(certificate, state):
    if type(state) is not ExactAdaptiveCarrierState:
        raise ValueError("A_CI_PC certificate requires the full C/W history")
    data = certificate.operands
    b = data["binding"]
    if state.graph.to_payload() != b["graph"].to_dict() or state.charge != b["charge"]:
        raise ValueError("state graph or exact charge differs from A_CI_PC certificate")
    from .grc_v4_spark_acipc import PRECISION

    f = _flint_module()
    with _ARB_CONTEXT_LOCK, f.ctx.workprec(PRECISION):
        delta = f.arb_mat(
            [
                [rational(x) - rational(c)]
                for x, c in zip(state.C, data["center"], strict=True)
            ]
            + [
                [f.arb(rational(w)).log() - rational(l)]
                for w, l in zip(state.W_A, data["logW_center"], strict=True)
            ]
        )
        coordinates = f.arb_mat(_matrix(data["U"])) * delta
        upper = max(abs(x).upper().fmpq() for x in coordinates.entries())
        lower = max(abs(x).lower().fmpq() for x in coordinates.entries())
        zsq = (
            sum(rational(x) ** 2 for row in state.Z_4 for x in row)
            / rational(data["carrier_radius"]) ** 2
        )
        upper, lower = max(upper * upper, zsq), max(lower * lower, zsq)
        need(
            upper <= 1 or lower > 1,
            "A_CI_PC logarithmic membership unresolved at boundary",
        )
        return upper <= 1, str(upper)

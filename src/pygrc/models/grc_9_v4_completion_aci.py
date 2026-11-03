"""Complete C/logW parallelotope proof and membership for native A_CI."""

from .grc_9_v4_completion_aos import _geometry
from .grc_v4_certification import _ARB_CONTEXT_LOCK
from .grc_v4_exact import _flint_module, exact_number
from .grc_v4_geometry import GRCV4Graph
from .grc_v4_spark import quartic_kernel, quartic_profile
from .grc_v4_spark_aci_math import ACIMath
from .grc_v4_spark_conductance import ExactConductanceState
from .grc_v4_spark_cos import _matrix
from .grc_v4_spark_cpc import need, norm
from .grc_v4_spark_state import rational
from .grc_v4_state import FrozenJSONMap


def verify(data):
    from .grc_9_v4_completion_certificate import binding
    from .grc_9_v4_completion_codec import CompletionPolicy, digest

    if (
        set(data) != {"schema_version", "binding", "center", "logW_center", "S", "U"}
        or data["schema_version"] != "grc9v4-native-aci-trap-operands-v1"
    ):
        raise ValueError("closed full A_CI domain operands required")
    b = data["binding"]
    kernel = quartic_kernel(
        GRCV4Graph.from_payload(b["graph"]), quartic_profile(b["profile"])
    )
    policy = CompletionPolicy.from_payload(b["policy"])
    if (
        kernel.profile.FAMILY != "A_CI"
        or policy.numerical_policy_id != kernel.profile.NUMERICS
        or policy.step_duration != "32"
        or b != binding(kernel, policy, b["role"], b["charge"])
    ):
        raise ValueError("A_CI certificate family/reference/policy binding")
    n, m = len(kernel.graph.live_node_ids), len(kernel.graph.live_edge_ids)
    d = n - 1 + m
    if (
        len(data["center"]) != n
        or len(data["logW_center"]) != m
        or sum(map(rational, data["center"])) != rational(b["charge"])
    ):
        raise ValueError("complete center and exact charge required")
    S, U = _matrix(data["S"]), _matrix(data["U"])
    f = _flint_module()
    if (S.nrows(), S.ncols(), U.nrows(), U.ncols()) != (n + m, d, d, n + m):
        raise ValueError("all independent C/logW directions required")
    identity = f.fmpq_mat([[int(i == j) for j in range(d)] for i in range(d)])
    if U * S != identity or any(sum(S[i, j] for i in range(n)) != 0 for j in range(d)):
        raise ValueError("exact full-rank charge-tangent C/logW chart required")
    with _ARB_CONTEXT_LOCK, f.ctx.workprec(kernel.precision_bits):
        math = ACIMath(kernel.graph)
        values = tuple(data["center"]) + tuple(data["logW_center"])
        radii = [sum(abs(S[i, j]) for j in range(d)) for i in range(n + m)]
        point = f.arb_mat([[rational(x)] for x in values])
        box = f.arb_mat([[f.arb(rational(x), radii[i])] for i, x in enumerate(values)])
        C = f.arb_mat(point.tolist()[:n])
        L = f.arb_mat(point.tolist()[n:])
        Cbox = f.arb_mat(box.tolist()[:n])
        Lbox = f.arb_mat(box.tolist()[n:])
        geometry = _geometry(kernel, policy, data["center"], L, S, Cbox, Lbox, math)
        J = math.jacobian(Cbox, Lbox)
        q = norm(f.arb_mat(U) * J * f.arb_mat(S))
        stage = math.step(C, L)
        change = f.arb_mat(
            (stage["after"] - C).tolist() + (stage["logW_after"] - L).tolist()
        )
        defect = norm(f.arb_mat(U) * change)
        margin = (1 - q - defect).lower()
        need(q < 1 and margin > 0, "full C/logW invariant contraction unresolved")
        full = math.step(Cbox, Lbox)
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
        root_bound = math.root_q
        need(root_bound < 1, "whole-domain selected root uniqueness")
        condition = m * norm(full["geometry"]) * norm(full["geometry"].inv())
        need(
            condition
            < exact_number(
                kernel.profile.baseline.params_resolved.solver.conditioning_limit
            ),
            "whole-domain conditioning",
        )
        numeric = kernel.uniform_rounding_bound(data["U"], str(margin.fmpq()))
        return FrozenJSONMap(
            {
                "q": str(q.upper().fmpq()),
                "center_defect": str(defect.upper().fmpq()),
                "image_margin": str(margin.fmpq()),
                "full_step_error": numeric["full_step_error"],
                "numerical_bound": numeric,
                "root_contraction": str(root_bound.upper().fmpq()),
                "root_domain": kernel.root_domain.to_dict(),
                "implicit_geometry_derivative": True,
                "conditioning_upper": str(condition.upper().fmpq()),
                "precision_bits": kernel.precision_bits,
                "relative_dimension": d,
                "resource_dimension": n - 1,
                "conductance_dimension": m,
                "state_chart": "C/logW",
                "exact_charge_preserved": True,
                "geometry": geometry,
                "operands_digest": digest(data),
            }
        )


def membership(certificate, state):
    if type(state) is not ExactConductanceState:
        raise ValueError("A_CI certificate requires the full C/W history")
    data = certificate.operands
    b = data["binding"]
    if state.graph.to_payload() != b["graph"].to_dict() or state.charge != b["charge"]:
        raise ValueError("state graph or exact charge differs from A_CI certificate")
    from .grc_v4_spark_aci import PRECISION

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
        need(
            upper <= 1 or lower > 1,
            "A_CI logarithmic membership unresolved at boundary",
        )
        return upper <= 1, str(upper)

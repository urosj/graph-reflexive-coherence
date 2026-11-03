"""Complete C/logW parallelotope proof and membership for native A_OS."""

from .grc_v4_certification import _ARB_CONTEXT_LOCK
from .grc_v4_exact import _flint_module
from .grc_v4_geometry import GRCV4Graph
from .grc_v4_spark import quartic_kernel, quartic_profile
from .grc_v4_spark_aos_math import AOSMath
from .grc_v4_spark_conductance import ExactConductanceState
from .grc_v4_spark_cos import _matrix
from .grc_v4_spark_cpc import need, norm
from .grc_v4_spark_state import rational, round_flux
from .grc_v4_state import FrozenJSONMap


def _geometry(kernel, policy, center, L, S, Cbox, Lbox, math):
    from .grc_9_v4_completion import classify, terminal_roster

    d = S.ncols()
    W = math.exp(Lbox)
    need(
        all(math.q(99, 100) < w < math.q(101, 100) for w in W.entries()),
        "whole-domain conductance box",
    )
    need(
        rational(kernel.selector_gap_lower) * rational("99/100") > rational("1/64"),
        "whole-domain weighted selector",
    )
    need(all(0 < c < 4 for c in Cbox.entries()), "whole-domain resource box")
    rows, _ = math.rows(Cbox, W)
    nodes = kernel.graph.live_node_ids
    adjacent, down = {x: set() for x in nodes}, {x: set() for x in nodes}
    gaps = {}
    sign = policy.landscape_sign
    for i, j in math.pairs:
        a, b = nodes[i], nodes[j]
        delta = sign * (rational(center[j]) - rational(center[i]))
        radius = sum(abs(S[j, k] - S[i, k]) for k in range(d))
        need(abs(delta) > radius, "domain crosses an edge-order hyperplane")
        gaps[a, b], gaps[b, a] = (
            (delta - radius, delta + radius),
            (-delta - radius, -delta + radius),
        )
        down[b if delta > 0 else a].add(a if delta > 0 else b)
        adjacent[a].add(b)
        adjacent[b].add(a)
    g, h, barrier, core = map(
        rational,
        (
            policy.epsilon_gradient,
            policy.epsilon_Hessian,
            policy.contrast,
            policy.minimum_resource,
        ),
    )
    anchors = set()
    for i, x in enumerate(nodes):
        lower = sum(
            (0 if v.contains(0) else min(abs(v.lower().fmpq()), abs(v.upper().fmpq())))
            ** 2
            for v in rows[i]
        )
        upper = sum(
            max(abs(v.lower().fmpq()), abs(v.upper().fmpq())) ** 2 for v in rows[i]
        )
        signed = [sign * v for v in rows[i]]
        seed = upper < g * g and all(v > h for v in signed)
        need(
            seed or lower >= g * g or any(v <= h for v in signed),
            "whole-domain weighted seed unresolved",
        )
        if seed:
            anchor = (
                bool(adjacent[x])
                and Cbox[i, 0] > core
                and all(gaps[x, y][0] > barrier for y in adjacent[x])
            )
            need(
                anchor
                or not adjacent[x]
                or Cbox[i, 0] <= core
                or any(gaps[x, y][1] <= barrier for y in adjacent[x]),
                "whole-domain weighted anchor unresolved",
            )
            if anchor:
                anchors.add(x)
    basins, terminals = terminal_roster(nodes, down, anchors)
    W0 = math.exp(L)
    state = ExactConductanceState(
        kernel.graph,
        tuple(center),
        str(sum(map(rational, center))),
        tuple(str(round_flux(w.mid().fmpq() * 2**64) / 2**64) for w in W0.entries()),
    )
    actual = classify(state, policy)
    need(
        (basins, terminals) == (actual.basins, actual.terminals),
        "represented center/domain roster mismatch",
    )
    return actual.to_payload()


def verify(data):
    from .grc_9_v4_completion_certificate import binding
    from .grc_9_v4_completion_codec import CompletionPolicy, digest

    if (
        set(data) != {"schema_version", "binding", "center", "logW_center", "S", "U"}
        or data["schema_version"] != "grc9v4-native-aos-trap-operands-v1"
    ):
        raise ValueError("closed full A_OS domain operands required")
    b = data["binding"]
    kernel = quartic_kernel(
        GRCV4Graph.from_payload(b["graph"]), quartic_profile(b["profile"])
    )
    policy = CompletionPolicy.from_payload(b["policy"])
    if (
        kernel.profile.FAMILY != "A_OS"
        or policy.numerical_policy_id != kernel.profile.NUMERICS
        or policy.step_duration != "32"
        or b != binding(kernel, policy, b["role"], b["charge"])
    ):
        raise ValueError("A_OS certificate family/reference/policy binding")
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
        math = AOSMath(kernel.graph)
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
            all(abs(x) < 1 for x in full["corrector"]["current"].entries()),
            "whole-domain current envelope",
        )
        need(
            all(
                math.q(99, 100) < w < math.q(101, 100)
                for w in math.exp(full["logW_after"]).entries()
            ),
            "whole-domain ideal writer box",
        )
        split = full["split_upper"]
        from .grc_v4_exact import exact_number

        need(
            split
            < f.arb(
                exact_number(
                    kernel.profile.baseline.params_resolved.realization.tolerance
                )
            ),
            "whole-domain exact OS tolerance",
        )
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
                "split_upper": str(split.upper().fmpq()),
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
        raise ValueError("A_OS certificate requires the full C/W history")
    data = certificate.operands
    b = data["binding"]
    if state.graph.to_payload() != b["graph"].to_dict() or state.charge != b["charge"]:
        raise ValueError("state graph or exact charge differs from A_OS certificate")
    from .grc_v4_spark_aos import PRECISION

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
            "A_OS logarithmic membership unresolved at boundary",
        )
        return upper <= 1, str(upper)

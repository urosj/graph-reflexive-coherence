"""Bounded native quartic C full-map certificate, recomputed from exact operands.

Family-bound Arb arithmetic encloses every OS stage or full CI implicit derivative. Exact FLINT checks the full charge chart and all spatial
predicates. No research module, trajectory, saved verdict or float is an oracle.
"""

from dataclasses import dataclass, field
from functools import lru_cache

from .grc_9_v4_completion import classify, terminal_roster
from .grc_9_v4_completion_codec import CompletionPolicy, digest
from .grc_v4_certification import _ARB_CONTEXT_LOCK, CertificationInconclusive
from .grc_v4_codec import canonical_json_bytes, decode_canonical_json
from .grc_v4_exact import _flint_module, exact_number
from .grc_v4_geometry import GRCV4Graph
from .grc_v4_spark import quartic_kernel, quartic_profile
from .grc_v4_spark_cos import _matrix
from .grc_v4_spark_carrier import ExactCarrierState, carrier_pairs
from .grc_v4_spark_state import (
    ExactResources,
    flint_operation,
    rational,
)
from .grc_v4_state import FrozenJSONMap


def binding(kernel, policy, role, charge):
    if role not in ("current", "reset"):
        raise ValueError("explicit current/reset certificate role required")
    rational(charge)
    return {
        "graph": kernel.graph.to_payload(),
        "profile": kernel.profile.to_payload(),
        "context": {"evaluator": "constant_zero_context_v1", "parameters": {}},
        "reference": {"K_4": "zero", "H_ref": "identity", "W": "unit"},
        "charge": charge,
        "duration": policy.step_duration,
        "role": role,
        "state_channels": ["C", "Z_4"] if kernel.profile.FAMILY in ("C_PC", "C_CI_PC") else ["C"],
        "policy": policy.to_payload(),
    }


def _need(condition, message):
    if not condition:
        raise CertificationInconclusive(message)


def _geometry(kernel, policy, center, S):
    nodes = kernel.graph.live_node_ids
    index = {x: i for i, x in enumerate(nodes)}
    c = tuple(map(rational, center.C))
    radii = [sum(abs(S[i, j]) for j in range(S.ncols())) for i in range(S.nrows())]
    low, high = [x - r for x, r in zip(c, radii)], [x + r for x, r in zip(c, radii)]
    _need(min(low) > 0, "whole-domain resource positivity unresolved")
    terms = {x: [[], [], []] for x in nodes}
    down, adjacent, gaps = {x: set() for x in nodes}, {x: set() for x in nodes}, {}
    sign = policy.landscape_sign
    for e in kernel.graph.port_graph.edges:
        a, b = e.tail.node_id, e.head.node_id
        i, j = index[a], index[b]
        delta = sign * (c[j] - c[i])
        radius = sum(abs(S[j, k] - S[i, k]) for k in range(S.ncols()))
        _need(abs(delta) > radius, "domain crosses an edge-order hyperplane")
        gaps[a, b], gaps[b, a] = (
            (delta - radius, delta + radius),
            (-delta - radius, -delta + radius),
        )
        down[b if delta > 0 else a].add(a if delta > 0 else b)
        adjacent[a].add(b)
        adjacent[b].add(a)
        for here, there in ((e.tail, e.head), (e.head, e.tail)):
            i, j = index[here.node_id], index[there.node_id]
            terms[here.node_id][(here.port - 1) // 3].append(
                (low[j] - high[i], high[j] - low[i])
            )
    anchors, seeds = set(), set()
    g, h, contrast, resource = map(
        rational,
        (
            policy.epsilon_gradient,
            policy.epsilon_Hessian,
            policy.contrast,
            policy.minimum_resource,
        ),
    )
    for x in nodes:
        rows = [
            (sum(t[0] for t in row) / len(row), sum(t[1] for t in row) / len(row))
            if row
            else (rational("0"), rational("0"))
            for row in terms[x]
        ]
        signed = rows if sign == 1 else [(-hi, -lo) for lo, hi in rows]
        norm_upper = sum(max(abs(lo), abs(hi)) ** 2 for lo, hi in rows)
        norm_lower = sum(
            (0 if lo <= 0 <= hi else min(abs(lo), abs(hi))) ** 2 for lo, hi in rows
        )
        seed = norm_upper < g * g and min(lo for lo, _ in signed) > h
        _need(
            seed or norm_lower >= g * g or min(hi for _, hi in signed) <= h,
            "whole-domain seed predicate unresolved",
        )
        if seed:
            seeds.add(x)
            i = index[x]
            anchor = (
                bool(adjacent[x])
                and low[i] > resource
                and all(gaps[x, y][0] > contrast for y in adjacent[x])
            )
            _need(
                anchor
                or not adjacent[x]
                or high[i] <= resource
                or any(gaps[x, y][1] <= contrast for y in adjacent[x]),
                "whole-domain anchor exclusion unresolved",
            )
            if anchor:
                anchors.add(x)
    basins, terminals = terminal_roster(nodes, down, anchors)
    point = classify(center, policy)
    _need(
        (basins, terminals) == (point.basins, point.terminals),
        "center/domain roster mismatch",
    )
    return point.to_payload()


def _norm(matrix):
    f = _flint_module()
    return (
        max(
            sum(abs(matrix[i, j]).upper() for j in range(matrix.ncols())).upper()
            for i in range(matrix.nrows())
        )
        if matrix.nrows()
        else f.arb(0)
    )


def _upper(value):
    return str(value.upper().fmpq())


def _lower(value):
    return str(value.lower().fmpq())


@flint_operation
def _analytic(kernel, C):
    """Interval full C_OS map and its analytic Jacobian at a resource box."""
    f = _flint_module()
    M, q = f.arb_mat, f.arb
    B, I, L, O, inverse = (
        M(_matrix(x))
        for x in (kernel._B, kernel._I, kernel._L, kernel._O, kernel._inverse)
    )
    Bt, n, m = B.transpose(), B.nrows(), B.ncols()
    site = M([[(C[i, 0] - 2) ** 3 - (C[i, 0] - 2)] for i in range(n)])
    j0p = -Bt * (B * Bt * C / 64 - site) / 1024
    fp = inverse * j0p / 2
    D = M([[O[i, j] * fp[i, 0] * fp[j, 0] / 8 for j in range(m)] for i in range(m)])
    H = I + D
    A = 3 * I / 4 + H * L
    inv = A.inv()
    j0 = -Bt * (B * H * Bt * C / 64 - site) / 1024
    y = inv * j0
    after = C - 32 * B * (j0 + y / 4)
    curvature = M(
        [
            [(3 * (C[i, 0] - 2) ** 2 - 1) if i == j else 0 for j in range(n)]
            for i in range(n)
        ]
    )
    dfp = inverse * (-Bt * (B * Bt / 64 - curvature) / 1024) / 2
    columns = []
    for k in range(n):
        dH = M(
            [
                [
                    O[i, j] * (dfp[i, k] * fp[j, 0] + fp[i, 0] * dfp[j, k]) / 8
                    for j in range(m)
                ]
                for i in range(m)
            ]
        )
        ek = M([[int(i == k)] for i in range(n)])
        dj0 = -Bt * (B * (dH * Bt * C + H * Bt * ek) / 64 - curvature * ek) / 1024
        dy = inv * (dj0 - dH * L * y)
        columns.append(ek - 32 * B * (dj0 + dy / 4))
    J = M([[columns[j][i, 0] for j in range(n)] for i in range(n)])
    # Correlated resolvent difference: never subtract unrelated H enclosures.
    alpha, beta = _norm(inverse * D * L), _norm(D)
    _need(alpha < 1 and beta < 1, "OS split Neumann premises unresolved")
    rhs = -L * D * Bt * C / (1024 * 64) - D * L * (2 * fp)
    dy_bound = _norm(inverse) * _norm(rhs) / (1 - alpha)
    df = (dy_bound / 2 + _norm(D * fp)) / (1 - beta)
    coefficient = sum((O[i, j] / 8) ** 2 for i in range(m) for j in range(m)).sqrt()
    split = coefficient * (2 * _norm(fp) * df + df**2)
    _need(
        split
        < q(
            exact_number(kernel.profile.baseline.params_resolved.realization.tolerance)
        ),
        "whole-domain OS split tolerance unresolved",
    )
    limit = q(
        exact_number(kernel.profile.baseline.params_resolved.solver.conditioning_limit)
    )
    condition = m * _norm(A) * _norm(inv)
    _need(
        condition < limit and m * _norm(H) < limit,
        "whole-domain conditioning unresolved",
    )
    _need(
        all(sum(J[i, j] for i in range(n)).contains(1) for j in range(n)),
        "derivative charge identity failed",
    )
    return after, J, split, condition


@lru_cache(maxsize=16)
@flint_operation
def _verify(raw):
    data = decode_canonical_json(raw)
    if data.get("schema_version") in ("grc9v4-native-cpc-trap-operands-v1", "grc9v4-native-ccipc-trap-operands-v1"):
        from .grc_9_v4_completion_cpc import verify
        return verify(data)
    if set(data) != {"schema_version", "binding", "center", "S", "U"} or data[
        "schema_version"
    ] not in (
        "grc9v4-native-cos-trap-operands-v1",
        "grc9v4-native-cci-trap-operands-v1",
    ):
        raise ValueError("closed full-domain operands required")
    b = data["binding"]
    kernel = quartic_kernel(
        GRCV4Graph.from_payload(b["graph"]),
        quartic_profile(b["profile"]),
    )
    policy = CompletionPolicy.from_payload(b["policy"])
    family = kernel.profile.FAMILY
    expected_schema = (
        "grc9v4-native-" + family.replace("_", "").lower() + "-trap-operands-v1"
    )
    if (
        data["schema_version"] != expected_schema
        or policy.numerical_policy_id != kernel.profile.NUMERICS
    ):
        raise ValueError("certificate family or numerical policy mismatch")
    analytic = _analytic if family == "C_OS" else lambda k, C: k.analytic(C)
    if b != binding(kernel, policy, b["role"], b["charge"]):
        raise ValueError("certificate equation/reference/context binding mismatch")
    if policy.step_duration != "32":
        raise ValueError("quartic C certificate requires duration 32")
    center = ExactResources(kernel.graph, tuple(data["center"]), b["charge"])
    S, U = _matrix(data["S"]), _matrix(data["U"])
    n = len(center.C)
    if (S.nrows(), S.ncols(), U.nrows(), U.ncols()) != (n, n - 1, n - 1, n):
        raise ValueError("complete physical charge chart required")
    f = _flint_module()
    identity = f.fmpq_mat([[int(i == j) for j in range(n - 1)] for i in range(n - 1)])
    if U * S != identity or any(
        sum(S[i, j] for i in range(n)) != 0 for j in range(n - 1)
    ):
        raise ValueError("full-rank exact charge-tangent chart required")
    geometry = _geometry(kernel, policy, center, S)
    precision = getattr(kernel, "precision_bits", 512)
    with _ARB_CONTEXT_LOCK, f.ctx.workprec(precision):
        c = f.arb_mat([[rational(x)] for x in center.C])
        box = f.arb_mat(
            [
                [f.arb(rational(x), sum(abs(S[i, j]) for j in range(n - 1)))]
                for i, x in enumerate(center.C)
            ]
        )
        _, J, split, condition = analytic(kernel, box)
        q = _norm(f.arb_mat(U) * J * f.arb_mat(S))
        after, _, _, _ = analytic(kernel, c)
        defect = _norm(f.arb_mat(U) * (after - c))
        margin = (1 - q - defect).lower()
        _need(q < 1 and margin > 0, "full-map strict invariant contraction unresolved")
        numeric = kernel.uniform_rounding_bound(data["U"], _lower(margin))
        result = {
            "q": _upper(q),
            "center_defect": _upper(defect),
            "image_margin": _lower(margin),
            "full_step_error": numeric["full_step_error"],
            "split_upper": _upper(split),
            "conditioning_upper": _upper(condition),
            "precision_bits": precision,
            "exact_charge_preserved": True,
            "geometry": geometry,
            "operands_digest": digest(data),
        }
    if family == "C_CI":
        result["root_derivative_upper"] = result.pop("split_upper")
        result["root_domain"] = kernel.root_domain.to_dict()
    return FrozenJSONMap(result)


@dataclass(frozen=True, slots=True)
class CompletionCertificate:
    operands: FrozenJSONMap
    proof: FrozenJSONMap = field(init=False)

    def __post_init__(self):
        operands = FrozenJSONMap(self.operands)
        proof = _verify(canonical_json_bytes(operands.to_dict()))
        object.__setattr__(self, "operands", operands)
        object.__setattr__(self, "proof", proof)

    @classmethod
    def create(cls, kernel, policy, role, center, S, U):
        if type(center) is not (ExactCarrierState if kernel.profile.FAMILY in ("C_PC", "C_CI_PC") else ExactResources) or center.graph != kernel.graph:
            raise ValueError("center must use the actual certificate graph")
        return cls(
            FrozenJSONMap(
                {
                    "schema_version": "grc9v4-native-"
                    + kernel.profile.FAMILY.replace("_", "").lower()
                    + "-trap-operands-v1",
                    "binding": binding(kernel, policy, role, center.charge),
                    "center": list(center.C),
                    "S": S,
                    "U": U,
                    **({"carrier_center": [list(r) for r in center.Z_4], "carrier_radius": "1/100000000",
                        "carrier_pairs": [list(p) for p in carrier_pairs(kernel.graph)]} if kernel.profile.FAMILY in ("C_PC", "C_CI_PC") else {}),
                }
            )
        )

    def require_binding(self, kernel, policy, role, charge):
        if self.operands["binding"].to_dict() != binding(kernel, policy, role, charge):
            raise ValueError(
                "stale/wrong certificate graph/profile/context/reference/role/policy/charge"
            )

    @flint_operation
    def membership(self, state):
        if self.operands["binding"]["profile"]["identity_payload"]["profile_family_id"] in ("C_PC", "C_CI_PC"):
            from .grc_9_v4_completion_cpc import membership
            return membership(self, state)
        if type(state) is not ExactResources:
            raise ValueError("resource-only certificate cannot omit a carrier")
        b = self.operands["binding"]
        if (
            state.graph.to_payload() != b["graph"].to_dict()
            or state.charge != b["charge"]
        ):
            raise ValueError("state graph or exact charge differs from certificate")
        delta = _flint_module().fmpq_mat(
            [
                [rational(x) - rational(c)]
                for x, c in zip(state.C, self.operands["center"], strict=True)
            ]
        )
        coordinates = _matrix(self.operands["U"]) * delta
        norm = max(abs(x) for x in coordinates.entries())
        return norm <= 1, str(norm)

    @property
    def certificate_id(self):
        return digest(self.to_payload())

    def to_payload(self):
        return {"operands": self.operands.to_dict(), "proof": self.proof.to_dict()}

    @classmethod
    def from_payload(cls, value):
        if set(value) != {"operands", "proof"}:
            raise ValueError("closed native certificate required")
        result = cls(FrozenJSONMap(value["operands"]))
        if result.to_payload() != value:
            raise ValueError("certificate proof differs from recomputed mathematics")
        return result

    @staticmethod
    def cache_info():
        return _verify.cache_info()._asdict()

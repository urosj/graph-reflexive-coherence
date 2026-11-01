"""Explicit quartic and exact-resource successors; no public capability grant.

Old binary64 declarations/states are not upgraded by these decoders. FLINT is
required only on use. Exact values use canonical rational strings on the wire.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from functools import wraps
import re
from types import MappingProxyType

from .grc_v4_codec import canonical_json_bytes, decode_canonical_json, payload_identity
from .grc_v4_geometry import GRCV4Graph
from .grc_v4_profile import GRCV4Profile, GRCV4ProfileIdentityPayload
from .grc_v4_state import FrozenJSONMap
from .grc_v4_exact import ExactBackend, exact_backend, exact_number, integer_ratio, is_exact

FLUX_BITS = 128
NUMERICAL_POLICY = "spark_cos_exact_flint_flux128_v1"
CHARGE_POLICY = MappingProxyType({
    "schema_version": "grcv4-charge-policy-v2",
    "policy_id": "exact_rational_incidence_charge_v1",
    "resource_encoding": "canonical_rational_strings_v1",
    "accumulation_order": "exact_rational_sum",
    "repair_policy": "never_mutate_resource",
})


def flint_operation(function):
    """This opt-in policy retains FLINT across calls and restores caller scope."""
    @wraps(function)
    def execute(*args, **kwargs):
        with exact_backend(ExactBackend.FLINT):
            return function(*args, **kwargs)
    return execute


@flint_operation
def rational(value):
    """Admit lossless canonical strings; never coerce floats or booleans."""
    if type(value) is not str or re.fullmatch(r"-?(?:0|[1-9][0-9]*)(?:/[1-9][0-9]*)?", value) is None:
        raise ValueError("canonical rational string required")
    operands = value.split("/")
    result = exact_number(int(operands[0]), int(operands[1]) if len(operands) == 2 else 1)
    if str(result) != value:
        raise ValueError("rational must be reduced without signed zero or /1")
    return result


def _identity(prefix, value):
    return prefix + sha256(canonical_json_bytes(value)).hexdigest()


@dataclass(frozen=True, slots=True)
class QuarticSite:
    c0: str = "2"
    a: str = "1"
    mu: str = "1"
    units_id: str = "grcv4_nondimensional_reference_v1"

    def __post_init__(self):
        c0, a, mu = map(rational, (self.c0, self.a, self.mu))
        if (not c0 > a > 0 or mu <= 0 or type(self.units_id) is not str or
                self.units_id != "grcv4_nondimensional_reference_v1"):
            raise ValueError("unsupported quartic coefficients or units")

    def evaluate(self, resource: str):
        x = rational(resource)
        if x < 0:
            raise ValueError("site resource must be nonnegative")
        z, a, mu = x - rational(self.c0), rational(self.a), rational(self.mu)
        return (mu * (z*z-a*a)**2 / 4, mu * (z**3-a*a*z), mu * (3*z*z-a*a))

    def to_payload(self):
        return dict(schema_version="grcv4-homogeneous-quartic-site-v1",
                    evaluator_id="homogeneous_quartic_site_v1", c0=self.c0,
                    a=self.a, mu=self.mu, units_id=self.units_id)

    @classmethod
    def from_payload(cls, value):
        data = FrozenJSONMap(value).to_dict()
        if set(data) != set(cls().to_payload()) or data["schema_version"] != "grcv4-homogeneous-quartic-site-v1" or data["evaluator_id"] != "homogeneous_quartic_site_v1":
            raise ValueError("explicit closed quartic site required")
        return cls(*(data[k] for k in ("c0", "a", "mu", "units_id")))


@dataclass(frozen=True, slots=True, eq=False)
class QuarticCOSProfile:
    """Explicit resolved-v2 declaration around validated unchanged v1 sections.

The private baseline is a structural validator, not an executable substitute
for the new law/charge policy. This type is deliberately not a GRCV4Profile.
"""
    baseline: GRCV4Profile
    site: QuarticSite

    def __post_init__(self):
        if type(self.baseline) is not GRCV4Profile or type(self.site) is not QuarticSite:
            raise TypeError("typed baseline and explicit site required")
        if self.baseline.identity_payload.profile_family_id != "C_OS":
            raise ValueError("only C_OS is implemented by this successor")
        if self.baseline.params_resolved.candidate.potential_evaluator_id != "quadratic_site_potential_zero_derivative_v1":
            raise ValueError("explicit zero-site predecessor required")
        if self.site.units_id != self.baseline.params_resolved.common.units_id:
            raise ValueError("site/common units mismatch")

    @property
    def params_resolved(self):
        data = self.baseline.params_resolved.to_payload()
        data["schema_version"] = "grcv4-resolved-params-v2"
        data["candidate"].update(schema_version="grcv4-candidate-c-params-v2",
                                 potential_evaluator_id="homogeneous_quartic_site_v1",
                                 site_binding=self.site.to_payload())
        data["charge"] = dict(CHARGE_POLICY)
        return FrozenJSONMap(data)

    @property
    def identity_payload(self):
        data = self.baseline.identity_payload.to_payload()
        data["params_hash"] = _identity("grcv4-params-sha256:", self.params_resolved.to_dict())
        return GRCV4ProfileIdentityPayload.from_payload(data)

    @property
    def complete_profile_id(self):
        return payload_identity("profile_identity_payload", self.identity_payload.to_payload())

    def to_payload(self):
        return dict(identity_payload=self.identity_payload.to_payload(),
                    params_resolved=self.params_resolved.to_dict(),
                    complete_profile_id=self.complete_profile_id)

    def to_canonical_bytes(self):
        return canonical_json_bytes(self.to_payload())

    def __eq__(self, other):
        return type(other) is type(self) and self.to_canonical_bytes() == other.to_canonical_bytes()

    def __hash__(self):
        return hash(self.to_canonical_bytes())

    @classmethod
    def from_canonical_bytes(cls, raw):
        return cls.from_payload(decode_canonical_json(raw))

    @classmethod
    def from_payload(cls, value):
        from .grc_v4_profile import ChargePolicy, resolve_profile

        data = FrozenJSONMap(value).to_dict()
        if set(data) != {"identity_payload", "params_resolved", "complete_profile_id"}:
            raise ValueError("closed quartic profile required")
        params = data["params_resolved"]
        if params.get("schema_version") != "grcv4-resolved-params-v2" or params.get("charge") != CHARGE_POLICY:
            raise ValueError("explicit resolved and exact-charge successors required")
        candidate = params["candidate"]
        if candidate.get("schema_version") != "grcv4-candidate-c-params-v2" or candidate.get("potential_evaluator_id") != "homogeneous_quartic_site_v1":
            raise ValueError("explicit quartic candidate successor required")
        site = QuarticSite.from_payload(candidate.pop("site_binding"))
        # Validate every unchanged section through the frozen decoder. This
        # projection is never published, executed or given the successor ID.
        params["schema_version"] = "grcv4-resolved-params-v1"
        candidate.update(schema_version="grcv4-candidate-c-params-v1",
                         potential_evaluator_id="quadratic_site_potential_zero_derivative_v1")
        params["charge"] = ChargePolicy.from_payload(dict(
            schema_version="grcv4-charge-policy-v1", policy_id="stable_pairwise_binary64_charge_v1",
            accumulation_order="canonical_live_vertex_balanced_binary_tree",
            rounding_mode="IEEE754_binary64_roundTiesToEven", absolute_tolerance=0,
            relative_tolerance=0, repair_policy="never_mutate_resource",
            remainder_policy="compatibility_projection_is_none")).to_payload()
        identity = dict(data["identity_payload"])
        identity["params_hash"] = payload_identity("resolved_params", params)
        result = cls(resolve_profile(params, identity), site)
        if canonical_json_bytes(result.to_payload()) != canonical_json_bytes(value):
            raise ValueError("quartic profile identity or content mismatch")
        return result


@dataclass(frozen=True, slots=True)
class ExactResources:
    graph: GRCV4Graph
    C: tuple[str, ...]
    charge: str

    def __post_init__(self):
        if type(self.graph) is not GRCV4Graph:
            raise TypeError("typed graph required")
        if type(self.C) not in (tuple, list):
            raise TypeError("ordered resource array required")
        values = tuple(self.C)
        if len(values) != len(self.graph.live_node_ids):
            raise ValueError("resource graph coverage mismatch")
        qs = tuple(map(rational, values))
        if any(x < 0 for x in qs) or sum(qs) != rational(self.charge):
            raise ValueError("nonnegative resources with exact declared charge required")
        object.__setattr__(self, "C", values)

    def to_payload(self):
        return dict(schema_version="grcv4-exact-resource-state-v1", graph=self.graph.to_payload(),
                    C=list(self.C), charge=self.charge)

    def to_canonical_bytes(self):
        return canonical_json_bytes(self.to_payload())

    @classmethod
    def from_canonical_bytes(cls, raw):
        value = decode_canonical_json(raw)
        if set(value) != {"schema_version", "graph", "C", "charge"} or value["schema_version"] != "grcv4-exact-resource-state-v1":
            raise ValueError("closed exact-resource state required")
        if type(value["C"]) is not list:
            raise ValueError("resource wire coordinates must be an array")
        return cls(GRCV4Graph.from_payload(value["graph"]), tuple(value["C"]), value["charge"])

    def advance(self, flux: tuple[str, ...], duration: str):
        if type(flux) not in (tuple, list):
            raise TypeError("ordered edge flux array required")
        dt = rational(duration)
        if dt < 0 or len(flux) != len(self.graph.oriented_edges):
            raise ValueError("nonnegative duration and complete edge flux required")
        values = list(map(rational, self.C))
        # Exact incidence transfers preserve the sum without adjusting a node.
        for edge, value in zip(self.graph.oriented_edges, flux, strict=True):
            transfer = dt * rational(value)
            values[self.graph.node_index(edge.tail_node_id)] -= transfer
            values[self.graph.node_index(edge.head_node_id)] += transfer
        return ExactResources(self.graph, tuple(map(str, values)), self.charge)

    def transfer(self, target: GRCV4Graph, matrix: tuple[tuple[str, ...], ...]):
        """Exact column-stochastic resource map; does not admit a topology event."""
        if type(target) is not GRCV4Graph or type(matrix) not in (tuple, list) or any(type(row) not in (tuple, list) for row in matrix):
            raise TypeError("typed target graph and ordered matrix rows required")
        A = tuple(tuple(map(rational, row)) for row in matrix)
        if len(A) != len(target.live_node_ids) or any(len(row) != len(self.C) for row in A):
            raise ValueError("transfer coverage mismatch")
        if any(x < 0 for row in A for x in row) or any(sum(row[j] for row in A) != 1 for j in range(len(self.C))):
            raise ValueError("exact nonnegative column-stochastic transfer required")
        C = tuple(map(rational, self.C))
        return ExactResources(target, tuple(str(sum(x*y for x, y in zip(row, C, strict=True))) for row in A), self.charge)

    def spatial_diagnostics(self, *, sign: int, gradient: str, hessian: str,
                            contrast: str, core_resource: str):
        """Unit-weight fixed-row arithmetic; no basin or completion classifier.

        Every predicate uses the exact authoritative C, with zero evaluation
        error. Equal adjacent values produce order zero; thresholds stay strict.
        The returned tuple follows the sole port owner's node order.
        """
        if type(sign) is not int or sign not in (-1, 1) or self.graph.port_graph is None:
            raise ValueError("signed fixed-port graph required")
        g, h, contrast_q, core = map(rational, (gradient, hessian, contrast, core_resource))
        if min(g, h, contrast_q, core) <= 0:
            raise ValueError("strict positive diagnostic thresholds required")
        C = dict(zip(self.graph.live_node_ids, map(rational, self.C), strict=True))
        terms = {node: [[], [], []] for node in C}
        neighbors = {node: set() for node in C}
        for edge in self.graph.port_graph.edges:
            for here, there in ((edge.tail, edge.head), (edge.head, edge.tail)):
                terms[here.node_id][(here.port-1)//3].append(C[there.node_id]-C[here.node_id])
                if here.node_id != there.node_id:
                    neighbors[here.node_id].add(there.node_id)
        rows = []
        for node in self.graph.live_node_ids:
            means = tuple(sum(row)/len(row) if row else rational("0") for row in terms[node])
            squared = sum(x*x for x in means)
            seed = squared < g*g and min(sign*x for x in means) > h
            anchor = (seed and bool(neighbors[node]) and C[node] > core and
                      all(sign*(C[v]-C[node]) > contrast_q for v in neighbors[node]))
            rows.append(FrozenJSONMap(dict(node_id=node, gradient=list(map(str, means)),
                gradient_squared=str(squared), minimum_signed_gradient=str(min(sign*x for x in means)),
                seed=bool(seed), anchor=bool(anchor), evaluation_error="0")))
        return tuple(rows)

    def edge_orders(self, sign: int):
        """Sign of psi(head)-psi(tail); an exact tie is always zero."""
        if type(sign) is not int or sign not in (-1, 1):
            raise ValueError("landscape sign must be -1 or 1")
        C = dict(zip(self.graph.live_node_ids, map(rational, self.C), strict=True))
        gaps = (sign*(C[e.head_node_id]-C[e.tail_node_id]) for e in self.graph.oriented_edges)
        return tuple(int(x > 0)-int(x < 0) for x in gaps)


@flint_operation
def round_flux(value):
    """Nearest/even on the fixed 2^-128 lattice, using integer arithmetic."""
    if not is_exact(value):
        raise TypeError("exact FLINT flux required")
    numerator, denominator = integer_ratio(value)
    numerator <<= FLUX_BITS
    sign = -1 if numerator < 0 else 1
    quotient, remainder = divmod(abs(numerator), denominator)
    quotient += int(2*remainder > denominator or (2*remainder == denominator and quotient % 2 == 1))
    result = exact_number(sign*quotient, 1 << FLUX_BITS)
    if abs(result-value) > exact_number(1, 1 << (FLUX_BITS+1)):
        raise ArithmeticError("flux rounding bound failed")
    return result

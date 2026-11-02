"""Explicit quartic A_OS declarations and exact positive conductance history."""

from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
from typing import ClassVar

from .grc_v4_codec import canonical_json_bytes, decode_canonical_json, payload_identity
from .grc_v4_geometry import GRCV4Graph
from .grc_v4_profile import GRCV4Profile
from .grc_v4_spark_state import (
    CHARGE_POLICY,
    ExactResources,
    QuarticCOSProfile,
    QuarticSite,
    flint_operation,
    rational,
)
from .grc_v4_state import FrozenJSONMap

AOS_NUMERICAL_POLICY = "spark_aos_arb256_flux128_conductance192_v1"
ACI_NUMERICAL_POLICY = "spark_aci_arb256_flux128_conductance192_v1"


def descriptor_identity(graph):
    from .grc_9_v4_topology import GRC9V4CandidateADifferentialReference

    value = GRC9V4CandidateADifferentialReference(graph.port_graph).to_payload()
    value.update(
        descriptor_version="grc9v4-candidate-a-fixed-row-exact-v1",
        rounding="exact_rational_weighted_row_v1",
    )
    return (
        "grcv4-a-descriptor-sha256:" + sha256(canonical_json_bytes(value)).hexdigest()
    )


@dataclass(frozen=True, slots=True, eq=False)
class QuarticAOSProfile(QuarticCOSProfile):
    FAMILY: ClassVar[str] = "A_OS"
    NUMERICS: ClassVar[str] = AOS_NUMERICAL_POLICY

    def __post_init__(self):
        if (
            type(self.baseline) is not GRCV4Profile
            or type(self.site) is not QuarticSite
        ):
            raise TypeError("typed A baseline and quartic site required")
        if self.baseline.identity_payload.profile_family_id != self.FAMILY:
            raise ValueError("quartic A family mismatch")
        if (
            self.baseline.params_resolved.candidate.site_potential_id
            != "quadratic_site_potential_zero_derivative_v1"
        ):
            raise ValueError("explicit zero-site predecessor required")
        if (
            self.baseline.params_resolved.common.units_id
            != "grcv4_nondimensional_reference_v1"
        ):
            raise ValueError("site/common units mismatch")

    @property
    def params_resolved(self):
        data = self.baseline.params_resolved.to_payload()
        data["schema_version"] = "grcv4-resolved-params-v2"
        data["candidate"].update(
            schema_version="grcv4-candidate-a-params-v2",
            site_potential_id="homogeneous_quartic_site_v1",
            site_binding=self.site.to_payload(),
        )
        data["charge"] = dict(CHARGE_POLICY)
        return FrozenJSONMap(data)

    @classmethod
    def from_payload(cls, value):
        from .grc_v4_profile import ChargePolicy, resolve_profile

        data = FrozenJSONMap(value).to_dict()
        if set(data) != {"identity_payload", "params_resolved", "complete_profile_id"}:
            raise ValueError("closed quartic A profile required")
        params = data["params_resolved"]
        if (
            params.get("schema_version") != "grcv4-resolved-params-v2"
            or params.get("charge") != CHARGE_POLICY
        ):
            raise ValueError("explicit resolved and exact-charge successors required")
        candidate = params["candidate"]
        if (
            candidate.get("schema_version") != "grcv4-candidate-a-params-v2"
            or candidate.get("site_potential_id") != "homogeneous_quartic_site_v1"
        ):
            raise ValueError("explicit quartic A candidate successor required")
        site = QuarticSite.from_payload(candidate.pop("site_binding"))
        params["schema_version"] = "grcv4-resolved-params-v1"
        candidate.update(
            schema_version="grcv4-candidate-a-params-v1",
            site_potential_id="quadratic_site_potential_zero_derivative_v1",
        )
        params["charge"] = ChargePolicy.from_payload(
            {
                "schema_version": "grcv4-charge-policy-v1",
                "policy_id": "stable_pairwise_binary64_charge_v1",
                "accumulation_order": "canonical_live_vertex_balanced_binary_tree",
                "rounding_mode": "IEEE754_binary64_roundTiesToEven",
                "absolute_tolerance": 0,
                "relative_tolerance": 0,
                "repair_policy": "never_mutate_resource",
                "remainder_policy": "compatibility_projection_is_none",
            }
        ).to_payload()
        identity = dict(data["identity_payload"])
        identity["params_hash"] = payload_identity("resolved_params", params)
        result = cls(resolve_profile(params, identity), site)
        if canonical_json_bytes(result.to_payload()) != canonical_json_bytes(value):
            raise ValueError("quartic A profile identity or content mismatch")
        return result


@dataclass(frozen=True, slots=True, eq=False)
class QuarticACIProfile(QuarticAOSProfile):
    FAMILY: ClassVar[str] = "A_CI"
    NUMERICS: ClassVar[str] = ACI_NUMERICAL_POLICY


@lru_cache(maxsize=16)
def _fixed_rows(raw):
    graph = GRCV4Graph.from_payload(decode_canonical_json(raw))
    if graph.port_graph is None:
        raise ValueError("fixed GRC9 port chart required")
    rows = [[[] for _ in range(3)] for _ in graph.live_node_ids]
    indices = {edge: i for i, edge in enumerate(graph.live_edge_ids)}
    for edge in graph.port_graph.edges:
        k = indices[edge.edge_id]
        for here, there in ((edge.tail, edge.head), (edge.head, edge.tail)):
            rows[graph.node_index(here.node_id)][(here.port - 1) // 3].append(
                (k, graph.node_index(there.node_id))
            )
    return tuple(tuple(tuple(row) for row in node) for node in rows)


def fixed_rows(graph):
    return _fixed_rows(canonical_json_bytes(graph.to_payload()))


@dataclass(frozen=True, slots=True)
class ExactConductanceState(ExactResources):
    W_A: tuple[str, ...]

    @flint_operation
    def __post_init__(self):
        ExactResources.__post_init__(self)
        if type(self.W_A) not in (tuple, list) or len(self.W_A) != len(
            self.graph.live_edge_ids
        ):
            raise ValueError("complete ordered edge conductance history required")
        values = tuple(self.W_A)
        if any(rational(x) <= 0 for x in values):
            raise ValueError("strictly positive conductance required")
        object.__setattr__(self, "W_A", values)

    def to_payload(self):
        return dict(
            ExactResources.to_payload(self),
            schema_version="grcv4-exact-conductance-state-v1",
            W_A=list(self.W_A),
        )

    @classmethod
    def from_canonical_bytes(cls, raw):
        value = decode_canonical_json(raw)
        if (
            set(value) != {"schema_version", "graph", "C", "charge", "W_A"}
            or value["schema_version"] != "grcv4-exact-conductance-state-v1"
        ):
            raise ValueError("closed full C/W state required")
        return cls(
            GRCV4Graph.from_payload(value["graph"]),
            value["C"],
            value["charge"],
            value["W_A"],
        )

    def advance(self, flux, duration):
        raise ValueError("A_OS requires an atomic resource/conductance writer")

    def advance_conductance(self, flux, duration, W):
        resources = ExactResources.advance(self, flux, duration)
        return type(self)(self.graph, resources.C, self.charge, W)

    def transfer(self, target, matrix):
        raise ValueError("conductance transfer requires explicit edge lineage")

    @flint_operation
    def spatial_diagnostics(self, *, sign, gradient, hessian, contrast, core_resource):
        if type(sign) is not int or sign not in (-1, 1):
            raise ValueError("signed fixed-port graph required")
        g, h, barrier, core = map(
            rational, (gradient, hessian, contrast, core_resource)
        )
        if min(g, h, barrier, core) <= 0:
            raise ValueError("strict positive diagnostic thresholds required")
        C, W = tuple(map(rational, self.C)), tuple(map(rational, self.W_A))
        result = []
        for i, terms in enumerate(fixed_rows(self.graph)):
            means = tuple(
                sum(W[k] * (C[j] - C[i]) for k, j in row) / sum(W[k] for k, _ in row)
                if row
                else rational("0")
                for row in terms
            )
            neighbors = {j for row in terms for _, j in row if j != i}
            squared = sum(x * x for x in means)
            seed = squared < g * g and min(sign * x for x in means) > h
            anchor = (
                seed
                and bool(neighbors)
                and C[i] > core
                and all(sign * (C[j] - C[i]) > barrier for j in neighbors)
            )
            result.append(
                FrozenJSONMap(
                    {
                        "node_id": self.graph.live_node_ids[i],
                        "gradient": list(map(str, means)),
                        "gradient_squared": str(squared),
                        "minimum_signed_gradient": str(min(sign * x for x in means)),
                        "seed": bool(seed),
                        "anchor": bool(anchor),
                        "evaluation_error": "0",
                    }
                )
            )
        return tuple(result)

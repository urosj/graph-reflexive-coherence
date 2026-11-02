"""Exact signed symmetric-star carrier states; explicit PC serialization only."""

from dataclasses import dataclass
from functools import lru_cache

from .grc_v4_codec import canonical_json_bytes, decode_canonical_json
from .grc_v4_geometry import GRCV4Graph
from .grc_v4_spark_state import ExactResources, flint_operation, rational


@lru_cache(maxsize=16)
def _pairs(encoded):
    graph = GRCV4Graph.from_payload(decode_canonical_json(encoded))
    endpoints = [{e.tail_node_id, e.head_node_id} for e in graph.oriented_edges]
    return tuple(
        (i, j)
        for i, a in enumerate(endpoints)
        for j, b in enumerate(endpoints)
        if i <= j and a & b
    )


def carrier_pairs(graph):
    return _pairs(canonical_json_bytes(graph.to_payload()))


@dataclass(frozen=True, slots=True)
class ExactCarrierState(ExactResources):
    Z_4: tuple[tuple[str, ...], ...]

    @flint_operation
    def __post_init__(self):
        ExactResources.__post_init__(self)
        if type(self.Z_4) not in (tuple, list) or any(
            type(row) not in (tuple, list) for row in self.Z_4
        ):
            raise TypeError("complete ordered carrier matrix required")
        m = len(self.graph.oriented_edges)
        z = tuple(tuple(row) for row in self.Z_4)
        if len(z) != m or any(len(row) != m for row in z):
            raise ValueError("carrier graph coverage")
        q = tuple(tuple(map(rational, row)) for row in z)
        pairs = set(carrier_pairs(self.graph))
        if any(
            q[i][j] != q[j][i] or ((min(i, j), max(i, j)) not in pairs and q[i][j] != 0)
            for i in range(m)
            for j in range(m)
        ):
            raise ValueError("exact symmetric star carrier required")
        if sum(x * x for row in q for x in row) > rational("1/4096"):
            raise ValueError("carrier Frobenius norm exceeds 1/64")
        object.__setattr__(self, "Z_4", z)

    def to_payload(self):
        return dict(
            ExactResources.to_payload(self),
            schema_version="grcv4-exact-carrier-state-v1",
            Z_4=[list(r) for r in self.Z_4],
        )

    @classmethod
    def from_canonical_bytes(cls, raw):
        v = decode_canonical_json(raw)
        if (
            set(v) != {"schema_version", "graph", "C", "charge", "Z_4"}
            or v["schema_version"] != "grcv4-exact-carrier-state-v1"
        ):
            raise ValueError("closed full C/Z state required")
        return cls(GRCV4Graph.from_payload(v["graph"]), v["C"], v["charge"], v["Z_4"])

    @classmethod
    def zero(cls, resources):
        m = len(resources.graph.oriented_edges)
        return cls(
            resources.graph,
            resources.C,
            resources.charge,
            tuple(("0",) * m for _ in range(m)),
        )

    def advance(self, flux, duration):
        raise ValueError("PC requires an atomic resource/carrier writer")

    def advance_carrier(self, flux, duration, Z):
        resources = ExactResources.advance(self, flux, duration)
        return type(self)(self.graph, resources.C, self.charge, Z)

    def transfer(self, target, matrix):
        raise ValueError("PC history transfer is owned by the explicit event policy")


def exact_state(value):
    cls = (
        ExactCarrierState
        if value.get("schema_version") == "grcv4-exact-carrier-state-v1"
        else ExactResources
    )
    return cls.from_canonical_bytes(canonical_json_bytes(value))

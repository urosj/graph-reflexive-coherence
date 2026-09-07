"""P9-3.1 fixed-graph coordinates, pairings and physical-flux flat/sharp.

The serialized order is the coordinate order. Positive tail-to-head flux has
positive outward divergence at its tail: B[tail,e]=+1, B[head,e]=-1. Loops
cancel in B; parallel edges keep distinct IDs. No legacy slots or port chart
enter this backend. Descriptor hashes below are versioned implementation-local
identities, not additions to the frozen wire schema or stage-cache admission.

All retained numerical storage is immutable binary64 tuples. Positivity is
checked exactly on those dyadic values; dense solves use the reviewed NumPy
dependency. Local positivity does not certify a complete profile's conditioning,
selector, stage provenance or solver domain.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
import hashlib
import math
from types import MappingProxyType
from typing import ClassVar, Literal, Self, TypeAlias, cast

from .grc_v4_codec import (
    JSONValue,
    _dependency,
    canonical_json_bytes,
    decode_canonical_json,
    decode_json,
    validate_payload,
)
from .grc_v4_profile import GRCV4CommonParams
from .grc_v4_state import _number, _text, _vector

NodeId: TypeAlias = str | int
Matrix: TypeAlias = tuple[tuple[float, ...], ...]
POSITIVITY_POLICY_ID = "exact_binary64_sylvester_bareiss_v1"


def _identity(prefix: str, payload: object) -> str:
    return prefix + ":" + hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def _node_id(value: object) -> NodeId:
    if type(value) is str:
        value.encode("utf-8")
        return value
    if type(value) not in (int, float):
        raise TypeError("node ID must be a JSON string or safe integer")
    number = _number(value)
    if not number.is_integer() or abs(number) > 2**53 - 1:
        raise ValueError("node ID must be a safe integer")
    return int(number)


def _ordered(value: object) -> Sequence[object]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise TypeError("expected an ordered sequence")
    return value


def _computed(value: float) -> float:
    # Arithmetic may produce -0. Its exact real value has a unique +0 wire
    # representation. Inputs still reject -0; no resource repair occurs here.
    if not math.isfinite(value):
        raise ValueError("nonfinite numerical result")
    return 0.0 if value == 0 else value


def _matvec(matrix: Matrix, vector: tuple[float, ...]) -> tuple[float, ...]:
    return tuple(
        _computed(sum(a * b for a, b in zip(row, vector, strict=True)))
        for row in matrix
    )


def _matrix(value: object, size: int) -> Matrix:
    try:
        view = memoryview(value)  # type: ignore[arg-type]
    except TypeError:
        rows = _ordered(value)
    else:
        if view.ndim != 2 or view.format not in "bBhHiIlLqQfd":
            raise TypeError("expected a real numeric matrix")
        if view.shape != (size, size):
            raise ValueError("matrix shape does not match its graph space")
        rows = view.tolist()
    matrix = tuple(_vector(row) for row in rows)
    if len(matrix) != size or any(len(row) != size for row in matrix):
        raise ValueError("matrix shape does not match its graph space")
    return matrix


def _require_positive_definite(matrix: Matrix) -> None:
    """Exact Sylvester criterion by fraction-free elimination, at every size.

    A common positive power-of-two denominator turns the finite binary64
    entries into an integer matrix without rounding or changing its inertia.
    Bareiss pivots are its leading principal determinants. All must be strictly
    positive; a nonpositive pivot rejects before any subsequent division.
    Divisions are exact and checked, including the final determinant. No
    floating factorization, eigenvalue estimate or tolerance decides admission.

    Integer work is local and discarded. Stored values and numerical solves
    remain binary64. Dense validation costs O(n**3) integer operations, with
    growing integer bit lengths; diagonal reference pairings avoid elimination.
    """
    size = len(matrix)
    if any(matrix[i][i] <= 0 for i in range(size)):
        raise ValueError("Hodge matrix must be positive definite")
    if all(matrix[i][j] == 0 for i in range(size) for j in range(i)):
        return  # Symmetry was checked by _spd; includes the empty space.

    ratios = [[x.as_integer_ratio() for x in row] for row in matrix]
    denominator = max(d for row in ratios for _, d in row)
    work = [[n * (denominator // d) for n, d in row] for row in ratios]
    previous = 1
    for k in range(size):
        pivot = work[k][k]
        if pivot <= 0:
            raise ValueError("Hodge matrix must be positive definite")
        for i in range(k + 1, size):
            for j in range(k + 1, size):
                numerator = pivot * work[i][j] - work[i][k] * work[k][j]
                quotient, remainder = divmod(numerator, previous)
                if remainder:
                    # An implementation/integer-arithmetic invariant failed.
                    # Never turn truncated division into a positivity decision.
                    raise ValueError("exact Hodge positivity certificate failed")
                work[i][j] = quotient
        previous = pivot


def _spd(value: object, size: int) -> Matrix:
    matrix = _matrix(value, size)
    if any(matrix[i][j] != matrix[j][i] for i in range(size) for j in range(i)):
        raise ValueError("Hodge matrix must be exactly symmetric")
    if size:
        _dependency("numpy")  # Preserve the declared numerical backend requirement.
    _require_positive_definite(matrix)
    return matrix


def _diagonal(values: tuple[float, ...]) -> Matrix:
    return tuple(
        tuple(x if i == j else 0.0 for j in range(len(values)))
        for i, x in enumerate(values)
    )


@dataclass(frozen=True, slots=True)
class OrientedEdge:
    edge_id: str
    tail_node_id: NodeId
    head_node_id: NodeId

    def __post_init__(self) -> None:
        _text(self.edge_id)
        object.__setattr__(self, "tail_node_id", _node_id(self.tail_node_id))
        object.__setattr__(self, "head_node_id", _node_id(self.head_node_id))

    def to_payload(self) -> dict[str, JSONValue]:
        return {
            "edge_id": self.edge_id,
            "tail_node_id": self.tail_node_id,
            "head_node_id": self.head_node_id,
        }


@dataclass(frozen=True, slots=True)
class GRCV4Graph:
    live_node_ids: tuple[NodeId, ...]
    oriented_edges: tuple[OrientedEdge, ...]
    _node_index: Mapping[NodeId, int] = field(init=False, repr=False, compare=False)
    _edge_index: Mapping[str, int] = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        nodes = tuple(_node_id(x) for x in _ordered(self.live_node_ids))
        edges = tuple(_ordered(self.oriented_edges))
        if any(type(edge) is not OrientedEdge for edge in edges):
            raise TypeError("expected typed oriented edges")
        object.__setattr__(self, "live_node_ids", nodes)
        object.__setattr__(self, "oriented_edges", edges)
        validate_payload("serialized_graph_payload", self.to_payload())
        node_index = {x: i for i, x in enumerate(nodes)}
        edge_index = {e.edge_id: i for i, e in enumerate(self.oriented_edges)}
        if len(node_index) != len(nodes) or len(edge_index) != len(edges):
            raise ValueError("duplicate live node or edge ID")
        if any(
            e.tail_node_id not in node_index or e.head_node_id not in node_index
            for e in self.oriented_edges
        ):
            raise ValueError("edge endpoint is not a live node")
        object.__setattr__(self, "_node_index", MappingProxyType(node_index))
        object.__setattr__(self, "_edge_index", MappingProxyType(edge_index))

    @classmethod
    def from_payload(cls, value: object) -> Self:
        data = validate_payload("serialized_graph_payload", value)
        raw_nodes = data["live_node_ids"]
        raw_edges = data["oriented_edges"]
        assert isinstance(raw_nodes, list) and isinstance(raw_edges, list)
        edges = []
        for row in raw_edges:
            assert isinstance(row, dict) and isinstance(row["edge_id"], str)
            edges.append(
                OrientedEdge(
                    row["edge_id"],
                    _node_id(row["tail_node_id"]),
                    _node_id(row["head_node_id"]),
                )
            )
        return cls(tuple(_node_id(x) for x in raw_nodes), tuple(edges))

    @classmethod
    def from_json(
        cls, data: str | bytes, *, encoding: Literal["configuration", "canonical"]
    ) -> Self:
        if type(encoding) is not str or encoding not in ("configuration", "canonical"):
            raise TypeError("encoding must select configuration or canonical")
        value = (
            decode_json(data)
            if encoding == "configuration"
            else decode_canonical_json(data)
        )
        return cls.from_payload(value)

    def to_payload(self) -> dict[str, JSONValue]:
        return {
            "schema_version": "grcv4-serialized-graph-v1",
            "live_node_ids": list(self.live_node_ids),
            "oriented_edges": [e.to_payload() for e in self.oriented_edges],
        }

    @property
    def graph_digest(self) -> str:
        return _identity("grc-graph-sha256", self.to_payload())

    @property
    def orientation_identity(self) -> str:
        return _identity(
            "grcv4-orientation-sha256",
            {
                "descriptor_version": "grcv4-ordered-outward-incidence-v1",
                "graph": self.to_payload(),
                "positive_flux": "tail_to_head",
                "incidence_tail": 1,
                "incidence_head": -1,
            },
        )

    @property
    def live_edge_ids(self) -> tuple[str, ...]:
        return tuple(edge.edge_id for edge in self.oriented_edges)

    def node_index(self, node_id: NodeId) -> int:
        return self._node_index[_node_id(node_id)]

    def edge_index(self, edge_id: str) -> int:
        _text(edge_id)
        return self._edge_index[edge_id]

    def star(self, node_id: NodeId) -> tuple[int, ...]:
        self.node_index(node_id)
        return tuple(
            i
            for i, e in enumerate(self.oriented_edges)
            if e.tail_node_id == node_id or e.head_node_id == node_id
        )

    @property
    def incidence(self) -> Matrix:
        return tuple(
            tuple(
                float(int(e.tail_node_id == node) - int(e.head_node_id == node))
                for e in self.oriented_edges
            )
            for node in self.live_node_ids
        )


@dataclass(frozen=True, slots=True)
class _Coordinates:
    graph: GRCV4Graph
    values: tuple[float, ...]
    VERTEX_SPACE: ClassVar[bool] = False

    def __post_init__(self) -> None:
        if type(self.graph) is not GRCV4Graph:
            raise TypeError("coordinates require a GRCV4Graph")
        values = _vector(self.values)
        size = len(
            self.graph.live_node_ids if self.VERTEX_SPACE else self.graph.oriented_edges
        )
        if len(values) != size:
            raise ValueError("coordinate size does not match its graph space")
        object.__setattr__(self, "values", values)


@dataclass(frozen=True, slots=True)
class VertexScalar(_Coordinates):
    VERTEX_SPACE: ClassVar[bool] = True


@dataclass(frozen=True, slots=True)
class OneForm(_Coordinates):
    pass


@dataclass(frozen=True, slots=True)
class PhysicalFlux(_Coordinates):
    pass


def _require_coordinates(
    value: _Coordinates, kind: type[_Coordinates], graph: GRCV4Graph
) -> None:
    if type(value) is not kind:
        raise TypeError(f"expected {kind.__name__}")
    if value.graph != graph:
        raise ValueError("foreign graph or coordinate orientation")


@dataclass(frozen=True, slots=True)
class GRCV4Differential:
    graph: GRCV4Graph
    common: GRCV4CommonParams

    def __post_init__(self) -> None:
        if (
            type(self.graph) is not GRCV4Graph
            or type(self.common) is not GRCV4CommonParams
        ):
            raise TypeError(
                "differential requires graph and resolved common parameters"
            )
        if (
            self.common.differential_backend_id != "oriented_incidence_d0_equals_BT_v1"
            or self.common.boundary_policy_id != "closed_no_flux_v1"
        ):
            raise ValueError("unimplemented differential backend or boundary policy")

    @property
    def identity(self) -> str:
        return _identity(
            "grcv4-differential-sha256",
            {
                "descriptor_version": "grcv4-incidence-differential-v1",
                "graph_digest": self.graph.graph_digest,
                "orientation_identity": self.graph.orientation_identity,
                "common": self.common.to_payload(),
            },
        )

    def d0(self, scalar: VertexScalar) -> OneForm:
        _require_coordinates(scalar, VertexScalar, self.graph)
        return OneForm(
            self.graph,
            tuple(
                _computed(
                    scalar.values[self.graph.node_index(e.tail_node_id)]
                    - scalar.values[self.graph.node_index(e.head_node_id)]
                )
                for e in self.graph.oriented_edges
            ),
        )

    def divergence(self, flux: PhysicalFlux) -> VertexScalar:
        _require_coordinates(flux, PhysicalFlux, self.graph)
        return VertexScalar(self.graph, _matvec(self.graph.incidence, flux.values))


@dataclass(frozen=True, slots=True)
class _Hodge:
    graph: GRCV4Graph
    matrix: Matrix
    VERTEX_SPACE: ClassVar[bool] = False

    def __post_init__(self) -> None:
        if type(self.graph) is not GRCV4Graph:
            raise TypeError("Hodge requires a GRCV4Graph")
        size = len(
            self.graph.live_node_ids if self.VERTEX_SPACE else self.graph.oriented_edges
        )
        object.__setattr__(self, "matrix", _spd(self.matrix, size))

    @property
    def identity(self) -> str:
        return _identity(
            "grcv4-pairing-sha256",
            {
                "descriptor_version": "grcv4-typed-pairing-v1",
                "kind": type(self).__name__,
                "graph_digest": self.graph.graph_digest,
                "orientation_identity": self.graph.orientation_identity,
                "matrix": self.matrix,
            },
        )

    def _pair(
        self, left: _Coordinates, right: _Coordinates, kind: type[_Coordinates]
    ) -> float:
        _require_coordinates(left, kind, self.graph)
        _require_coordinates(right, kind, self.graph)
        return _computed(
            sum(
                a * b
                for a, b in zip(
                    left.values, _matvec(self.matrix, right.values), strict=True
                )
            )
        )


@dataclass(frozen=True, slots=True)
class VertexHodge(_Hodge):
    VERTEX_SPACE: ClassVar[bool] = True

    def pair(self, left: VertexScalar, right: VertexScalar) -> float:
        return self._pair(left, right, VertexScalar)


@dataclass(frozen=True, slots=True)
class OneFormHodge(_Hodge):
    def pair(self, left: OneForm, right: OneForm) -> float:
        return self._pair(left, right, OneForm)


@dataclass(frozen=True, slots=True)
class PhysicalFluxFlatMap:
    """Paired realization G_J=H1_form^-1, applied by solve, never pseudoinverse."""

    one_form_hodge: OneFormHodge

    def __post_init__(self) -> None:
        if type(self.one_form_hodge) is not OneFormHodge:
            raise TypeError("flat map requires a structural one-form Hodge")

    @property
    def identity(self) -> str:
        return _identity(
            "grcv4-flat-sha256",
            {
                "descriptor_version": "grcv4-paired-flat-spd-direct-v1",
                "one_form_hodge_identity": self.one_form_hodge.identity,
            },
        )

    def flat(self, flux: PhysicalFlux) -> OneForm:
        hodge = self.one_form_hodge
        _require_coordinates(flux, PhysicalFlux, hodge.graph)
        if not flux.values:
            return OneForm(hodge.graph, ())
        np = _dependency("numpy")
        try:
            result = np.linalg.solve(
                np.array(hodge.matrix, dtype=np.float64),
                np.array(flux.values, dtype=np.float64),
            )
        except np.linalg.LinAlgError as exc:
            raise ValueError("flat solve failed; no fallback") from exc
        return OneForm(hodge.graph, tuple(_computed(float(x)) for x in result))

    def sharp(self, form: OneForm) -> PhysicalFlux:
        hodge = self.one_form_hodge
        _require_coordinates(form, OneForm, hodge.graph)
        return PhysicalFlux(hodge.graph, _matvec(hodge.matrix, form.values))


@dataclass(frozen=True, slots=True)
class GRCV4Pairings:
    vertex: VertexHodge
    one_form: OneFormHodge

    def __post_init__(self) -> None:
        if (
            type(self.vertex) is not VertexHodge
            or type(self.one_form) is not OneFormHodge
        ):
            raise TypeError("expected separately typed vertex and one-form pairings")
        if self.vertex.graph != self.one_form.graph:
            raise ValueError("pairings require the same graph and orientation")

    @property
    def flat_map(self) -> PhysicalFluxFlatMap:
        return PhysicalFluxFlatMap(self.one_form)


def reference_pairings(
    graph: GRCV4Graph,
    *,
    vertex_measure: tuple[float, ...],
    reference_edge_weights: tuple[float, ...],
) -> GRCV4Pairings:
    """H0=diag(mu), H1_form=diag(W_ref); neither supplies mobility authority."""
    mu = _vector(vertex_measure, positive=True)
    weights = _vector(reference_edge_weights, positive=True)
    return GRCV4Pairings(
        VertexHodge(graph, _diagonal(mu)), OneFormHodge(graph, _diagonal(weights))
    )


def _permutation(value: object, size: int) -> tuple[int, ...]:
    sequence = tuple(_ordered(value))
    if any(type(x) is not int for x in sequence):
        raise ValueError("expected a complete integer coordinate permutation")
    indices = cast(tuple[int, ...], sequence)
    if sorted(indices) != list(range(size)):
        raise ValueError("expected a complete integer coordinate permutation")
    return indices


@dataclass(frozen=True, slots=True)
class GraphCoordinateAction:
    """Fixed-space P and signed U: each target row selects a source index.

    The caller declares both graphs and the bijections. Endpoint checks reject
    topology changes; this operation carries no state/event transport authority.
    """

    source: GRCV4Graph
    target: GRCV4Graph
    vertex_permutation: tuple[int, ...]
    edge_permutation: tuple[int, ...]
    edge_signs: tuple[int, ...]

    def __post_init__(self) -> None:
        if type(self.source) is not GRCV4Graph or type(self.target) is not GRCV4Graph:
            raise TypeError("coordinate actions require source and target graphs")
        p = _permutation(self.vertex_permutation, len(self.source.live_node_ids))
        u = _permutation(self.edge_permutation, len(self.source.oriented_edges))
        signs = tuple(_ordered(self.edge_signs))
        if (
            len(self.target.live_node_ids) != len(p)
            or len(self.target.oriented_edges) != len(u)
            or len(signs) != len(u)
            or any(type(s) is not int or s not in (-1, 1) for s in signs)
        ):
            raise ValueError("fixed-space coordinate action requires signed bijections")
        for i, e in enumerate(self.target.oriented_edges):
            origin = self.source.oriented_edges[u[i]]
            endpoints = (
                self.source.node_index(origin.tail_node_id),
                self.source.node_index(origin.head_node_id),
            )
            if signs[i] == -1:
                endpoints = endpoints[::-1]
            if endpoints != (
                p[self.target.node_index(e.tail_node_id)],
                p[self.target.node_index(e.head_node_id)],
            ):
                raise ValueError("coordinate action changes graph incidence")
        object.__setattr__(self, "vertex_permutation", p)
        object.__setattr__(self, "edge_permutation", u)
        object.__setattr__(self, "edge_signs", signs)

    def vertex_scalar(self, value: VertexScalar) -> VertexScalar:
        _require_coordinates(value, VertexScalar, self.source)
        return VertexScalar(
            self.target, tuple(value.values[i] for i in self.vertex_permutation)
        )

    def one_form(self, value: OneForm) -> OneForm:
        _require_coordinates(value, OneForm, self.source)
        return OneForm(
            self.target,
            tuple(
                _computed(s * value.values[i])
                for i, s in zip(self.edge_permutation, self.edge_signs, strict=True)
            ),
        )

    def physical_flux(self, value: PhysicalFlux) -> PhysicalFlux:
        _require_coordinates(value, PhysicalFlux, self.source)
        return PhysicalFlux(
            self.target,
            tuple(
                _computed(s * value.values[i])
                for i, s in zip(self.edge_permutation, self.edge_signs, strict=True)
            ),
        )

    def vertex_hodge(self, value: VertexHodge) -> VertexHodge:
        if type(value) is not VertexHodge:
            raise TypeError("expected VertexHodge")
        if value.graph != self.source:
            raise ValueError("foreign graph or coordinate orientation")
        return VertexHodge(
            self.target,
            tuple(
                tuple(value.matrix[i][j] for j in self.vertex_permutation)
                for i in self.vertex_permutation
            ),
        )

    def one_form_hodge(self, value: OneFormHodge) -> OneFormHodge:
        if type(value) is not OneFormHodge:
            raise TypeError("expected OneFormHodge")
        if value.graph != self.source:
            raise ValueError("foreign graph or coordinate orientation")
        return OneFormHodge(
            self.target,
            tuple(
                tuple(
                    _computed(
                        self.edge_signs[i] * self.edge_signs[j] * value.matrix[a][b]
                    )
                    for j, b in enumerate(self.edge_permutation)
                )
                for i, a in enumerate(self.edge_permutation)
            ),
        )

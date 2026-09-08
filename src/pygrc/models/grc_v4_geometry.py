"""P9-3.1/P9-3.2 fixed-graph geometry, domain and exact stage/cache inputs.

The serialized order is the coordinate order. Positive tail-to-head flux has
positive outward divergence at its tail: B[tail,e]=+1, B[head,e]=-1. Loops
cancel in B; parallel edges keep distinct IDs. No legacy slots or port chart
enter this backend. Descriptor hashes below are versioned implementation-local
identities, not additions to the frozen wire schema. Pure pairing descriptors
do not establish freshness; the separate stage/cache package binds its inputs.

All retained numerical storage is immutable binary64 tuples. Positivity is
checked exactly on those dyadic values; dense solves use the reviewed NumPy
dependency. Local positivity does not certify a complete profile's conditioning,
selector or solver domain. Stage/cache identity does not authenticate a caller.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from fractions import Fraction
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
    payload_identity,
    validate_payload,
)
from .grc_v4_profile import GRCV4CommonParams, GRCV4Profile, validate_profile_references
from .grc_v4_state import (
    FrozenJSONMap,
    GRCV4AuthoritativeState,
    _index,
    _number,
    _text,
    _vector,
)

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


class GeometryDomainError(ValueError):
    """Finite computed geometry lies outside the positive-definite domain."""


class NonfiniteGeometryError(ValueError):
    """Computed nonfinite value, distinct from a finite geometry-domain failure."""


def _computed(value: float) -> float:
    # Arithmetic may produce -0. Its exact real value has a unique +0 wire
    # representation. Inputs still reject -0; no resource repair occurs here.
    if not math.isfinite(value):
        raise NonfiniteGeometryError("nonfinite numerical result")
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


def _require_positive_definite(
    matrix: tuple[tuple[float | Fraction, ...], ...],
) -> None:
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
        raise GeometryDomainError("Hodge matrix must be positive definite")
    if all(matrix[i][j] == 0 for i in range(size) for j in range(i)):
        return  # Symmetry was checked by _spd; includes the empty space.

    ratios = [[x.as_integer_ratio() for x in row] for row in matrix]
    denominator = max(d for row in ratios for _, d in row)
    if denominator & (denominator - 1) or any(
        denominator % d for row in ratios for _, d in row
    ):
        raise ValueError("positivity validation requires exact dyadic entries")
    work = [[n * (denominator // d) for n, d in row] for row in ratios]
    previous = 1
    for k in range(size):
        pivot = work[k][k]
        if pivot <= 0:
            raise GeometryDomainError("Hodge matrix must be positive definite")
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


# P9-3.2: fixed-graph structural crossing and stage-bound derived operations.
# These are implementation-local reconstruction records, not new wire schemas,
# a candidate current solver, or complete-profile runtime support.


def _symmetric(value: object, graph: GRCV4Graph) -> Matrix:
    if type(graph) is not GRCV4Graph:
        raise TypeError("structural matrix requires a V4 graph")
    matrix = _matrix(value, len(graph.oriented_edges))
    if any(matrix[i][j] != matrix[j][i] for i in range(len(matrix)) for j in range(i)):
        raise ValueError("structural matrix must be exactly symmetric")
    return matrix


STRUCTURAL_COORDINATES_ID = "grcv4-vertex-star-dense-row-major-v1"


def _structural_matrix(value: object, graph: GRCV4Graph) -> Matrix:
    """The shipped star-supported bilinear carrier space, stored densely.

    This is assembly support, not support of the inverse Hodge or response.
    Signed/indefinite increments are permitted; H_profile owns positivity.
    """
    matrix = _symmetric(value, graph)
    endpoints = tuple({e.tail_node_id, e.head_node_id} for e in graph.oriented_edges)
    if any(
        matrix[i][j] != 0 and endpoints[i].isdisjoint(endpoints[j])
        for i in range(len(matrix))
        for j in range(i)
    ):
        raise ValueError(
            "structural matrix has support outside the declared vertex stars"
        )
    return matrix


@dataclass(frozen=True, slots=True)
class K4Tensor:
    """Total K4 represented by its separate baseline and structural increment.

    Keeping the two terms avoids subtracting rounded, nearly equal totals to
    recover a lost increment. Neither term is a mobility or an admitted Hodge.
    """

    graph: GRCV4Graph
    base: Matrix
    increment: Matrix

    def __post_init__(self) -> None:
        object.__setattr__(self, "base", _structural_matrix(self.base, self.graph))
        object.__setattr__(
            self, "increment", _structural_matrix(self.increment, self.graph)
        )

    @property
    def base_preimage(self) -> dict[str, JSONValue]:
        return {
            "schema_version": "grcv4-k4-identity-v1",
            "K4_base": [list(r) for r in self.base],
        }

    @property
    def identity(self) -> str:
        return _identity(
            "grcv4-structural-tensor-sha256",
            {
                "descriptor_version": "grcv4-baseline-plus-increment-v1",
                "graph": self.graph.to_payload(),
                "base": self.base,
                "increment": self.increment,
            },
        )


@dataclass(frozen=True, slots=True)
class StarAssembly:
    """Common overlap-normalized assembly, before a candidate's adapter/gain.

    The binary64 cover coefficient is multiplied by both represented form
    values exactly, then rounded once. This avoids intermediate range loss
    and makes each component invariant under swapping its two inputs. True
    final underflow is retained; an unrepresentable result fails closed.
    Component rounding need not preserve exact semidefiniteness. Admission
    of the total Hodge remains H_profile's separate responsibility.
    """

    form: OneForm
    matrix: Matrix = field(init=False)

    def __post_init__(self) -> None:
        if type(self.form) is not OneForm:
            raise TypeError("star assembly requires a lowered structural one-form")
        graph = self.form.graph
        stars = tuple(set(graph.star(v)) for v in graph.live_node_ids)
        multiplicities = tuple(
            sum(e in star for star in stars) for e in range(len(graph.oriented_edges))
        )
        size = len(multiplicities)
        rows = [[0.0] * size for _ in range(size)]
        # The co-occurrence expression is the stated star sum algebraically.
        # It preserves the exact diagonal partition (m_e/m_e=1), including
        # once-counted loops, without squaring an approximate inverse sqrt.
        for i in range(size):
            for j in range(i, size):
                count = sum(i in star and j in star for star in stars)
                if count:
                    weight = count / math.sqrt(multiplicities[i] * multiplicities[j])
                    try:
                        value = _computed(
                            float(
                                Fraction(weight)
                                * Fraction(self.form.values[i])
                                * Fraction(self.form.values[j])
                            )
                        )
                    except OverflowError as exc:
                        raise NonfiniteGeometryError(
                            "nonfinite numerical result"
                        ) from exc
                    rows[i][j] = rows[j][i] = value
        object.__setattr__(self, "matrix", tuple(tuple(row) for row in rows))

    @property
    def graph(self) -> GRCV4Graph:
        return self.form.graph

    @property
    def identity(self) -> str:
        return _identity(
            "grcv4-star-assembly-sha256",
            {
                "descriptor_version": "grcv4-vertex-star-cooccurrence-product-v2",
                "graph": self.graph.to_payload(),
                "form": self.form.values,
            },
        )


@dataclass(frozen=True, slots=True)
class GRCV4Context:
    """The shipped constant-zero context contract; no opaque evaluator input."""

    contract_id: str
    value: FrozenJSONMap

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", FrozenJSONMap(self.value))
        if (
            type(self.contract_id) is not str
            or self.contract_id != "constant_zero_context_v1"
            or self.value
        ):
            raise ValueError(
                "unimplemented context contract or nonzero context payload"
            )

    def to_payload(self) -> dict[str, JSONValue]:
        return {"contract_id": self.contract_id, "value": {}}


def _geometry_declarations(profile: GRCV4Profile, context: GRCV4Context) -> None:
    if type(profile) is not GRCV4Profile or type(context) is not GRCV4Context:
        raise TypeError("geometry requires a complete profile and typed context")
    params, identity = profile.params_resolved, profile.identity_payload
    required = (
        (identity.geometry_profile_id, "affine_reference_relative_v1"),
        (params.geometry.geometry_domain_id, "positive_hodge_fixed_graph_v1"),
        (params.geometry.flat_sharp_solver_id, "spd_direct_v1"),
        (params.geometry.star_cover_id, "vertex_star_exact_overlap_v1"),
        (params.geometry.overlap_normalization_id, "edge_multiplicity_inverse_sqrt_v1"),
        (
            params.geometry.candidate_adapter_id,
            f"candidate_{identity.candidate.lower()}_exact_star_adapter_v1",
        ),
        (params.common.measure_profile_id, "unit_vertex_measure_v1"),
        (params.common.context_contract_id, context.contract_id),
        (params.common.units_id, "grcv4_nondimensional_reference_v1"),
    )
    if any(actual != expected for actual, expected in required):
        raise ValueError("unimplemented or mismatched geometry declaration")
    # The common/current domain, candidate solver and gauge declarations are
    # identity inputs here. Their candidate-specific execution is not admitted
    # by this local positive geometry check.


@dataclass(frozen=True, slots=True)
class GRCV4ReferenceGeometry:
    graph: GRCV4Graph
    profile: GRCV4Profile
    context: GRCV4Context
    K4_base: Matrix
    edge_weights: FrozenJSONMap
    pairings: GRCV4Pairings = field(init=False)
    differential: GRCV4Differential = field(init=False)

    def __post_init__(self) -> None:
        _geometry_declarations(self.profile, self.context)
        base = _structural_matrix(self.K4_base, self.graph)
        weights = FrozenJSONMap(self.edge_weights)
        object.__setattr__(self, "K4_base", base)
        object.__setattr__(self, "edge_weights", weights)
        validate_profile_references(
            self.profile,
            live_edge_ids=self.graph.live_edge_ids,
            k4_preimage=self.k4_preimage,
            reference_hodge_preimage=self.hodge_preimage,
        )
        object.__setattr__(
            self,
            "differential",
            GRCV4Differential(self.graph, self.profile.params_resolved.common),
        )
        object.__setattr__(
            self,
            "pairings",
            reference_pairings(
                self.graph,
                vertex_measure=(1.0,) * len(self.graph.live_node_ids),
                reference_edge_weights=_vector(
                    tuple(weights[e] for e in self.graph.live_edge_ids), positive=True
                ),
            ),
        )

    @property
    def k4_preimage(self) -> dict[str, JSONValue]:
        return {
            "schema_version": "grcv4-k4-identity-v1",
            "K4_base": [list(r) for r in self.K4_base],
        }

    @property
    def hodge_preimage(self) -> dict[str, JSONValue]:
        return validate_payload(
            "reference_hodge_identity_payload",
            {
                "schema_version": "grcv4-reference-hodge-identity-v1",
                "edge_weights": self.edge_weights,
            },
        )

    @property
    def identity(self) -> str:
        return _identity("grcv4-reference-geometry-sha256", self.to_payload())

    def to_payload(self) -> dict[str, JSONValue]:
        return {
            "descriptor_version": "grcv4-reference-geometry-v1",
            "structural_coordinates_id": STRUCTURAL_COORDINATES_ID,
            "graph": self.graph.to_payload(),
            "profile": self.profile.to_payload(),
            "context": self.context.to_payload(),
            "K4_base": [list(r) for r in self.K4_base],
            "reference_hodge": self.hodge_preimage,
        }

    @classmethod
    def from_payload(cls, value: object) -> GRCV4ReferenceGeometry:
        data = _local_payload(
            value,
            {
                "descriptor_version",
                "graph",
                "profile",
                "context",
                "K4_base",
                "reference_hodge",
                "structural_coordinates_id",
            },
            "descriptor_version",
            "grcv4-reference-geometry-v1",
        )
        if data["structural_coordinates_id"] != STRUCTURAL_COORDINATES_ID:
            raise ValueError("unimplemented structural coordinates")
        profile = GRCV4Profile.from_canonical_bytes(
            canonical_json_bytes(data["profile"])
        )
        context = _context_payload(data["context"])
        hodge = validate_payload(
            "reference_hodge_identity_payload", data["reference_hodge"]
        )
        return cls(
            GRCV4Graph.from_payload(data["graph"]),
            profile,
            context,
            cast(Matrix, data["K4_base"]),
            FrozenJSONMap(cast(Mapping[str, object], hodge["edge_weights"])),
        )

    def geometry(self) -> GRCV4Geometry:
        return GRCV4Geometry(self, self.pairings.one_form)


@dataclass(frozen=True, slots=True)
class GRCV4Geometry:
    """Admitted fixed-graph Hodge package, also usable as a solver trial input.

    Positivity of this package is not a candidate-current/root certificate.
    A trial need not already satisfy the future coupled geometry residual.
    """

    reference: GRCV4ReferenceGeometry
    one_form_hodge: OneFormHodge

    def __post_init__(self) -> None:
        if (
            type(self.reference) is not GRCV4ReferenceGeometry
            or type(self.one_form_hodge) is not OneFormHodge
        ):
            raise TypeError("geometry requires a bound reference and one-form Hodge")
        if self.one_form_hodge.graph != self.reference.graph:
            raise ValueError("geometry uses foreign graph coordinates")

    @property
    def pairings(self) -> GRCV4Pairings:
        return GRCV4Pairings(self.reference.pairings.vertex, self.one_form_hodge)

    @property
    def identity(self) -> str:
        return _identity(
            "grcv4-geometry-sha256",
            {
                "descriptor_version": "grcv4-fixed-reference-positive-geometry-v1",
                "reference_identity": self.reference.identity,
                "one_form_hodge_identity": self.one_form_hodge.identity,
                "positivity_policy_id": POSITIVITY_POLICY_ID,
            },
        )


def H_profile(
    K_4: K4Tensor,
    *,
    reference: GRCV4ReferenceGeometry,
    context: GRCV4Context,
    profile: GRCV4Profile,
) -> GRCV4Geometry:
    """Accepted affine reference-relative map; explicitly consumes Delta K4.

    Exact dyadic positivity checks the mathematical affine expression before
    rounding; the public Hodge constructor separately checks retained binary64
    entries. No square-root estimate decides the congruent I+Theta domain.
    Products/additions retain declared binary64 operation order, canonical zero
    and fail-closed nonfinite behavior. Exact neutral controls reuse reference.
    """
    if type(K_4) is not K4Tensor or type(reference) is not GRCV4ReferenceGeometry:
        raise TypeError("H_profile requires typed K4 and reference geometry")
    _geometry_declarations(profile, context)
    if (
        profile != reference.profile
        or context != reference.context
        or K_4.graph != reference.graph
    ):
        raise ValueError("geometry reference/profile/context/graph mismatch")
    if K_4.base != reference.K4_base:
        raise ValueError("K4 baseline differs from the declared reference preimage")
    gain = profile.params_resolved.geometry.kappa_H
    if gain == 0 or not any(x for row in K_4.increment for x in row):
        return reference.geometry()
    ref = reference.pairings.one_form.matrix
    exact = tuple(
        tuple(
            Fraction(a) + Fraction(gain) * Fraction(b)
            for a, b in zip(left, right, strict=True)
        )
        for left, right in zip(ref, K_4.increment, strict=True)
    )
    _require_positive_definite(exact)
    result = tuple(
        tuple(
            _computed(a + _computed(gain * b)) for a, b in zip(left, right, strict=True)
        )
        for left, right in zip(ref, K_4.increment, strict=True)
    )
    return GRCV4Geometry(reference, OneFormHodge(reference.graph, result))


GeometryStage: TypeAlias = Literal[
    "pre_read",
    "os_predictor",
    "os_corrector",
    "ci_trial",
    "cipc_trial",
    "rg2b_section",
    "pc_old_history",
    "post_continuity",
    "reset_readmission",
    "target_readmission",
]
_STAGE_REALIZATIONS = {
    "os_predictor": "OS",
    "os_corrector": "OS",
    "ci_trial": "CI",
    "cipc_trial": "CI+PC",
    "rg2b_section": "RG2b",
    "pc_old_history": "PC",
}
_COMMON_STAGES = frozenset(
    {"pre_read", "post_continuity", "reset_readmission", "target_readmission"}
)


def _state_payload(value: GRCV4AuthoritativeState) -> dict[str, JSONValue]:
    return {
        "C": list(value.C),
        "W_A": None if value.W_A is None else list(value.W_A),
        "Z_4": None if value.Z_4 is None else list(value.Z_4),
    }


def _geometry_state(
    value: GRCV4AuthoritativeState, reference: GRCV4ReferenceGeometry
) -> GRCV4AuthoritativeState:
    if type(value) is not GRCV4AuthoritativeState:
        raise TypeError("stage requires current and reset authoritative values")
    result = GRCV4AuthoritativeState(value.C, value.W_A, value.Z_4)
    graph, identity = reference.graph, reference.profile.identity_payload
    if len(result.C) != len(graph.live_node_ids) or (result.W_A is not None) != (
        identity.candidate == "A"
    ):
        raise ValueError("stage resource/candidate coordinates mismatch")
    if result.W_A is not None and len(result.W_A) != len(graph.oriented_edges):
        raise ValueError("stage A history/live-edge mismatch")
    if (result.Z_4 is not None) != (identity.realization in ("PC", "CI+PC")):
        raise ValueError("stage realization/history coordinates mismatch")
    if result.Z_4 is not None:
        n = len(graph.oriented_edges)
        if len(result.Z_4) != n * n:
            raise ValueError(
                "stage carrier requires declared dense row-major edge bilinear coordinates"
            )
        increment = _structural_matrix(
            tuple(result.Z_4[i * n : (i + 1) * n] for i in range(n)), graph
        )
        H_profile(
            K4Tensor(graph, reference.K4_base, increment),
            reference=reference,
            context=reference.context,
            profile=reference.profile,
        )
    return result


@dataclass(frozen=True, slots=True)
class GeometryStageInputs:
    """Exact reconstruction inputs captured independently by the stage owner.

    Reset/scientific/lifecycle IDs are rebuilt from their frozen preimages,
    including Q_target and ordered receipt IDs. This does not authenticate a
    caller/receipt ledger or admit a full lifecycle/charge/current-solver state.
    Concrete current/reset values are also retained, never replaced by IDs.
    """

    geometry: GRCV4Geometry
    context: GRCV4Context
    current: GRCV4AuthoritativeState
    reset: GRCV4AuthoritativeState
    operation_id: str
    Q_target: float
    receipt_ids: tuple[str, ...]
    step_index: int
    time: float
    dt: float
    stage: GeometryStage
    evaluation_index: int
    trial_current: PhysicalFlux | None

    def __post_init__(self) -> None:
        if (
            type(self.geometry) is not GRCV4Geometry
            or type(self.context) is not GRCV4Context
        ):
            raise TypeError("stage requires admitted geometry and typed context")
        ref = self.geometry.reference
        if self.context != ref.context:
            raise ValueError("stage context differs from geometry context")
        for name in ("current", "reset"):
            object.__setattr__(self, name, _geometry_state(getattr(self, name), ref))
        _text(self.operation_id)
        object.__setattr__(self, "Q_target", _number(self.Q_target))
        object.__setattr__(self, "receipt_ids", tuple(_ordered(self.receipt_ids)))
        # Validate the exact frozen identity preimages, including receipt grammar.
        # Charge equality and ledger payload authenticity belong to their owners.
        _index(self.step_index)
        _index(self.evaluation_index)
        for name in ("time", "dt"):
            number = _number(getattr(self, name))
            if number < 0:
                raise ValueError("stage clock and duration must be nonnegative")
            object.__setattr__(self, name, number)
        self.source_lifecycle_id
        if (
            type(self.stage) is not str
            or self.stage not in _COMMON_STAGES | _STAGE_REALIZATIONS.keys()
        ):
            raise ValueError("unknown geometry stage")
        if (
            self.stage in _STAGE_REALIZATIONS
            and _STAGE_REALIZATIONS[self.stage]
            != ref.profile.identity_payload.realization
        ):
            raise ValueError("geometry stage belongs to another realization")
        if (
            self.stage not in ("ci_trial", "cipc_trial", "rg2b_section")
            and self.evaluation_index != 0
        ):
            raise ValueError("noniterated stage requires evaluation_index zero")
        if self.trial_current is not None:
            _require_coordinates(self.trial_current, PhysicalFlux, ref.graph)
        if self.stage in ("ci_trial", "cipc_trial") and self.trial_current is None:
            raise ValueError("joint-root evaluation must bind its trial current")
        if self.stage == "os_predictor" and self.geometry != ref.geometry():
            raise ValueError("OS predictor requires the supplied reference geometry")
        if self.stage == "pc_old_history":
            assert self.current.Z_4 is not None
            n = len(ref.graph.oriented_edges)
            increment = tuple(self.current.Z_4[i * n : (i + 1) * n] for i in range(n))
            expected = H_profile(
                K4Tensor(ref.graph, ref.K4_base, increment),
                reference=ref,
                context=self.context,
                profile=ref.profile,
            )
            if self.geometry != expected:
                raise ValueError(
                    "PC read geometry must derive from old committed history"
                )

    @property
    def reset_preimage(self) -> dict[str, JSONValue]:
        ref = self.geometry.reference
        return {
            "schema_version": "grcv4-reset-baseline-v1",
            "active_model_identity": ref.profile.complete_profile_id,
            "graph_digest": ref.graph.graph_digest,
            "orientation_identity": ref.graph.orientation_identity,
            "authoritative": _state_payload(self.reset),
            "Q_target": self.Q_target,
            "context_contract_id": self.context.contract_id,
        }

    @property
    def reset_id(self) -> str:
        return payload_identity("grcv4_reset_payload", self.reset_preimage)

    @property
    def scientific_state_preimage(self) -> dict[str, JSONValue]:
        ref = self.geometry.reference
        return {
            "schema_version": "grcv4-scientific-state-v1",
            "active_model_identity": ref.profile.complete_profile_id,
            "graph_digest": ref.graph.graph_digest,
            "orientation_identity": ref.graph.orientation_identity,
            "step_index": self.step_index,
            "time": self.time,
            "authoritative": _state_payload(self.current),
            "reset_digest": self.reset_id,
            "Q_target": self.Q_target,
            "context_contract_id": self.context.contract_id,
            # The shipped constant-zero contract has no trajectory-varying value.
            "context_value_digest": None,
        }

    @property
    def scientific_state_id(self) -> str:
        return payload_identity(
            "scientific_state_payload", self.scientific_state_preimage
        )

    @property
    def source_lifecycle_id(self) -> str:
        return payload_identity(
            "lifecycle_envelope_payload",
            {
                "schema_version": "grcv4-lifecycle-envelope-v1",
                "scientific_state_digest": self.scientific_state_id,
                "receipt_ids": list(self.receipt_ids),
            },
        )

    def to_payload(self) -> dict[str, JSONValue]:
        return {
            "descriptor_version": "grcv4-geometry-stage-inputs-v1",
            "reference": self.geometry.reference.to_payload(),
            "H1_form": [list(r) for r in self.geometry.one_form_hodge.matrix],
            "context": self.context.to_payload(),
            "current": _state_payload(self.current),
            "reset": _state_payload(self.reset),
            "operation_id": self.operation_id,
            "Q_target": self.Q_target,
            "receipt_ids": list(self.receipt_ids),
            "source_lifecycle_id": self.source_lifecycle_id,
            "scientific_state_id": self.scientific_state_id,
            "reset_id": self.reset_id,
            "step_index": self.step_index,
            "time": self.time,
            "dt": self.dt,
            "stage": self.stage,
            "evaluation_index": self.evaluation_index,
            "trial_current": None
            if self.trial_current is None
            else list(self.trial_current.values),
        }

    @property
    def identity(self) -> str:
        return _identity("grcv4-geometry-stage-sha256", self.to_payload())

    @classmethod
    def from_payload(cls, value: object) -> GeometryStageInputs:
        data = _local_payload(
            value,
            {
                "descriptor_version",
                "reference",
                "H1_form",
                "context",
                "current",
                "reset",
                "operation_id",
                "Q_target",
                "receipt_ids",
                "source_lifecycle_id",
                "scientific_state_id",
                "reset_id",
                "step_index",
                "time",
                "dt",
                "stage",
                "evaluation_index",
                "trial_current",
            },
            "descriptor_version",
            "grcv4-geometry-stage-inputs-v1",
        )
        ref = GRCV4ReferenceGeometry.from_payload(data["reference"])
        geometry = GRCV4Geometry(
            ref, OneFormHodge(ref.graph, cast(Matrix, data["H1_form"]))
        )
        current, reset = (
            _state_from_payload(data[name]) for name in ("current", "reset")
        )
        trial = data["trial_current"]
        result = cls(
            geometry,
            _context_payload(data["context"]),
            current,
            reset,
            cast(str, data["operation_id"]),
            cast(float, data["Q_target"]),
            cast(tuple[str, ...], data["receipt_ids"]),
            cast(int, data["step_index"]),
            cast(float, data["time"]),
            cast(float, data["dt"]),
            cast(GeometryStage, data["stage"]),
            cast(int, data["evaluation_index"]),
            None
            if trial is None
            else PhysicalFlux(ref.graph, cast(tuple[float, ...], trial)),
        )
        if any(
            data[name] != getattr(result, name)
            for name in ("reset_id", "scientific_state_id", "source_lifecycle_id")
        ):
            raise ValueError(
                "stage authority identity differs from reconstructed preimage"
            )
        return result


DerivedGeometryKind: TypeAlias = Literal[
    "d0", "divergence", "flat", "sharp", "star_assembly", "H_profile"
]
GeometryOperand: TypeAlias = VertexScalar | OneForm | PhysicalFlux | K4Tensor
GeometryOutput: TypeAlias = (
    VertexScalar | OneForm | PhysicalFlux | StarAssembly | GRCV4Geometry
)
_DERIVED_OPERANDS: dict[str, type[GeometryOperand]] = {
    "d0": VertexScalar,
    "divergence": PhysicalFlux,
    "flat": PhysicalFlux,
    "sharp": OneForm,
    "star_assembly": OneForm,
    "H_profile": K4Tensor,
}


def _operand_payload(operand: GeometryOperand) -> dict[str, JSONValue]:
    if type(operand) is K4Tensor:
        return {
            "type": "K4Tensor",
            "base": [list(r) for r in operand.base],
            "increment": [list(r) for r in operand.increment],
        }
    if type(operand) not in (VertexScalar, OneForm, PhysicalFlux):
        raise TypeError("unsupported derived geometry operand")
    assert isinstance(operand, _Coordinates)
    return {"type": type(operand).__name__, "values": list(operand.values)}


def _output_payload(output: GeometryOutput) -> dict[str, JSONValue]:
    if type(output) is GRCV4Geometry:
        return {
            "type": "GRCV4Geometry",
            "identity": output.identity,
            "H1_form": [list(r) for r in output.one_form_hodge.matrix],
        }
    if type(output) is StarAssembly:
        return {
            "type": "StarAssembly",
            "identity": output.identity,
            "matrix": [list(r) for r in output.matrix],
        }
    assert isinstance(output, _Coordinates)
    return {"type": type(output).__name__, "values": list(output.values)}


@dataclass(frozen=True, slots=True)
class GeometryStageCache:
    """Closed, actually evaluated primitive cache; no callback or causal state.

    Consumers must supply fresh expected inputs, operation and operand. Import
    rebuilds the operation and compares the result; a recomputed cache hash
    cannot authenticate arbitrary stored output. No candidate selector/current
    solver cache is implemented or admitted by this wrapper.
    """

    inputs: GeometryStageInputs
    kind: DerivedGeometryKind
    operand: GeometryOperand
    value: GeometryOutput = field(init=False)

    def __post_init__(self) -> None:
        if type(self.inputs) is not GeometryStageInputs or type(self.kind) is not str:
            raise TypeError("cache requires typed stage inputs and a literal operation")
        if (
            self.kind not in _DERIVED_OPERANDS
            or type(self.operand) is not _DERIVED_OPERANDS[self.kind]
        ):
            raise TypeError("derived operation/operand type mismatch")
        geometry = self.inputs.geometry
        ref = geometry.reference
        if self.operand.graph != ref.graph:
            raise ValueError("cache operand has foreign graph coordinates")
        value: GeometryOutput
        if self.kind == "H_profile":
            assert isinstance(self.operand, K4Tensor)
            if (
                self.inputs.stage == "pc_old_history"
                and tuple(x for row in self.operand.increment for x in row)
                != self.inputs.current.Z_4
            ):
                raise ValueError("PC geometry operand must be old committed history")
            value = H_profile(
                self.operand,
                reference=ref,
                context=self.inputs.context,
                profile=ref.profile,
            )
        elif self.kind == "star_assembly":
            assert isinstance(self.operand, OneForm)
            value = StarAssembly(self.operand)
        elif self.kind == "d0":
            assert isinstance(self.operand, VertexScalar)
            value = ref.differential.d0(self.operand)
        elif self.kind == "divergence":
            assert isinstance(self.operand, PhysicalFlux)
            value = ref.differential.divergence(self.operand)
        elif self.kind == "flat":
            assert isinstance(self.operand, PhysicalFlux)
            value = geometry.pairings.flat_map.flat(self.operand)
        else:
            assert isinstance(self.operand, OneForm)
            value = geometry.pairings.flat_map.sharp(self.operand)
        object.__setattr__(self, "value", value)

    def consume(
        self,
        *,
        expected_inputs: GeometryStageInputs,
        expected_kind: DerivedGeometryKind,
        expected_operand: GeometryOperand,
    ) -> GeometryOutput:
        if (
            type(expected_inputs) is not GeometryStageInputs
            or type(expected_kind) is not str
        ):
            raise TypeError("cache consumer must supply independent typed expectations")
        if (
            canonical_json_bytes(self.inputs.to_payload())
            != canonical_json_bytes(expected_inputs.to_payload())
            or self.kind != expected_kind
            or type(self.operand) is not type(expected_operand)
            or self.operand != expected_operand
        ):
            raise ValueError(
                "stale_cache: stage, identity, inputs, role or operand differs"
            )
        return self.value

    def to_payload(self) -> dict[str, JSONValue]:
        return {
            "descriptor_version": "grcv4-derived-geometry-cache-v1",
            "inputs": self.inputs.to_payload(),
            "kind": self.kind,
            "operand": _operand_payload(self.operand),
            "output": _output_payload(self.value),
        }

    @property
    def identity(self) -> str:
        return _identity("grcv4-derived-geometry-cache-sha256", self.to_payload())

    def to_canonical_bytes(self) -> bytes:
        return canonical_json_bytes(
            {"payload": self.to_payload(), "cache_id": self.identity}
        )

    @classmethod
    def from_canonical_bytes(
        cls,
        value: str | bytes,
        *,
        expected_inputs: GeometryStageInputs,
        expected_kind: DerivedGeometryKind,
        expected_operand: GeometryOperand,
    ) -> GeometryStageCache:
        if (
            type(expected_inputs) is not GeometryStageInputs
            or type(expected_kind) is not str
        ):
            raise TypeError("cache import requires independent typed expectations")
        envelope = _local_payload(decode_canonical_json(value), {"payload", "cache_id"})
        data = _local_payload(
            envelope["payload"],
            {"descriptor_version", "inputs", "kind", "operand", "output"},
            "descriptor_version",
            "grcv4-derived-geometry-cache-v1",
        )
        # Compare independently supplied expectations before invoking a solver
        # or rebuilding untrusted stale numerical work.
        if (
            canonical_json_bytes(data["inputs"])
            != canonical_json_bytes(expected_inputs.to_payload())
            or data["kind"] != expected_kind
            or canonical_json_bytes(data["operand"])
            != canonical_json_bytes(_operand_payload(expected_operand))
        ):
            raise ValueError(
                "stale_cache: imported provenance does not match the consumer"
            )
        rebuilt = cls(expected_inputs, expected_kind, expected_operand)
        if (
            canonical_json_bytes(data) != canonical_json_bytes(rebuilt.to_payload())
            or envelope["cache_id"] != rebuilt.identity
        ):
            raise ValueError(
                "invalid derived cache: reconstructed output or identity differs"
            )
        return rebuilt


def _local_payload(
    value: object,
    keys: set[str],
    version_key: str | None = None,
    version: str | None = None,
) -> dict[str, JSONValue]:
    # JCS copy enforces finite I-JSON values and detaches mutable input. These
    # closed local reconstruction envelopes never extend the frozen wire schema.
    data = decode_canonical_json(canonical_json_bytes(value))
    if not isinstance(data, dict) or set(data) != keys:
        raise ValueError("unexpected local reconstruction fields")
    if version_key is not None and data[version_key] != version:
        raise ValueError("unsupported local reconstruction version")
    return data


def _context_payload(value: object) -> GRCV4Context:
    data = _local_payload(value, {"contract_id", "value"})
    if not isinstance(data["value"], dict):
        raise TypeError("context value must be a mapping")
    return GRCV4Context(cast(str, data["contract_id"]), FrozenJSONMap(data["value"]))


def _state_from_payload(value: object) -> GRCV4AuthoritativeState:
    data = _local_payload(value, {"C", "W_A", "Z_4"})
    return GRCV4AuthoritativeState(
        cast(tuple[float, ...], data["C"]),
        cast(tuple[float, ...] | None, data["W_A"]),
        cast(tuple[float, ...] | None, data["Z_4"]),
    )

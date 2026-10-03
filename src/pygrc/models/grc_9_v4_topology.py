"""P9-8.1a/b/d: port graph, fixed-row differential and column coarse/Split.

Rows are directional classes; columns are interface families. The chart is
fixed mechanical data, not a dynamical field. Coordinates use one-based JSON
integers: integral-valued floats normalize to int, as with generic graph node
IDs. Booleans, coercible objects and fractional coordinates are not admitted.

Endpoints and edges validate their own values; GRC9V4PortGraph owns collective
membership and occupancy admission. Its digest covers only the canonical port
payload; the generic view derives from that same owner. Structural graph and
wire admission alone admit no model or expansion event.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar, Final, Literal, Self, cast

from .grc_v4_codec import (
    JSONValue,
    canonical_json_bytes,
    decode_canonical_json,
    decode_json,
    payload_identity,
    validate_payload,
)
from .grc_v4_exact import (
    ExactBackend,
    ExactScalar,
    current_exact_backend,
    exact_backend,
    exact_number,
    integer_ratio,
)
from .grc_v4_geometry import (
    GRCV4Graph,
    Matrix,
    NodeId,
    NonfiniteGeometryError,
    OrientedEdge,
    VertexScalar,
    _diagonal,
    _identity,
    _local_payload,
    _node_id,
    _ordered,
    _require_coordinates,
)
from .grc_v4_profile import CandidateCParams, GRCV4Profile, _Record
from .grc_v4_state import (
    GRCV4AuthoritativeState,
    _authority,
    _index,
    _number,
    _text,
    _vector,
)

if TYPE_CHECKING:
    from .grc_9_v3 import GRC9V3

PORT_CHART_ID: Final = "fixed_3x3_row_column"
PORT_COUNT: Final = 9
PORT_ROWS: Final = ((1, 2, 3), (4, 5, 6), (7, 8, 9))
PORT_COLUMNS: Final = ((1, 4, 7), (2, 5, 8), (3, 6, 9))


def _coordinate(value: object, upper: int, label: str) -> int:
    if type(value) not in (int, float):
        raise TypeError(f"{label} must be a JSON integer")
    number = _number(value)
    if not number.is_integer() or not 1 <= number <= upper:
        raise ValueError(f"{label} must be an integer in 1..{upper}")
    return int(number)


def port_to_row_column(port: int) -> tuple[int, int]:
    """Return the fixed one-based (mode row, polarity column) of a port."""
    row, column = divmod(_coordinate(port, PORT_COUNT, "port") - 1, 3)
    return row + 1, column + 1


def row_column_to_port(row: int, column: int) -> int:
    """Return the port r = column + 3*(row-1) for valid chart coordinates."""
    row = _coordinate(row, 3, "row")
    column = _coordinate(column, 3, "column")
    return column + 3 * (row - 1)


@dataclass(frozen=True, slots=True)
class GRC9V4PortEndpoint:
    """A locally valid endpoint; graph admission checks membership and occupancy.

    Node IDs inherit the generic graph contract, including the empty string.
    After normalization, node_id is exactly str or int and port is exactly int.
    Within this endpoint class, field equality therefore preserves typed node
    identity: 1 and 1.0 normalize together, while 1 and "1" remain distinct.
    Reassess equality/hash if the admitted field types change. Canonical graph
    identity must use its typed/JCS payload and digest, never Python hash().
    """

    node_id: NodeId
    port: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "node_id", _node_id(self.node_id))
        object.__setattr__(self, "port", _coordinate(self.port, PORT_COUNT, "port"))

    def to_payload(self) -> dict[str, JSONValue]:
        return {"node_id": self.node_id, "port": self.port}


def _copy_endpoint(value: object) -> GRC9V4PortEndpoint:
    if type(value) is not GRC9V4PortEndpoint:
        raise TypeError("expected a GRC9V4PortEndpoint")
    return GRC9V4PortEndpoint(value.node_id, value.port)


@dataclass(frozen=True, slots=True)
class GRC9V4PortEdge:
    """An identified, oriented edge; membership and occupancy need graph admission.

    Tail/head order is the selected orientation, not a second direction flag.
    Endpoint records are copied and revalidated on entry, including replace().
    """

    edge_id: str
    kind: Literal["boundary", "spine", "tree"]
    tail: GRC9V4PortEndpoint
    head: GRC9V4PortEndpoint

    def __post_init__(self) -> None:
        _text(self.edge_id)
        if type(self.kind) is not str or self.kind not in ("boundary", "spine", "tree"):
            raise ValueError("edge kind must be boundary, spine or tree")
        object.__setattr__(self, "tail", _copy_endpoint(self.tail))
        object.__setattr__(self, "head", _copy_endpoint(self.head))

    def to_payload(self) -> dict[str, JSONValue]:
        return {
            "edge_id": self.edge_id,
            "kind": self.kind,
            "tail": self.tail.to_payload(),
            "head": self.head.to_payload(),
        }


def _copy_edge(value: object) -> GRC9V4PortEdge:
    if type(value) is not GRC9V4PortEdge:
        raise TypeError("expected a GRC9V4PortEdge")
    return GRC9V4PortEdge(value.edge_id, value.kind, value.tail, value.head)


@dataclass(frozen=True, slots=True)
class GRC9V4PortGraph:
    """The admitted port graph, detached from caller-owned sequences and records.

    Node and edge order and tail/head orientation are preserved. Node IDs use
    the generic graph contract, including empty strings. Empty graphs, isolates,
    parallel edges and loops are legal when every incidence has its own port.
    A loop consumes two distinct ports; different edge IDs never waive occupancy.

    The wire envelope derives schema_version and graph_digest from this owner;
    neither a supplied digest nor a generic graph is stored as separate authority.
    Python equality/hash is not wire identity.
    Admission says nothing about event eligibility or constitutive admission.
    """

    live_node_ids: tuple[NodeId, ...]
    edges: tuple[GRC9V4PortEdge, ...]

    def __post_init__(self) -> None:
        nodes = tuple(_node_id(node) for node in _ordered(self.live_node_ids))
        edges = tuple(_copy_edge(edge) for edge in _ordered(self.edges))
        live_nodes = set(nodes)
        if len(live_nodes) != len(nodes):
            raise ValueError("duplicate live node ID")

        edge_ids: set[str] = set()
        occupied: set[GRC9V4PortEndpoint] = set()
        for edge in edges:
            if edge.edge_id in edge_ids:
                raise ValueError("duplicate edge ID")
            edge_ids.add(edge.edge_id)
            for endpoint in (edge.tail, edge.head):
                if endpoint.node_id not in live_nodes:
                    raise ValueError("edge endpoint must name a live node")
                if endpoint in occupied:
                    raise ValueError("port endpoint is already occupied")
                occupied.add(endpoint)

        object.__setattr__(self, "live_node_ids", nodes)
        object.__setattr__(self, "edges", edges)

    def edge_at(self, node_id: NodeId, port: int) -> GRC9V4PortEdge | None:
        """Return the occupying edge, or None for an inactive port on a live node.

        Validate coordinates and live membership even when no edge is found.
        Both ports of a loop resolve to the same stable edge. The lookup is
        derived from the sole graph owner and introduces no authoritative cache.
        """
        endpoint = GRC9V4PortEndpoint(node_id, port)
        if endpoint.node_id not in self.live_node_ids:
            raise KeyError(endpoint.node_id)
        return next(
            (edge for edge in self.edges if endpoint in (edge.tail, edge.head)), None
        )

    @property
    def schema_version(self) -> Literal["grc9v4-port-graph-v1"]:
        return "grc9v4-port-graph-v1"

    def to_payload(self) -> dict[str, JSONValue]:
        """Detached content preimage; graph_digest is deliberately excluded."""
        return {
            "schema_version": self.schema_version,
            "live_node_ids": list(self.live_node_ids),
            "edges": [edge.to_payload() for edge in self.edges],
        }

    @classmethod
    def from_payload(cls, value: object) -> Self:
        """Admit the closed content payload, including collective port constraints."""
        data = validate_payload("port_graph_payload", value)
        nodes, rows = data["live_node_ids"], data["edges"]
        assert isinstance(nodes, list) and isinstance(rows, list)
        edges = []
        for row in rows:
            assert isinstance(row, dict) and isinstance(row["edge_id"], str)
            endpoints = []
            for side in ("tail", "head"):
                endpoint = row[side]
                assert isinstance(endpoint, dict)
                endpoints.append(
                    GRC9V4PortEndpoint(
                        _node_id(endpoint["node_id"]),
                        _coordinate(endpoint["port"], PORT_COUNT, "port"),
                    )
                )
            edges.append(
                GRC9V4PortEdge(
                    row["edge_id"],
                    cast(Literal["boundary", "spine", "tree"], row["kind"]),
                    endpoints[0],
                    endpoints[1],
                )
            )
        return cls(tuple(_node_id(node) for node in nodes), tuple(edges))

    @property
    def graph_digest(self) -> str:
        return payload_identity("port_graph_payload", self.to_payload())

    def to_envelope(self) -> dict[str, JSONValue]:
        """Detached serialized_port_graph with its reconstructed content digest."""
        payload = self.to_payload()
        return {
            **payload,
            "graph_digest": payload_identity("port_graph_payload", payload),
        }

    @classmethod
    def from_envelope(cls, value: object) -> Self:
        data = validate_payload("serialized_port_graph", value)
        graph = cls.from_payload(
            {key: data[key] for key in ("schema_version", "live_node_ids", "edges")}
        )
        expected = data["graph_digest"]
        assert isinstance(expected, str)
        payload_identity("port_graph_payload", graph.to_payload(), expected=expected)
        return graph

    def to_canonical_bytes(self) -> bytes:
        """Encode the envelope, not just its content preimage."""
        return canonical_json_bytes(self.to_envelope())

    @classmethod
    def from_json(
        cls, data: str | bytes, *, encoding: Literal["configuration", "canonical"]
    ) -> Self:
        """Decode an envelope using exactly the selected existing JSON route."""
        if type(encoding) is not str or encoding not in ("configuration", "canonical"):
            raise TypeError("encoding must select configuration or canonical")
        value = (
            decode_json(data)
            if encoding == "configuration"
            else decode_canonical_json(data)
        )
        return cls.from_envelope(value)

    @property
    def orientation_identity(self) -> str:
        # Reuse the generic outward-incidence descriptor, binding the port
        # payload itself rather than hashing a second projected graph.
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

    def generic_projection(self) -> GRC9V4GraphProjection:
        return GRC9V4GraphProjection(self)


# The normative envelope name denotes the same owner, with computed read-only
# schema_version/graph_digest. Supplied envelopes enter through from_envelope();
# there is no second DTO with independently authoritative graph fields.
GRC9V4SerializedPortGraph = GRC9V4PortGraph


@dataclass(frozen=True, slots=True)
class GRC9V4GraphProjection:
    """Read-only generic topology surface backed solely by its admitted owner.

    No standalone graph payload/codec is exposed. Identities delegate to the
    port owner; oriented edges and incidence are disposable derived values.
    This view does not bypass the generic numerical backend's exact-type gates;
    numerical/row-weight integration belongs to the later specialization leaves.
    """

    port_graph: GRC9V4PortGraph

    def __post_init__(self) -> None:
        if type(self.port_graph) is not GRC9V4PortGraph:
            raise TypeError("projection requires a GRC9V4PortGraph")
        if (
            type(self.port_graph.live_node_ids) is not tuple
            or type(self.port_graph.edges) is not tuple
        ):
            raise TypeError("projection requires immutable graph storage")
        # Recheck admission even for supplied typed objects. Retain only the
        # immutable original owner, not the temporary validation copy.
        GRC9V4PortGraph(self.port_graph.live_node_ids, self.port_graph.edges)
        # A view cannot retain a tampered owner that merely normalizes to an
        # admitted copy: its own exposed fields must already be normalized.
        nodes = list(self.port_graph.live_node_ids)
        for edge in self.port_graph.edges:
            for endpoint in (edge.tail, edge.head):
                nodes.append(endpoint.node_id)
                if type(endpoint.port) is not int:
                    raise TypeError("projection requires normalized ports")
        if any(type(node) not in (str, int) for node in nodes):
            raise TypeError("projection requires normalized node IDs")

    @property
    def live_node_ids(self) -> tuple[NodeId, ...]:
        return self.port_graph.live_node_ids

    @property
    def oriented_edges(self) -> tuple[OrientedEdge, ...]:
        return tuple(
            OrientedEdge(edge.edge_id, edge.tail.node_id, edge.head.node_id)
            for edge in self.port_graph.edges
        )

    @property
    def live_edge_ids(self) -> tuple[str, ...]:
        return tuple(edge.edge_id for edge in self.port_graph.edges)

    @property
    def graph_digest(self) -> str:
        return self.port_graph.graph_digest

    @property
    def orientation_identity(self) -> str:
        return self.port_graph.orientation_identity

    def node_index(self, node_id: NodeId) -> int:
        node = _node_id(node_id)
        try:
            return self.live_node_ids.index(node)
        except ValueError:
            raise KeyError(node) from None

    def edge_index(self, edge_id: str) -> int:
        _text(edge_id)
        try:
            return self.live_edge_ids.index(edge_id)
        except ValueError:
            raise KeyError(edge_id) from None

    def star(self, node_id: NodeId) -> tuple[int, ...]:
        node = self.live_node_ids[self.node_index(node_id)]
        return tuple(
            i
            for i, edge in enumerate(self.port_graph.edges)
            if edge.tail.node_id == node or edge.head.node_id == node
        )

    @property
    def incidence(self) -> Matrix:
        edges = self.oriented_edges
        return tuple(
            tuple(
                float(int(edge.tail_node_id == node) - int(edge.head_node_id == node))
                for edge in edges
            )
            for node in self.live_node_ids
        )


def _hessian_sign(value: object) -> int:
    if type(value) is not int or value not in (-1, 1):
        raise ValueError("hessian_sign must be exactly -1 or +1")
    return value


def _rounded(value: ExactScalar) -> float:
    """One binary64 rounding of an exact dyadic/rational row expression."""
    try:
        numerator, denominator = integer_ratio(value)
        result = numerator / denominator
    except OverflowError as exc:
        raise NonfiniteGeometryError("row result is outside binary64") from exc
    # Python integer division supplies the same binary64 rounding for either
    # exact backend; native scalar float conversions need not share that rule.
    return 0.0 if result == 0 else result


@dataclass(frozen=True, slots=True)
class GRC9V4RowSummary:
    """Derived fixed-frame values, never resource state or graph K4."""

    node_id: NodeId
    gradient: tuple[float, ...]
    net_flux: tuple[float, ...]
    hessian_sign: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "node_id", _node_id(self.node_id))
        _hessian_sign(self.hessian_sign)
        for name in ("gradient", "net_flux"):
            values = _vector(getattr(self, name))
            if len(values) != 3:
                raise ValueError("row summary requires exactly three coordinates")
            object.__setattr__(self, name, values)

    @property
    def hessian(self) -> Matrix:
        return _diagonal(self.gradient)

    @property
    def signed_hessian(self) -> Matrix:
        return _diagonal(
            tuple(0.0 if x == 0 else self.hessian_sign * x for x in self.gradient)
        )


# Each entry is an endpoint incidence: weight, neighbor-minus-local resource,
# and outward current. A loop contributes at BOTH of its distinct ports.
_RowTerms = tuple[
    tuple[tuple[tuple[ExactScalar, ExactScalar, ExactScalar], ...], ...], ...
]


@dataclass(frozen=True, slots=True)
class GRC9V4RowDifferential:
    """Pure mechanical operator on the sole port owner, not profile admission.

    Explicit nonnegative weights are allowed here, including exact zero rows.
    Enabled callers use GRC9V4PostbeatRows to select their authoritative weight
    source. No generic incidence/Hodge backend is replaced by this row basis.
    Exact rational accumulation of admitted binary64 inputs avoids spurious
    zero denominators, product underflow, overflow and cancellation. Each
    returned coordinate rounds once to binary64; unrepresentable outputs fail.
    """

    port_graph: GRC9V4PortGraph
    hessian_sign: int = 1

    def __post_init__(self) -> None:
        GRC9V4GraphProjection(self.port_graph)
        _hessian_sign(self.hessian_sign)

    def _terms(self, C: object, weights: object, current: object) -> _RowTerms:
        resource = _vector(C, nonnegative=True)
        w = _vector(weights, nonnegative=True)
        j = _vector(current)
        nodes, edges = self.port_graph.live_node_ids, self.port_graph.edges
        if len(resource) != len(nodes) or len(w) != len(edges) or len(j) != len(edges):
            raise ValueError("row coordinates do not match the port graph")
        indices = {node: index for index, node in enumerate(nodes)}
        values = tuple(exact_number(x) for x in resource)
        terms: list[list[list[tuple[ExactScalar, ExactScalar, ExactScalar]]]] = [
            [[], [], []] for _ in nodes
        ]
        for edge, weight, flux in zip(edges, w, j, strict=True):
            for here, there, sign in (
                (edge.tail, edge.head, 1),
                (edge.head, edge.tail, -1),
            ):
                i, k = indices[here.node_id], indices[there.node_id]
                row, _ = port_to_row_column(here.port)
                terms[i][row - 1].append(
                    (
                        exact_number(weight),
                        values[k] - values[i],
                        sign * exact_number(flux),
                    )
                )
        return tuple(tuple(tuple(row) for row in node) for node in terms)

    def evaluate(
        self, C: object, weights: object, current: object
    ) -> tuple[GRC9V4RowSummary, ...]:
        """Fresh summaries in live-node order; current is tail-to-head positive."""
        result = []
        for node, rows in zip(
            self.port_graph.live_node_ids, self._terms(C, weights, current), strict=True
        ):
            gradient, flux = [], []
            for row in rows:
                denominator = sum((w for w, _, _ in row), exact_number())
                numerator = sum((w * delta for w, delta, _ in row), exact_number())
                gradient.append(
                    _rounded(numerator / denominator) if denominator else 0.0
                )
                flux.append(_rounded(sum((j for _, _, j in row), exact_number())))
            result.append(
                GRC9V4RowSummary(node, tuple(gradient), tuple(flux), self.hessian_sign)
            )
        return tuple(result)

    def legacy_node_tensors(
        self,
        C: object,
        weights: object,
        current: object,
        *,
        lambda_c: float,
        xi_c: float,
        zeta_c: float,
    ) -> tuple[Matrix, ...]:
        """Historical diagonal node diagnostic; NEVER the graph tensor K4.

        xi multiplies a row-local squared mismatch. zeta multiplies the square
        of TOTAL outward flux, identically on all three diagonals.
        """
        coefficients = _vector((lambda_c, xi_c, zeta_c), nonnegative=True)
        lam, xi, zeta = (exact_number(x) for x in coefficients)
        resource = _vector(C, nonnegative=True)
        terms = self._terms(resource, weights, current)
        result = []
        for c, rows in zip(resource, terms, strict=True):
            total = sum((j for row in rows for _, _, j in row), exact_number())
            isotropic = lam * exact_number(c) + zeta * total**2
            result.append(
                _diagonal(
                    tuple(
                        _rounded(
                            isotropic
                            + xi
                            * sum((w * delta**2 for w, delta, _ in row), exact_number())
                        )
                        for row in rows
                    )
                )
            )
        return tuple(result)


@dataclass(frozen=True, slots=True, eq=False)
class GRC9RowWeightPolicy(_Record):
    """The existing closed identity-bearing row-weight policy."""

    SCHEMA: ClassVar[str] = "row_weight_policy"
    schema_version: Literal["grc9v4-row-weight-policy-v1"] = (
        "grc9v4-row-weight-policy-v1"
    )
    candidate_a_source: Literal["committed_postbeat_W_A"] = "committed_postbeat_W_A"
    candidate_c_source: Literal["stable_edge_W_C_tr"] = "stable_edge_W_C_tr"
    disabled_source: Literal["exact_delegate_native_base_conductance"] = (
        "exact_delegate_native_base_conductance"
    )
    evaluation_stage: Literal["fresh_postbeat_candidate_detection"] = (
        "fresh_postbeat_candidate_detection"
    )


@dataclass(frozen=True, slots=True)
class GRC9V4PostbeatRows:
    """Detached inputs for fresh enabled row evaluation at an explicit stage.

    The native lifecycle owner must supply its committed state/current after
    the ordinary beat. This record checks content, coverage and stage; like
    GeometryStageInputs, it cannot authenticate chronology or a caller's claim
    of commit. No generic graph is constructed and no constitutive/solver
    admission or native lifecycle execution is implied. Identity binds every
    computation input; old records are snapshots, never refreshed live caches.
    """

    port_graph: GRC9V4PortGraph
    profile: GRCV4Profile
    committed: GRCV4AuthoritativeState
    physical_current: tuple[float, ...]
    step_index: int
    hessian_sign: int
    stage: Literal["fresh_postbeat_candidate_detection"] = (
        "fresh_postbeat_candidate_detection"
    )
    policy: GRC9RowWeightPolicy = field(default_factory=GRC9RowWeightPolicy)

    def __post_init__(self) -> None:
        graph = GRC9V4GraphProjection(self.port_graph)
        _hessian_sign(self.hessian_sign)
        _index(self.step_index)
        if type(self.policy) is not GRC9RowWeightPolicy:
            raise TypeError("expected GRC9RowWeightPolicy")
        object.__setattr__(
            self, "policy", GRC9RowWeightPolicy.from_payload(self.policy.to_payload())
        )
        if type(self.stage) is not str or self.stage != self.policy.evaluation_stage:
            raise ValueError("row bridge requires fresh postbeat candidate detection")
        if type(self.profile) is not GRCV4Profile:
            raise TypeError("row bridge requires a complete V4 profile")
        profile = GRCV4Profile.from_canonical_bytes(self.profile.to_canonical_bytes())
        object.__setattr__(self, "profile", profile)
        state = _authority(self.committed)
        size = len(graph.live_edge_ids)
        if len(state.C) != len(graph.live_node_ids):
            raise ValueError("committed resource does not match live nodes")
        candidate_a = profile.identity_payload.candidate == "A"
        carrier = profile.identity_payload.realization in ("PC", "CI+PC")
        if (state.W_A is not None) != candidate_a or (
            state.W_A is not None and len(state.W_A) != size
        ):
            raise ValueError("committed W_A disagrees with candidate or live edges")
        if (state.Z_4 is not None) != carrier or (
            state.Z_4 is not None and len(state.Z_4) != size * size
        ):
            raise ValueError("committed Z_4 disagrees with realization or edge space")
        if not candidate_a:
            candidate = profile.params_resolved.candidate
            assert isinstance(candidate, CandidateCParams)
            if set(candidate.W_C_tr) != set(graph.live_edge_ids):
                raise ValueError("W_C_tr must cover exactly the live stable edge IDs")
        object.__setattr__(self, "committed", state)
        current = _vector(self.physical_current)
        if len(current) != size:
            raise ValueError("physical current does not match live edges")
        object.__setattr__(self, "physical_current", current)

    @property
    def weight_source(self) -> str:
        return (
            self.policy.candidate_a_source
            if self.committed.W_A is not None
            else self.policy.candidate_c_source
        )

    @property
    def weights(self) -> tuple[float, ...]:
        if self.committed.W_A is not None:
            return self.committed.W_A
        candidate = self.profile.params_resolved.candidate
        assert isinstance(candidate, CandidateCParams)
        return _vector(
            tuple(candidate.W_C_tr[edge.edge_id] for edge in self.port_graph.edges),
            positive=True,
        )

    @property
    def identity(self) -> str:
        """Implementation-local input identity, not a new wire/scientific owner."""
        return _identity(
            "grc9v4-row-inputs-sha256",
            {
                "descriptor_version": "grc9v4-postbeat-row-inputs-v1",
                "graph_digest": self.port_graph.graph_digest,
                "orientation_identity": self.port_graph.orientation_identity,
                "complete_profile_id": self.profile.complete_profile_id,
                "policy": self.policy.to_payload(),
                "stage": self.stage,
                "step_index": self.step_index,
                "hessian_sign": self.hessian_sign,
                "committed": {
                    "C": self.committed.C,
                    "W_A": self.committed.W_A,
                    "Z_4": self.committed.Z_4,
                },
                "physical_current": self.physical_current,
            },
        )

    def evaluate(self) -> tuple[GRC9V4RowSummary, ...]:
        return GRC9V4RowDifferential(self.port_graph, self.hessian_sign).evaluate(
            self.committed.C, self.weights, self.physical_current
        )


def delegate_native_row_weights(delegate: GRC9V3) -> tuple[tuple[int, float], ...]:
    """Inspect exact GRC9V3 native base conductance, preserving native edge IDs.

    This disabled-side bridge performs no rebuild, step, port conversion or
    enabled evaluation. Missing native transport state fails the request; it
    never falls back to port-edge conductance, V4 mobility or stale row caches.
    The later compatibility owner controls the branch and native sampling stage.
    """
    from .grc_9_v3 import GRC9V3

    if type(delegate) is not GRC9V3:
        raise TypeError("disabled weights require the exact GRC9V3 delegate")
    state = delegate.get_state()
    edges = tuple(state.topology.iter_live_edge_ids())
    if set(state.base_conductance) != set(edges):
        raise ValueError("delegate native base conductance is incomplete")
    values = _vector(
        tuple(state.base_conductance[edge] for edge in edges), nonnegative=True
    )
    return tuple(zip(edges, values, strict=True))


@dataclass(frozen=True, slots=True, eq=False)
class GRC9CoarsePolicy(_Record):
    """Both normative field encodings are mandatory, not global alternatives."""

    SCHEMA: ClassVar[str] = "coarse_policy"
    schema_version: Literal["grc9v4-coarse-policy-v1"] = "grc9v4-coarse-policy-v1"
    nonnegative_field_mode: Literal["simplex_profile"] = "simplex_profile"
    signed_flux_mode: Literal["positive_negative_split"] = "positive_negative_split"


CoarseFieldFamily = Literal["nonnegative", "signed_flux"]


class CoarseFieldTypeError(TypeError):
    """A request or encoding selects the wrong port-field family."""


class CoarseDomainError(ValueError):
    """A coarse value is outside the exact binary64 reconstruction domain."""


def _field_family(value: object) -> CoarseFieldFamily:
    if type(value) is not str or value not in ("nonnegative", "signed_flux"):
        raise CoarseFieldTypeError("field family must be nonnegative or signed_flux")
    return cast(CoarseFieldFamily, value)


def _requested_family(actual: CoarseFieldFamily, requested: object) -> None:
    if _field_family(requested) != actual:
        raise CoarseFieldTypeError("request and stored field family differ")


def _coarse_number(value: object) -> ExactScalar:
    # Explicit exact derived coordinates, not a relaxation of JSON/state input.
    if type(value) is type(exact_number()):
        return value
    if type(value) not in (int, float):
        raise TypeError(
            "coarse coordinate requires the selected exact backend or JSON number"
        )
    return exact_number(_number(value))


def _coarse_float(value: ExactScalar) -> float:
    try:
        numerator, denominator = integer_ratio(value)
        result = numerator / denominator
    except OverflowError as exc:
        raise CoarseDomainError("Split coordinate is outside binary64") from exc
    if exact_number(result) != value:
        raise CoarseDomainError("Split coordinate is not exactly representable")
    return 0.0 if result == 0 else result


@dataclass(frozen=True, slots=True)
class GRC9V4ColumnProfile:
    """Exact derived total/profile for one column, with rows in order 1..3.

    Totals may exceed binary64 and ratios need not be dyadic. Every product
    must reconstruct an admitted finite binary64 fine coordinate exactly.
    Zero total has the unique uniform profile; no tolerance or repair is used.
    This in-memory value is not a new authoritative state or wire schema.
    Retained native scalars keep their construction backend after its scope
    exits. Mixed-backend inputs reject; backend choice is not content identity.
    """

    total: ExactScalar
    profile: tuple[ExactScalar, ...]
    backend: ExactBackend = field(
        default_factory=current_exact_backend, compare=False, repr=False
    )

    def __post_init__(self) -> None:
        with exact_backend(self.backend):
            self._validate()

    def _validate(self) -> None:
        total = _coarse_number(self.total)
        profile = tuple(_coarse_number(x) for x in _ordered(self.profile))
        if total < 0 or len(profile) != 3 or any(x < 0 for x in profile):
            raise CoarseDomainError("expected a nonnegative total and simplex3")
        if sum(profile) != 1:
            raise CoarseDomainError("column profile must sum exactly to one")
        if total == 0 and profile != (exact_number(1, 3),) * 3:
            raise CoarseDomainError("zero total requires the canonical uniform profile")
        for x in profile:
            _coarse_float(total * x)
        object.__setattr__(self, "total", total)
        object.__setattr__(self, "profile", profile)

    def split(self) -> tuple[float, ...]:
        with exact_backend(self.backend):
            return tuple(_coarse_float(self.total * x) for x in self.profile)


def _copy_column(value: object) -> GRC9V4ColumnProfile:
    if type(value) is not GRC9V4ColumnProfile:
        raise CoarseFieldTypeError("expected a nonnegative column profile")
    return GRC9V4ColumnProfile(value.total, value.profile, backend=value.backend)


@dataclass(frozen=True, slots=True)
class GRC9V4SignedColumn:
    """Canonical J+/J- channels; overlapping support would break G o Split."""

    positive: GRC9V4ColumnProfile
    negative: GRC9V4ColumnProfile

    def __post_init__(self) -> None:
        positive, negative = _copy_column(self.positive), _copy_column(self.negative)
        if positive.backend is not negative.backend:
            raise CoarseFieldTypeError(
                "signed channels belong to different exact backends"
            )
        if any(
            p > 0 and n > 0
            for p, n in zip(positive.split(), negative.split(), strict=True)
        ):
            raise CoarseDomainError(
                "positive and negative channels must have disjoint support"
            )
        object.__setattr__(self, "positive", positive)
        object.__setattr__(self, "negative", negative)

    @property
    def backend(self) -> ExactBackend:
        return self.positive.backend

    def split(self) -> tuple[float, ...]:
        return tuple(
            p if p > 0 else -n if n > 0 else 0.0
            for p, n in zip(self.positive.split(), self.negative.split(), strict=True)
        )


def _nonnegative_column(values: tuple[float, ...]) -> GRC9V4ColumnProfile:
    exact = tuple(exact_number(x) for x in values)
    total = sum(exact, exact_number())
    profile = tuple(x / total for x in exact) if total else (exact_number(1, 3),) * 3
    return GRC9V4ColumnProfile(total, profile)


@dataclass(frozen=True, slots=True)
class GRC9V4PortField:
    """Detached fine field: live-node order, then literal ports 1..9.

    This is a declared field snapshot, not authenticated live state. All chart
    positions exist, including inactive ports. Edge gathering supplies zero at
    inactive ports; callers can also declare other port-attached scalar fields.
    """

    port_graph: GRC9V4PortGraph
    field_family: CoarseFieldFamily
    values: tuple[tuple[float, ...], ...]

    def __post_init__(self) -> None:
        GRC9V4GraphProjection(self.port_graph)
        family = _field_family(self.field_family)
        values = tuple(
            _vector(row, nonnegative=family == "nonnegative")
            for row in _ordered(self.values)
        )
        if len(values) != len(self.port_graph.live_node_ids) or any(
            len(row) != 9 for row in values
        ):
            raise CoarseDomainError("field needs one nine-port row per live node")
        object.__setattr__(self, "values", values)

    @classmethod
    def from_edge_values(
        cls,
        port_graph: GRC9V4PortGraph,
        field_family: CoarseFieldFamily,
        edge_values: tuple[float, ...],
    ) -> Self:
        """Gather in stable edge order; signed values are outward at the tail."""
        GRC9V4GraphProjection(port_graph)
        family = _field_family(field_family)
        values = _vector(edge_values, nonnegative=family == "nonnegative")
        if len(values) != len(port_graph.edges):
            raise CoarseDomainError("edge field shape mismatch")
        rows = {node: [0.0] * 9 for node in port_graph.live_node_ids}
        for edge, value in zip(port_graph.edges, values, strict=True):
            rows[edge.tail.node_id][edge.tail.port - 1] = value
            rows[edge.head.node_id][edge.head.port - 1] = (
                -value if family == "signed_flux" and value != 0 else value
            )
        return cls(port_graph, family, tuple(tuple(row) for row in rows.values()))

    @property
    def identity(self) -> str:
        return _identity(
            "grc9v4-port-field-sha256",
            {
                "descriptor_version": "grc9v4-port-field-v1",
                "graph_digest": self.port_graph.graph_digest,
                "field_family": self.field_family,
                "values": self.values,
            },
        )


@dataclass(frozen=True, slots=True)
class GRC9V4CoarseField:
    """Exact column encoding in live-node order, then columns 1..3.

    No source fine values or cache are stored. Split revalidates this encoding
    and the caller's graph binding. Identity is an implementation-local content
    descriptor; rational numerator/denominator strings are not JSON numbers.
    Full model serialization and cache lifecycle remain with later owners.
    The retained backend is implementation ownership only and is not hashed.
    """

    port_graph: GRC9V4PortGraph
    field_family: CoarseFieldFamily
    columns: tuple[tuple[GRC9V4ColumnProfile | GRC9V4SignedColumn, ...], ...]
    policy: GRC9CoarsePolicy = field(default_factory=GRC9CoarsePolicy)
    backend: ExactBackend = field(
        default_factory=current_exact_backend, compare=False, repr=False
    )

    def __post_init__(self) -> None:
        with exact_backend(self.backend):
            self._validate()

    def _validate(self) -> None:
        GRC9V4GraphProjection(self.port_graph)
        family = _field_family(self.field_family)
        if type(self.policy) is not GRC9CoarsePolicy:
            raise CoarseFieldTypeError("expected GRC9CoarsePolicy")
        object.__setattr__(
            self, "policy", GRC9CoarsePolicy.from_payload(self.policy.to_payload())
        )
        rows: list[tuple[GRC9V4ColumnProfile | GRC9V4SignedColumn, ...]] = []
        for row in _ordered(self.columns):
            columns: list[GRC9V4ColumnProfile | GRC9V4SignedColumn] = []
            for column in _ordered(row):
                if family == "nonnegative":
                    columns.append(_copy_column(column))
                else:
                    if type(column) is not GRC9V4SignedColumn:
                        raise CoarseFieldTypeError(
                            "signed flux requires positive/negative channels"
                        )
                    columns.append(GRC9V4SignedColumn(column.positive, column.negative))
                if columns[-1].backend is not self.backend:
                    raise CoarseFieldTypeError(
                        "column belongs to another exact backend"
                    )
            if len(columns) != 3:
                raise CoarseDomainError("expected three columns per node")
            rows.append(tuple(columns))
        if len(rows) != len(self.port_graph.live_node_ids):
            raise CoarseDomainError("coarse node shape mismatch")
        object.__setattr__(self, "columns", tuple(rows))

    @property
    def identity(self) -> str:
        def column_payload(column: GRC9V4ColumnProfile) -> list[list[str]]:
            return [
                [str(n) for n in integer_ratio(x)]
                for x in (column.total, *column.profile)
            ]

        return _identity(
            "grc9v4-coarse-field-sha256",
            {
                "descriptor_version": "grc9v4-exact-column-field-v1",
                "graph_digest": self.port_graph.graph_digest,
                "field_family": self.field_family,
                "policy": self.policy.to_payload(),
                "columns": [
                    [
                        column_payload(column)
                        if isinstance(column, GRC9V4ColumnProfile)
                        else [
                            column_payload(column.positive),
                            column_payload(column.negative),
                        ]
                        for column in row
                    ]
                    for row in self.columns
                ],
            },
        )


def coarse_grain_columns(
    port_field: GRC9V4PortField,
    *,
    field_family: CoarseFieldFamily,
    policy: GRC9CoarsePolicy | None = None,
) -> GRC9V4CoarseField:
    """The chart-specific G operator; the request must name the field family."""
    if type(port_field) is not GRC9V4PortField:
        raise CoarseFieldTypeError("expected a GRC9V4PortField")
    source = GRC9V4PortField(
        port_field.port_graph, port_field.field_family, port_field.values
    )
    _requested_family(source.field_family, field_family)
    rows: list[tuple[GRC9V4ColumnProfile | GRC9V4SignedColumn, ...]] = []
    for values in source.values:
        columns: list[GRC9V4ColumnProfile | GRC9V4SignedColumn] = []
        for ports in PORT_COLUMNS:
            coordinates = tuple(values[p - 1] for p in ports)
            columns.append(
                _nonnegative_column(coordinates)
                if field_family == "nonnegative"
                else GRC9V4SignedColumn(
                    _nonnegative_column(tuple(max(x, 0.0) for x in coordinates)),
                    _nonnegative_column(
                        tuple(-x if x < 0 else 0.0 for x in coordinates)
                    ),
                )
            )
        rows.append(tuple(columns))
    return GRC9V4CoarseField(
        source.port_graph,
        source.field_family,
        tuple(rows),
        GRC9CoarsePolicy() if policy is None else policy,
    )


def split_columns(
    coarse: GRC9V4CoarseField,
    *,
    field_family: CoarseFieldFamily,
    port_graph: GRC9V4PortGraph,
) -> GRC9V4PortField:
    """Exact inverse on the admitted encoding; no graph fission or mutation."""
    if type(coarse) is not GRC9V4CoarseField:
        raise CoarseFieldTypeError("expected a GRC9V4CoarseField")
    source = GRC9V4CoarseField(
        coarse.port_graph,
        coarse.field_family,
        coarse.columns,
        coarse.policy,
        backend=coarse.backend,
    )
    _requested_family(source.field_family, field_family)
    GRC9V4GraphProjection(port_graph)
    if port_graph.graph_digest != source.port_graph.graph_digest:
        raise CoarseDomainError("Split graph binding differs from the coarse snapshot")
    rows = []
    for columns in source.columns:
        values = [0.0] * 9
        for ports, column in zip(PORT_COLUMNS, columns, strict=True):
            for port, value in zip(ports, column.split(), strict=True):
                values[port - 1] = value
        rows.append(tuple(values))
    return GRC9V4PortField(port_graph, source.field_family, tuple(rows))


@dataclass(frozen=True, slots=True)
class GRC9V4CandidateADifferentialReference:
    """Closed fixed-row A recipe; incoming W is a required stage operand.

    This descriptor binds the port owner, never a cached gradient or retained
    weight vector. The WLS initializer remains a separate, unchanged contract.
    """

    port_graph: GRC9V4PortGraph

    def __post_init__(self) -> None:
        if type(self.port_graph) is not GRC9V4PortGraph:
            raise TypeError("fixed-row A requires the exact port graph owner")
        object.__setattr__(
            self,
            "port_graph",
            GRC9V4PortGraph.from_payload(self.port_graph.to_payload()),
        )

    @property
    def graph(self) -> GRCV4Graph:
        return GRCV4Graph.from_port_graph(self.port_graph)

    def to_payload(self) -> dict[str, JSONValue]:
        return {
            "descriptor_version": "grc9v4-candidate-a-fixed-row-v1",
            "port_graph": self.port_graph.to_payload(),
            "frame_mode": "fixed_port_chart",
            "hessian_backend": "row_basis_diagonal",
            "curvature_backend": "none",
            "read_weights": "incoming_W_A",
            "writer_weights": "incoming_W_A",
            "writer_resources": "admitted_final_C",
            "writer_current": "selected_physical_current",
            "empty_row": "exact_zero",
            "rounding": "exact_row_ratio_then_binary64_v1",
        }

    @property
    def identity(self) -> str:
        return _identity("grcv4-a-descriptor-sha256", self.to_payload())

    @classmethod
    def from_payload(cls, value: object) -> Self:
        data = _local_payload(
            value,
            {
                "descriptor_version",
                "port_graph",
                "frame_mode",
                "hessian_backend",
                "curvature_backend",
                "read_weights",
                "writer_weights",
                "writer_resources",
                "writer_current",
                "empty_row",
                "rounding",
            },
        )
        result = cls(GRC9V4PortGraph.from_payload(data["port_graph"]))
        if canonical_json_bytes(data) != canonical_json_bytes(result.to_payload()):
            raise ValueError("unsupported fixed-row A recipe")
        return result

    def rebuild(self, C: VertexScalar, incoming_W: tuple[float, ...]) -> Matrix:
        return tuple(
            tuple(_rounded(x) for x in row) for row in self.rebuild_exact(C, incoming_W)
        )

    def rebuild_exact(
        self, C: VertexScalar, incoming_W: tuple[float, ...]
    ) -> tuple[tuple[ExactScalar, ...], ...]:
        """Unrounded fixed-row operands for analytic residual/domain proofs.

        The same admitted incidence terms supply binary64 point descriptors.
        No stored or rounded summary can become an analytic proof operand.
        """
        _require_coordinates(C, VertexScalar, self.graph)
        weights = _vector(incoming_W, positive=True)
        terms = GRC9V4RowDifferential(self.port_graph)._terms(
            C.values, weights, (0.0,) * len(self.port_graph.edges)
        )
        result = []
        for rows in terms:
            gradient = []
            for row in rows:
                denominator = sum((w for w, _, _ in row), exact_number())
                numerator = sum((w * delta for w, delta, _ in row), exact_number())
                gradient.append(
                    numerator / denominator if denominator else exact_number()
                )
            result.append(tuple(gradient))
        return tuple(result)

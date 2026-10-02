"""P9-8.1a: chart, admitted port graph, envelope and generic read-only view.

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

from dataclasses import dataclass
from typing import Final, Literal, Self, cast

from .grc_v4_codec import (
    JSONValue,
    canonical_json_bytes,
    decode_canonical_json,
    decode_json,
    payload_identity,
    validate_payload,
)
from .grc_v4_geometry import Matrix, NodeId, OrientedEdge, _identity, _node_id, _ordered
from .grc_v4_state import _number, _text

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

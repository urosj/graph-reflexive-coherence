"""P9-8.1a.1–.2: fixed nine-port chart and immutable port-graph admission.

Rows are directional classes; columns are interface families. The chart is
fixed mechanical data, not a dynamical field. Coordinates use one-based JSON
integers: integral-valued floats normalize to int, as with generic graph node
IDs. Booleans, coercible objects and fractional coordinates are not admitted.

Endpoints and edges validate their own values; GRC9V4PortGraph owns collective
membership and occupancy admission. Graph identity/projection and event
eligibility belong to their separate consumers; structural graph admission
alone admits no model or expansion event.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Literal

from .grc_v4_geometry import NodeId, _node_id, _ordered
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

    This is the structural graph owner for the later payload/digest codec and
    read-only generic projection. Python equality/hash is not wire identity.
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

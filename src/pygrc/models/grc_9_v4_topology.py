"""P9-8.1a.1: fixed nine-port chart and immutable endpoint primitives.

Rows are directional classes; columns are interface families. The chart is
fixed mechanical data, not a dynamical field. Coordinates use one-based JSON
integers: integral-valued floats normalize to int, as with generic graph node
IDs. Booleans, coercible objects and fractional coordinates are not admitted.

An endpoint validates only its own values. Graph membership, unique endpoint
occupancy, graph identity/projection and event eligibility belong to their
separate consumers; constructing an endpoint admits no graph or model.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from .grc_v4_geometry import NodeId, _node_id
from .grc_v4_state import _number

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

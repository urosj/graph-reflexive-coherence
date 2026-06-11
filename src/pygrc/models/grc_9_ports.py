"""Pure port/row/column helpers for the GRC9 nine-slot substrate."""

from __future__ import annotations

from collections.abc import Iterable

from pygrc.core import PORT_COLUMN_COUNT, PORT_ROW_COUNT, PORTS_PER_NODE


PortId = int
ModeRow = int
PolarityColumn = int

_MIN_PORT_ID = 1
_MAX_PORT_ID = PORTS_PER_NODE


def port_to_rc(port: PortId) -> tuple[ModeRow, PolarityColumn]:
    """Return the 1-based `(row, column)` pair for one 1-based port id."""

    if port not in range(_MIN_PORT_ID, _MAX_PORT_ID + 1):
        raise ValueError("port must be within the canonical 1..9 range")
    zero_based = port - 1
    row = zero_based // PORT_COLUMN_COUNT + 1
    column = zero_based % PORT_COLUMN_COUNT + 1
    return (row, column)


def rc_to_port(row: ModeRow, column: PolarityColumn) -> PortId:
    """Return the 1-based port id for one 1-based `(row, column)` pair."""

    if row not in range(1, PORT_ROW_COUNT + 1):
        raise ValueError("row must be within the canonical 1..3 range")
    if column not in range(1, PORT_COLUMN_COUNT + 1):
        raise ValueError("column must be within the canonical 1..3 range")
    return column + PORT_COLUMN_COUNT * (row - 1)


def port_id_to_slot(port: PortId) -> int:
    """Convert one public 1-based port id to the backend's 0-based slot id."""

    port_to_rc(port)
    return port - 1


def slot_to_port_id(slot: int) -> PortId:
    """Convert one backend 0-based slot id to the public 1-based port id."""

    if slot not in range(PORTS_PER_NODE):
        raise ValueError("slot must be within the canonical 0..8 range")
    return slot + 1


def occupied_ports_in_row(
    occupied_ports: Iterable[PortId],
    row: ModeRow,
) -> tuple[PortId, ...]:
    """Return occupied ports belonging to one row in deterministic order."""

    if row not in range(1, PORT_ROW_COUNT + 1):
        raise ValueError("row must be within the canonical 1..3 range")
    normalized = sorted({int(port) for port in occupied_ports})
    return tuple(port for port in normalized if port_to_rc(port)[0] == row)


def occupied_ports_in_column(
    occupied_ports: Iterable[PortId],
    column: PolarityColumn,
) -> tuple[PortId, ...]:
    """Return occupied ports belonging to one column in deterministic order."""

    if column not in range(1, PORT_COLUMN_COUNT + 1):
        raise ValueError("column must be within the canonical 1..3 range")
    normalized = sorted({int(port) for port in occupied_ports})
    return tuple(port for port in normalized if port_to_rc(port)[1] == column)


__all__ = [
    "ModeRow",
    "PolarityColumn",
    "PortId",
    "occupied_ports_in_column",
    "occupied_ports_in_row",
    "port_id_to_slot",
    "port_to_rc",
    "rc_to_port",
    "slot_to_port_id",
]

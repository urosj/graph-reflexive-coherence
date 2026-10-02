"""Fixed-chart and local endpoint checks; no graph/event conformance claim."""

from __future__ import annotations

import math
import unittest
from dataclasses import FrozenInstanceError, replace
from decimal import Decimal
from enum import IntEnum
from fractions import Fraction
from typing import Any

import numpy as np

from pygrc.models.grc_9_v4_topology import (
    PORT_CHART_ID,
    PORT_COLUMNS,
    PORT_COUNT,
    PORT_ROWS,
    GRC9V4PortEndpoint,
    port_to_row_column,
    row_column_to_port,
)
from pygrc.models.grc_v4_geometry import OrientedEdge

# Literal specification table, independent of either implementation direction.
CHART = (
    (1, 1, 1),
    (2, 1, 2),
    (3, 1, 3),
    (4, 2, 1),
    (5, 2, 2),
    (6, 2, 3),
    (7, 3, 1),
    (8, 3, 2),
    (9, 3, 3),
)


class IntegerLabel(IntEnum):
    ONE = 1


class Coercible:
    def __int__(self) -> int:
        raise AssertionError("unexpected int coercion")

    def __float__(self) -> float:
        raise AssertionError("unexpected float coercion")


class FixedChartTests(unittest.TestCase):
    def test_all_nine_literal_pairs_and_both_roundtrips(self) -> None:
        self.assertEqual(PORT_CHART_ID, "fixed_3x3_row_column")
        self.assertEqual(PORT_COUNT, 9)
        for port, row, column in CHART:
            with self.subTest(port=port):
                self.assertEqual(port_to_row_column(port), (row, column))
                self.assertEqual(row_column_to_port(row, column), port)
                self.assertEqual(row_column_to_port(*port_to_row_column(port)), port)
                self.assertEqual(
                    port_to_row_column(row_column_to_port(row, column)), (row, column)
                )

    def test_rows_and_columns_are_distinct_immutable_partitions(self) -> None:
        self.assertEqual(PORT_ROWS, ((1, 2, 3), (4, 5, 6), (7, 8, 9)))
        self.assertEqual(PORT_COLUMNS, ((1, 4, 7), (2, 5, 8), (3, 6, 9)))
        for partition in (PORT_ROWS, PORT_COLUMNS):
            self.assertEqual(
                sorted(port for group in partition for port in group),
                list(range(1, 10)),
            )
            self.assertIs(type(partition), tuple)
            self.assertTrue(all(type(group) is tuple for group in partition))
        for row, ports in enumerate(PORT_ROWS, 1):
            for column, columns in enumerate(PORT_COLUMNS, 1):
                self.assertEqual(
                    set(ports) & set(columns), {row_column_to_port(row, column)}
                )
        mutable_view: Any = PORT_ROWS
        with self.assertRaises(TypeError):
            mutable_view[0][0] = 9

    def test_integral_json_numbers_normalize_without_rounding(self) -> None:
        for port, row, column in CHART:
            value: Any = float(port)
            self.assertEqual(port_to_row_column(value), (row, column))
            result = row_column_to_port(float(row), float(column))  # type: ignore[arg-type]
            self.assertEqual(result, port)
            self.assertIs(type(result), int)
        # Adjacent floats are not integers; rounding/truncation would admit them.
        for center in (1.0, 3.0, 9.0):
            for direction in (-math.inf, math.inf):
                value = math.nextafter(center, direction)
                with self.subTest(value=value), self.assertRaises(ValueError):
                    port_to_row_column(value)

    def test_all_coordinate_consumers_reject_bad_values(self) -> None:
        wrong_types: tuple[Any, ...] = (
            True,
            False,
            "1",
            b"1",
            None,
            [],
            {},
            Fraction(1),
            Decimal(1),
            IntegerLabel.ONE,
            np.int64(1),
            np.float64(1),
            Coercible(),
        )
        outside = (0, -0.0, -1, 10, 2**53, 10**100, 1.5, math.nan, math.inf, -math.inf)
        for value in (*wrong_types, *outside):
            for label, consumer in (
                ("port", port_to_row_column),
                ("endpoint", lambda v: GRC9V4PortEndpoint("node", v)),
                ("row", lambda v: row_column_to_port(v, 1)),
                ("column", lambda v: row_column_to_port(1, v)),
            ):
                with (
                    self.subTest(value=repr(value), consumer=label),
                    self.assertRaises((TypeError, ValueError)),
                ):
                    consumer(value)
        for value in (4, 9):
            self.assertIsInstance(port_to_row_column(value), tuple)
            for coordinates in ((value, 1), (1, value)):
                with self.assertRaises(ValueError):
                    row_column_to_port(*coordinates)


class PortEndpointTests(unittest.TestCase):
    def test_node_identity_matches_generic_graph_and_stays_typed(self) -> None:
        for node in (
            "",
            "node",
            "1",
            "\u00e9",
            "e\u0301",
            -1,
            0,
            2**53 - 1,
            -(2**53 - 1),
            1.0,
        ):
            endpoint = GRC9V4PortEndpoint(node, 2.0)  # type: ignore[arg-type]
            generic = OrientedEdge("edge", node, "other")  # type: ignore[arg-type]
            self.assertEqual(endpoint.node_id, generic.tail_node_id)
            self.assertIs(type(endpoint.node_id), type(generic.tail_node_id))
            self.assertEqual(endpoint.port, 2)
            self.assertIs(type(endpoint.port), int)
        self.assertNotEqual(GRC9V4PortEndpoint(1, 1), GRC9V4PortEndpoint("1", 1))
        self.assertNotEqual(
            GRC9V4PortEndpoint("\u00e9", 1), GRC9V4PortEndpoint("e\u0301", 1)
        )
        self.assertEqual(GRC9V4PortEndpoint(1.0, 1.0), GRC9V4PortEndpoint(1, 1))  # type: ignore[arg-type]
        self.assertEqual(len({GRC9V4PortEndpoint(1, 1), GRC9V4PortEndpoint("1", 1)}), 2)

    def test_invalid_node_ids_rejected_without_coercion(self) -> None:
        values: tuple[Any, ...] = (
            True,
            False,
            2**53,
            -(2**53),
            float(2**53),
            -0.0,
            1.5,
            math.nan,
            math.inf,
            np.int64(1),
            np.float64(1),
            IntegerLabel.ONE,
            Coercible(),
            [],
            {},
            b"node",
            "\ud800",
        )
        for node in values:
            with (
                self.subTest(node=repr(node)),
                self.assertRaises((TypeError, ValueError)),
            ):
                GRC9V4PortEndpoint(node, 1)

    def test_frozen_endpoint_and_replacement_revalidation(self) -> None:
        endpoint = GRC9V4PortEndpoint("node", 1)
        for field, value in (("port", 2), ("node_id", "changed")):
            with self.subTest(field=field), self.assertRaises(FrozenInstanceError):
                setattr(endpoint, field, value)
        self.assertFalse(hasattr(endpoint, "__dict__"))
        self.assertEqual(replace(endpoint, port=9), GRC9V4PortEndpoint("node", 9))
        for changes in ({"port": True}, {"port": 10}, {"node_id": True}):
            with (
                self.subTest(changes=changes),
                self.assertRaises((TypeError, ValueError)),
            ):
                replace(endpoint, **changes)
        self.assertEqual(endpoint, GRC9V4PortEndpoint("node", 1))


if __name__ == "__main__":
    unittest.main()

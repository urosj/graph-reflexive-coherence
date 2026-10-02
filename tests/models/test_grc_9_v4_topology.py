"""Chart and structural port-graph checks; no codec/event conformance claim."""

from __future__ import annotations

import math
import unittest
from dataclasses import FrozenInstanceError, replace
from decimal import Decimal
from enum import IntEnum
from fractions import Fraction
from itertools import product
from typing import Any

import numpy as np

from pygrc.models.grc_9_v4_topology import (
    PORT_CHART_ID,
    PORT_COLUMNS,
    PORT_COUNT,
    PORT_ROWS,
    GRC9V4PortEdge,
    GRC9V4PortEndpoint,
    GRC9V4PortGraph,
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


def edge(
    edge_id: str,
    tail: tuple[Any, int],
    head: tuple[Any, int],
    kind: Any = "boundary",
) -> GRC9V4PortEdge:
    return GRC9V4PortEdge(
        edge_id, kind, GRC9V4PortEndpoint(*tail), GRC9V4PortEndpoint(*head)
    )


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


class PortEdgeTests(unittest.TestCase):
    def test_kinds_identity_and_selected_orientation(self) -> None:
        for kind in ("boundary", "spine", "tree"):
            for edge_id in ("edge", "1", " ", "\u00e9", "e\u0301"):
                with self.subTest(kind=kind, edge_id=edge_id):
                    original = edge(edge_id, ("z", 9), (1.0, 2), kind)
                    self.assertEqual(original.edge_id, edge_id)
                    self.assertEqual(original.kind, kind)
                    self.assertEqual(original.tail, GRC9V4PortEndpoint("z", 9))
                    self.assertEqual(original.head, GRC9V4PortEndpoint(1, 2))
                    reversed_edge = replace(
                        original, tail=original.head, head=original.tail
                    )
                    self.assertEqual(reversed_edge.tail, original.head)
                    self.assertEqual(reversed_edge.head, original.tail)
                    self.assertEqual(reversed_edge.edge_id, edge_id)
                    self.assertEqual(reversed_edge.kind, kind)
                    self.assertNotEqual(original, reversed_edge)

    def test_rejects_nonstring_empty_or_malformed_ids_and_unknown_kinds(self) -> None:
        class StringLabel(str):
            pass

        invalid: tuple[Any, ...] = (
            True,
            1,
            1.0,
            b"boundary",
            None,
            [],
            {},
            Coercible(),
            np.str_("boundary"),
            StringLabel("boundary"),
            "",
            "\ud800",
        )
        original = edge("e", ("a", 1), ("b", 1))
        for field in ("edge_id", "kind"):
            for value in invalid:
                with (
                    self.subTest(field=field, value=repr(value)),
                    self.assertRaises((TypeError, ValueError)),
                ):
                    replace(original, **{field: value})
        for kind in ("Boundary", "boundary ", "internal", "", "\u0074ree\x00"):
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                replace(original, kind=kind)  # type: ignore[arg-type]

    def test_requires_endpoint_records_and_revalidates_their_values(self) -> None:
        class EndpointSubclass(GRC9V4PortEndpoint):
            pass

        original = edge("e", ("a", 1), ("b", 1))
        wrong: tuple[Any, ...] = (
            None,
            ("a", 1),
            {"node_id": "a", "port": 1},
            EndpointSubclass("a", 1),
        )
        for field in ("tail", "head"):
            for value in wrong:
                with (
                    self.subTest(field=field, value=value),
                    self.assertRaises(TypeError),
                ):
                    replace(original, **{field: value})
            for corrupt_field, corrupt_value in (("node_id", True), ("port", 10)):
                endpoint = GRC9V4PortEndpoint("a", 1)
                object.__setattr__(endpoint, corrupt_field, corrupt_value)
                with (
                    self.subTest(field=field, corrupt_field=corrupt_field),
                    self.assertRaises((TypeError, ValueError)),
                ):
                    changes: dict[str, Any] = {field: endpoint}
                    replace(original, **changes)

    def test_edge_is_frozen_and_detached_from_supplied_endpoints(self) -> None:
        tail, head = GRC9V4PortEndpoint("a", 1), GRC9V4PortEndpoint("b", 2)
        record = GRC9V4PortEdge("e", "tree", tail, head)
        self.assertIsNot(record.tail, tail)
        self.assertIsNot(record.head, head)
        self.assertFalse(hasattr(record, "__dict__"))
        for field, value in (
            ("edge_id", "other"),
            ("kind", "spine"),
            ("tail", head),
            ("head", tail),
        ):
            with self.subTest(field=field), self.assertRaises(FrozenInstanceError):
                setattr(record, field, value)
        # Even bypassing frozen on caller-owned records cannot alter this edge.
        object.__setattr__(tail, "node_id", "changed")
        object.__setattr__(head, "port", 9)
        self.assertEqual(record, edge("e", ("a", 1), ("b", 2), "tree"))


class PortGraphTests(unittest.TestCase):
    def test_empty_isolated_disconnected_parallel_and_loop_graphs(self) -> None:
        self.assertEqual(GRC9V4PortGraph((), ()).edges, ())
        isolated = GRC9V4PortGraph(("", "isolated"), ())
        self.assertEqual(isolated.live_node_ids, ("", "isolated"))
        edges = (
            edge("parallel-z", ("a", 1), ("b", 9)),
            edge("parallel-a", ("b", 8), ("a", 2), "spine"),
            edge("loop", ("c", 1), ("c", 9), "tree"),
        )
        graph = GRC9V4PortGraph(("c", "isolated", "b", "a"), edges)
        self.assertEqual(graph.live_node_ids, ("c", "isolated", "b", "a"))
        self.assertEqual(graph.edges, edges)
        self.assertEqual(
            tuple(e.edge_id for e in graph.edges), ("parallel-z", "parallel-a", "loop")
        )

    def test_normalized_typed_nodes_and_empty_string_membership(self) -> None:
        nodes: Any = [1.0, "1", "", 0.0, -1.0, "\u00e9", "e\u0301"]
        edges = (
            edge("typed", (1, 1), ("1", 1)),
            edge("empty", ("", 1), (0, 1)),
            edge("unicode", ("\u00e9", 1), ("e\u0301", 1)),
        )
        graph = GRC9V4PortGraph(nodes, edges)
        self.assertEqual(graph.live_node_ids, (1, "1", "", 0, -1, "\u00e9", "e\u0301"))
        self.assertEqual(
            tuple(type(n) for n in graph.live_node_ids),
            (int, str, str, int, int, str, str),
        )
        for missing in (1, "1", "", "\u00e9", "e\u0301"):
            reduced = tuple(n for n in graph.live_node_ids if n != missing)
            with (
                self.subTest(missing=missing),
                self.assertRaisesRegex(ValueError, "live node"),
            ):
                GRC9V4PortGraph(reduced, edges)

    def test_duplicate_node_and_edge_ids_rejected_after_normalization(self) -> None:
        duplicates: tuple[Any, ...] = (
            (1, 1.0),
            (0, 0.0),
            (-1.0, -1),
            ("", ""),
            ("a", "a"),
            (2**53 - 1, float(2**53 - 1)),
        )
        for nodes in duplicates:
            with (
                self.subTest(nodes=nodes),
                self.assertRaisesRegex(ValueError, "duplicate live node"),
            ):
                GRC9V4PortGraph(nodes, ())
        # Disjoint ports and different kinds cannot excuse duplicate edge IDs.
        for kind in ("boundary", "spine", "tree"):
            edges = (edge("e", ("a", 1), ("b", 1)), edge("e", ("a", 2), ("b", 2), kind))
            with (
                self.subTest(kind=kind),
                self.assertRaisesRegex(ValueError, "duplicate edge"),
            ):
                GRC9V4PortGraph(("a", "b"), edges)

    def test_invalid_live_node_ids_rejected_without_coercion(self) -> None:
        invalid: tuple[Any, ...] = (
            True,
            False,
            None,
            b"a",
            [],
            {},
            1.5,
            -0.0,
            math.nan,
            math.inf,
            2**53,
            -(2**53),
            10**100,
            Decimal(1),
            Fraction(1),
            IntegerLabel.ONE,
            np.int64(1),
            np.float64(1),
            Coercible(),
            "\ud800",
        )
        for node in invalid:
            with (
                self.subTest(node=repr(node)),
                self.assertRaises((TypeError, ValueError)),
            ):
                GRC9V4PortGraph((node,), ())

    def test_dangling_tail_head_and_edges_on_empty_graph_rejected(self) -> None:
        for tail, head in (
            (("absent", 1), ("a", 1)),
            (("a", 1), ("absent", 1)),
            (("absent", 1), ("absent", 2)),
        ):
            record = edge("e", tail, head)
            for nodes in ((), ("a", "b")):
                with (
                    self.subTest(tail=tail, head=head, nodes=nodes),
                    self.assertRaisesRegex(ValueError, "live node"),
                ):
                    GRC9V4PortGraph(nodes, (record,))

    def test_reoccupied_endpoint_rejected_in_all_tail_head_positions(self) -> None:
        for first_position, second_position in product(range(2), repeat=2):
            first = [("a", 1), ("b", 2)]
            second = [("c", 3), ("d", 4)]
            second[second_position] = first[first_position]
            records = (
                edge("first", first[0], first[1]),
                edge("second", second[0], second[1], "tree"),
            )
            for ordered in (records, records[::-1]):
                with (
                    self.subTest(first=first_position, second=second_position),
                    self.assertRaisesRegex(ValueError, "already occupied"),
                ):
                    GRC9V4PortGraph(("a", "b", "c", "d"), ordered)
        for tail, head in ((("a", 1), ("b", 1)), (("b", 1), ("a", 1))):
            # Exact duplicate and reversed endpoint pairs also reject.
            records = (
                edge("first", ("a", 1), ("b", 1)),
                edge("second", tail, head),
            )
            with self.assertRaisesRegex(ValueError, "already occupied"):
                GRC9V4PortGraph(("a", "b"), records)

    def test_a_loop_needs_two_distinct_ports_and_consumes_both(self) -> None:
        with self.assertRaisesRegex(ValueError, "already occupied"):
            GRC9V4PortGraph(("a",), (edge("loop", ("a", 1), ("a", 1)),))
        loop = edge("loop", ("a", 1), ("a", 9))
        for port in (1, 9):
            with (
                self.subTest(port=port),
                self.assertRaisesRegex(ValueError, "already occupied"),
            ):
                GRC9V4PortGraph(
                    ("a", "b"), (loop, edge("other", ("b", 1), ("a", port)))
                )

    def test_degree_nine_admitted_and_attempted_tenth_rejected(self) -> None:
        spokes = tuple(edge(f"e{p}", ("hub", p), (p, 1)) for p in range(1, 10))
        nodes = ("hub", *range(1, 11))
        graph = GRC9V4PortGraph(nodes, spokes)
        self.assertEqual(len(graph.edges), 9)
        for reused in range(1, 10):
            for reverse in (False, True):
                tenth = edge("tenth", ("hub", reused), (10, 1))
                if reverse:
                    tenth = replace(tenth, tail=tenth.head, head=tenth.tail)
                with (
                    self.subTest(port=reused, reverse=reverse),
                    self.assertRaisesRegex(ValueError, "already occupied"),
                ):
                    replace(graph, edges=(*graph.edges, tenth))
        with self.assertRaises(ValueError):
            edge("tenth", ("hub", 10), (10, 1))

    def test_exhaustive_two_edge_incidence_patterns_with_typed_nodes(self) -> None:
        # Literal endpoint tokens are the oracle, independent of record equality.
        # Every role, loop, reversal, parallel pair and typed-node collision is
        # exercised over low/middle/high ports: 6**4 = 1296 ordered patterns.
        tokens = ((1, 1), (1, 5), (1, 9), ("1", 1), ("1", 5), ("1", 9))
        admitted = rejected = 0
        for incidences in product(tokens, repeat=4):
            first = edge("first", incidences[0], incidences[1])
            second = edge("second", incidences[2], incidences[3], "spine")
            expected = all(incidences.count(token) <= 1 for token in tokens)
            with self.subTest(incidences=incidences):
                if expected:
                    graph = GRC9V4PortGraph(("1", 1), (first, second))
                    self.assertEqual(graph.edges, (first, second))
                    admitted += 1
                else:
                    with self.assertRaisesRegex(ValueError, "already occupied"):
                        GRC9V4PortGraph(("1", 1), (first, second))
                    rejected += 1
        self.assertEqual((admitted, rejected), (360, 936))

    def test_inputs_must_be_ordered_sequences_of_exact_records(self) -> None:
        class EdgeSubclass(GRC9V4PortEdge):
            pass

        record = edge("e", ("a", 1), ("b", 1))
        for field in ("live_node_ids", "edges"):
            invalid: tuple[Any, ...] = (
                None,
                "ab",
                b"ab",
                bytearray(b"ab"),
                {"a": 1},
                {"a", "b"},
                iter(("a", "b")),
            )
            for value in invalid:
                fields: dict[str, Any] = {"live_node_ids": (), "edges": ()}
                fields[field] = value
                with (
                    self.subTest(field=field, value=repr(value)),
                    self.assertRaises(TypeError),
                ):
                    GRC9V4PortGraph(**fields)
        invalid_edges: tuple[Any, ...] = (
            None,
            {
                "edge_id": "e",
                "kind": "boundary",
                "tail": record.tail,
                "head": record.head,
            },
            OrientedEdge("e", "a", "b"),
            EdgeSubclass("e", "boundary", record.tail, record.head),
        )
        for value in invalid_edges:
            with self.subTest(value=value), self.assertRaises(TypeError):
                GRC9V4PortGraph(("a", "b"), (value,))

    def test_graph_detaches_nested_inputs_and_freezes_all_owned_fields(self) -> None:
        nodes: Any = ["a", "b"]
        original = edge("e", ("a", 1), ("b", 2))
        records: Any = [original]
        graph = GRC9V4PortGraph(nodes, records)
        self.assertIs(type(graph.live_node_ids), tuple)
        self.assertIs(type(graph.edges), tuple)
        self.assertIsNot(graph.edges[0], original)
        self.assertIsNot(graph.edges[0].tail, original.tail)
        self.assertIsNot(graph.edges[0].head, original.head)
        nodes[:] = ["changed"]
        records.clear()
        object.__setattr__(original, "edge_id", "changed")
        object.__setattr__(original.tail, "node_id", "changed")
        object.__setattr__(original.head, "port", 9)
        self.assertEqual(graph.live_node_ids, ("a", "b"))
        self.assertEqual(graph.edges, (edge("e", ("a", 1), ("b", 2)),))
        for record, field, value in (
            (graph, "live_node_ids", ()),
            (graph, "edges", ()),
            (graph.edges[0], "edge_id", "changed"),
            (graph.edges[0].tail, "port", 9),
            (graph.edges[0].head, "node_id", "other"),
        ):
            self.assertFalse(hasattr(record, "__dict__"))
            with self.subTest(field=field), self.assertRaises(FrozenInstanceError):
                setattr(record, field, value)

    def test_graph_revalidates_supplied_records_and_replacements(self) -> None:
        for field, value in (("edge_id", ""), ("kind", "unknown"), ("tail", None)):
            record = edge("e", ("a", 1), ("b", 1))
            object.__setattr__(record, field, value)
            with self.subTest(field=field), self.assertRaises((TypeError, ValueError)):
                GRC9V4PortGraph(("a", "b"), (record,))
        for endpoint_field, endpoint_value in (("node_id", True), ("port", 0)):
            record = edge("e", ("a", 1), ("b", 1))
            object.__setattr__(record.head, endpoint_field, endpoint_value)
            with (
                self.subTest(field=endpoint_field),
                self.assertRaises((TypeError, ValueError)),
            ):
                GRC9V4PortGraph(("a", "b"), (record,))
        original = GRC9V4PortGraph(("a", "b"), (edge("e", ("a", 1), ("b", 1)),))
        with self.assertRaisesRegex(ValueError, "live node"):
            replace(original, live_node_ids=("a",))
        with self.assertRaisesRegex(ValueError, "duplicate live node"):
            replace(original, live_node_ids=("a", "b", "a"))
        with self.assertRaisesRegex(ValueError, "duplicate edge"):
            replace(original, edges=(*original.edges, *original.edges))
        extended = replace(original, live_node_ids=("a", "b", "isolated"))
        self.assertEqual(extended.edges, original.edges)
        self.assertEqual(original.live_node_ids, ("a", "b"))


if __name__ == "__main__":
    unittest.main()

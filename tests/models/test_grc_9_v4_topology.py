"""Chart, port-graph envelope and projection checks; no event conformance claim."""

from __future__ import annotations

import json
import math
import os
import subprocess
import sys
import unittest
from collections.abc import Callable
from copy import deepcopy
from dataclasses import FrozenInstanceError, replace
from decimal import Decimal
from enum import IntEnum
from fractions import Fraction
from hashlib import sha256
from itertools import product
from pathlib import Path
from typing import Any, Literal

import numpy as np

from pygrc.models.grc_9_v4_topology import (
    PORT_CHART_ID,
    PORT_COLUMNS,
    PORT_COUNT,
    PORT_ROWS,
    GRC9V4GraphProjection,
    GRC9V4PortEdge,
    GRC9V4PortEndpoint,
    GRC9V4PortGraph,
    GRC9V4SerializedPortGraph,
    port_to_row_column,
    row_column_to_port,
)
from pygrc.models.grc_v4_codec import V4IdentityError, canonical_json_bytes
from pygrc.models.grc_v4_geometry import GRCV4Graph, OrientedEdge, VertexScalar

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


def port_payload() -> dict[str, Any]:
    """Literal mixed-ID parallel/loop graph; declared order is significant."""
    return {
        "schema_version": "grc9v4-port-graph-v1",
        "live_node_ids": ["1", 1, ""],
        "edges": [
            {
                "edge_id": "z",
                "kind": "boundary",
                "tail": {"node_id": 1, "port": 1},
                "head": {"node_id": "1", "port": 2},
            },
            {
                "edge_id": "a",
                "kind": "spine",
                "tail": {"node_id": "1", "port": 3},
                "head": {"node_id": 1, "port": 4},
            },
            {
                "edge_id": "loop",
                "kind": "tree",
                "tail": {"node_id": "", "port": 8},
                "head": {"node_id": "", "port": 9},
            },
        ],
    }


def independent_ascii_digest(payload: object, prefix: str = "grc-graph-sha256") -> str:
    """Independent only for the ASCII, integer-token preimages used below."""
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode()
    return prefix + ":" + sha256(encoded).hexdigest()


def port_envelope(payload: dict[str, Any]) -> dict[str, Any]:
    return {**deepcopy(payload), "graph_digest": independent_ascii_digest(payload)}


class PortGraphCodecTests(unittest.TestCase):
    def test_frozen_payload_envelope_vector_and_independent_preimage(self) -> None:
        path = (
            Path(__file__).resolve().parents[2]
            / "specs/grc-v4-conformance-vectors.json"
        )
        vectors = json.loads(path.read_text())
        (vector,) = [
            v
            for v in vectors["port_graph_envelope_vectors"]
            if v["vector_id"] == "GRC9V4-PORT-GRAPH-PAYLOAD-DIGEST-ENVELOPE"
        ]
        (identity,) = [
            v
            for v in vectors["identity_vectors"]
            if v["vector_id"] == "IDENTITY-GRC9V4-SOURCE-GRAPH"
        ]
        payload, envelope = vector["payload"], vector["serialized_port_graph"]
        canonical = identity["canonical_jcs_utf8"].encode("utf-8")
        self.assertEqual(canonical.hex(), identity["canonical_jcs_utf8_hex"])
        expected = "grc-graph-sha256:" + sha256(canonical).hexdigest()
        self.assertEqual(expected, vector["expected"]["graph_digest"])
        self.assertEqual(expected, independent_ascii_digest(payload))
        graph = GRC9V4SerializedPortGraph.from_envelope(envelope)
        self.assertIs(GRC9V4SerializedPortGraph, GRC9V4PortGraph)
        self.assertIs(type(graph), GRC9V4PortGraph)
        self.assertEqual(graph.schema_version, "grc9v4-port-graph-v1")
        self.assertEqual(graph.to_payload(), payload)
        self.assertEqual(canonical_json_bytes(graph.to_payload()), canonical)
        self.assertEqual(graph.graph_digest, expected)
        self.assertEqual(graph.to_envelope(), envelope)
        self.assertEqual(GRC9V4PortGraph.from_payload(payload), graph)
        self.assertNotIn("graph_digest", graph.to_payload())
        self.assertNotEqual(independent_ascii_digest(envelope), expected)
        self.assertEqual(
            GRC9V4PortGraph.from_json(graph.to_canonical_bytes(), encoding="canonical"),
            graph,
        )

    def test_roundtrip_empty_isolated_and_mixed_graphs_through_both_routes(
        self,
    ) -> None:
        for graph in (
            GRC9V4PortGraph((), ()),
            GRC9V4PortGraph(("isolated", ""), ()),
            GRC9V4PortGraph.from_payload(port_payload()),
        ):
            with self.subTest(nodes=graph.live_node_ids):
                envelope = graph.to_envelope()
                self.assertEqual(
                    set(envelope),
                    {"schema_version", "live_node_ids", "edges", "graph_digest"},
                )
                self.assertEqual(GRC9V4PortGraph.from_envelope(envelope), graph)
                for value in (json.dumps(envelope), json.dumps(envelope).encode()):
                    self.assertEqual(
                        GRC9V4PortGraph.from_json(value, encoding="configuration"),
                        graph,
                    )
                for value in (
                    graph.to_canonical_bytes(),
                    graph.to_canonical_bytes().decode(),
                ):
                    self.assertEqual(
                        GRC9V4PortGraph.from_json(value, encoding="canonical"), graph
                    )
        for bad_encoding in (None, True, b"canonical", "guess"):
            with self.subTest(encoding=bad_encoding), self.assertRaises(TypeError):
                GRC9V4PortGraph.from_json("{}", encoding=bad_encoding)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            GRC9V4PortGraph.from_json("{}")  # type: ignore[call-arg]

    def test_closed_schema_rejects_missing_extra_and_wrong_version_fields(self) -> None:
        for location in ((), ("edges", 0), ("edges", 0, "tail"), ("edges", 0, "head")):
            original = port_envelope(port_payload())
            target: Any = original
            for key in location:
                target = target[key]
            for field in (*target, "unexpected"):
                data = deepcopy(original)
                bad: Any = data
                for key in location:
                    bad = bad[key]
                if field == "unexpected":
                    bad[field] = 1
                else:
                    del bad[field]
                with (
                    self.subTest(location=location, field=field),
                    self.assertRaises(ValueError),
                ):
                    GRC9V4PortGraph.from_envelope(data)
        for version in ("grcv4-serialized-graph-v1", "grc9v4-port-graph-v2", True):
            data = port_envelope(port_payload())
            data["schema_version"] = version
            with self.subTest(version=version), self.assertRaises(ValueError):
                GRC9V4PortGraph.from_envelope(data)
        with self.assertRaises(ValueError):
            GRC9V4PortGraph.from_payload(port_envelope(port_payload()))
        with self.assertRaises(ValueError):
            GRC9V4PortGraph.from_envelope(port_payload())

    def test_malformed_forged_and_recursively_hashed_digests_rejected(self) -> None:
        original = port_envelope(port_payload())
        wrong: tuple[Any, ...] = (
            None,
            1,
            True,
            "",
            "grc-graph-sha256:" + "0" * 64,
            original["graph_digest"].upper(),
            original["graph_digest"] + "\n",
            independent_ascii_digest(original),
        )
        for digest in wrong:
            data = {**original, "graph_digest": digest}
            with self.subTest(digest=digest), self.assertRaises(ValueError):
                GRC9V4PortGraph.from_envelope(data)
        # A schema-valid content change needs its own digest; no repair of input.
        data = deepcopy(original)
        data["edges"][0]["kind"] = "tree"
        with self.assertRaises(V4IdentityError):
            GRC9V4PortGraph.from_envelope(data)

    def test_rehashed_structural_defects_reject_through_actual_decoders(self) -> None:
        mutations: dict[str, Callable[[dict[str, Any]], None]] = {
            "dangling": lambda p: p["edges"][0]["tail"].update(node_id="absent"),
            "empty-not-live": lambda p: p["live_node_ids"].remove(""),
            "typed-not-live": lambda p: p["live_node_ids"].remove(1),
            "duplicate-node": lambda p: p["live_node_ids"].append(1),
            "duplicate-edge": lambda p: p["edges"][1].update(edge_id="z"),
            "occupancy": lambda p: p["edges"][1]["head"].update(port=1),
            "same-port-loop": lambda p: p["edges"][2]["head"].update(port=8),
        }
        for name, mutate in mutations.items():
            payload = port_payload()
            mutate(payload)
            envelope = port_envelope(payload)
            with self.subTest(defect=name):
                with self.assertRaises(ValueError):
                    GRC9V4PortGraph.from_payload(payload)
                with self.assertRaises(ValueError):
                    GRC9V4PortGraph.from_envelope(envelope)
                with self.assertRaises(ValueError):
                    GRC9V4PortGraph.from_json(
                        json.dumps(envelope), encoding="configuration"
                    )
                with self.assertRaises(ValueError):
                    GRC9V4PortGraph.from_json(
                        canonical_json_bytes(envelope), encoding="canonical"
                    )

    def test_integral_float_normalization_preserves_identity_but_not_typed_collisions(
        self,
    ) -> None:
        graph = GRC9V4PortGraph.from_payload(port_payload())
        data = port_envelope(port_payload())
        data["live_node_ids"][1] = 1.0
        for row in data["edges"]:
            for side in ("tail", "head"):
                endpoint = row[side]
                endpoint["port"] = float(endpoint["port"])
                if type(endpoint["node_id"]) is int:
                    endpoint["node_id"] = float(endpoint["node_id"])
        restored = GRC9V4PortGraph.from_json(json.dumps(data), encoding="configuration")
        self.assertEqual(restored.to_canonical_bytes(), graph.to_canonical_bytes())
        self.assertIs(type(restored.live_node_ids[1]), int)
        self.assertTrue(all(type(e.tail.port) is int for e in restored.edges))
        data["live_node_ids"].append(1)
        with self.assertRaises(ValueError):
            GRC9V4PortGraph.from_envelope(data)

    def test_wire_and_native_values_keep_the_strict_numeric_domain(self) -> None:
        invalid: tuple[Any, ...] = (
            True,
            False,
            -0.0,
            1.5,
            2**53,
            float(2**53),
            10**100,
            math.nan,
            math.inf,
            Decimal(1),
            IntegerLabel.ONE,
            np.float64(1),
            Coercible(),
            "\ud800",
        )
        for value in invalid:
            for location in ("node", "port"):
                data = port_envelope(port_payload())
                if location == "node":
                    data["live_node_ids"][1] = value
                    data["edges"][0]["tail"]["node_id"] = value
                    data["edges"][1]["head"]["node_id"] = value
                else:
                    data["edges"][0]["tail"]["port"] = value
                with (
                    self.subTest(value=repr(value), location=location),
                    self.assertRaises((TypeError, ValueError)),
                ):
                    GRC9V4PortGraph.from_envelope(data)
        # Canonical decoding admits large binary64 tokens in general, but node
        # admission must still reject them even when the envelope is rehashed.
        payload = port_payload()
        payload["live_node_ids"].append(float(2**53))
        envelope = {
            **payload,
            "graph_digest": "grc-graph-sha256:"
            + sha256(canonical_json_bytes(payload)).hexdigest(),
        }
        with self.assertRaises(ValueError):
            GRC9V4PortGraph.from_json(
                canonical_json_bytes(envelope), encoding="canonical"
            )
        for node in (2**53 - 1, -(2**53 - 1)):
            graph = GRC9V4PortGraph((node,), ())
            self.assertEqual(
                GRC9V4PortGraph.from_json(
                    graph.to_canonical_bytes(), encoding="canonical"
                ),
                graph,
            )

    def test_strict_json_duplicate_keys_and_canonical_route_are_not_bypassed(
        self,
    ) -> None:
        envelope = port_envelope(port_payload())
        raw = json.dumps(envelope)
        bad = (
            raw.replace(
                '"schema_version":',
                '"schema_version":"grc9v4-port-graph-v1","schema_version":',
                1,
            ),
            raw.replace('"port": 1', '"port": 1, "port": 1', 1),
            raw.replace('"port": 1', '"port": -0', 1),
            raw.replace('"port": 1', '"port": NaN', 1),
            raw.replace('"port": 1', '"port": 1e-999', 1),
            raw + " trailing",
        )
        for text in bad:
            for encoding in ("configuration", "canonical"):
                with (
                    self.subTest(raw=text[:80], encoding=encoding),
                    self.assertRaises(ValueError),
                ):
                    GRC9V4PortGraph.from_json(text, encoding=encoding)
        with self.assertRaises(ValueError):
            GRC9V4PortGraph.from_json(raw, encoding="canonical")
        with self.assertRaises(ValueError):
            GRC9V4PortGraph.from_json(b"\xff", encoding="configuration")

    def test_identity_binds_order_ports_kinds_ids_and_orientation(self) -> None:
        original = port_payload()
        graph = GRC9V4PortGraph.from_payload(original)
        cases: list[dict[str, Any]] = []
        for field in ("live_node_ids", "edges"):
            data = deepcopy(original)
            data[field].reverse()
            cases.append(data)
        for field, value in (("port", 5), ("node_id", "")):
            data = deepcopy(original)
            data["edges"][0]["tail"][field] = value
            cases.append(data)
        for field, value in (("kind", "tree"), ("edge_id", "renamed")):
            data = deepcopy(original)
            data["edges"][0][field] = value
            cases.append(data)
        data = deepcopy(original)
        row = data["edges"][0]
        row["tail"], row["head"] = row["head"], row["tail"]
        cases.append(data)
        for data in cases:
            with self.subTest(payload=data):
                changed = GRC9V4PortGraph.from_envelope(port_envelope(data))
                self.assertNotEqual(changed.graph_digest, graph.graph_digest)
                self.assertNotEqual(
                    changed.orientation_identity, graph.orientation_identity
                )
                self.assertEqual(changed.graph_digest, independent_ascii_digest(data))
        reordered = {key: original[key] for key in reversed(original)}
        reordered["edges"] = [
            {key: row[key] for key in reversed(row)} for row in original["edges"]
        ]
        self.assertEqual(
            GRC9V4PortGraph.from_payload(reordered).to_canonical_bytes(),
            graph.to_canonical_bytes(),
        )

    def test_unicode_stays_utf8_and_is_not_normalized(self) -> None:
        graph = GRC9V4PortGraph(("\u00e9", "e\u0301", "\U0001f600"), ())
        expected = (
            '{"edges":[],"live_node_ids":["é","é","😀"],'
            '"schema_version":"grc9v4-port-graph-v1"}'
        ).encode()
        self.assertEqual(canonical_json_bytes(graph.to_payload()), expected)
        self.assertEqual(
            graph.graph_digest, "grc-graph-sha256:" + sha256(expected).hexdigest()
        )
        self.assertEqual(
            GRC9V4PortGraph.from_json(graph.to_canonical_bytes(), encoding="canonical"),
            graph,
        )
        self.assertNotEqual(
            GRC9V4PortGraph(("é",), ()).graph_digest,
            GRC9V4PortGraph(("e\u0301",), ()).graph_digest,
        )

    def test_mutating_input_or_export_cannot_change_graph_or_digest(self) -> None:
        original = port_envelope(port_payload())
        graph = GRC9V4PortGraph.from_envelope(original)
        before = graph.to_canonical_bytes()
        original["live_node_ids"].clear()
        original["edges"][0]["tail"]["port"] = 9
        for exported in (graph.to_payload(), graph.to_envelope()):
            mutable: Any = exported
            mutable["edges"][0]["tail"]["port"] = 9
            mutable["live_node_ids"].reverse()
            mutable["edges"].clear()
        self.assertEqual(graph.to_canonical_bytes(), before)
        self.assertEqual(GRC9V4PortGraph.from_json(before, encoding="canonical"), graph)


class PortGraphProjectionTests(unittest.TestCase):
    def test_generic_order_lookup_incidence_and_orientation_descriptor(self) -> None:
        graph = GRC9V4PortGraph.from_payload(port_payload())
        view = graph.generic_projection()
        self.assertEqual(view.live_node_ids, ("1", 1, ""))
        self.assertEqual(view.live_edge_ids, ("z", "a", "loop"))
        self.assertEqual(
            view.oriented_edges,
            (
                OrientedEdge("z", 1, "1"),
                OrientedEdge("a", "1", 1),
                OrientedEdge("loop", "", ""),
            ),
        )
        self.assertEqual(view.incidence, ((-1, 1, 0), (1, -1, 0), (0, 0, 0)))
        for node, index, star in (("1", 0, (0, 1)), (1, 1, (0, 1)), ("", 2, (2,))):
            self.assertEqual(view.node_index(node), index)
            self.assertEqual(view.star(node), star)
        self.assertEqual(view.node_index(1.0), 1)  # type: ignore[arg-type]
        for i, edge_id in enumerate(("z", "a", "loop")):
            self.assertEqual(view.edge_index(edge_id), i)
        descriptor = {
            "descriptor_version": "grcv4-ordered-outward-incidence-v1",
            "graph": port_payload(),
            "positive_flux": "tail_to_head",
            "incidence_tail": 1,
            "incidence_head": -1,
        }
        self.assertEqual(view.graph_digest, independent_ascii_digest(port_payload()))
        self.assertEqual(
            view.orientation_identity,
            independent_ascii_digest(descriptor, "grcv4-orientation-sha256"),
        )
        for lookup in (view.node_index, view.edge_index, view.star):
            with self.assertRaises(KeyError):
                lookup("missing")
            with self.assertRaises((TypeError, ValueError)):
                lookup(True)  # type: ignore[arg-type]

    def test_projection_is_one_owner_with_no_standalone_codec_or_generic_identity(
        self,
    ) -> None:
        graph = GRC9V4PortGraph.from_payload(port_payload())
        view = graph.generic_projection()
        self.assertIs(view.port_graph, graph)
        self.assertFalse(hasattr(view, "__dict__"))
        self.assertEqual(view.__slots__, ("port_graph",))
        for name in (
            "to_payload",
            "to_envelope",
            "to_canonical_bytes",
            "from_payload",
            "from_json",
        ):
            self.assertFalse(hasattr(view, name))
        with self.assertRaises(FrozenInstanceError):
            view.port_graph = GRC9V4PortGraph((), ())  # type: ignore[misc]
        # The generic graph with ports/kinds erased would have another identity.
        # No such graph is stored by this view, nor passed through numerical gates.
        generic = GRCV4Graph(view.live_node_ids, view.oriented_edges)
        self.assertNotEqual(view.graph_digest, generic.graph_digest)
        with self.assertRaises(TypeError):
            VertexScalar(view, (0, 0, 0))  # type: ignore[arg-type]
        exported = view.oriented_edges
        with self.assertRaises(FrozenInstanceError):
            exported[0].tail_node_id = "changed"  # type: ignore[misc]
        object.__setattr__(exported[0], "tail_node_id", "changed")
        self.assertEqual(view.oriented_edges[0], OrientedEdge("z", 1, "1"))
        self.assertEqual(view.graph_digest, graph.graph_digest)

    def test_projection_rejects_unadmitted_inputs_and_corrupted_typed_graphs(
        self,
    ) -> None:
        class GraphSubclass(GRC9V4PortGraph):
            pass

        wrong: tuple[Any, ...] = (
            port_payload(),
            (),
            None,
            GRCV4Graph((), ()),
            GraphSubclass((), ()),
        )
        for value in wrong:
            with self.subTest(value=value), self.assertRaises(TypeError):
                GRC9V4GraphProjection(value)
        for field, value in (("node_id", "absent"), ("port", 0)):
            graph = GRC9V4PortGraph.from_payload(port_payload())
            object.__setattr__(graph.edges[0].tail, field, value)
            with self.subTest(field=field), self.assertRaises(ValueError):
                graph.generic_projection()
        graph = GRC9V4PortGraph.from_payload(port_payload())
        object.__setattr__(graph.edges[1].head, "port", 1)
        with self.assertRaises(ValueError):
            GRC9V4GraphProjection(graph)
        for field in ("live_node_ids", "edges"):
            graph = GRC9V4PortGraph.from_payload(port_payload())
            object.__setattr__(graph, field, list(getattr(graph, field)))
            with self.subTest(storage=field), self.assertRaises(TypeError):
                graph.generic_projection()
        for location in ("node", "endpoint-node", "endpoint-port"):
            graph = GRC9V4PortGraph.from_payload(port_payload())
            if location == "node":
                object.__setattr__(graph, "live_node_ids", ("1", 1.0, ""))
            elif location == "endpoint-node":
                object.__setattr__(graph.edges[0].tail, "node_id", 1.0)
            else:
                object.__setattr__(graph.edges[0].tail, "port", 1.0)
            with self.subTest(normalization=location), self.assertRaises(TypeError):
                graph.generic_projection()

    def test_empty_and_isolated_views_and_edge_reversal(self) -> None:
        for nodes, incidence in (((), ()), (("isolated",), ((),))):
            view = GRC9V4PortGraph(nodes, ()).generic_projection()
            self.assertEqual(view.incidence, incidence)
            self.assertEqual(view.oriented_edges, ())
            if nodes:
                self.assertEqual(view.star("isolated"), ())
        graph = GRC9V4PortGraph.from_payload(port_payload())
        first = graph.edges[0]
        reversed_graph = replace(
            graph,
            edges=(replace(first, tail=first.head, head=first.tail), *graph.edges[1:]),
        )
        view = reversed_graph.generic_projection()
        self.assertEqual(view.incidence, ((1, 1, 0), (-1, -1, 0), (0, 0, 0)))
        self.assertEqual(view.live_edge_ids, graph.generic_projection().live_edge_ids)
        self.assertNotEqual(view.orientation_identity, graph.orientation_identity)
        restored = GRC9V4PortGraph.from_json(
            reversed_graph.to_canonical_bytes(), encoding="canonical"
        )
        self.assertEqual(restored.generic_projection(), view)

    def test_ports_and_kinds_remain_identity_even_when_generic_adjacency_is_equal(
        self,
    ) -> None:
        graph = GRC9V4PortGraph.from_payload(port_payload())
        first = graph.edges[0]
        for changed_edge in (
            replace(first, kind="tree"),
            replace(first, tail=replace(first.tail, port=5)),
        ):
            changed = replace(graph, edges=(changed_edge, *graph.edges[1:]))
            view = changed.generic_projection()
            self.assertEqual(
                view.oriented_edges, graph.generic_projection().oriented_edges
            )
            self.assertEqual(view.incidence, graph.generic_projection().incidence)
            self.assertNotEqual(view.graph_digest, graph.graph_digest)
            self.assertNotEqual(view.orientation_identity, graph.orientation_identity)


def independent_envelope_bytes(payload: dict[str, Any]) -> bytes:
    """These review inputs contain only ASCII strings and safe integer tokens."""
    return json.dumps(
        port_envelope(payload), sort_keys=True, separators=(",", ":")
    ).encode()


def saturated_payload(*, loops: bool = False) -> dict[str, Any]:
    if loops:
        rows = [
            {
                "edge_id": f"loop-{p}",
                "kind": "tree",
                "tail": {"node_id": 0, "port": p},
                "head": {"node_id": 0, "port": p + 1},
            }
            for p in (1, 3, 5, 7)
        ]
        rows.append(
            {
                "edge_id": "spoke",
                "kind": "boundary",
                "tail": {"node_id": 0, "port": 9},
                "head": {"node_id": 9, "port": 1},
            }
        )
    else:
        rows = [
            {
                "edge_id": f"e{p}",
                "kind": "boundary",
                "tail": {"node_id": 0, "port": p},
                "head": {"node_id": p, "port": 1},
            }
            for p in range(1, 10)
        ]
    return {
        "schema_version": "grc9v4-port-graph-v1",
        "live_node_ids": list(range(11)),
        "edges": rows,
    }


class PortGraphIntegratedReviewTests(unittest.TestCase):
    def test_frozen_source_and_seventeen_target_graphs_with_every_port_lookup(
        self,
    ) -> None:
        path = (
            Path(__file__).resolve().parents[2]
            / "specs/grc-v4-conformance-vectors.json"
        )
        vectors = json.loads(path.read_text())
        source = vectors["port_graph_envelope_vectors"][0]
        cases = [
            (source["vector_id"], source["payload"], source["expected"]["graph_digest"])
        ]
        for row in vectors["grc9_expansion_vectors"]:
            expected = row["expected"]
            cases.append(
                (
                    row["fixture_id"],
                    expected["identity_payloads"]["target_graph"],
                    expected["target_graph_digest"],
                )
            )
        self.assertEqual(len(cases), 18)
        for name, payload, digest in cases:
            with self.subTest(fixture=name):
                self.assertEqual(independent_ascii_digest(payload), digest)
                graph = GRC9V4PortGraph.from_json(
                    independent_envelope_bytes(payload), encoding="canonical"
                )
                self.assertEqual(graph.to_payload(), payload)
                self.assertEqual(graph.graph_digest, digest)
                view = graph.generic_projection()
                self.assertIs(view.port_graph, graph)
                self.assertEqual(view.graph_digest, digest)
                self.assertEqual(view.live_node_ids, tuple(payload["live_node_ids"]))
                self.assertEqual(
                    view.oriented_edges,
                    tuple(
                        OrientedEdge(
                            e["edge_id"], e["tail"]["node_id"], e["head"]["node_id"]
                        )
                        for e in payload["edges"]
                    ),
                )
                occupied = {
                    (e[side]["node_id"], e[side]["port"]): e["edge_id"]
                    for e in payload["edges"]
                    for side in ("tail", "head")
                }
                self.assertEqual(len(occupied), 2 * len(payload["edges"]))
                for node in payload["live_node_ids"]:
                    for port, row_index, column in CHART:
                        edge_at = graph.edge_at(
                            node, row_column_to_port(row_index, column)
                        )
                        self.assertEqual(
                            None if edge_at is None else edge_at.edge_id,
                            occupied.get((node, port)),
                        )
                for incidence_column in zip(*view.incidence, strict=True):
                    self.assertEqual(sum(incidence_column), 0)

    def test_port_lookup_distinguishes_inactive_missing_typed_and_loop_endpoints(
        self,
    ) -> None:
        graph = GRC9V4PortGraph.from_json(
            independent_envelope_bytes(port_payload()), encoding="canonical"
        )
        expected = {
            (1, 1): "z",
            ("1", 2): "z",
            ("1", 3): "a",
            (1, 4): "a",
            ("", 8): "loop",
            ("", 9): "loop",
        }
        for node in (1, "1", ""):
            for port in range(1, 10):
                found = graph.edge_at(node, port)
                self.assertEqual(
                    None if found is None else found.edge_id, expected.get((node, port))
                )
        self.assertEqual(graph.edge_at(1.0, 1.0), graph.edges[0])  # type: ignore[arg-type]
        self.assertIs(graph.edge_at("", 8), graph.edge_at("", 9))
        self.assertIsNone(GRC9V4PortGraph(("isolated",), ()).edge_at("isolated", 9))
        for unknown in ("absent", 0, "0"):
            with self.subTest(node=unknown), self.assertRaises(KeyError):
                graph.edge_at(unknown, 1)
        invalid: tuple[Any, ...] = (
            True,
            False,
            -0.0,
            1.5,
            math.nan,
            math.inf,
            2**53,
            IntegerLabel.ONE,
            np.int64(1),
            Coercible(),
        )
        for value in invalid:
            with (
                self.subTest(node=repr(value)),
                self.assertRaises((TypeError, ValueError)),
            ):
                graph.edge_at(value, 1)
        for value in (*invalid, 0, 10, "1", None):
            with (
                self.subTest(port=repr(value)),
                self.assertRaises((TypeError, ValueError)),
            ):
                graph.edge_at(1, value)

    def test_all_512_saturated_orientations_through_wire_and_projection(self) -> None:
        for mask in range(512):
            payload = saturated_payload()
            signs = [(-1 if mask & (1 << i) else 1) for i in range(9)]
            for i, row in enumerate(payload["edges"]):
                if signs[i] == -1:
                    row["tail"], row["head"] = row["head"], row["tail"]
            with self.subTest(mask=mask):
                encoded = independent_envelope_bytes(payload)
                graph = GRC9V4PortGraph.from_json(encoded, encoding="canonical")
                view = graph.generic_projection()
                self.assertEqual(graph.to_canonical_bytes(), encoded)
                expected = (
                    tuple(signs),
                    *(
                        tuple(-signs[j] if i == j else 0 for j in range(9))
                        for i in range(9)
                    ),
                    (0,) * 9,
                )
                self.assertEqual(view.incidence, expected)
                self.assertEqual(view.star(0), tuple(range(9)))
                for port in range(1, 10):
                    found = graph.edge_at(0, port)
                    self.assertIsNotNone(found)
                    assert found is not None
                    self.assertEqual(found.edge_id, f"e{port}")
                    self.assertEqual(view.edge_index(found.edge_id), port - 1)

    def test_all_1296_incidence_patterns_through_canonical_admission(self) -> None:
        tokens: tuple[tuple[str | int, int], ...] = (
            (1, 1),
            (1, 5),
            (1, 9),
            ("1", 1),
            ("1", 5),
            ("1", 9),
        )
        admitted = rejected = 0
        for incidences in product(tokens, repeat=4):
            payload = port_payload()
            payload["live_node_ids"] = ["1", 1]
            payload["edges"] = payload["edges"][:2]
            for i, row in enumerate(payload["edges"]):
                for j, side in enumerate(("tail", "head")):
                    node, port = incidences[2 * i + j]
                    row[side] = {"node_id": node, "port": port}
            raw = independent_envelope_bytes(payload)
            with self.subTest(incidences=incidences):
                if all(incidences.count(token) <= 1 for token in tokens):
                    graph = GRC9V4PortGraph.from_json(raw, encoding="canonical")
                    self.assertEqual(graph.to_canonical_bytes(), raw)
                    view = graph.generic_projection()
                    self.assertEqual(view.live_edge_ids, ("z", "a"))
                    for i, endpoint in enumerate(incidences):
                        found = graph.edge_at(*endpoint)
                        self.assertIsNotNone(found)
                        assert found is not None
                        self.assertEqual(found.edge_id, ("z", "a")[i // 2])
                    admitted += 1
                else:
                    with self.assertRaisesRegex(ValueError, "already occupied"):
                        GRC9V4PortGraph.from_json(raw, encoding="canonical")
                    rejected += 1
        self.assertEqual((admitted, rejected), (360, 936))

    def test_rehashed_tenth_incidence_rejects_even_when_loops_hide_in_incidence(
        self,
    ) -> None:
        rejected = 0
        for loops in (False, True):
            source = saturated_payload(loops=loops)
            graph = GRC9V4PortGraph.from_json(
                independent_envelope_bytes(source), encoding="canonical"
            )
            self.assertTrue(all(graph.edge_at(0, p) is not None for p in range(1, 10)))
            self.assertEqual(len(graph.generic_projection().star(0)), 5 if loops else 9)
            if loops:
                self.assertEqual(
                    graph.generic_projection().incidence[0], (0, 0, 0, 0, 1)
                )
            for port in range(1, 10):
                for reverse in (False, True):
                    payload = deepcopy(source)
                    overflow = {
                        "edge_id": "overflow",
                        "kind": "spine",
                        "tail": {"node_id": 0, "port": port},
                        "head": {"node_id": 10, "port": 1},
                    }
                    if reverse:
                        overflow["tail"], overflow["head"] = (
                            overflow["head"],
                            overflow["tail"],
                        )
                    payload["edges"].append(overflow)
                    for encoding in ("configuration", "canonical"):
                        with (
                            self.subTest(
                                loops=loops,
                                port=port,
                                reverse=reverse,
                                encoding=encoding,
                            ),
                            self.assertRaisesRegex(ValueError, "already occupied"),
                        ):
                            GRC9V4PortGraph.from_json(
                                independent_envelope_bytes(payload), encoding=encoding
                            )
                        rejected += 1
        self.assertEqual(rejected, 72)

    def test_replacement_and_detached_exports_keep_existing_view_stable(self) -> None:
        data = port_envelope(port_payload())
        graph = GRC9V4PortGraph.from_envelope(data)
        view = graph.generic_projection()
        before = (
            graph.to_canonical_bytes(),
            view.graph_digest,
            view.orientation_identity,
        )
        first = graph.edges[0]
        replacement = replace(
            graph,
            edges=(replace(first, tail=replace(first.tail, port=5)), *graph.edges[1:]),
        )
        self.assertEqual(graph.edge_at(1, 1), first)
        self.assertIsNone(replacement.edge_at(1, 1))
        self.assertEqual(replacement.edge_at(1, 5), replacement.edges[0])
        self.assertIs(view.port_graph, graph)
        self.assertNotEqual(replacement.graph_digest, view.graph_digest)
        data["edges"][0]["tail"]["port"] = 5
        for exported in (graph.to_payload(), graph.to_envelope()):
            mutable: Any = exported
            mutable["edges"].reverse()
            mutable["live_node_ids"].clear()
        for name in ("schema_version", "graph_digest"):
            with (
                self.subTest(field=name),
                self.assertRaises((FrozenInstanceError, TypeError)),
            ):
                setattr(graph, name, "forged")
        with self.assertRaises(FrozenInstanceError):
            first.kind = "spine"  # type: ignore[misc]
        self.assertEqual(
            (graph.to_canonical_bytes(), view.graph_digest, view.orientation_identity),
            before,
        )
        self.assertEqual(graph.edge_at(1, 1), first)

    def test_warm_decoders_reject_type_confusions_cycles_and_extra_authority(
        self,
    ) -> None:
        valid = port_payload()
        encoding: Literal["configuration", "canonical"]
        # Prime all routes before attacking numerically-equal Boolean fields.
        raw = independent_envelope_bytes(valid)
        GRC9V4PortGraph.from_json(raw, encoding="canonical")
        mutations: dict[str, Callable[[dict[str, Any]], None]] = {
            "boolean-port": lambda p: p["edges"][0]["tail"].update(port=True),
            "boolean-node": lambda p: p["edges"][0]["tail"].update(node_id=True),
            "integer-edge-id": lambda p: p["edges"][0].update(edge_id=1),
            "empty-edge-id": lambda p: p["edges"][0].update(edge_id=""),
            "unknown-kind": lambda p: p["edges"][0].update(kind="internal"),
            "orientation-sign": lambda p: p["edges"][0].update(orientation_sign=1),
            "second-graph": lambda p: p.update(generic_graph={}),
            "port-cache": lambda p: p.update(port_cache={}),
            "resource-coordinate": lambda p: p["edges"][0]["tail"].update(resource=0),
        }
        for name, mutate in mutations.items():
            payload = deepcopy(valid)
            mutate(payload)
            for encoding in ("configuration", "canonical"):
                with (
                    self.subTest(defect=name, encoding=encoding),
                    self.assertRaises(ValueError),
                ):
                    GRC9V4PortGraph.from_json(
                        independent_envelope_bytes(payload), encoding=encoding
                    )
        cyclic = port_envelope(valid)
        cyclic["edges"][0]["tail"]["port"] = cyclic
        with self.assertRaises(ValueError):
            GRC9V4PortGraph.from_envelope(cyclic)
        duplicate = raw.decode().replace('"port":1', '"port":1,"\\u0070ort":1', 1)
        for encoding in ("configuration", "canonical"):
            with self.subTest(duplicate=encoding), self.assertRaises(ValueError):
                GRC9V4PortGraph.from_json(duplicate, encoding=encoding)

    def test_wire_identities_do_not_depend_on_python_hash_seed(self) -> None:
        graph = GRC9V4PortGraph.from_payload(port_payload())
        raw = graph.to_canonical_bytes()
        expected = (
            raw.decode()
            + "\n"
            + graph.graph_digest
            + "\n"
            + graph.orientation_identity
            + "\n"
        )
        script = """import sys
from pygrc.models.grc_9_v4_topology import GRC9V4PortGraph
graph = GRC9V4PortGraph.from_json(sys.stdin.buffer.read(), encoding="canonical")
view = graph.generic_projection()
print(graph.to_canonical_bytes().decode())
print(view.graph_digest)
print(view.orientation_identity)
"""
        root = Path(__file__).resolve().parents[2]
        for seed in ("0", "1", "73"):
            env = {
                **os.environ,
                "PYTHONHASHSEED": seed,
                "PYTHONPATH": str(root / "src"),
                "OPENBLAS_NUM_THREADS": "1",
            }
            result = subprocess.run(
                [sys.executable, "-c", script],
                input=raw,
                capture_output=True,
                env=env,
                cwd=root,
                check=True,
                timeout=30,
            )
            with self.subTest(seed=seed):
                self.assertEqual(result.stdout.decode(), expected)


if __name__ == "__main__":
    unittest.main()

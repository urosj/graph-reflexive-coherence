"""P9-3.1 independent finite-graph and rational-pairing witnesses.

Expected matrices and 2x2 inverse actions below are hand/scalar Fraction
calculations, not calls back into the production implementation or NumPy.
These primitive tests do not admit a full numerical profile.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from fractions import Fraction
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any
import unittest
from unittest.mock import patch
import venv

import numpy as np

from pygrc.models.grc_v4_codec import V4DependencyError, canonical_json_bytes
from pygrc.models.grc_v4_geometry import (
    GRCV4Differential,
    GRCV4Graph,
    GRCV4Pairings,
    GraphCoordinateAction,
    OneForm,
    OneFormHodge,
    OrientedEdge,
    PhysicalFlux,
    PhysicalFluxFlatMap,
    VertexHodge,
    VertexScalar,
    reference_pairings,
)
from pygrc.models.grc_v4_profile import GRCV4CommonParams


def graph_payload() -> dict[str, Any]:
    return {
        "schema_version": "grcv4-serialized-graph-v1",
        "live_node_ids": ["b", 1, "1"],
        "oriented_edges": [
            {"edge_id": "z", "tail_node_id": "b", "head_node_id": 1},
            {"edge_id": "a", "tail_node_id": 1, "head_node_id": "1"},
        ],
    }


def common_payload() -> dict[str, Any]:
    return {
        "schema_version": "grcv4-common-params-v1",
        "differential_backend_id": "oriented_incidence_d0_equals_BT_v1",
        "boundary_policy_id": "closed_no_flux_v1",
        "measure_profile_id": "unit_vertex_measure_v1",
        "context_contract_id": "constant_zero_context_v1",
        "units_id": "grcv4_nondimensional_reference_v1",
        "gauge_id": "component_zero_mean_potential_v1",
        "normalization_id": "unnormalized_vertex_stiffness_v1",
        "domain_id": "fixed_graph_strict_gap_spd_v1",
        "default_step_request": None,
    }


def independent_ascii_id(prefix: str, value: object) -> str:
    """For these ASCII, integer-token preimages only; not a general JCS oracle."""
    return (
        prefix
        + ":"
        + sha256(
            json.dumps(
                value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
            ).encode()
        ).hexdigest()
    )


def coordinate_action(graph: GRCV4Graph) -> GraphCoordinateAction:
    # Target vertex order selects old [2,0,1]; target edge order [1,0],
    # with edge 1 reversed. IDs are also relabeled, not sorted or inferred.
    target = GRCV4Graph(
        ("x", "y", "q"),
        (OrientedEdge("new-a", "x", "q"), OrientedEdge("new-z", "y", "q")),
    )
    return GraphCoordinateAction(graph, target, (2, 0, 1), (1, 0), (-1, 1))


def reconstruct(value: dict[str, Any]) -> dict[str, Any]:
    """Portable replay entry used by the retained P9-3.1 evidence inputs."""
    graph = GRCV4Graph.from_payload(value["graph"])
    differential = GRCV4Differential(
        graph, GRCV4CommonParams.from_payload(value["common"])
    )
    hodge = OneFormHodge(graph, value["H1_form"])
    flat = PhysicalFluxFlatMap(hodge)
    flux = PhysicalFlux(graph, value["flux"])
    form = flat.flat(flux)
    return {
        "graph_digest": graph.graph_digest,
        "orientation_identity": graph.orientation_identity,
        "differential_identity": differential.identity,
        "one_form_hodge_identity": hodge.identity,
        "flat_identity": flat.identity,
        "incidence": graph.incidence,
        "d0": differential.d0(VertexScalar(graph, value["scalar"])).values,
        "divergence": differential.divergence(flux).values,
        "flat": form.values,
        "sharp_flat": flat.sharp(form).values,
        "form_pairing": hodge.pair(form, form),
    }


def replay_input() -> dict[str, Any]:
    return {
        "graph": graph_payload(),
        "common": common_payload(),
        "H1_form": [[2, 1], [1, 3]],
        "flux": [3, -2],
        "scalar": [4, 2, 1],
    }


class GraphTests(unittest.TestCase):
    graph: GRCV4Graph
    common: GRCV4CommonParams

    @classmethod
    def setUpClass(cls) -> None:
        cls.graph = GRCV4Graph.from_payload(graph_payload())
        cls.common = GRCV4CommonParams.from_payload(common_payload())

    def test_serialized_order_mixed_ids_and_lookup(self) -> None:
        self.assertEqual(self.graph.live_node_ids, ("b", 1, "1"))
        self.assertEqual(self.graph.live_edge_ids, ("z", "a"))
        self.assertEqual(self.graph.node_index(1), 1)
        self.assertEqual(self.graph.node_index("1"), 2)
        self.assertEqual(self.graph.edge_index("z"), 0)
        self.assertEqual(self.graph.star(1), (0, 1))
        for fn, value in [
            (self.graph.node_index, "absent"),
            (self.graph.edge_index, "absent"),
        ]:
            with self.assertRaises(KeyError):
                fn(value)
        with self.assertRaises(TypeError):
            self.graph.node_index(True)

    def test_graph_digest_has_independent_canonical_preimage(self) -> None:
        self.assertEqual(
            self.graph.graph_digest,
            independent_ascii_id("grc-graph-sha256", graph_payload()),
        )

    def test_orientation_identity_binds_sign_convention_and_order(self) -> None:
        preimage = {
            "descriptor_version": "grcv4-ordered-outward-incidence-v1",
            "graph": graph_payload(),
            "positive_flux": "tail_to_head",
            "incidence_tail": 1,
            "incidence_head": -1,
        }
        self.assertEqual(
            self.graph.orientation_identity,
            independent_ascii_id("grcv4-orientation-sha256", preimage),
        )
        reordered = replace(self.graph, oriented_edges=self.graph.oriented_edges[::-1])
        reversed_edge = replace(
            self.graph.oriented_edges[0], tail_node_id=1, head_node_id="b"
        )
        reversed_graph = replace(
            self.graph, oriented_edges=(reversed_edge, self.graph.oriented_edges[1])
        )
        for graph in [
            reordered,
            reversed_graph,
            replace(self.graph, live_node_ids=(1, "1", "b")),
        ]:
            self.assertNotEqual(self.graph.graph_digest, graph.graph_digest)
            self.assertNotEqual(
                self.graph.orientation_identity, graph.orientation_identity
            )

    def test_detached_mutable_input_and_output(self) -> None:
        source = graph_payload()
        graph = GRCV4Graph.from_payload(source)
        digest = graph.graph_digest
        source["oriented_edges"][0]["edge_id"] = "mutated"
        payload: Any = graph.to_payload()
        payload["live_node_ids"][0] = "changed"
        self.assertEqual(graph.graph_digest, digest)
        with self.assertRaises(TypeError):
            graph._node_index["b"] = 10  # type: ignore[index]
        with self.assertRaises(FrozenInstanceError):
            setattr(graph, "live_node_ids", ())

    def test_direct_construction_copies_ordered_lists(self) -> None:
        nodes: Any = ["a", "b"]
        edges: Any = [OrientedEdge("e", "a", "b")]
        graph = GRCV4Graph(nodes, edges)
        nodes.clear()
        edges.clear()
        self.assertEqual(graph.incidence, ((1.0,), (-1.0,)))

    def test_direct_and_wire_integral_float_ids_agree(self) -> None:
        data = graph_payload()
        data["live_node_ids"][1] = 1.0
        data["oriented_edges"][0]["head_node_id"] = 1.0
        self.assertEqual(GRCV4Graph.from_payload(data), self.graph)
        self.assertIs(type(GRCV4Graph.from_payload(data).live_node_ids[1]), int)
        self.assertEqual(OrientedEdge("e", 1.0, "1"), OrientedEdge("e", 1, "1"))  # type: ignore[arg-type]

    def test_graph_wire_reconstruction_is_explicit(self) -> None:
        raw = json.dumps(graph_payload())
        self.assertEqual(
            GRCV4Graph.from_json(raw, encoding="configuration"), self.graph
        )
        self.assertEqual(
            GRCV4Graph.from_json(
                canonical_json_bytes(graph_payload()), encoding="canonical"
            ),
            self.graph,
        )
        with self.assertRaises(ValueError):
            GRCV4Graph.from_json(raw, encoding="canonical")
        with self.assertRaises(TypeError):
            GRCV4Graph.from_json(raw, encoding="guess")  # type: ignore[arg-type]

    def test_duplicate_edge_missing_endpoint_and_extra_fields_rejected(self) -> None:
        for mutation in ["duplicate", "endpoint", "extra", "duplicate-node"]:
            data = graph_payload()
            if mutation == "duplicate":
                data["oriented_edges"][1]["edge_id"] = "z"
            elif mutation == "endpoint":
                data["oriented_edges"][0]["tail_node_id"] = "not-live"
            elif mutation == "extra":
                data["legacy_slots"] = {}
            else:
                data["live_node_ids"][2] = 1.0
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                GRCV4Graph.from_payload(data)

    def test_bad_node_ids_rejected_before_coercion(self) -> None:
        for value in [
            True,
            False,
            2**53,
            -(2**53),
            float(2**53),
            1.5,
            float("nan"),
            float("inf"),
            -0.0,
            object(),
            np.int64(1),
        ]:
            with (
                self.subTest(value=repr(value)),
                self.assertRaises((TypeError, ValueError)),
            ):
                OrientedEdge("e", value, "b")  # type: ignore[arg-type]
        with self.assertRaises(UnicodeError):
            OrientedEdge("e", "\ud800", "b")

    def test_closed_graph_allows_isolates_parallel_edges_and_loops(self) -> None:
        graph = GRCV4Graph(
            ("u", "v", "isolated"),
            (
                OrientedEdge("e0", "u", "v"),
                OrientedEdge("e1", "u", "v"),
                OrientedEdge("loop", "v", "v"),
            ),
        )
        self.assertEqual(graph.incidence, ((1, 1, 0), (-1, -1, 0), (0, 0, 0)))
        self.assertEqual(graph.star("v"), (0, 1, 2))
        self.assertEqual(graph.star("isolated"), ())
        diff = GRCV4Differential(graph, self.common)
        self.assertEqual(diff.d0(VertexScalar(graph, (5, 2, 100))).values, (3, 3, 0))
        self.assertEqual(
            diff.divergence(PhysicalFlux(graph, (2, -1, 100))).values, (1, -1, 0)
        )

    def test_empty_spaces_have_explicit_zero_maps(self) -> None:
        for nodes in [(), ("isolated",)]:
            graph = GRCV4Graph(nodes, ())
            diff = GRCV4Differential(graph, self.common)
            self.assertEqual(
                diff.divergence(PhysicalFlux(graph, ())).values, (0,) * len(nodes)
            )
            self.assertEqual(diff.d0(VertexScalar(graph, (4,) * len(nodes))).values, ())
            self.assertEqual(
                PhysicalFluxFlatMap(OneFormHodge(graph, ()))
                .flat(PhysicalFlux(graph, ()))
                .values,
                (),
            )

    def test_differential_and_divergence_independent_expected(self) -> None:
        diff = GRCV4Differential(self.graph, self.common)
        self.assertEqual(self.graph.incidence, ((1, 0), (-1, 1), (0, -1)))
        self.assertEqual(diff.d0(VertexScalar(self.graph, (4, 2, 1))).values, (2, 1))
        self.assertEqual(
            diff.divergence(PhysicalFlux(self.graph, (3, -2))).values, (3, -5, 2)
        )
        self.assertEqual(diff.d0(VertexScalar(self.graph, (7, 7, 7))).values, (0, 0))

    def test_discrete_unweighted_adjoint_identity(self) -> None:
        diff = GRCV4Differential(self.graph, self.common)
        scalar = VertexScalar(self.graph, (4, 2, 1))
        flux = PhysicalFlux(self.graph, (3, -2))
        left = sum(x * y for x, y in zip(scalar.values, diff.divergence(flux).values))
        right = sum(x * y for x, y in zip(diff.d0(scalar).values, flux.values))
        self.assertEqual(left, 4)
        self.assertEqual(left, right)

    def test_differential_identity_is_reconstructible_and_context_bound(self) -> None:
        diff = GRCV4Differential(self.graph, self.common)
        preimage = {
            "descriptor_version": "grcv4-incidence-differential-v1",
            "graph_digest": self.graph.graph_digest,
            "orientation_identity": self.graph.orientation_identity,
            "common": common_payload(),
        }
        self.assertEqual(
            diff.identity, independent_ascii_id("grcv4-differential-sha256", preimage)
        )
        for field in [
            "measure_profile_id",
            "context_contract_id",
            "normalization_id",
            "units_id",
        ]:
            changes: dict[str, Any] = {field: "different_declared_identity"}
            common = replace(self.common, **changes)
            self.assertNotEqual(
                diff.identity, GRCV4Differential(self.graph, common).identity
            )

    def test_unknown_backend_or_boundary_is_not_an_alias(self) -> None:
        for field, value in [
            ("differential_backend_id", "grc_v3_ego_frame_v1"),
            ("differential_backend_id", "nine_port_rows"),
            ("boundary_policy_id", "open_external_flux"),
        ]:
            with self.assertRaisesRegex(ValueError, "unimplemented"):
                changes: dict[str, Any] = {field: value}
                GRCV4Differential(self.graph, replace(self.common, **changes))

    def test_coordinate_type_and_graph_are_load_bearing(self) -> None:
        diff = GRCV4Differential(self.graph, self.common)
        with self.assertRaises(TypeError):
            diff.divergence(OneForm(self.graph, (1, 2)))  # type: ignore[arg-type]
        other = replace(self.graph, oriented_edges=self.graph.oriented_edges[::-1])
        with self.assertRaises(ValueError):
            diff.divergence(PhysicalFlux(other, (1, 2)))
        with self.assertRaises(ValueError):
            OneForm(self.graph, (1,))
        self.assertNotEqual(
            OneForm(self.graph, (1, 2)), PhysicalFlux(self.graph, (1, 2))
        )


class PairingTests(unittest.TestCase):
    graph: GRCV4Graph
    hodge: OneFormHodge

    @classmethod
    def setUpClass(cls) -> None:
        cls.graph = GRCV4Graph.from_payload(graph_payload())
        cls.hodge = OneFormHodge(cls.graph, ((2, 1), (1, 3)))

    def test_nonidentity_flat_rational_inverse(self) -> None:
        # [[2,1],[1,3]]^-1 [3,-2] = [11/5,-7/5].
        flat = PhysicalFluxFlatMap(self.hodge)
        form = flat.flat(PhysicalFlux(self.graph, (3, -2)))
        for actual, expected in zip(form.values, (Fraction(11, 5), Fraction(-7, 5))):
            self.assertAlmostEqual(actual, float(expected), delta=2e-15)
        for actual, component in zip(flat.sharp(form).values, (3, -2)):
            self.assertAlmostEqual(actual, component, delta=2e-15)
        self.assertAlmostEqual(
            self.hodge.pair(form, form), float(Fraction(47, 5)), delta=4e-15
        )
        self.assertNotEqual(form.values, (3, -2))

    def test_pairings_are_distinct_and_nonunit(self) -> None:
        pairings = reference_pairings(
            self.graph, vertex_measure=(2, 3, 4), reference_edge_weights=(2, 5)
        )
        self.assertEqual(
            pairings.vertex.pair(
                VertexScalar(self.graph, (1, 2, -1)),
                VertexScalar(self.graph, (2, -1, 3)),
            ),
            -14,
        )
        self.assertEqual(
            pairings.one_form.pair(
                OneForm(self.graph, (2, 1)), OneForm(self.graph, (1, 3))
            ),
            19,
        )
        self.assertEqual(
            pairings.flat_map.flat(PhysicalFlux(self.graph, (4, 10))).values, (2, 2)
        )

    def test_same_numbers_do_not_substitute_types(self) -> None:
        loop_graph = GRCV4Graph(("u",), (OrientedEdge("loop", "u", "u"),))
        h0 = VertexHodge(loop_graph, ((2,),))
        h1 = OneFormHodge(loop_graph, ((2,),))
        self.assertNotEqual(h0, h1)
        self.assertNotEqual(h0.identity, h1.identity)
        with self.assertRaises(TypeError):
            PhysicalFluxFlatMap(h0)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            h1.pair(PhysicalFlux(loop_graph, (1,)), OneForm(loop_graph, (1,)))  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            PhysicalFluxFlatMap(h1).sharp(PhysicalFlux(loop_graph, (1,)))  # type: ignore[arg-type]

    def test_hodge_identity_binds_every_entry_and_map_role(self) -> None:
        different = OneFormHodge(self.graph, ((2, 0.5), (0.5, 3)))
        self.assertNotEqual(self.hodge.identity, different.identity)
        self.assertNotEqual(
            self.hodge.identity, PhysicalFluxFlatMap(self.hodge).identity
        )
        # Independently spell integer-token preimage, using no numerical implementation.
        payload = {
            "descriptor_version": "grcv4-typed-pairing-v1",
            "kind": "OneFormHodge",
            "graph_digest": self.graph.graph_digest,
            "orientation_identity": self.graph.orientation_identity,
            "matrix": [[2, 1], [1, 3]],
        }
        self.assertEqual(
            self.hodge.identity, independent_ascii_id("grcv4-pairing-sha256", payload)
        )

    def test_wrong_graph_flat_sharp_and_pairing_rejected(self) -> None:
        graph = replace(self.graph, oriented_edges=self.graph.oriented_edges[::-1])
        flat = PhysicalFluxFlatMap(self.hodge)
        with self.assertRaises(ValueError):
            flat.flat(PhysicalFlux(graph, (1, 2)))
        with self.assertRaises(ValueError):
            flat.sharp(OneForm(graph, (1, 2)))
        with self.assertRaises(ValueError):
            self.hodge.pair(OneForm(self.graph, (1, 2)), OneForm(graph, (1, 2)))
        with self.assertRaises(ValueError):
            GRCV4Pairings(
                VertexHodge(graph, ((1, 0, 0), (0, 1, 0), (0, 0, 1))), self.hodge
            )

    def test_shape_nonfinite_asymmetric_and_non_spd_rejected(self) -> None:
        matrices = [
            [],
            [[1]],
            [[1, 0], [0]],
            [[1, 0], [0, 0]],
            [[1, 2], [2, 1]],
            [[1, 0.5], [0.25, 1]],
            [[1, float("nan")], [0, 1]],
            [[float("inf"), 0], [0, 1]],
            [[1, -0.0], [0, 1]],
            [[True, 0], [0, 1]],
            [[2**53, 0], [0, 1]],
        ]
        for matrix in matrices:
            with (
                self.subTest(matrix=matrix),
                self.assertRaises((TypeError, ValueError)),
            ):
                OneFormHodge(self.graph, matrix)  # type: ignore[arg-type]

    def test_numeric_arrays_are_detached_and_bad_dtypes_rejected(self) -> None:
        storage = np.array([[2.0, 1.0], [1.0, 3.0]])
        vector = np.array([2.0, 4.0])
        hodge = OneFormHodge(self.graph, storage)  # type: ignore[arg-type]
        form = OneForm(self.graph, vector[::-1])  # type: ignore[arg-type]
        storage[:] = 100
        vector[:] = 100
        self.assertEqual(hodge.matrix, ((2, 1), (1, 3)))
        self.assertEqual(form.values, (4, 2))
        copy = np.asarray(hodge.matrix)
        copy[:] = 0
        self.assertEqual(hodge.matrix, ((2, 1), (1, 3)))
        for dtype in [object, bool, complex]:
            with self.assertRaises(TypeError):
                OneFormHodge(self.graph, np.eye(2, dtype=dtype))  # type: ignore[arg-type]
        for value in [np.eye(2), {1, 2}, iter([1, 2]), "12", np.array([True, False])]:
            with self.assertRaises(TypeError):
                OneForm(self.graph, value)  # type: ignore[arg-type]

    def test_nonfinite_arithmetic_fails_without_regularization(self) -> None:
        huge = OneFormHodge(self.graph, ((1e308, 0), (0, 1)))
        with self.assertRaisesRegex(ValueError, "nonfinite"):
            PhysicalFluxFlatMap(huge).sharp(OneForm(self.graph, (2, 1)))
        small = OneFormHodge(self.graph, ((1e-308, 0), (0, 1)))
        with self.assertRaisesRegex(ValueError, "nonfinite"):
            PhysicalFluxFlatMap(small).flat(PhysicalFlux(self.graph, (10, 1)))

    def test_arithmetic_zero_is_canonical_but_input_negative_zero_rejected(
        self,
    ) -> None:
        value = PhysicalFluxFlatMap(OneFormHodge(self.graph, ((2, 0), (0, 3)))).sharp(
            OneForm(self.graph, (0, -1))
        )
        self.assertEqual(math.copysign(1, value.values[0]), 1)
        with self.assertRaises(ValueError):
            PhysicalFlux(self.graph, (-0.0, 1))

    def test_missing_numpy_dependency_reports_v4_extra(self) -> None:
        with patch(
            "pygrc.models.grc_v4_codec.importlib.import_module", side_effect=ImportError
        ):
            with self.assertRaisesRegex(V4DependencyError, r"pygrc\[v4\]"):
                OneFormHodge(self.graph, ((2, 1), (1, 3)))


class CovarianceTests(unittest.TestCase):
    graph: GRCV4Graph
    action: GraphCoordinateAction
    common: GRCV4CommonParams

    @classmethod
    def setUpClass(cls) -> None:
        cls.graph = GRCV4Graph.from_payload(graph_payload())
        cls.action = coordinate_action(cls.graph)
        cls.common = GRCV4CommonParams.from_payload(common_payload())

    def test_signed_incidence_differential_and_divergence(self) -> None:
        action = self.action
        self.assertEqual(action.target.incidence, ((1, 0), (0, 1), (-1, -1)))
        source = GRCV4Differential(self.graph, self.common)
        target = GRCV4Differential(action.target, self.common)
        scalar = VertexScalar(self.graph, (4, 2, 1))
        flux = PhysicalFlux(self.graph, (3, -2))
        self.assertEqual(
            target.d0(action.vertex_scalar(scalar)), action.one_form(source.d0(scalar))
        )
        self.assertEqual(
            target.divergence(action.physical_flux(flux)),
            action.vertex_scalar(source.divergence(flux)),
        )

    def test_signed_nonidentity_hodge_flat_sharp_covariance(self) -> None:
        hodge = OneFormHodge(self.graph, ((2, 1), (1, 3)))
        transformed = self.action.one_form_hodge(hodge)
        self.assertEqual(transformed.matrix, ((3, -1), (-1, 2)))
        flux = PhysicalFlux(self.graph, (3, -2))
        original_form = PhysicalFluxFlatMap(hodge).flat(flux)
        transformed_form = PhysicalFluxFlatMap(transformed).flat(
            self.action.physical_flux(flux)
        )
        for actual, expected in zip(
            transformed_form.values, self.action.one_form(original_form).values
        ):
            self.assertAlmostEqual(actual, expected, delta=2e-15)
        self.assertAlmostEqual(
            hodge.pair(original_form, original_form),
            transformed.pair(transformed_form, transformed_form),
            delta=4e-15,
        )
        self.assertEqual(
            self.action.physical_flux(
                PhysicalFluxFlatMap(hodge).sharp(OneForm(self.graph, (2, -1)))
            ),
            PhysicalFluxFlatMap(transformed).sharp(
                self.action.one_form(OneForm(self.graph, (2, -1)))
            ),
        )

    def test_dense_vertex_pairing_covariance(self) -> None:
        hodge = VertexHodge(self.graph, ((2, 1, 0), (1, 3, 0), (0, 0, 4)))
        transformed = self.action.vertex_hodge(hodge)
        self.assertEqual(transformed.matrix, ((4, 0, 0), (0, 2, 1), (0, 1, 3)))
        x = VertexScalar(self.graph, (1, 2, -1))
        self.assertEqual(
            hodge.pair(x, x),
            transformed.pair(
                self.action.vertex_scalar(x), self.action.vertex_scalar(x)
            ),
        )

    def test_invalid_permutations_signs_and_topology_changes_rejected(self) -> None:
        mutations: list[dict[str, Any]] = [
            {"vertex_permutation": (0, 0, 1)},
            {"edge_permutation": (0,)},
            {"edge_permutation": (True, 0)},
            {"edge_signs": (0, 1)},
            {"edge_signs": (-1.0, 1)},
            {"edge_signs": (1, 1)},
            {"target": self.graph},
        ]
        for changes in mutations:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                replace(self.action, **changes)
        with self.assertRaises(TypeError):
            self.action.one_form(PhysicalFlux(self.graph, (1, 2)))  # type: ignore[arg-type]


class ReconstructionTests(unittest.TestCase):
    def test_replay_across_hash_seeds_outside_checkout(self) -> None:
        # Copy only the replay test module and data; pygrc must resolve from the
        # installed environment without cwd/PYTHONPATH repository assistance.
        expected = json.dumps(reconstruct(replay_input()), sort_keys=True)
        with tempfile.TemporaryDirectory(prefix="p931-reconstruct-") as tmp:
            directory = Path(tmp)
            script = directory / "replay.py"
            script.write_bytes(Path(__file__).read_bytes())
            payload = directory / "inputs.json"
            payload.write_text(json.dumps(replay_input()))
            for seed in ["0", "113", "987654"]:
                environment = dict(os.environ, PYTHONHASHSEED=seed)
                environment.pop("PYTHONPATH", None)
                result = subprocess.run(
                    [sys.executable, str(script), "--reconstruct", str(payload)],
                    cwd=directory,
                    env=environment,
                    text=True,
                    capture_output=True,
                    check=True,
                )
                self.assertEqual(result.stdout.strip(), expected)

    @unittest.skipUnless(
        os.environ.get("GRCV4_PACKAGE_TESTS") == "1",
        "opt-in clean wheel/sdist primitive reconstruction",
    )
    def test_clean_installed_wheel_and_sdist_primitives(self) -> None:
        """Exercise the new modules, assets and declared extra away from source."""
        from tests.models.test_grc_v4_transport import a_params, c_payload

        root = Path(__file__).resolve().parents[2]
        wheelhouse = Path(os.environ["GRCV4_WHEELHOUSE"]).resolve()
        environment = {
            k: v for k, v in os.environ.items() if k not in {"PYTHONPATH", "PYTHONHOME"}
        }
        source_paths = [
            "src/pygrc/models/grc_v4_geometry.py",
            "src/pygrc/models/grc_v4_transport.py",
        ]
        supplied = {
            **replay_input(),
            "a_params": a_params().to_payload(),
            "c_params": c_payload(),
            "source_hashes": {
                Path(name).stem: sha256((root / name).read_bytes()).hexdigest()
                for name in source_paths
            },
        }
        consumer = """
import hashlib, importlib, importlib.metadata, json, pathlib, sys
from pygrc.models.grc_v4_geometry import GRCV4Graph, OrientedEdge, OneForm, OneFormHodge, VertexHodge, PhysicalFlux, PhysicalFluxFlatMap
from pygrc.models.grc_v4_profile import CandidateAParams, CandidateCParams, list_supported_profiles
from pygrc.models.grc_v4_transport import CandidateAMobility, CandidateCMobility
data=json.load(sys.stdin)
for name, expected in data['source_hashes'].items():
    module=importlib.import_module('pygrc.models.'+name)
    location=pathlib.Path(module.__file__).resolve()
    assert location.is_relative_to(pathlib.Path(sys.prefix).resolve()), str(location)
    assert hashlib.sha256(location.read_bytes()).hexdigest()==expected
assert any(r.startswith('numpy==2.4.6') and 'v4' in r for r in importlib.metadata.requires('pygrc'))
graph=GRCV4Graph.from_payload(data['graph'])
flat=PhysicalFluxFlatMap(OneFormHodge(graph,data['H1_form']))
form=flat.flat(PhysicalFlux(graph,data['flux']))
a=CandidateAMobility(graph,CandidateAParams.from_payload(data['a_params']),(3,7))
c=CandidateCMobility(graph,CandidateCParams.from_payload(data['c_params']))
assert not list_supported_profiles()
boundary_graph=GRCV4Graph(('u','v'),(OrientedEdge('a','u','v'),OrientedEdge('b','u','v')))
import math
for constructor in (OneFormHodge,VertexHodge):
    for last in (2.,math.nextafter(2.,0.)):
        for matrix in (((2.,2.),(2.,last)),((last,2.),(2.,2.))):
            try: constructor(boundary_graph,matrix)
            except ValueError: pass
            else: raise AssertionError('installed nonpositive Hodge accepted')
    constructor(boundary_graph,((2.,2.),(2.,math.nextafter(2.,math.inf))))
for scale in (float.fromhex('0x0.0000000000001p-1022'),1e-308,1.,1e308):
    positive=OneFormHodge(boundary_graph,((scale,0.),(0.,scale)))
    assert PhysicalFluxFlatMap(positive).flat(PhysicalFlux(boundary_graph,(scale,scale))).values==(1.,1.)
print(json.dumps({'flat':form.values,'sharp_flat':flat.sharp(form).values,
                  'A':a.apply(OneForm(graph,(2,-3))).values,
                  'C':c.apply(OneForm(graph,(2,-3))).values}))
"""
        with tempfile.TemporaryDirectory(prefix="grcv4-p931-package-") as scratch:
            temporary = Path(scratch)
            source = temporary / "source"
            source.mkdir()
            shutil.copytree(
                root / "src",
                source / "src",
                ignore=shutil.ignore_patterns("__pycache__", "*.egg-info"),
            )
            for filename in ["pyproject.toml", "README.md", "LICENSE"]:
                shutil.copyfile(root / filename, source / filename)

            def run(command: list[str], cwd: Path, stdin: str | None = None) -> str:
                result = subprocess.run(
                    command,
                    cwd=cwd,
                    env=environment,
                    input=stdin,
                    text=True,
                    capture_output=True,
                    timeout=240,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                return result.stdout

            dist = temporary / "dist"
            run(
                [
                    sys.executable,
                    "-m",
                    "build",
                    "--no-isolation",
                    "--outdir",
                    str(dist),
                ],
                source,
            )
            for archive in [next(dist.glob("*.whl")), next(dist.glob("*.tar.gz"))]:
                with self.subTest(archive=archive.name):
                    isolated = temporary / (archive.name + "-env")
                    venv.EnvBuilder(with_pip=True).create(isolated)
                    python = isolated / "bin/python"
                    outside = temporary / (archive.name + "-consumer")
                    outside.mkdir()
                    run(
                        [
                            str(python),
                            "-m",
                            "pip",
                            "install",
                            "--no-index",
                            "--find-links",
                            str(wheelhouse),
                            str(archive) + "[v4]",
                        ],
                        outside,
                    )
                    result = json.loads(
                        run(
                            [str(python), "-I", "-c", consumer],
                            outside,
                            json.dumps(supplied),
                        )
                    )
                    self.assertEqual(result["A"], [12, -42])
                    self.assertEqual(result["C"], [12, -45])
                    for actual, expected in zip(result["flat"], [11 / 5, -7 / 5]):
                        self.assertAlmostEqual(actual, expected, delta=2e-15)
                    for actual, expected in zip(result["sharp_flat"], [3, -2]):
                        self.assertAlmostEqual(actual, expected, delta=2e-15)
                    run([str(python), "-m", "pip", "check"], outside)


class OutlierTests(unittest.TestCase):
    @staticmethod
    def rational_solve(matrix: list[list[int]], rhs: list[int]) -> list[Fraction]:
        # Independent exact Gaussian elimination; no production/NumPy solver.
        size = len(rhs)
        rows = [
            [Fraction(x) for x in row] + [Fraction(value)]
            for row, value in zip(matrix, rhs)
        ]
        for column in range(size):
            pivot = rows[column][column]
            rows[column] = [x / pivot for x in rows[column]]
            for i in range(size):
                if i != column:
                    gain = rows[i][column]
                    rows[i] = [x - gain * y for x, y in zip(rows[i], rows[column])]
        return [row[-1] for row in rows]

    def test_seeded_dense_spd_against_exact_rational_oracle(self) -> None:
        import random

        generator = random.Random(931)
        for size in range(1, 7):
            graph = GRCV4Graph(
                ("u", "v", "isolated"),
                tuple(OrientedEdge(f"parallel-{i}", "u", "v") for i in range(size)),
            )
            for case in range(4):
                raw = [
                    [generator.randint(-3, 3) for _ in range(size)] for _ in range(size)
                ]
                matrix = [
                    [
                        sum(raw[k][i] * raw[k][j] for k in range(size)) + int(i == j)
                        for j in range(size)
                    ]
                    for i in range(size)
                ]
                rhs = [generator.randint(-17, 17) for _ in range(size)]
                expected = self.rational_solve(matrix, rhs)
                with self.subTest(dimension=size, case=case):
                    result = PhysicalFluxFlatMap(OneFormHodge(graph, matrix)).flat(  # type: ignore[arg-type]
                        PhysicalFlux(graph, tuple(rhs))
                    )
                    for actual, exact in zip(result.values, expected):
                        target = float(exact)
                        self.assertAlmostEqual(
                            actual, target, delta=4e-14 + 2e-14 * abs(target)
                        )

    def test_all_48_small_signed_coordinate_actions(self) -> None:
        import itertools

        graph = GRCV4Graph.from_payload(graph_payload())
        common = GRCV4CommonParams.from_payload(common_payload())
        scalar = VertexScalar(graph, (4, -2, 1))
        flux = PhysicalFlux(graph, (3, -2))
        source_diff = GRCV4Differential(graph, common)
        target_ids = ("renamed", "", 2**53 - 1)
        for p in itertools.permutations(range(3)):
            source_to_target = {old: target_ids[new] for new, old in enumerate(p)}
            for u in itertools.permutations(range(2)):
                for signs in itertools.product((-1, 1), repeat=2):
                    edges = []
                    for i, old in enumerate(u):
                        edge = graph.oriented_edges[old]
                        tail, head = (
                            graph.node_index(edge.tail_node_id),
                            graph.node_index(edge.head_node_id),
                        )
                        if signs[i] == -1:
                            tail, head = head, tail
                        edges.append(
                            OrientedEdge(
                                f"renamed-{i}",
                                source_to_target[tail],
                                source_to_target[head],
                            )
                        )
                    target = GRCV4Graph(target_ids, tuple(edges))
                    action = GraphCoordinateAction(graph, target, p, u, signs)
                    with self.subTest(vertices=p, edges=u, signs=signs):
                        expected = tuple(
                            tuple(
                                graph.incidence[p[i]][u[j]] * signs[j] for j in range(2)
                            )
                            for i in range(3)
                        )
                        self.assertEqual(target.incidence, expected)
                        diff = GRCV4Differential(target, common)
                        self.assertEqual(
                            diff.d0(action.vertex_scalar(scalar)),
                            action.one_form(source_diff.d0(scalar)),
                        )
                        self.assertEqual(
                            diff.divergence(action.physical_flux(flux)),
                            action.vertex_scalar(source_diff.divergence(flux)),
                        )

    def test_empty_numeric_buffers_preserve_declared_shape(self) -> None:
        graph = GRCV4Graph((), ())
        for shape in [(0, 1), (0, 7), (1, 0), (2, 0), (0, 0, 0)]:
            with self.subTest(shape=shape), self.assertRaises((TypeError, ValueError)):
                OneFormHodge(graph, np.empty(shape))  # type: ignore[arg-type]
        self.assertEqual(OneFormHodge(graph, np.empty((0, 0))).matrix, ())  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            OneFormHodge(graph, np.empty((0, 0), dtype=object))  # type: ignore[arg-type]

    def test_extreme_safe_ids_empty_strings_and_unicode_remain_distinct(self) -> None:
        nodes = (0, 2**53 - 1, -(2**53 - 1), "", "e\u0301", "é", "🧭")
        graph = GRCV4Graph(nodes, (OrientedEdge("edge\n🧭", "e\u0301", "é"),))
        reconstructed = GRCV4Graph.from_json(
            canonical_json_bytes(graph.to_payload()), encoding="canonical"
        )
        self.assertEqual(reconstructed, graph)
        self.assertNotEqual(graph.node_index("e\u0301"), graph.node_index("é"))
        self.assertEqual(graph.star(""), ())
        self.assertEqual(graph.incidence[-3:-1], ((1,), (-1,)))

    def test_duplicate_wire_keys_and_unsafe_numeric_tokens_fail(self) -> None:
        raw = json.dumps(graph_payload())
        duplicate = raw.replace(
            '"live_node_ids":', '"live_node_ids":[],"live_node_ids":', 1
        )
        with self.assertRaises(ValueError):
            GRCV4Graph.from_json(duplicate, encoding="configuration")
        for token in ["9007199254740992", "1e100", "1e-400", "-0"]:
            value = raw.replace('["b", 1, "1"]', '["b", ' + token + ', "1"]')
            with self.subTest(token=token), self.assertRaises(ValueError):
                GRCV4Graph.from_json(value, encoding="configuration")

    def test_power_of_two_dynamic_range_has_exact_inverse_action(self) -> None:
        graph = GRCV4Graph.from_payload(graph_payload())
        hodge = OneFormHodge(graph, ((2.0**-500, 0), (0, 2.0**500)))
        flat = PhysicalFluxFlatMap(hodge)
        flux = PhysicalFlux(graph, (2.0**-498, 2.0**499))
        self.assertEqual(flat.flat(flux).values, (4, 0.5))
        self.assertEqual(flat.sharp(OneForm(graph, (4, 0.5))), flux)
        # This exercises a pure factor; it is not conditioning-domain admission.

    def test_scaled_singular_and_indefinite_inputs_fail_closed(self) -> None:
        graph = GRCV4Graph.from_payload(graph_payload())
        for scale in [1e-308, 2.0**-500, 1.0, 2.0**500, 1e308]:
            for matrix in [((scale, scale), (scale, scale)), ((scale, 0), (0, -scale))]:
                with self.subTest(matrix=matrix), self.assertRaises(ValueError):
                    OneFormHodge(graph, matrix)

    def test_noncontiguous_unsigned_matrix_input_checks_exact_integer_range(
        self,
    ) -> None:
        graph = GRCV4Graph.from_payload(graph_payload())
        unsafe = np.array([[2**64 - 1, 0], [0, 1]], dtype=np.uint64)
        with self.assertRaises(ValueError):
            OneFormHodge(graph, unsafe[::-1, ::-1])  # type: ignore[arg-type]
        valid = np.array([[3, 1], [1, 2]], dtype=np.int64)
        valid_view: Any = valid[::-1, ::-1]
        self.assertEqual(OneFormHodge(graph, valid_view).matrix, ((2, 1), (1, 3)))

    def test_rejected_primitive_calls_preserve_all_supplied_buffers(self) -> None:
        graph = GRCV4Graph.from_payload(graph_payload())
        matrix = np.array([[2.0, 1.0], [0.0, 3.0]])
        before = matrix.tobytes(), graph.to_payload(), graph.orientation_identity
        with self.assertRaises(ValueError):
            OneFormHodge(graph, matrix)  # type: ignore[arg-type]
        self.assertEqual(
            (matrix.tobytes(), graph.to_payload(), graph.orientation_identity), before
        )
        common = GRCV4CommonParams.from_payload(common_payload())
        scalar = VertexScalar(graph, (1e308, -1e308, 0))
        with self.assertRaisesRegex(ValueError, "nonfinite"):
            GRCV4Differential(graph, common).d0(scalar)
        self.assertEqual(scalar.values, (1e308, -1e308, 0))


class ExactPositiveDomainTests(unittest.TestCase):
    @staticmethod
    def graph(size: int) -> GRCV4Graph:
        # Equal vertex/form dimensions exercise both public Hodge constructors.
        return GRCV4Graph(
            tuple(range(size)),
            tuple(OrientedEdge(f"edge-{i}", 0, size - 1) for i in range(size)),
        )

    @staticmethod
    def determinant(matrix: tuple[tuple[float, ...], ...]) -> Fraction:
        # Independent Leibniz expansion. No elimination, NumPy or production
        # positivity helper participates in this small-dimensional oracle.
        import itertools

        result = Fraction(0)
        size = len(matrix)
        for order in itertools.permutations(range(size)):
            inversions = sum(
                order[i] > order[j] for i in range(size) for j in range(i + 1, size)
            )
            product = Fraction((-1) ** inversions)
            for i, j in enumerate(order):
                product *= Fraction(matrix[i][j])
            result += product
        return result

    def check_admission(
        self, graph: GRCV4Graph, matrix: tuple[tuple[float, ...], ...], positive: bool
    ) -> None:
        for constructor in (OneFormHodge, VertexHodge):
            with self.subTest(constructor=constructor.__name__):
                if positive:
                    hodge = constructor(graph, matrix)
                    self.assertEqual(hodge.matrix, matrix)
                else:
                    with self.assertRaisesRegex(ValueError, "positive definite"):
                        constructor(graph, matrix)

    def test_literal_audit_boundary_both_types_and_signed_orders(self) -> None:
        import itertools

        graph = self.graph(2)
        for lower_right in (
            math.nextafter(2.0, 0.0),
            2.0,
            math.nextafter(2.0, math.inf),
        ):
            matrix = ((2.0, 2.0), (2.0, lower_right))
            positive = self.determinant(matrix) > 0
            for order in ((0, 1), (1, 0)):
                for signs in itertools.product((-1, 1), repeat=2):
                    moved = tuple(
                        tuple(
                            signs[i] * signs[j] * matrix[a][b]
                            for j, b in enumerate(order)
                        )
                        for i, a in enumerate(order)
                    )
                    with self.subTest(
                        entry=lower_right.hex(), order=order, signs=signs
                    ):
                        self.check_admission(graph, moved, positive)

    def test_exact_nonpositive_scale_family_in_both_orders(self) -> None:
        graph = self.graph(2)
        scales = [float(k) for k in range(1, 65)] + [
            2.0**e for e in (-900, -500, -100, 100, 500, 900)
        ]
        for scale in scales:
            for neighbor in (scale, math.nextafter(scale, 0.0)):
                matrix = ((scale, scale), (scale, neighbor))
                self.assertLessEqual(self.determinant(matrix), 0)
                for order in ((0, 1), (1, 0)):
                    moved = tuple(tuple(matrix[i][j] for j in order) for i in order)
                    with self.subTest(
                        scale=scale.hex(), neighbor=neighbor.hex(), order=order
                    ):
                        self.check_admission(graph, moved, False)

    def test_three_dimensional_exhaustive_leibniz_oracle(self) -> None:
        import itertools

        graph = self.graph(3)
        # 4**6 symmetric integer matrices; includes positive determinant with
        # two negative directions, zero early pivots and zero final pivots.
        for a, b, c, d, e, f in itertools.product((-1.0, 0.0, 1.0, 2.0), repeat=6):
            matrix = ((a, d, e), (d, b, f), (e, f, c))
            positive = all(
                self.determinant(tuple(tuple(row[:k]) for row in matrix[:k])) > 0
                for k in (1, 2, 3)
            )
            with self.subTest(matrix=matrix):
                self.check_admission(graph, matrix, positive)

    def test_general_dimensional_inertia_by_explicit_congruence(self) -> None:
        # H=L diag(d) L.T, L unit lower triangular. This known invertible
        # congruence supplies the expected inertia without any determinant or
        # numerical eigensolver. Entries/scalings remain exactly representable.
        for size in range(3, 9):
            graph = self.graph(size)
            for ending in ((4, 4), (4, 0), (4, -1), (-1, -1)):
                diagonal = (4,) * (size - 2) + ending
                base = tuple(
                    tuple(sum(diagonal[: min(i, j) + 1]) for j in range(size))
                    for i in range(size)
                )
                positive = all(x > 0 for x in diagonal)
                for exponent in (-900, -100, 0, 100, 900):
                    for order in (
                        tuple(range(size)),
                        tuple(reversed(range(size))),
                        tuple(range(1, size)) + (0,),
                    ):
                        moved = tuple(
                            tuple(
                                math.ldexp(
                                    float(base[i][j] * (-1) ** (a + b)), exponent
                                )
                                for b, j in enumerate(order)
                            )
                            for a, i in enumerate(order)
                        )
                        with self.subTest(
                            size=size, ending=ending, scale=exponent, order=order
                        ):
                            self.check_admission(graph, moved, positive)

    def test_positive_scaled_identity_controls_survive(self) -> None:
        scales = (
            float.fromhex("0x0.0000000000001p-1022"),
            1e-308,
            2.0**-500,
            1.0,
            2.0**500,
            1e308,
        )
        for size in (1, 2):
            graph = self.graph(size)
            for scale in scales:
                matrix = tuple(
                    tuple(scale if i == j else 0.0 for j in range(size))
                    for i in range(size)
                )
                with self.subTest(size=size, scale=scale.hex()):
                    self.check_admission(graph, matrix, True)
                    flat = PhysicalFluxFlatMap(OneFormHodge(graph, matrix))
                    self.assertEqual(
                        flat.flat(PhysicalFlux(graph, (scale,) * size)).values,
                        (1,) * size,
                    )

    def test_non_diagonal_mixed_dyadic_denominators(self) -> None:
        graph = self.graph(3)
        # Exact diagonal congruence of an SPD matrix with diagonal 1 and
        # neighboring off-diagonals 1/4. Global binary64 exponent range is wide.
        matrix = (
            (2.0**-1000, 2.0**-502, 0.0),
            (2.0**-502, 1.0, 2.0**498),
            (0.0, 2.0**498, 2.0**1000),
        )
        self.assertGreater(self.determinant(matrix), 0)
        for order in ((0, 1, 2), (2, 1, 0), (1, 2, 0)):
            moved = tuple(tuple(matrix[i][j] for j in order) for i in order)
            self.check_admission(graph, moved, True)

    def test_cholesky_return_or_exception_cannot_decide_positivity(self) -> None:
        graph = self.graph(2)
        for effect in (None, np.linalg.LinAlgError("audit numerical uncertainty")):
            with patch.object(np.linalg, "cholesky", side_effect=effect):
                self.check_admission(graph, ((2.0, 2.0), (2.0, 2.0)), False)
                self.check_admission(graph, ((2.0, 1.0), (1.0, 3.0)), True)

    def test_regression_detects_restoration_of_the_old_screen(self) -> None:
        from pygrc.models import grc_v4_geometry as geometry

        def old_screen(matrix: tuple[tuple[float, ...], ...]) -> None:
            np.linalg.cholesky(np.array(matrix))

        # Simulate the native audit's completed factorization deterministically:
        # a different BLAS may already reject this witness. The public rejection
        # assertion must catch the old screen accepting a returned factor.
        with (
            patch.object(geometry, "_require_positive_definite", old_screen),
            patch.object(np.linalg, "cholesky", return_value=np.eye(2)),
        ):
            with self.assertRaises(AssertionError):
                with self.assertRaises(ValueError):
                    OneFormHodge(self.graph(2), ((2.0, 2.0), (2.0, 2.0)))

    def test_rejection_preserves_original_matrix_and_graph(self) -> None:
        graph = self.graph(2)
        for array in (
            np.array([[2.0, 2.0], [2.0, 2.0]]),
            np.array([[2.0, 2.0], [2.0, math.nextafter(2.0, 0.0)]]),
        ):
            before = array.tobytes(), graph.to_payload(), graph.orientation_identity
            for constructor in (OneFormHodge, VertexHodge):
                with self.assertRaises(ValueError):
                    constructor(graph, array)  # type: ignore[arg-type]
                self.assertEqual(
                    (array.tobytes(), graph.to_payload(), graph.orientation_identity),
                    before,
                )


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--reconstruct":
        print(
            json.dumps(
                reconstruct(json.loads(Path(sys.argv[2]).read_text())), sort_keys=True
            )
        )
    else:
        unittest.main()

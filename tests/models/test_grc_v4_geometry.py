"""P9-3.1/P9-3.2 independent geometry and stage-cache witnesses.

Expected matrices and 2x2 inverse actions below are hand/scalar Fraction
calculations, not calls back into the production implementation or NumPy.
These local geometry tests do not execute a candidate current or numerical step.
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
from typing import Any, cast
import unittest
from unittest.mock import patch
import venv

import numpy as np

from pygrc.models import grc_v4_geometry as geometry_stage
from pygrc.models.grc_v4_codec import payload_identity
from pygrc.models.grc_v4_profile import resolve_profile
from pygrc.models.grc_v4_state import FrozenJSONMap, GRCV4AuthoritativeState

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
from pygrc.models.grc_v4_profile import CandidateCParams, GRCV4CommonParams


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
            "stage": stage_inputs_fixture().to_payload(),
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
from dataclasses import replace
from pygrc.models.grc_v4_geometry import GeometryStageInputs, GeometryStageCache, K4Tensor, H_profile
from pygrc.models.grc_v4_codec import canonical_json_bytes
stage=None
data=json.load(sys.stdin)
stage=GeometryStageInputs.from_payload(data['stage'])
ref=stage.geometry.reference
operand=PhysicalFlux(ref.graph,(4,6))
cache=GeometryStageCache(stage,'flat',operand)
restored=GeometryStageCache.from_canonical_bytes(cache.to_canonical_bytes(),expected_inputs=stage,expected_kind='flat',expected_operand=operand)
assert restored.consume(expected_inputs=stage,expected_kind='flat',expected_operand=operand).values==(2,2)
assert H_profile(K4Tensor(ref.graph,ref.K4_base,((2,1),(1,4))),reference=ref,context=ref.context,profile=ref.profile).one_form_hodge.matrix==((3,.5),(.5,5))
try: restored.consume(expected_inputs=replace(stage,stage='post_continuity'),expected_kind='flat',expected_operand=operand)
except ValueError as exc: assert 'stale_cache' in str(exc)
else: raise AssertionError('installed stale stage accepted')
raw=json.loads(cache.to_canonical_bytes())
raw['payload']['output']['values'][0]=999
raw['cache_id']='grcv4-derived-geometry-cache-sha256:'+hashlib.sha256(canonical_json_bytes(raw['payload'])).hexdigest()
try: GeometryStageCache.from_canonical_bytes(canonical_json_bytes(raw),expected_inputs=stage,expected_kind='flat',expected_operand=operand)
except ValueError: pass
else: raise AssertionError('installed rehashed false cache accepted')
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


# P9-3.2 independent reconstruction, domain and stage pressure.


def stage_reference_fixture(
    candidate: str = "C",
    realization: str = "OS",
    *,
    graph: GRCV4Graph | None = None,
    weights: dict[str, float] | None = None,
    base: list[list[float]] | None = None,
    gain: float = 0.5,
    changes: dict[str, dict[str, Any]] | None = None,
) -> geometry_stage.GRCV4ReferenceGeometry:
    from tests.models.test_grc_v4_profile import family_fixture, reidentify

    graph = GRCV4Graph.from_payload(graph_payload()) if graph is None else graph
    weights = (
        {e: float(i + 2) for i, e in reversed(list(enumerate(graph.live_edge_ids)))}
        if weights is None
        else weights
    )
    n = len(graph.oriented_edges)
    base = (
        [[float(i == j) for j in range(n)] for i in range(n)] if base is None else base
    )
    params, identity = family_fixture(candidate, realization)
    params["geometry"].update(
        K4_base_digest=payload_identity(
            "k4_identity_payload",
            {"schema_version": "grcv4-k4-identity-v1", "K4_base": base},
        ),
        reference_hodge_digest=payload_identity(
            "reference_hodge_identity_payload",
            {
                "schema_version": "grcv4-reference-hodge-identity-v1",
                "edge_weights": weights,
            },
        ),
        candidate_adapter_id=f"candidate_{candidate.lower()}_exact_star_adapter_v1",
        kappa_H=gain,
    )
    if candidate == "C":
        params["candidate"]["W_C_tr"] = weights
        params["candidate"]["W_C_tr_content_digest"] = payload_identity(
            "wctr_identity_payload",
            {"schema_version": "grcv4-wctr-identity-v1", "W_C_tr": weights},
        )
    if changes:
        for group, values in changes.items():
            if group == "identity":
                identity.update(values)
            else:
                params[group].update(values)
    reidentify(params, identity)
    profile = resolve_profile(params, identity)
    context = geometry_stage.GRCV4Context("constant_zero_context_v1", FrozenJSONMap({}))
    return geometry_stage.GRCV4ReferenceGeometry(
        graph, profile, context, tuple(tuple(r) for r in base), FrozenJSONMap(weights)
    )


def stage_inputs_fixture(
    ref: geometry_stage.GRCV4ReferenceGeometry | None = None,
    *,
    stage: str = "pre_read",
) -> geometry_stage.GeometryStageInputs:
    ref = stage_reference_fixture() if ref is None else ref
    n, m = len(ref.graph.live_node_ids), len(ref.graph.oriented_edges)
    current = GRCV4AuthoritativeState(
        tuple(float(i + 1) for i in range(n)),
        (2.0,) * m if ref.profile.identity_payload.candidate == "A" else None,
        (0.0,) * (m * m)
        if ref.profile.identity_payload.realization in ("PC", "CI+PC")
        else None,
    )
    return geometry_stage.GeometryStageInputs(
        ref.geometry(),
        ref.context,
        current,
        current,
        "ordinary-step-1",
        float(sum(current.C)),
        (),
        0,
        0.0,
        1.0,
        cast(geometry_stage.GeometryStage, stage),
        0,
        PhysicalFlux(ref.graph, (0.0,) * m)
        if stage in ("ci_trial", "cipc_trial")
        else None,
    )


def replace_stage(
    subject: geometry_stage.GeometryStageInputs, **changes: Any
) -> geometry_stage.GeometryStageInputs:
    """Permit deliberate invalid argument types in negative admission fixtures."""
    return replace(subject, **changes)


def reconstruct_stage(data: object) -> dict[str, Any]:
    """Portable consumer: input payloads, no repository fixtures or callbacks."""
    inputs = geometry_stage.GeometryStageInputs.from_payload(data)
    ref = inputs.geometry.reference
    flux = PhysicalFlux(
        ref.graph, tuple(float(i + 2) for i in range(len(ref.graph.oriented_edges)))
    )
    cache = geometry_stage.GeometryStageCache(inputs, "flat", flux)
    restored = geometry_stage.GeometryStageCache.from_canonical_bytes(
        cache.to_canonical_bytes(),
        expected_inputs=inputs,
        expected_kind="flat",
        expected_operand=flux,
    )
    result = restored.consume(
        expected_inputs=inputs, expected_kind="flat", expected_operand=flux
    )
    assert isinstance(result, OneForm)
    return {
        "stage_id": inputs.identity,
        "cache_id": restored.identity,
        "flat": list(result.values),
        "input_roundtrip": inputs.to_payload(),
    }


class GeometryAdmissionTests(unittest.TestCase):
    def test_structural_support_is_star_local_and_not_inverse_support(self) -> None:
        graph = GRCV4Graph(
            ("u", "v", "w", "x"),
            (
                OrientedEdge("a", "u", "v"),
                OrientedEdge("b", "v", "w"),
                OrientedEdge("c", "w", "x"),
            ),
        )
        ref = stage_reference_fixture(graph=graph)
        nonlocal_matrix = ((0, 0, 1), (0, 0, 0), (1, 0, 0))
        with self.assertRaisesRegex(ValueError, "outside.*stars"):
            geometry_stage.K4Tensor(graph, ref.K4_base, nonlocal_matrix)
        with self.assertRaisesRegex(ValueError, "outside.*stars"):
            stage_reference_fixture(
                graph=graph, base=[list(r) for r in nonlocal_matrix]
            )
        delta = ((2, 1, 0), (1, 2, 1), (0, 1, 2))
        geometry = geometry_stage.H_profile(
            geometry_stage.K4Tensor(graph, ref.K4_base, delta),
            reference=ref,
            context=ref.context,
            profile=ref.profile,
        )
        # A local tridiagonal Hodge has nonlocal inverse action: no masking.
        lowered = geometry.pairings.flat_map.flat(PhysicalFlux(graph, (0, 0, 1)))
        self.assertNotEqual(lowered.values[0], 0)
        payload = ref.to_payload()
        payload["structural_coordinates_id"] = "unbound_carrier"
        with self.assertRaises(ValueError):
            geometry_stage.GRCV4ReferenceGeometry.from_payload(payload)
        pc = stage_reference_fixture("C", "PC", graph=graph)
        stage = stage_inputs_fixture(pc)
        with self.assertRaisesRegex(ValueError, "outside.*stars"):
            replace(
                stage,
                current=GRCV4AuthoritativeState(
                    stage.current.C,
                    None,
                    tuple(x for row in nonlocal_matrix for x in row),
                ),
            )

    def test_affine_baseline_increment_and_fixed_vertex_measure(self) -> None:
        ref = stage_reference_fixture(base=[[13.0, 2.0], [2.0, -7.0]])
        tensor = geometry_stage.K4Tensor(
            ref.graph, ref.K4_base, ((2.0, 1.0), (1.0, 4.0))
        )
        actual = geometry_stage.H_profile(
            tensor, reference=ref, context=ref.context, profile=ref.profile
        )
        self.assertEqual(actual.one_form_hodge.matrix, ((3.0, 0.5), (0.5, 5.0)))
        self.assertEqual(
            actual.pairings.vertex.matrix,
            ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)),
        )
        self.assertIs(actual.reference.differential, ref.differential)
        self.assertNotEqual(actual.identity, ref.geometry().identity)
        with self.assertRaises(TypeError):
            geometry_stage.H_profile(tensor)  # type: ignore[call-arg]
        with self.assertRaises(TypeError):
            geometry_stage.H_profile(
                cast(Any, OneForm(ref.graph, (1, 2))),
                reference=ref,
                context=ref.context,
                profile=ref.profile,
            )

    def test_neutral_controls_are_reference_exact_with_nonzero_baseline(self) -> None:
        for gain, delta in [
            (0.0, ((1e308, 0.0), (0.0, -1e308))),
            (2.0, ((0.0, 0.0), (0.0, 0.0))),
        ]:
            ref = stage_reference_fixture(base=[[1e308, 0.0], [0.0, -1e308]], gain=gain)
            actual = geometry_stage.H_profile(
                geometry_stage.K4Tensor(ref.graph, ref.K4_base, delta),
                reference=ref,
                context=ref.context,
                profile=ref.profile,
            )
            self.assertEqual(actual, ref.geometry())
            self.assertEqual(actual.identity, ref.geometry().identity)

    def test_reference_digest_dimension_and_baseline_fail_closed(self) -> None:
        ref = stage_reference_fixture()
        for bad in [((1.0,),), ((1.0, 1.0), (0.0, 1.0)), ((1.0, 0.0), (0.0, 2.0))]:
            with self.subTest(base=bad), self.assertRaises(ValueError):
                replace(ref, K4_base=bad)
        with self.assertRaises(ValueError):
            replace(ref, edge_weights=FrozenJSONMap({"z": 2.0, "a": 4.0}))
        with self.assertRaises(ValueError):
            geometry_stage.H_profile(
                geometry_stage.K4Tensor(
                    ref.graph, ((2.0, 0.0), (0.0, 2.0)), ((0.0, 0.0), (0.0, 0.0))
                ),
                reference=ref,
                context=ref.context,
                profile=ref.profile,
            )
        # The frozen identity fixture has nine edge weights but a 2x2 K4. It
        # remains a valid declaration, and cannot stand in for a graph domain.
        from tests.models.test_grc_v4_profile import fixture

        profile = resolve_profile(*fixture())
        assert isinstance(profile.params_resolved.candidate, CandidateCParams)
        graph = GRCV4Graph(
            ("u", "v"),
            tuple(
                OrientedEdge(e, "u", "v")
                for e in profile.params_resolved.candidate.W_C_tr
            ),
        )
        with self.assertRaises(ValueError):
            geometry_stage.GRCV4ReferenceGeometry(
                graph,
                profile,
                ref.context,
                ((1.0, 0.0), (0.0, 1.0)),
                FrozenJSONMap(profile.params_resolved.candidate.W_C_tr),
            )

    def test_valid_recomputed_C_reference_hashes_do_not_hide_weight_disagreement(
        self,
    ) -> None:
        ref = stage_reference_fixture()
        for weights in (
            {"z": 4.0, "a": 6.0},
            {"z": 2.0, "a": 4.0},
            {"z": 1.0, "a": 1.5},
        ):
            payload = ref.profile.to_payload()
            params, identity = payload["params_resolved"], payload["identity_payload"]
            assert isinstance(params, dict) and isinstance(identity, dict)
            geometry = params["geometry"]
            assert isinstance(geometry, dict)
            geometry["reference_hodge_digest"] = payload_identity(
                "reference_hodge_identity_payload",
                {
                    "schema_version": "grcv4-reference-hodge-identity-v1",
                    "edge_weights": weights,
                },
            )
            identity["params_hash"] = payload_identity("resolved_params", params)
            profile = resolve_profile(params, identity)
            with (
                self.subTest(weights=weights),
                self.assertRaisesRegex(ValueError, "weights must match"),
            ):
                geometry_stage.GRCV4ReferenceGeometry(
                    ref.graph, profile, ref.context, ref.K4_base, FrozenJSONMap(weights)
                )

    def test_unknown_geometry_algorithms_and_context_are_not_aliases(self) -> None:
        fields = {
            "geometry": [
                "star_cover_id",
                "overlap_normalization_id",
                "candidate_adapter_id",
                "flat_sharp_solver_id",
                "geometry_domain_id",
            ],
            "common": ["measure_profile_id"],
            "identity": ["geometry_profile_id"],
        }
        for group, names in fields.items():
            for name in names:
                with (
                    self.subTest(field=name),
                    self.assertRaisesRegex(ValueError, "geometry declaration"),
                ):
                    stage_reference_fixture(changes={group: {name: "unimplemented_v1"}})
        for contract, value in [
            ("arbitrary_context", {}),
            ("constant_zero_context_v1", {"forcing": 0}),
            ("constant_zero_context_v1", {"callback": "noop"}),
        ]:
            with self.assertRaises(ValueError):
                geometry_stage.GRCV4Context(
                    contract, FrozenJSONMap(cast(dict[str, Any], value))
                )

    def test_reference_order_is_stable_ID_based_and_inputs_are_detached(self) -> None:
        weights = {"a": 3.0, "z": 2.0}
        base = [[1.0, 0.0], [0.0, 1.0]]
        ref = stage_reference_fixture(weights=weights, base=base)
        before = ref.to_payload()
        weights["z"] = 100.0
        base[0][0] = 100.0
        self.assertEqual(ref.to_payload(), before)
        self.assertEqual(ref.pairings.one_form.matrix, ((2.0, 0.0), (0.0, 3.0)))
        restored = geometry_stage.GRCV4ReferenceGeometry.from_payload(before)
        self.assertEqual(restored, ref)
        self.assertEqual(restored.identity, ref.identity)
        with self.assertRaises(FrozenInstanceError):
            ref.K4_base = ()  # type: ignore[misc]

    def test_full_reference_empty_domain_is_not_inferred_from_empty_primitive(
        self,
    ) -> None:
        graph = GRCV4Graph((), ())
        self.assertEqual(geometry_stage.StarAssembly(OneForm(graph, ())).matrix, ())
        for candidate in ("A", "C"):
            with self.assertRaises(ValueError):
                stage_reference_fixture(candidate, graph=graph, weights={}, base=[])

    def test_positive_boundary_and_rounding_collapse_fail_closed(self) -> None:
        ref = stage_reference_fixture(weights={"a": 1.0, "z": 1.0}, gain=1.0)
        for value, admitted in [
            (-1.0, False),
            (math.nextafter(-1.0, -math.inf), False),
            (math.nextafter(-1.0, 0.0), True),
        ]:
            tensor = geometry_stage.K4Tensor(
                ref.graph, ref.K4_base, ((value, 0.0), (0.0, 0.0))
            )
            with self.subTest(value=value):
                if admitted:
                    self.assertGreater(
                        geometry_stage.H_profile(
                            tensor,
                            reference=ref,
                            context=ref.context,
                            profile=ref.profile,
                        ).one_form_hodge.matrix[0][0],
                        0,
                    )
                else:
                    with self.assertRaisesRegex(ValueError, "positive definite"):
                        geometry_stage.H_profile(
                            tensor,
                            reference=ref,
                            context=ref.context,
                            profile=ref.profile,
                        )
        # Exact 1+(1+u)*(-1+u)=u^2 is positive, but the declared binary64
        # multiply/add collapses to zero. Both expression and stored matrix
        # must be admitted; a positive exact expression alone cannot certify it.
        u = 2.0**-52
        ref = stage_reference_fixture(weights={"a": 1.0, "z": 1.0}, gain=1.0 + u)
        tensor = geometry_stage.K4Tensor(
            ref.graph, ref.K4_base, ((-1.0 + u, 0.0), (0.0, 0.0))
        )
        self.assertEqual(
            Fraction(1) + Fraction(1.0 + u) * Fraction(-1.0 + u), Fraction(u) ** 2
        )
        with self.assertRaisesRegex(ValueError, "positive definite"):
            geometry_stage.H_profile(
                tensor, reference=ref, context=ref.context, profile=ref.profile
            )

    def test_affine_overflow_and_scaled_positive_controls(self) -> None:
        for size in (1, 2, 4):
            graph = ExactPositiveDomainTests.graph(size)
            for scale in (5e-324, 1e-308, 2.0**-500, 1.0, 2.0**500, 1e308):
                ref = stage_reference_fixture(
                    graph=graph, weights={e: scale for e in graph.live_edge_ids}
                )
                zero = tuple((0.0,) * size for _ in range(size))
                self.assertEqual(
                    geometry_stage.H_profile(
                        geometry_stage.K4Tensor(graph, ref.K4_base, zero),
                        reference=ref,
                        context=ref.context,
                        profile=ref.profile,
                    ),
                    ref.geometry(),
                )
        ref = stage_reference_fixture(gain=1e308)
        tensor = geometry_stage.K4Tensor(
            ref.graph, ref.K4_base, ((2.0, 0.0), (0.0, 2.0))
        )
        before = ref.to_payload(), tensor.identity
        with self.assertRaisesRegex(ValueError, "nonfinite"):
            geometry_stage.H_profile(
                tensor, reference=ref, context=ref.context, profile=ref.profile
            )
        self.assertEqual((ref.to_payload(), tensor.identity), before)

    def test_affine_covariance_all_signed_actions_and_nonzero_base(self) -> None:
        import itertools

        ref = stage_reference_fixture(base=[[3.0, 1.0], [1.0, 4.0]])
        delta = ((2.0, 1.0), (1.0, 4.0))
        tensor = geometry_stage.K4Tensor(ref.graph, ref.K4_base, delta)
        actual = geometry_stage.H_profile(
            tensor, reference=ref, context=ref.context, profile=ref.profile
        )
        for nodes in itertools.permutations(range(3)):
            for edges in itertools.permutations(range(2)):
                for signs in itertools.product((-1, 1), repeat=2):
                    target_graph = GRCV4Graph(
                        tuple(ref.graph.live_node_ids[i] for i in nodes),
                        tuple(
                            OrientedEdge(
                                ref.graph.oriented_edges[old].edge_id,
                                ref.graph.oriented_edges[old].tail_node_id
                                if signs[i] == 1
                                else ref.graph.oriented_edges[old].head_node_id,
                                ref.graph.oriented_edges[old].head_node_id
                                if signs[i] == 1
                                else ref.graph.oriented_edges[old].tail_node_id,
                            )
                            for i, old in enumerate(edges)
                        ),
                    )
                    action = GraphCoordinateAction(
                        ref.graph,
                        target_graph,
                        tuple(nodes),
                        tuple(edges),
                        tuple(signs),
                    )

                    def move(
                        matrix: tuple[tuple[float, ...], ...],
                    ) -> list[list[float]]:
                        return [
                            [
                                float(signs[i] * signs[j]) * matrix[a][b]
                                if matrix[a][b]
                                else 0.0
                                for j, b in enumerate(edges)
                            ]
                            for i, a in enumerate(edges)
                        ]

                    # Stable edge IDs retain their reference weights after reordering.
                    target = stage_reference_fixture(
                        graph=action.target,
                        weights={"a": 3.0, "z": 2.0},
                        base=move(ref.K4_base),
                    )
                    result = geometry_stage.H_profile(
                        geometry_stage.K4Tensor(
                            action.target,
                            target.K4_base,
                            tuple(tuple(r) for r in move(delta)),
                        ),
                        reference=target,
                        context=target.context,
                        profile=target.profile,
                    )
                    self.assertEqual(
                        result.one_form_hodge.matrix,
                        tuple(tuple(r) for r in move(actual.one_form_hodge.matrix)),
                    )


class StarAssemblyTests(unittest.TestCase):
    def test_hand_derived_chain_parallel_loop_and_disconnected_cases(self) -> None:
        graph = GRCV4Graph.from_payload(graph_payload())
        self.assertEqual(
            geometry_stage.StarAssembly(OneForm(graph, (2, 3))).matrix,
            ((4.0, 3.0), (3.0, 9.0)),
        )
        graph = GRCV4Graph(
            ("u", "v", "isolated"),
            (
                OrientedEdge("loop", "u", "u"),
                OrientedEdge("p", "u", "v"),
                OrientedEdge("q", "u", "v"),
            ),
        )
        matrix = geometry_stage.StarAssembly(OneForm(graph, (2, 3, -4))).matrix
        self.assertEqual(tuple(matrix[i][i] for i in range(3)), (4, 9, 16))
        self.assertEqual(matrix[1][2], -12)
        self.assertAlmostEqual(matrix[0][1], 6 / math.sqrt(2), delta=2e-15)
        self.assertAlmostEqual(matrix[0][2], -8 / math.sqrt(2), delta=2e-15)
        graph = GRCV4Graph(
            ("u", "v", "x", "y"),
            (OrientedEdge("a", "u", "v"), OrientedEdge("b", "x", "y")),
        )
        self.assertEqual(
            geometry_stage.StarAssembly(OneForm(graph, (2, 3))).matrix, ((4, 0), (0, 9))
        )

    def test_seeded_multigraphs_against_decimal_restriction_sum(self) -> None:
        from decimal import Decimal, localcontext
        import random

        rng = random.Random(932)
        for case in range(80):
            n = rng.randrange(1, 8)
            m = rng.randrange(0, 9)
            endpoints = [(rng.randrange(n), rng.randrange(n)) for _ in range(m)]
            graph = GRCV4Graph(
                tuple(range(n)),
                tuple(
                    OrientedEdge(f"e-{i}", a, b) for i, (a, b) in enumerate(endpoints)
                ),
            )
            values = tuple(float(rng.randrange(-7, 8)) for _ in range(m))
            actual = geometry_stage.StarAssembly(OneForm(graph, values)).matrix
            # Independent scatter of each local rank-one form at high precision;
            # neither graph.star nor production weights/assembly are the oracle.
            with localcontext() as ctx:
                ctx.prec = 70
                local_edges = [
                    [i for i, (a, b) in enumerate(endpoints) if v == a or v == b]
                    for v in range(n)
                ]
                expected = [[Decimal(0)] * m for _ in range(m)]
                for edges in local_edges:
                    local = {
                        i: Decimal(values[i])
                        / Decimal(sum(i in star for star in local_edges)).sqrt()
                        for i in edges
                    }
                    for i in edges:
                        for j in edges:
                            expected[i][j] += local[i] * local[j]
                for i in range(m):
                    for j in range(m):
                        with self.subTest(case=case, i=i, j=j):
                            self.assertAlmostEqual(
                                actual[i][j], float(expected[i][j]), delta=2e-14
                            )
                            self.assertEqual(actual[i][j], actual[j][i])
                    self.assertEqual(actual[i][i], values[i] ** 2)

    def test_only_lowered_forms_are_consumed_and_overflow_rejects(self) -> None:
        graph = GRCV4Graph.from_payload(graph_payload())
        for value in [
            PhysicalFlux(graph, (2, 3)),
            VertexScalar(graph, (2, 3, 4)),
            [2, 3],
        ]:
            with self.assertRaises(TypeError):
                geometry_stage.StarAssembly(value)  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "nonfinite"):
            geometry_stage.StarAssembly(OneForm(graph, (1e308, 1.0)))
        self.assertEqual(
            geometry_stage.StarAssembly(OneForm(graph, (0, 0))).matrix, ((0, 0), (0, 0))
        )


class StageCacheTests(unittest.TestCase):
    def test_frozen_state_preimages_and_rehashed_subject_mismatches(self) -> None:
        stage = stage_inputs_fixture()
        ref = stage.geometry.reference
        reset = {
            "schema_version": "grcv4-reset-baseline-v1",
            "active_model_identity": ref.profile.complete_profile_id,
            "graph_digest": ref.graph.graph_digest,
            "orientation_identity": ref.graph.orientation_identity,
            "authoritative": {"C": [1, 2, 3], "W_A": None, "Z_4": None},
            "Q_target": 6,
            "context_contract_id": "constant_zero_context_v1",
        }
        reset_id = independent_ascii_id("grcv4-reset-sha256", reset)
        scientific = {
            "schema_version": "grcv4-scientific-state-v1",
            "active_model_identity": ref.profile.complete_profile_id,
            "graph_digest": ref.graph.graph_digest,
            "orientation_identity": ref.graph.orientation_identity,
            "step_index": 0,
            "time": 0,
            "authoritative": {"C": [1, 2, 3], "W_A": None, "Z_4": None},
            "reset_digest": reset_id,
            "Q_target": 6,
            "context_contract_id": "constant_zero_context_v1",
            "context_value_digest": None,
        }
        scientific_id = independent_ascii_id("grcv4-state-sha256", scientific)
        lifecycle_id = independent_ascii_id(
            "grcv4-lifecycle-sha256",
            {
                "schema_version": "grcv4-lifecycle-envelope-v1",
                "scientific_state_digest": scientific_id,
                "receipt_ids": [],
            },
        )
        self.assertEqual(stage.reset_preimage, reset)
        self.assertEqual(stage.scientific_state_preimage, scientific)
        self.assertEqual(
            (stage.reset_id, stage.scientific_state_id, stage.source_lifecycle_id),
            (reset_id, scientific_id, lifecycle_id),
        )
        for name in ("reset_id", "scientific_state_id", "source_lifecycle_id"):
            data = stage.to_payload()
            data[name] = str(data[name])[:-64] + "f" * 64
            with self.assertRaisesRegex(ValueError, "authority identity"):
                geometry_stage.GeometryStageInputs.from_payload(data)
        for receipt_ids in (("fake",), ("grc-receipt-sha256:" + "a" * 64 + "\n",)):
            with self.assertRaises(ValueError):
                replace(stage, receipt_ids=receipt_ids)
        first = "grc-receipt-sha256:" + "a" * 64
        second = "grc-receipt-sha256:" + "b" * 64
        left = replace(stage, receipt_ids=(first, second))
        right = replace(stage, receipt_ids=(second, first))
        self.assertEqual(left.scientific_state_id, right.scientific_state_id)
        self.assertNotEqual(left.source_lifecycle_id, right.source_lifecycle_id)

    def test_all_primitive_producers_have_independent_expected_values(self) -> None:
        stage = stage_inputs_fixture()
        ref = stage.geometry.reference
        graph = ref.graph
        cases: list[
            tuple[
                geometry_stage.DerivedGeometryKind,
                geometry_stage.GeometryOperand,
                object,
            ]
        ] = [
            ("d0", VertexScalar(graph, (4, 2, 1)), (2.0, 1.0)),
            ("divergence", PhysicalFlux(graph, (3, -2)), (3.0, -5.0, 2.0)),
            ("flat", PhysicalFlux(graph, (4, 6)), (2.0, 2.0)),
            ("sharp", OneForm(graph, (2, 3)), (4.0, 9.0)),
            ("star_assembly", OneForm(graph, (2, 3)), ((4.0, 3.0), (3.0, 9.0))),
            (
                "H_profile",
                geometry_stage.K4Tensor(graph, ref.K4_base, ((2.0, 1.0), (1.0, 4.0))),
                ((3.0, 0.5), (0.5, 5.0)),
            ),
        ]
        fresh = geometry_stage.GeometryStageInputs.from_payload(stage.to_payload())
        for kind, operand, expected in cases:
            cache = geometry_stage.GeometryStageCache(stage, kind, operand)
            value = cache.consume(
                expected_inputs=fresh, expected_kind=kind, expected_operand=operand
            )
            actual: object
            if isinstance(value, geometry_stage.StarAssembly):
                actual = value.matrix
            elif isinstance(value, geometry_stage.GRCV4Geometry):
                actual = value.one_form_hodge.matrix
            else:
                actual = value.values
            self.assertEqual(actual, expected)
            restored = geometry_stage.GeometryStageCache.from_canonical_bytes(
                cache.to_canonical_bytes(),
                expected_inputs=fresh,
                expected_kind=kind,
                expected_operand=operand,
            )
            self.assertEqual(restored.to_canonical_bytes(), cache.to_canonical_bytes())

    def test_identical_predictor_and_corrector_matrices_do_not_share_authority(
        self,
    ) -> None:
        stage = stage_inputs_fixture(stage="os_predictor")
        graph = stage.geometry.reference.graph
        flux = PhysicalFlux(graph, (4, 6))
        cache = geometry_stage.GeometryStageCache(stage, "flat", flux)
        corrector = replace(stage, stage="os_corrector")
        self.assertEqual(stage.geometry, corrector.geometry)
        self.assertNotEqual(stage.identity, corrector.identity)
        with self.assertRaisesRegex(ValueError, "stale_cache"):
            cache.consume(
                expected_inputs=corrector, expected_kind="flat", expected_operand=flux
            )
        fresh = geometry_stage.GeometryStageCache(corrector, "flat", flux)
        self.assertEqual(fresh.value, cache.value)
        self.assertNotEqual(fresh.identity, cache.identity)

    def test_every_stage_input_is_bound_even_when_operation_output_is_unchanged(
        self,
    ) -> None:
        stage = stage_inputs_fixture()
        graph = stage.geometry.reference.graph
        flux = PhysicalFlux(graph, (4, 6))
        cache = geometry_stage.GeometryStageCache(stage, "flat", flux)
        variants = [
            replace_stage(stage, **{name: value})
            for name, value in [
                ("operation_id", "operation-2"),
                ("Q_target", 7.0),
                ("receipt_ids", ("grc-receipt-sha256:" + "1" * 64,)),
                ("step_index", 1),
                ("time", 1.0),
                ("dt", 2.0),
                ("stage", "post_continuity"),
                ("current", GRCV4AuthoritativeState((3, 2, 1), None, None)),
                ("reset", GRCV4AuthoritativeState((3, 2, 1), None, None)),
                ("trial_current", PhysicalFlux(graph, (0, 0))),
            ]
        ]
        for changed in variants:
            with (
                self.subTest(stage=changed.to_payload()),
                self.assertRaisesRegex(ValueError, "stale_cache"),
            ):
                cache.consume(
                    expected_inputs=changed, expected_kind="flat", expected_operand=flux
                )
            self.assertEqual(
                geometry_stage.GeometryStageCache(changed, "flat", flux).value,
                cache.value,
            )
        with self.assertRaisesRegex(ValueError, "stale_cache"):
            cache.consume(
                expected_inputs=stage, expected_kind="divergence", expected_operand=flux
            )
        with self.assertRaisesRegex(ValueError, "stale_cache"):
            cache.consume(
                expected_inputs=stage,
                expected_kind="flat",
                expected_operand=PhysicalFlux(graph, (8, 12)),
            )

    def test_changed_profile_reference_and_geometry_invalidate_cache(self) -> None:
        stage = stage_inputs_fixture()
        ref = stage.geometry.reference
        flux = PhysicalFlux(ref.graph, (4, 6))
        cache = geometry_stage.GeometryStageCache(stage, "flat", flux)
        other = stage_inputs_fixture(stage_reference_fixture(gain=2.0))
        self.assertEqual(
            other.geometry.one_form_hodge.matrix, stage.geometry.one_form_hodge.matrix
        )
        other_base = stage_inputs_fixture(
            stage_reference_fixture(base=[[3.0, 1.0], [1.0, 4.0]])
        )
        dense = replace(
            stage,
            geometry=geometry_stage.GRCV4Geometry(
                ref, OneFormHodge(ref.graph, ((2.0, 1.0), (1.0, 3.0)))
            ),
        )
        for variant in (other, other_base, dense):
            with self.assertRaisesRegex(ValueError, "stale_cache"):
                cache.consume(
                    expected_inputs=variant, expected_kind="flat", expected_operand=flux
                )

    def test_joint_trials_bind_evaluation_and_current_even_with_identical_geometry(
        self,
    ) -> None:
        for candidate in ("A", "C"):
            for realization, label in (("CI", "ci_trial"), ("CI+PC", "cipc_trial")):
                stage = stage_inputs_fixture(
                    stage_reference_fixture(candidate, realization), stage=label
                )
                graph = stage.geometry.reference.graph
                flux = PhysicalFlux(graph, (4, 6))
                cache = geometry_stage.GeometryStageCache(stage, "flat", flux)
                for altered in (
                    replace(stage, evaluation_index=1),
                    replace(stage, trial_current=PhysicalFlux(graph, (1, 0))),
                ):
                    with self.assertRaisesRegex(ValueError, "stale_cache"):
                        cache.consume(
                            expected_inputs=altered,
                            expected_kind="flat",
                            expected_operand=flux,
                        )
                with self.assertRaisesRegex(ValueError, "trial current"):
                    replace(stage, trial_current=None)

    def test_realization_stage_labels_are_closed_and_not_solver_execution(self) -> None:
        labels = {
            "OS": ("os_predictor", "os_corrector"),
            "CI": ("ci_trial",),
            "CI+PC": ("cipc_trial",),
            "PC": ("pc_old_history",),
            "RG2b": ("rg2b_section",),
        }
        for candidate in ("A", "C"):
            for realization, admitted in labels.items():
                ref = stage_reference_fixture(candidate, realization)
                for label in (
                    "pre_read",
                    "post_continuity",
                    "reset_readmission",
                    "target_readmission",
                    *admitted,
                ):
                    stage_inputs_fixture(ref, stage=label)
                for label in set(sum(labels.values(), ())) - set(admitted):
                    with self.assertRaises(ValueError):
                        stage_inputs_fixture(ref, stage=label)
        stage = stage_inputs_fixture()
        for name, value in [
            ("stage", "os_second_corrector"),
            ("stage", None),
            ("evaluation_index", True),
            ("evaluation_index", 1),
            ("step_index", -1),
            ("step_index", 2**53),
            ("time", -0.0),
            ("time", math.inf),
            ("dt", -1.0),
            ("operation_id", ""),
        ]:
            with (
                self.subTest(field=name, value=value),
                self.assertRaises((TypeError, ValueError)),
            ):
                replace_stage(stage, **{name: value})

    def test_current_reset_authority_shape_and_old_PC_history(self) -> None:
        stage = stage_inputs_fixture()
        for name in ("current", "reset"):
            for invalid in [
                GRCV4AuthoritativeState((1, 2), None, None),
                GRCV4AuthoritativeState((1, 2, 3), (1, 2), None),
                GRCV4AuthoritativeState((1, 2, 3), None, (0, 0, 0, 0)),
            ]:
                with self.assertRaises(ValueError):
                    replace_stage(stage, **{name: invalid})
        ref = stage_reference_fixture("C", "PC")
        stage = stage_inputs_fixture(ref, stage="pc_old_history")
        old = GRCV4AuthoritativeState(stage.current.C, None, (2, 1, 1, 4))
        new_geometry = geometry_stage.H_profile(
            geometry_stage.K4Tensor(ref.graph, ref.K4_base, ((2, 1), (1, 4))),
            reference=ref,
            context=ref.context,
            profile=ref.profile,
        )
        with self.assertRaisesRegex(ValueError, "old committed history"):
            replace(stage, geometry=new_geometry)
        with self.assertRaisesRegex(ValueError, "old committed history"):
            geometry_stage.GeometryStageCache(
                stage,
                "H_profile",
                geometry_stage.K4Tensor(ref.graph, ref.K4_base, ((2, 1), (1, 4))),
            )
        accepted = geometry_stage.GeometryStageCache(
            stage,
            "H_profile",
            geometry_stage.K4Tensor(ref.graph, ref.K4_base, ((0, 0), (0, 0))),
        )
        self.assertEqual(accepted.value, stage.geometry)
        changed = replace(stage, current=old, geometry=new_geometry)
        self.assertEqual(changed.geometry.one_form_hodge.matrix, ((3, 0.5), (0.5, 5)))
        # Even outside the read stage, both retained point images must be positive.
        for realization in ("PC", "CI+PC"):
            subject = stage_inputs_fixture(stage_reference_fixture("C", realization))
            for name in ("current", "reset"):
                with self.assertRaises(ValueError):
                    replace_stage(
                        subject,
                        **{
                            name: GRCV4AuthoritativeState(
                                subject.current.C, None, (-4, 0, 0, -6)
                            )
                        },
                    )
        for values in [(1, 2), (1, 0, 1, 1)]:
            with self.assertRaises(ValueError):
                replace(
                    stage,
                    current=GRCV4AuthoritativeState(stage.current.C, None, values),
                )

    def test_A_retained_values_are_provenance_even_for_geometry_only_results(
        self,
    ) -> None:
        stage = stage_inputs_fixture(stage_reference_fixture("A"))
        graph = stage.geometry.reference.graph
        flux = PhysicalFlux(graph, (4, 6))
        cache = geometry_stage.GeometryStageCache(stage, "flat", flux)
        for name in ("current", "reset"):
            changed = replace_stage(
                stage, **{name: GRCV4AuthoritativeState(stage.current.C, (3, 4), None)}
            )
            with self.assertRaisesRegex(ValueError, "stale_cache"):
                cache.consume(
                    expected_inputs=changed, expected_kind="flat", expected_operand=flux
                )
        with self.assertRaises(ValueError):
            replace(stage, current=GRCV4AuthoritativeState(stage.current.C, (3,), None))

    def test_stale_import_is_rejected_before_any_numerical_rebuild(self) -> None:
        stage = stage_inputs_fixture()
        graph = stage.geometry.reference.graph
        flux = PhysicalFlux(graph, (4, 6))
        cache = geometry_stage.GeometryStageCache(stage, "flat", flux)
        with patch.object(
            np.linalg, "solve", side_effect=AssertionError("stale cache reached solver")
        ):
            with self.assertRaisesRegex(ValueError, "stale_cache"):
                geometry_stage.GeometryStageCache.from_canonical_bytes(
                    cache.to_canonical_bytes(),
                    expected_inputs=replace(stage, stage="post_continuity"),
                    expected_kind="flat",
                    expected_operand=flux,
                )

    def test_rehashed_corrupt_outputs_unknown_fields_and_boolean_aliases_reject(
        self,
    ) -> None:
        stage = stage_inputs_fixture()
        graph = stage.geometry.reference.graph
        flux = PhysicalFlux(graph, (4, 6))
        cache = geometry_stage.GeometryStageCache(stage, "flat", flux)
        for mode in (
            "output",
            "extra",
            "version",
            "boolean_input",
            "boolean_output",
            "role",
            "operand",
        ):
            data = json.loads(cache.to_canonical_bytes())
            payload = data["payload"]
            if mode == "output":
                payload["output"]["values"][0] = 9
            elif mode == "extra":
                payload["extra"] = "opaque cache state"
            elif mode == "version":
                payload["descriptor_version"] = "unknown"
            elif mode == "boolean_input":
                payload["inputs"]["step_index"] = False
            elif mode == "boolean_output":
                payload["output"]["values"][0] = True
            elif mode == "role":
                payload["kind"] = "sharp"
            else:
                payload["operand"]["values"][0] = 8
            data["cache_id"] = (
                "grcv4-derived-geometry-cache-sha256:"
                + sha256(canonical_json_bytes(payload)).hexdigest()
            )
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                geometry_stage.GeometryStageCache.from_canonical_bytes(
                    canonical_json_bytes(data),
                    expected_inputs=stage,
                    expected_kind="flat",
                    expected_operand=flux,
                )
        data = json.loads(cache.to_canonical_bytes())
        data["payload"]["inputs"]["step_index"] = False
        with self.assertRaises(ValueError):
            geometry_stage.GeometryStageCache.from_canonical_bytes(
                canonical_json_bytes(data),
                expected_inputs=stage,
                expected_kind="flat",
                expected_operand=flux,
            )

    def test_wrong_operand_roles_foreign_coordinates_and_caller_mutation(self) -> None:
        stage = stage_inputs_fixture()
        ref = stage.geometry.reference
        graph = ref.graph
        for kind, operand in [
            ("flat", OneForm(graph, (4, 6))),
            ("sharp", PhysicalFlux(graph, (4, 6))),
            ("star_assembly", PhysicalFlux(graph, (4, 6))),
            ("arbitrary_callback", OneForm(graph, (4, 6))),
        ]:
            with self.assertRaises(TypeError):
                geometry_stage.GeometryStageCache(stage, kind, operand)  # type: ignore[arg-type]
        foreign = replace(graph, oriented_edges=graph.oriented_edges[::-1])
        with self.assertRaises(ValueError):
            geometry_stage.GeometryStageCache(
                stage, "flat", PhysicalFlux(foreign, (4, 6))
            )
        data = stage.to_payload()
        restored = geometry_stage.GeometryStageInputs.from_payload(data)
        before = restored.to_payload()
        data["current"] = {"C": [99], "W_A": None, "Z_4": None}
        self.assertEqual(restored.to_payload(), before)
        flux = PhysicalFlux(graph, (4, 6))
        cache = geometry_stage.GeometryStageCache(restored, "flat", flux)
        before_bytes = cache.to_canonical_bytes()
        with self.assertRaises(ValueError):
            cache.consume(
                expected_inputs=replace(restored, operation_id="different"),
                expected_kind="flat",
                expected_operand=flux,
            )
        self.assertEqual(cache.to_canonical_bytes(), before_bytes)

    def test_mutation_control_detects_omitted_stage_guard(self) -> None:
        stage = stage_inputs_fixture(stage="os_predictor")
        flux = PhysicalFlux(stage.geometry.reference.graph, (4, 6))
        cache = geometry_stage.GeometryStageCache(stage, "flat", flux)

        def unsafe(
            cache: geometry_stage.GeometryStageCache, **kwargs: object
        ) -> geometry_stage.GeometryOutput:
            return cache.value

        with patch.object(geometry_stage.GeometryStageCache, "consume", unsafe):
            with self.assertRaises(AssertionError):
                with self.assertRaises(ValueError):
                    cache.consume(
                        expected_inputs=replace(stage, stage="os_corrector"),
                        expected_kind="flat",
                        expected_operand=flux,
                    )

    def test_stage_reconstruction_outside_checkout_and_hash_seed_independence(
        self,
    ) -> None:
        inputs = stage_inputs_fixture().to_payload()
        expected = reconstruct_stage(inputs)
        environment = {
            k: v for k, v in os.environ.items() if k not in {"PYTHONPATH", "PYTHONHOME"}
        }
        with tempfile.TemporaryDirectory(prefix="grcv4-p932-replay-") as directory:
            root = Path(directory)
            consumer = root / "consumer.py"
            source = Path(__file__).read_text()
            consumer.write_text(source)
            payload = root / "inputs.json"
            payload.write_text(json.dumps(inputs))
            for seed in ("0", "1", "932"):
                run = subprocess.run(
                    [
                        sys.executable,
                        str(consumer),
                        "--reconstruct-stage",
                        str(payload),
                    ],
                    cwd=root,
                    env={**environment, "PYTHONHASHSEED": seed},
                    text=True,
                    capture_output=True,
                    check=True,
                )
                self.assertEqual(json.loads(run.stdout), expected)


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--reconstruct":
        print(
            json.dumps(
                reconstruct(json.loads(Path(sys.argv[2]).read_text())), sort_keys=True
            )
        )
    elif len(sys.argv) == 3 and sys.argv[1] == "--reconstruct-stage":
        print(
            json.dumps(
                reconstruct_stage(json.loads(Path(sys.argv[2]).read_text())),
                sort_keys=True,
            )
        )
    else:
        unittest.main()

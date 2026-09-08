"""P9-4.1 reference-map and P9-4.2 fixed-stage current pressure.

Expectations use scalar rational products, explicit coordinate permutations
and independent ASCII hashing. Profile helpers construct inputs only.
"""

from __future__ import annotations

from copy import deepcopy
from contextlib import contextmanager
from dataclasses import FrozenInstanceError, replace
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import random
import sys
from types import ModuleType
from typing import Any, Callable, Iterator
import unittest

from pygrc.models.grc_v4_candidate_c import CandidateCTransport
from pygrc.models.grc_v4_codec import canonical_json_bytes, payload_identity
from pygrc.models.grc_v4_geometry import (
    GRCV4Graph,
    GRCV4Geometry,
    OneForm,
    OneFormHodge,
    OrientedEdge,
    PhysicalFlux,
    PhysicalFluxFlatMap,
    VertexScalar,
)
from pygrc.models.grc_v4_profile import GRCV4Profile, resolve_profile
from tests.models.test_grc_v4_geometry import (
    _P934Result,
    _p934_coverage,
    _p934_ids,
    _p934_loaded_sources,
    graph_payload,
    stage_reference_fixture,
)
from tests.models.test_grc_v4_profile import family_fixture, reidentify


def profile_fixture(
    weights: dict[str, Any] | None = None,
    *,
    eta: float = 3,
    realization: str = "OS",
    changes: dict[str, dict[str, Any]] | None = None,
) -> GRCV4Profile:
    weights = {"a": 5, "z": 2} if weights is None else weights
    params, identity = family_fixture("C", realization)
    params["candidate"].update(
        W_C_tr=weights,
        W_C_tr_content_digest=payload_identity(
            "wctr_identity_payload",
            {"schema_version": "grcv4-wctr-identity-v1", "W_C_tr": weights},
        ),
        eta_C=eta,
    )
    params["geometry"]["reference_hodge_digest"] = payload_identity(
        "reference_hodge_identity_payload",
        {
            "schema_version": "grcv4-reference-hodge-identity-v1",
            "edge_weights": weights,
        },
    )
    if changes:
        for group, updates in changes.items():
            if group == "identity":
                identity.update(updates)
            else:
                params[group].update(updates)
    reidentify(params, identity)
    return resolve_profile(params, identity)


class CandidateCReferenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.graph = GRCV4Graph.from_payload(graph_payload())
        self.binding = CandidateCTransport(self.graph, profile_fixture())

    def test_exact_siblings_and_typed_operator_actions(self) -> None:
        bound = self.binding
        self.assertEqual(bound.params.transport_id, "C-HM-STIFFNESS-BASELINE-v1")
        self.assertEqual(bound.structural_hodge.matrix, ((2, 0), (0, 5)))
        self.assertEqual(bound.mobility.matrix, ((6, 0), (0, 15)))
        self.assertIs(type(bound.structural_hodge), OneFormHodge)
        self.assertEqual(
            bound.mobility.apply(OneForm(self.graph, (2, -3))),
            PhysicalFlux(self.graph, (12, -45)),
        )
        self.assertEqual(
            PhysicalFluxFlatMap(bound.structural_hodge)
            .flat(PhysicalFlux(self.graph, (4, 10)))
            .values,
            (2, 2),
        )
        with self.assertRaises(TypeError):
            PhysicalFluxFlatMap(bound.mobility)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            bound.mobility.apply(PhysicalFlux(self.graph, (2, 3)))  # type: ignore[arg-type]

    def test_equal_matrices_still_have_separate_constructor_identities(self) -> None:
        bound = CandidateCTransport(self.graph, profile_fixture(eta=1))
        self.assertEqual(bound.structural_hodge.matrix, bound.mobility.matrix)
        self.assertNotEqual(
            bound.structural_hodge_constructor_identity,
            bound.mobility_constructor_identity,
        )
        # Independent JSON/SHA oracle for these ASCII, integer-token payloads.
        for payload, identity, policy, kind in [
            (
                bound.structural_hodge_constructor_payload,
                bound.structural_hodge_constructor_identity,
                "diag_W_C_tr_structural_hodge_v1",
                "one_form_hodge",
            ),
            (
                bound.mobility_constructor_payload,
                bound.mobility_constructor_identity,
                "eta_C_diag_W_C_tr_mobility_v1",
                "physical_flux_mobility",
            ),
        ]:
            self.assertEqual(payload["constructor_id"], policy)
            self.assertEqual(payload["output_type"], kind)
            expected = hashlib.sha256(
                json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest()
            self.assertEqual(
                identity, "grcv4-c-reference-constructor-sha256:" + expected
            )

    def test_gain_changes_only_mobility_constructor(self) -> None:
        altered = CandidateCTransport(self.graph, profile_fixture(eta=7))
        self.assertEqual(altered.mobility.diagonal, (14, 35))
        self.assertEqual(altered.structural_hodge, self.binding.structural_hodge)
        self.assertEqual(
            altered.structural_hodge_constructor_identity,
            self.binding.structural_hodge_constructor_identity,
        )
        self.assertNotEqual(
            altered.mobility_constructor_identity,
            self.binding.mobility_constructor_identity,
        )
        self.assertNotEqual(altered.identity, self.binding.identity)

    def test_map_value_and_stable_id_are_identity_inputs(self) -> None:
        for weights in [{"a": 5, "z": 3}, {"a": 2, "z": 5}]:
            altered = CandidateCTransport(self.graph, profile_fixture(weights))
            self.assertNotEqual(
                altered.params.W_C_tr_content_digest,
                self.binding.params.W_C_tr_content_digest,
            )
            self.assertNotEqual(
                altered.structural_hodge_constructor_identity,
                self.binding.structural_hodge_constructor_identity,
            )
            self.assertNotEqual(
                altered.mobility_constructor_identity,
                self.binding.mobility_constructor_identity,
            )
        reordered = CandidateCTransport(self.graph, profile_fixture({"z": 2, "a": 5}))
        self.assertEqual(
            reordered.to_canonical_bytes(), self.binding.to_canonical_bytes()
        )
        self.assertEqual(reordered.identity, self.binding.identity)

    def test_unrelated_profile_controls_do_not_condition_reference_constructors(
        self,
    ) -> None:
        for changes in [
            {"candidate": {name: value}}
            for name, value in [
                ("kappa_M_C", 0),
                ("kappa_M_C", 19),
                ("chi_C", 0),
                ("zeta_C", 0),
                ("tau_C", 0),
                ("C_ref", 17),
                ("Lambda_C", 11),
                ("kappa_Phi_C", 23),
            ]
        ] + [{"geometry": {"kappa_H": 9}}]:
            with self.subTest(changes=changes):
                bound = CandidateCTransport(
                    self.graph, profile_fixture(changes=changes)
                )
                self.assertEqual(bound.mobility.matrix, self.binding.mobility.matrix)
                self.assertEqual(
                    bound.structural_hodge_constructor_identity,
                    self.binding.structural_hodge_constructor_identity,
                )
                self.assertEqual(
                    bound.mobility_constructor_identity,
                    self.binding.mobility_constructor_identity,
                )
                if bound.profile != self.binding.profile:
                    self.assertNotEqual(bound.identity, self.binding.identity)

    def test_all_five_declarations_bind_without_advertising_execution(self) -> None:
        from pygrc.models.grc_v4_profile import list_supported_profiles

        for realization in ["OS", "CI", "RG2b", "PC", "CI+PC"]:
            with self.subTest(realization=realization):
                bound = CandidateCTransport(
                    self.graph, profile_fixture(realization=realization)
                )
                self.assertEqual(
                    bound.mobility_constructor_identity,
                    self.binding.mobility_constructor_identity,
                )
                self.assertEqual(
                    bound.profile.identity_payload.realization, realization
                )
        self.assertEqual(list_supported_profiles(), frozenset())

    def test_units_declaration_is_part_of_each_typed_constructor_identity(self) -> None:
        bound = CandidateCTransport(
            self.graph,
            profile_fixture(
                changes={
                    "common": {"units_id": "test_alternative_units_v1"},
                    "identity": {"units_id": "test_alternative_units_v1"},
                }
            ),
        )
        self.assertEqual(bound.mobility.matrix, self.binding.mobility.matrix)
        self.assertNotEqual(
            bound.mobility_constructor_identity,
            self.binding.mobility_constructor_identity,
        )
        self.assertNotEqual(
            bound.structural_hodge_constructor_identity,
            self.binding.structural_hodge_constructor_identity,
        )
        # These are declarations. No unit conversion or executable-profile
        # admission is inferred for this alternative synthetic unit policy.

    def test_complete_reference_geometry_agrees_with_sibling_hodge(self) -> None:
        reference = stage_reference_fixture()
        bound = CandidateCTransport(reference.graph, reference.profile)
        self.assertEqual(bound.structural_hodge, reference.pairings.one_form)
        for matrix in [((2.0, 0.0), (0.0, 7.0)), ((9.0, 2.0), (2.0, 3.0))]:
            trial = GRCV4Geometry(reference, OneFormHodge(reference.graph, matrix))
            self.assertNotEqual(trial.one_form_hodge, bound.structural_hodge)
            rebuilt = CandidateCTransport(
                trial.reference.graph, trial.reference.profile
            )
            self.assertEqual(rebuilt.mobility.matrix, bound.mobility.matrix)
            self.assertEqual(
                rebuilt.mobility_constructor_identity,
                bound.mobility_constructor_identity,
            )
            with self.assertRaises(TypeError):
                CandidateCTransport(reference.graph, trial)  # type: ignore[arg-type]

        with self.assertRaises(TypeError):
            CandidateCTransport(reference.graph, reference.geometry())  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            CandidateCTransport(reference.graph, bound.structural_hodge)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            replace(bound, h=reference.geometry())  # type: ignore[call-arg]

    def test_reference_hodge_mismatch_rejects_even_with_reidentified_profile(
        self,
    ) -> None:
        wrong = payload_identity(
            "reference_hodge_identity_payload",
            {
                "schema_version": "grcv4-reference-hodge-identity-v1",
                "edge_weights": {"z": 5, "a": 2},
            },
        )
        profile = profile_fixture(
            changes={"geometry": {"reference_hodge_digest": wrong}}
        )
        with self.assertRaises(ValueError):
            CandidateCTransport(self.graph, profile)

    def test_map_must_cover_exact_target_edges_without_copy_or_resize(self) -> None:
        for weights in [
            {"z": 2},
            {"a": 5},
            {"z": 2, "a": 5, "extra": 1},
            {"a": 5, "renamed-z": 2},
        ]:
            with (
                self.subTest(weights=weights),
                self.assertRaisesRegex(ValueError, "exactly"),
            ):
                CandidateCTransport(self.graph, profile_fixture(weights))

    def test_map_domain_and_gain_reject_without_repair(self) -> None:
        invalid: list[Any] = [
            0,
            -0.0,
            -1,
            True,
            None,
            "2",
            [],
            {},
            math.inf,
            -math.inf,
            math.nan,
            2**53,
        ]
        for bad in invalid:
            with self.subTest(weight=bad), self.assertRaises((TypeError, ValueError)):
                profile_fixture({"a": 5, "z": bad})
            with self.subTest(gain=bad), self.assertRaises((TypeError, ValueError)):
                profile_fixture(eta=bad)
        for weights in [{}, {"": 2, "a": 5}, {1: 2, "a": 5}]:
            with (
                self.subTest(weights=weights),
                self.assertRaises((TypeError, ValueError)),
            ):
                profile_fixture(weights)  # type: ignore[arg-type]

    def test_transport_and_constructor_policy_ids_cannot_be_substituted(self) -> None:
        for name, bad in [
            ("transport_id", "C-HM-STIFFNESS-BASELINE-v2"),
            ("E_H_policy_id", "eta_C_diag_W_C_tr_mobility_v1"),
            ("E_M_policy_id", "diag_W_C_tr_structural_hodge_v1"),
        ]:
            with self.subTest(name=name), self.assertRaises(ValueError):
                profile_fixture(changes={"candidate": {name: bad}})

    def test_complete_profile_and_map_identity_tampering_rejects(self) -> None:
        original: Any = self.binding.to_payload()
        for field in [
            "complete_profile_id",
            "params_hash",
            "W_C_tr_content_digest",
            "W_C_tr",
        ]:
            value = deepcopy(original)
            profile = value["profile"]
            if field == "complete_profile_id":
                profile[field] = profile[field][:-1] + (
                    "0" if profile[field][-1] != "0" else "1"
                )
            elif field == "params_hash":
                profile["identity_payload"][field] = "grcv4-params-sha256:" + "0" * 64
            elif field == "W_C_tr":
                profile["params_resolved"]["candidate"][field]["z"] = 7
            else:
                profile["params_resolved"]["candidate"][field] = (
                    "grcv4-wctr-sha256:" + "0" * 64
                )
            with self.subTest(field=field), self.assertRaises(ValueError):
                CandidateCTransport.from_payload(value)
        self.assertEqual(original, self.binding.to_payload())

    def test_binary64_positive_extremes_and_product_boundaries(self) -> None:
        tiny = math.ulp(0.0)
        for eta, weight in [
            (1, tiny),
            (1, sys.float_info.max),
            (tiny, sys.float_info.max),
            (sys.float_info.max, tiny),
            (0.5, 2 * tiny),
            (2, sys.float_info.max / 2),
            (0.1, 0.3),
            (math.nextafter(1, 2), tiny),
        ]:
            with self.subTest(eta=eta, weight=weight):
                expected = float(Fraction(eta) * Fraction(weight))
                bound = CandidateCTransport(
                    self.graph, profile_fixture({"z": weight, "a": weight}, eta=eta)
                )
                self.assertEqual(bound.mobility.diagonal, (expected, expected))
                self.assertGreater(expected, 0)
                self.assertEqual(
                    CandidateCTransport.from_canonical_bytes(
                        bound.to_canonical_bytes()
                    ),
                    bound,
                )
        for eta, weight in [(0.5, tiny), (tiny, tiny), (2, sys.float_info.max)]:
            with self.subTest(eta=eta, weight=weight), self.assertRaises(ValueError):
                CandidateCTransport(
                    self.graph, profile_fixture({"z": weight, "a": weight}, eta=eta)
                )

    def test_random_scalar_rational_oracle_across_wide_exponents(self) -> None:
        rng = random.Random(941)
        for _ in range(80):
            eta = math.ldexp(rng.uniform(0.5, 1), rng.randint(-500, 500))
            weights = {
                edge: math.ldexp(rng.uniform(0.5, 1), rng.randint(-500, 500))
                for edge in reversed(self.graph.live_edge_ids)
            }
            bound = CandidateCTransport(self.graph, profile_fixture(weights, eta=eta))
            self.assertEqual(
                bound.mobility.diagonal,
                tuple(
                    float(Fraction(eta) * Fraction(weights[e]))
                    for e in self.graph.live_edge_ids
                ),
            )

    def test_graph_outliers_and_signed_permutation_covariance(self) -> None:
        # Loops, parallel edges, disconnected components and an isolated vertex.
        edges = (
            OrientedEdge("parallel-2", "u", "v"),
            OrientedEdge("loop", "u", "u"),
            OrientedEdge("parallel-1", "u", "v"),
            OrientedEdge("far", "x", "y"),
        )
        graph = GRCV4Graph(("u", "v", "x", "y", "isolated"), edges)
        weights = {"far": 7, "parallel-1": 5, "loop": 3, "parallel-2": 2}
        base = CandidateCTransport(graph, profile_fixture(weights))
        form = (2, 3, -4, 5)
        flux = base.mobility.apply(OneForm(graph, form)).values
        rng = random.Random(941)
        for _ in range(30):
            order = rng.sample(range(4), 4)
            signs = [rng.choice([-1, 1]) for _ in order]
            target_edges = tuple(
                OrientedEdge(
                    edges[i].edge_id,
                    edges[i].tail_node_id if sign == 1 else edges[i].head_node_id,
                    edges[i].head_node_id if sign == 1 else edges[i].tail_node_id,
                )
                for i, sign in zip(order, signs, strict=True)
            )
            target = GRCV4Graph(tuple(reversed(graph.live_node_ids)), target_edges)
            bound = CandidateCTransport(target, base.profile)
            moved_form = tuple(
                sign * form[i] for i, sign in zip(order, signs, strict=True)
            )
            self.assertEqual(
                bound.mobility.apply(OneForm(target, moved_form)).values,
                tuple(sign * flux[i] for i, sign in zip(order, signs, strict=True)),
            )
            self.assertEqual(
                bound.params.W_C_tr_content_digest, base.params.W_C_tr_content_digest
            )
            self.assertEqual(
                bound.structural_hodge.matrix,
                tuple(
                    tuple(weights[edges[i].edge_id] if i == j else 0 for j in order)
                    for i in order
                ),
            )
        renamed = GRCV4Graph(
            graph.live_node_ids,
            tuple(replace(e, edge_id="new:" + e.edge_id) for e in edges),
        )
        with self.assertRaises(ValueError):
            CandidateCTransport(renamed, base.profile)
        readmitted = CandidateCTransport(
            renamed, profile_fixture({"new:" + e: v for e, v in weights.items()})
        )
        self.assertEqual(readmitted.mobility.matrix, base.mobility.matrix)
        self.assertNotEqual(
            readmitted.mobility_constructor_identity, base.mobility_constructor_identity
        )

    def test_unicode_and_numeric_looking_edge_ids_roundtrip(self) -> None:
        graph = GRCV4Graph(
            (1, "1"),
            (
                OrientedEdge("e\u0301", 1, "1"),
                OrientedEdge("é", "1", 1),
                OrientedEdge("01", 1, 1),
                OrientedEdge("1", "1", "1"),
            ),
        )
        bound = CandidateCTransport(
            graph, profile_fixture({"1": 7, "01": 5, "é": 3, "e\u0301": 2})
        )
        self.assertEqual(bound.mobility.diagonal, (6, 9, 15, 21))
        restored = CandidateCTransport.from_canonical_bytes(bound.to_canonical_bytes())
        self.assertEqual(restored, bound)
        self.assertEqual(restored.identity, bound.identity)

    def test_noncanonical_duplicate_or_extra_wire_authority_rejects(self) -> None:
        encoded = self.binding.to_canonical_bytes()
        for wire in [
            b" " + encoded,
            encoded.replace(b'"z":2', b'"z":2,"z":7', 1),
            encoded.replace(b'"z":2', b'"z":NaN', 1),
        ]:
            with self.subTest(data=wire[:40]), self.assertRaises(ValueError):
                CandidateCTransport.from_canonical_bytes(wire)
        for name in [
            "mobility",
            "structural_hodge",
            "C",
            "h",
            "history",
            "constructor_id",
        ]:
            data: Any = self.binding.to_payload()
            data[name] = [[2, 0], [0, 5]]
            before = canonical_json_bytes(data)
            with self.subTest(name=name), self.assertRaises(ValueError):
                CandidateCTransport.from_payload(data)
            self.assertEqual(canonical_json_bytes(data), before)

    def test_no_mutable_source_or_output_aliases(self) -> None:
        data: Any = self.binding.to_payload()
        restored = CandidateCTransport.from_payload(data)
        expected = restored.to_canonical_bytes()
        data["profile"]["params_resolved"]["candidate"]["W_C_tr"]["z"] = 19
        projected: Any = restored.to_payload()
        projected["graph"]["live_node_ids"].append("extra")
        descriptor = restored.mobility_constructor_payload
        descriptor["eta_C"] = 0
        self.assertEqual(restored.to_canonical_bytes(), expected)
        self.assertEqual(restored.mobility.diagonal, (6, 15))
        with self.assertRaises(FrozenInstanceError):
            restored.mobility = self.binding.mobility  # type: ignore[misc]
        with self.assertRaises(TypeError):
            restored.params.W_C_tr["z"] = 9  # type: ignore[index]

    def test_wrong_candidate_bare_params_and_graph_duplicates_reject(self) -> None:
        ref = stage_reference_fixture(candidate="A")
        for source in [
            ref.profile,
            self.binding.params,
            self.binding.profile.to_payload(),
            None,
        ]:
            with self.subTest(source=type(source)), self.assertRaises(TypeError):
                CandidateCTransport(self.graph, source)  # type: ignore[arg-type]
        data = graph_payload()
        data["oriented_edges"].append(data["oriented_edges"][0].copy())
        with self.assertRaises(ValueError):
            GRCV4Graph.from_payload(data)
        # Schema requires a nonempty C map; an edgeless target cannot bind it.
        with self.assertRaises(ValueError):
            CandidateCTransport(GRCV4Graph(("isolated",), ()), self.binding.profile)


def current_fixture(
    *,
    graph: GRCV4Graph | None = None,
    weights: dict[str, float] | None = None,
    hodge: tuple[tuple[float, ...], ...] | None = None,
    resource: tuple[float, ...] | None = None,
    realization: str = "OS",
    stage: str = "pre_read",
    changes: dict[str, dict[str, Any]] | None = None,
) -> Any:
    from pygrc.models.grc_v4_geometry import GRCV4Geometry
    from pygrc.models.grc_v4_state import GRCV4AuthoritativeState
    from tests.models.test_grc_v4_geometry import stage_inputs_fixture

    updates = {
        "candidate": {"tau_C": 0.2},
        "solver": {"absolute_tolerance": 1e-11, "relative_tolerance": 1e-11},
    }
    for group, values in (changes or {}).items():
        updates.setdefault(group, {}).update(values)
    ref = stage_reference_fixture(
        "C", realization, graph=graph, weights=weights, changes=updates
    )
    inputs = stage_inputs_fixture(ref, stage=stage)
    if resource is not None:
        state = GRCV4AuthoritativeState(resource, None, inputs.current.Z_4)
        inputs = replace(inputs, current=state, reset=state, Q_target=sum(resource))
    if hodge is not None:
        inputs = replace(
            inputs, geometry=GRCV4Geometry(ref, OneFormHodge(ref.graph, hodge))
        )
    return inputs


def dense_current_oracle(inputs: Any) -> dict[str, Any]:
    """Literal independent dense equations; no production selector/solve helpers."""
    import numpy as np

    ref = inputs.geometry.reference
    p = ref.profile.params_resolved.candidate
    b = np.array(ref.graph.incidence)
    h = np.array(inputs.geometry.one_form_hodge.matrix)
    c = np.array(inputs.current.C)
    values, vectors = np.linalg.eigh(b @ h @ b.T)
    selected = vectors[:, values < p.Lambda_C]
    projector = selected @ selected.T
    sector = projector @ c
    rho = np.tanh(sector / p.C_ref)
    edge_rho = np.array(
        [
            0.5
            * (
                rho[ref.graph.node_index(e.tail_node_id)]
                + rho[ref.graph.node_index(e.head_node_id)]
            )
            for e in ref.graph.oriented_edges
        ]
    )
    d = np.diag(np.exp(0.5 * p.kappa_M_C * edge_rho))
    hm = d @ h @ d
    phi = p.kappa_Phi_C * b @ hm @ b.T @ c
    j0 = -p.eta_C * np.diag([p.W_C_tr[e] for e in ref.graph.live_edge_ids]) @ b.T @ phi
    ident = hm @ np.linalg.inv(h)
    q = ident @ np.linalg.inv(h)
    delta = b.T @ b @ hm
    response = np.linalg.inv(np.eye(len(h)) + p.tau_C * delta)
    flux_response = np.linalg.inv(q) @ response @ q
    block = np.eye(len(h)) - p.zeta_C * p.chi_C * flux_response
    current = np.linalg.solve(block, j0)
    return dict(
        projector=projector,
        sector=sector,
        hm=hm,
        phi=phi,
        j0=j0,
        ident=ident,
        q=q,
        delta=delta,
        response=response,
        flux_response=flux_response,
        block=block,
        current=current,
        read=p.chi_C * flux_response @ current,
    )


class CandidateCCurrentTests(unittest.TestCase):
    @staticmethod
    def edge_graph() -> GRCV4Graph:
        return GRCV4Graph(("u", "v"), (OrientedEdge("e", "u", "v"),))

    def test_scalar_chain_has_literal_independent_solution(self) -> None:
        from pygrc.models.grc_v4_candidate_c import CandidateCCurrent

        inputs = current_fixture(
            graph=self.edge_graph(),
            weights={"e": 2},
            resource=(3, 1),
            changes={
                "candidate": {
                    "kappa_M_C": 0,
                    "eta_C": 0.5,
                    "kappa_Phi_C": 1,
                    "tau_C": 0.25,
                    "zeta_C": 0.5,
                    "chi_C": 0.5,
                }
            },
        )
        actual = CandidateCCurrent(inputs)
        self.assertEqual(actual.algebra.selector.projector, ((0.5, 0.5), (0.5, 0.5)))
        self.assertEqual(actual.algebra.selector.selected.values, (2, 2))
        self.assertEqual(actual.algebra.potential.values, (4, -4))
        self.assertEqual(actual.algebra.baseline.values, (-8,))
        self.assertEqual(actual.algebra.response, ((0.5,),))
        self.assertEqual(actual.algebra.current_block, ((0.875,),))
        self.assertEqual(actual.current.values, (-64 / 7,))
        self.assertEqual(actual.read.flux.values, (-16 / 7,))
        self.assertEqual(actual.read.causal_flat.values, (-8 / 7,))
        residual = Fraction(-64 / 7) + 8 - Fraction(1, 2) * Fraction(-16 / 7)
        self.assertEqual(actual.closure_residual_squared, str(residual**2))

    def test_scalar_random_controls_against_closed_formula(self) -> None:
        from pygrc.models.grc_v4_candidate_c import CandidateCCurrent

        rng = random.Random(942)
        for case in range(30):
            weight = 2.0 ** rng.randint(-3, 3)
            c0, c1 = rng.uniform(0, 2), rng.uniform(0, 2)
            km, kphi, eta = rng.uniform(-1, 1), rng.uniform(-2, 2), rng.uniform(0.2, 2)
            tau, chi, zeta = (
                rng.uniform(0, 1),
                rng.uniform(-1, 1),
                rng.uniform(-0.5, 0.8),
            )
            inputs = current_fixture(
                graph=self.edge_graph(),
                weights={"e": weight},
                resource=(c0, c1),
                changes={
                    "candidate": {
                        "Lambda_C": weight,
                        "kappa_M_C": km,
                        "kappa_Phi_C": kphi,
                        "eta_C": eta,
                        "tau_C": tau,
                        "chi_C": chi,
                        "zeta_C": zeta,
                    }
                },
            )
            with self.subTest(case=case):
                actual = CandidateCCurrent(inputs)
                hm = weight * math.exp(km * math.tanh((c0 + c1) / 2))
                j0 = -2 * eta * weight * kphi * hm * (c0 - c1)
                expected = j0 * (1 + 2 * tau * hm) / (1 + 2 * tau * hm - zeta * chi)
                self.assertAlmostEqual(
                    actual.current.values[0],
                    expected,
                    delta=2e-12 * max(1, abs(expected)),
                )
                self.assertAlmostEqual(
                    actual.read.flux.values[0],
                    chi * expected / (1 + 2 * tau * hm),
                    delta=2e-12 * max(1, abs(expected)),
                )

    def test_frozen_weighted_three_node_algebra_vector(self) -> None:
        from pygrc.models.grc_v4_candidate_c import _CandidateCAlgebra, _c_solve
        from pygrc.models.grc_v4_geometry import VertexScalar, reference_pairings

        vector = json.loads(
            (
                Path(__file__).resolve().parents[2]
                / "specs/grc-v4-conformance-vectors.json"
            ).read_text()
        )["candidate_c_algebra_vectors"][0]
        data, expected = vector["inputs"], vector["expected"]
        graph = GRCV4Graph(
            ("a", "b", "c"),
            (OrientedEdge("e0", "b", "a"), OrientedEdge("e1", "c", "b")),
        )
        inputs = current_fixture(
            graph=graph,
            weights={"e0": 2, "e1": 3},
            resource=tuple(data["C"]),
            changes={
                "candidate": {
                    "Lambda_C": 4,
                    "eta_C": data["eta_C"],
                    "kappa_M_C": data["kappa_M_C"],
                    "kappa_Phi_C": data["kappa_Phi_C"],
                    "tau_C": data["resolvent_tau_C"],
                    "zeta_C": data["zeta_C"],
                    "chi_C": data["chi_C"],
                }
            },
        )
        algebra = _CandidateCAlgebra(
            CandidateCTransport(graph, inputs.geometry.reference.profile),
            VertexScalar(graph, tuple(data["C"])),
            reference_pairings(
                graph,
                vertex_measure=tuple(data["H0_diagonal"]),
                reference_edge_weights=tuple(data["W_C_tr"]),
            ),
        )
        policy = inputs.geometry.reference.profile.params_resolved.solver
        total = PhysicalFlux(
            graph,
            tuple(
                r[0]
                for r in _c_solve(
                    algebra.current_block,
                    tuple((x,) for x in algebra.baseline.values),
                    policy,
                    "algebra witness",
                    [],
                )
            ),
        )
        read = algebra.read_back(total, "algebra_witness_only")
        for field, actual in {
            "baseline_potential": algebra.potential.values,
            "baseline_current": algebra.baseline.values,
            "total_current": total.values,
            "read_current": read.flux.values,
            "retained_h1_diagonal": tuple(
                algebra.retained_hodge.matrix[i][i] for i in range(2)
            ),
        }.items():
            for value, target in zip(actual, expected[field], strict=True):
                self.assertAlmostEqual(value, target, delta=1e-12, msg=field)
        self.assertEqual(algebra.selector.rank, 2)

    def test_dense_nonreference_hodge_matches_literal_equations(self) -> None:
        import numpy as np
        from pygrc.models.grc_v4_candidate_c import CandidateCCurrent

        inputs = current_fixture(
            hodge=((3, 0.75), (0.75, 1.5)),
            resource=(0.2, 1.5, 2.4),
            changes={
                "candidate": {
                    "Lambda_C": 3,
                    "kappa_M_C": 0.7,
                    "chi_C": 0.6,
                    "zeta_C": 0.4,
                }
            },
        )
        actual = CandidateCCurrent(inputs)
        expected = dense_current_oracle(inputs)
        for field, value in {
            "projector": actual.algebra.selector.projector,
            "sector": actual.algebra.selector.selected.values,
            "hm": actual.algebra.retained_hodge.matrix,
            "phi": actual.algebra.potential.values,
            "j0": actual.algebra.baseline.values,
            "ident": actual.algebra.identification,
            "q": actual.algebra.physical_identification,
            "delta": actual.algebra.laplacian,
            "response": actual.algebra.response,
            "flux_response": actual.algebra.flux_response,
            "block": actual.algebra.current_block,
            "current": actual.current.values,
            "read": actual.read.flux.values,
        }.items():
            np.testing.assert_allclose(
                np.asarray(value, dtype=float),
                expected[field],
                rtol=3e-12,
                atol=3e-12,
                err_msg=field,
            )
        self.assertNotEqual(
            actual.algebra.retained_hodge.matrix,
            actual.algebra.transport.structural_hodge.matrix,
        )
        self.assertNotEqual(
            actual.algebra.physical_identification, actual.algebra.flat_matrix
        )
        self.assertNotEqual(actual.algebra.flux_response, actual.algebra.response)

    def test_selector_ties_zero_and_exterior_strata(self) -> None:
        from pygrc.models.grc_v4_candidate_c import CandidateCCurrent

        for cutoff, rank in [(-1, 0), (0.5, 1), (3, 2)]:
            with self.subTest(cutoff=cutoff):
                actual = CandidateCCurrent(
                    current_fixture(
                        graph=self.edge_graph(),
                        weights={"e": 1},
                        changes={"candidate": {"Lambda_C": cutoff}},
                    )
                )
                self.assertEqual(actual.algebra.selector.rank, rank)
        for cutoff in (0, 2):
            with (
                self.subTest(cutoff=cutoff),
                self.assertRaisesRegex(ValueError, "exact spectrum"),
            ):
                CandidateCCurrent(
                    current_fixture(
                        graph=self.edge_graph(),
                        weights={"e": 1},
                        changes={"candidate": {"Lambda_C": cutoff}},
                    )
                )
        for cutoff, rank in [
            (math.nextafter(2, 0), 1),
            (math.nextafter(2, math.inf), 2),
        ]:
            actual = CandidateCCurrent(
                current_fixture(
                    graph=self.edge_graph(),
                    weights={"e": 1},
                    changes={"candidate": {"Lambda_C": cutoff}},
                )
            )
            self.assertEqual(actual.algebra.selector.rank, rank)

    def test_exact_inertia_handles_zero_diagonal_pivots(self) -> None:
        from pygrc.models.grc_v4_candidate_c import _c_inertia

        for matrix, expected in [
            (((0, 2), (2, 0)), (1, 0, 1)),
            (((0, 0), (0, 0)), (0, 2, 0)),
            (((0, 2, 0), (2, 0, 0), (0, 0, 0)), (1, 1, 1)),
            (((1, 1), (1, 1)), (0, 1, 1)),
            (((-1, 0), (0, 2)), (1, 0, 1)),
        ]:
            self.assertEqual(
                _c_inertia(tuple(tuple(Fraction(x) for x in row) for row in matrix)),
                expected,
            )

    def test_selector_pair_permutation_sign_and_repeated_cluster_rotations(
        self,
    ) -> None:
        import numpy as np
        from unittest.mock import patch
        from pygrc.models.grc_v4_candidate_c import CandidateCSelector

        graph = GRCV4Graph(
            (0, 1, 2, 3), tuple(OrientedEdge(str(i), i, (i + 1) % 4) for i in range(4))
        )
        inputs = current_fixture(
            graph=graph,
            weights={str(i): 1 for i in range(4)},
            resource=(0, 1, 2, 4),
            changes={"candidate": {"Lambda_C": 3}},
        )
        resource = VertexScalar(graph, inputs.current.C)
        real = np.linalg.eigh
        expected = CandidateCSelector(resource, inputs.geometry.pairings, 3)

        def varied(a: Any) -> Any:
            values, vectors = real(a)
            angle = 0.371
            rotation = np.array(
                [
                    [math.cos(angle), -math.sin(angle)],
                    [math.sin(angle), math.cos(angle)],
                ]
            )
            vectors[:, 1:3] = vectors[:, 1:3] @ rotation
            order = [3, 1, 0, 2]
            return values[order], vectors[:, order] * np.array([-1, 1, -1, 1])

        with patch.object(np.linalg, "eigh", side_effect=varied):
            actual = CandidateCSelector(resource, inputs.geometry.pairings, 3)
        np.testing.assert_allclose(
            actual.projector, expected.projector, atol=2e-14, rtol=0
        )
        self.assertEqual(actual.rank, 3)
        self.assertAlmostEqual(sum(actual.selected.values), 7, delta=2e-14)

    def test_selector_rejects_unresolved_or_malformed_decomposition(self) -> None:
        import numpy as np
        from unittest.mock import patch
        from pygrc.models.grc_v4_candidate_c import CandidateCSelector
        from pygrc.models.grc_v4_geometry import VertexScalar

        graph = GRCV4Graph(
            (0, 1, 2), (OrientedEdge("a", 0, 1), OrientedEdge("b", 1, 2))
        )
        inputs = current_fixture(graph=graph, weights={"a": 1, "b": 1})
        resource = VertexScalar(graph, (0, 1, 3))
        for values, vectors in [
            (np.array([0, 1, 3]), np.zeros((3, 3))),
            (np.array([0, float("nan"), 3]), np.eye(3)),
            (np.array([0, 1, 3]), np.eye(3)),
        ]:
            with (
                patch.object(np.linalg, "eigh", return_value=(values, vectors)),
                self.assertRaises(ValueError),
            ):
                CandidateCSelector(resource, inputs.geometry.pairings, 2)
        with self.assertRaisesRegex(ValueError, "unresolved"):
            CandidateCSelector(resource, inputs.geometry.pairings, math.nextafter(3, 0))

    def test_disconnected_isolated_parallel_and_loop_coordinates(self) -> None:
        import numpy as np
        from pygrc.models.grc_v4_candidate_c import CandidateCCurrent

        graph = GRCV4Graph(
            ("u", "v", "w", "x", "isolated"),
            (
                OrientedEdge("parallel2", "u", "v"),
                OrientedEdge("loop", "u", "u"),
                OrientedEdge("other", "x", "w"),
                OrientedEdge("parallel1", "v", "u"),
            ),
        )
        inputs = current_fixture(
            graph=graph,
            weights={e.edge_id: 1 for e in graph.oriented_edges},
            resource=(1, 3, 5, 7, 11),
            changes={"candidate": {"Lambda_C": 0.5}},
        )
        actual = CandidateCCurrent(inputs)
        self.assertEqual(actual.algebra.selector.rank, 3)
        self.assertEqual(actual.algebra.selector.selected.values, (2, 2, 6, 6, 11))
        self.assertEqual(actual.algebra.baseline.values[1], 0)
        self.assertEqual(actual.current.values[1], 0)
        np.testing.assert_allclose(
            actual.current.values, dense_current_oracle(inputs)["current"], atol=2e-12
        )
        self.assertEqual(actual.algebra.potential.values[-1], 0)

    def test_offdiagonal_loop_and_cycle_modes_match_oracle(self) -> None:
        import numpy as np
        from pygrc.models.grc_v4_candidate_c import CandidateCCurrent

        graph = GRCV4Graph(
            (0, 1),
            (OrientedEdge("a", 0, 1), OrientedEdge("b", 1, 0), OrientedEdge("l", 0, 0)),
        )
        inputs = current_fixture(
            graph=graph,
            weights={"a": 1, "b": 1, "l": 1},
            resource=(0.2, 1.7),
            hodge=((2, 0.3, 0.2), (0.3, 1.5, 0.1), (0.2, 0.1, 1)),
            changes={"candidate": {"Lambda_C": 20, "kappa_M_C": 1.1}},
        )
        actual = CandidateCCurrent(inputs)
        expected = dense_current_oracle(inputs)
        np.testing.assert_allclose(
            actual.current.values, expected["current"], atol=2e-12
        )
        self.assertEqual(actual.algebra.baseline.values[2], 0)
        self.assertNotEqual(actual.current.values[2], 0)

    def test_only_loop_graph_has_full_selector_and_harmonic_response(self) -> None:
        from pygrc.models.grc_v4_candidate_c import CandidateCCurrent

        graph = GRCV4Graph(("u",), (OrientedEdge("loop", "u", "u"),))
        actual = CandidateCCurrent(
            current_fixture(graph=graph, weights={"loop": 2}, resource=(3,))
        )
        self.assertEqual(actual.algebra.selector.rank, 1)
        self.assertEqual(actual.current.values, (0,))
        self.assertEqual(actual.algebra.response, ((1,),))
        with self.assertRaisesRegex(ValueError, "singular"):
            CandidateCCurrent(
                current_fixture(
                    graph=graph,
                    weights={"loop": 2},
                    changes={"candidate": {"zeta_C": 0.5, "chi_C": 2}},
                )
            )

    def test_one_chi_gate_linearity_and_zero_input(self) -> None:
        import numpy as np
        from pygrc.models.grc_v4_candidate_c import (
            CandidateCCurrent,
            CandidateCSelectedForm,
        )

        inputs = current_fixture(
            hodge=((2, 0.4), (0.4, 3)),
            changes={"candidate": {"chi_C": 0.25, "zeta_C": 0}},
        )
        actual = CandidateCCurrent(inputs)
        graph = inputs.geometry.reference.graph
        j = PhysicalFlux(graph, (1, -2))
        once = actual.read_back(j)
        double = actual.read_back(PhysicalFlux(graph, (2, -4)))
        np.testing.assert_allclose(
            double.flux.values, np.array(once.flux.values) * 2, atol=1e-14
        )
        self.assertIs(type(once.selected_input), CandidateCSelectedForm)
        self.assertIs(type(once.ungated_flat), OneForm)
        self.assertIs(type(once.flux), PhysicalFlux)
        np.testing.assert_allclose(
            once.causal_flat.values,
            np.array(once.ungated_flat.values) * 0.25,
            atol=1e-14,
        )
        self.assertEqual(
            actual.read_back(PhysicalFlux(graph, (0, 0))).flux.values, (0, 0)
        )
        with self.assertRaises(TypeError):
            actual.read_back(OneForm(graph, (1, 2)))  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            actual.read_back(once.selected_input)  # type: ignore[arg-type]

    def test_zero_controls_are_independent_current_equations(self) -> None:
        import numpy as np
        from pygrc.models.grc_v4_candidate_c import CandidateCCurrent

        def run(**updates: float) -> Any:
            return CandidateCCurrent(
                current_fixture(
                    hodge=((2, 0.4), (0.4, 3)),
                    resource=(0.1, 1.1, 2.3),
                    changes={
                        "candidate": {
                            "Lambda_C": 4,
                            "kappa_M_C": 0.7,
                            "chi_C": 0.6,
                            "zeta_C": 0.4,
                            **updates,
                        }
                    },
                )
            )

        actual = run()
        km = run(kappa_M_C=0)
        chi = run(chi_C=0)
        zeta = run(zeta_C=0)
        tau = run(tau_C=0)
        self.assertNotEqual(actual.algebra.baseline, km.algebra.baseline)
        for neutral in (chi, zeta, tau):
            self.assertEqual(actual.algebra.baseline, neutral.algebra.baseline)
        self.assertEqual(chi.current, chi.algebra.baseline)
        self.assertEqual(zeta.current, zeta.algebra.baseline)
        self.assertEqual(chi.read.flux.values, (0, 0))
        self.assertNotEqual(zeta.read.flux.values, (0, 0))
        np.testing.assert_allclose(
            tau.current.values,
            np.array(tau.algebra.baseline.values) / (1 - 0.4 * 0.6),
            atol=1e-12,
        )
        self.assertNotEqual(
            tau.algebra.retained_hodge, tau.inputs.geometry.one_form_hodge
        )

    def test_singular_current_and_zero_rhs_do_not_get_a_fallback(self) -> None:
        from pygrc.models.grc_v4_candidate_c import CandidateCCurrent

        for resource in ((0, 0), (1, 2)):
            with (
                self.subTest(resource=resource),
                self.assertRaisesRegex(ValueError, "singular"),
            ):
                CandidateCCurrent(
                    current_fixture(
                        graph=self.edge_graph(),
                        weights={"e": 1},
                        resource=resource,
                        changes={"candidate": {"tau_C": 0, "zeta_C": 0.5, "chi_C": 2}},
                    )
                )
        # A negative but regular scalar block is mathematically invertible;
        # declaration alone still does not admit a complete runtime profile.
        actual = CandidateCCurrent(
            current_fixture(
                graph=self.edge_graph(),
                weights={"e": 1},
                resource=(1, 2),
                changes={"candidate": {"tau_C": 0, "zeta_C": 0.5, "chi_C": 3}},
            )
        )
        self.assertEqual(actual.algebra.current_block, ((-0.5,),))
        self.assertEqual(
            actual.current.values, tuple(-2 * x for x in actual.algebra.baseline.values)
        )

    def test_conditioning_bounds_are_checked_in_actual_euclidean_coordinates(
        self,
    ) -> None:
        from pygrc.models.grc_v4_candidate_c import _c_condition

        # Orthogonally rotated singular values 4 and 2: exact equality admits.
        cert = _c_condition(((3, 1), (1, 3)), 2, "physical test")
        self.assertEqual(cert["condition_upper_squared"], "4")
        with self.assertRaisesRegex(ValueError, "conditioning"):
            _c_condition(((3, 1), (1, 3)), math.nextafter(2, 0), "physical test")
        self.assertEqual(
            _c_condition(((1, 0), (0, 1)), 1, "identity")["condition_upper_squared"],
            "1",
        )
        # A similarity retains eigenvalues but can lose a Euclidean margin.
        _c_condition(((0.5, 0), (0, 1)), 2, "retained")
        with self.assertRaisesRegex(ValueError, "conditioning"):
            _c_condition(((0.5, 5), (0, 1)), 2, "physical similarity")

    def test_exact_current_singularity_is_not_hidden_by_rounded_resolvent(self) -> None:
        from pygrc.models.grc_v4_candidate_c import CandidateCCurrent

        # nu=2, tau=1, beta=3: 1-beta/(1+tau*nu)=0 exactly, whereas
        # 1-Fraction(3)*Fraction(1/3) is nonzero. Scalar cond_2 is always 1.
        self.assertNotEqual(1 - 3 * Fraction(1 / 3), 0)
        for resource in ((1, 1), (0, 2)):
            with (
                self.subTest(resource=resource),
                self.assertRaisesRegex(ValueError, "singular"),
            ):
                CandidateCCurrent(
                    current_fixture(
                        graph=self.edge_graph(),
                        weights={"e": 1},
                        resource=resource,
                        changes={
                            "candidate": {
                                "kappa_M_C": 0,
                                "tau_C": 1,
                                "zeta_C": 3,
                                "chi_C": 1,
                            }
                        },
                    )
                )
        # A triangle has a harmonic edge mode for every SPD retained Hodge.
        graph = GRCV4Graph(
            (0, 1, 2),
            (OrientedEdge("a", 0, 1), OrientedEdge("b", 1, 2), OrientedEdge("c", 2, 0)),
        )
        with self.assertRaisesRegex(ValueError, "singular"):
            CandidateCCurrent(
                current_fixture(
                    graph=graph,
                    weights={"a": 1, "b": 1, "c": 1},
                    resource=(0.2, 1, 3),
                    hodge=((3, 0.5, 0.25), (0.5, 2, 0.5), (0.25, 0.5, 1)),
                    changes={"candidate": {"chi_C": 1, "zeta_C": 1}},
                )
            )

    def test_positive_pairing_audit_witness_reaches_current_conditioning_guard(
        self,
    ) -> None:
        from pygrc.models.grc_v4_candidate_c import CandidateCCurrent

        graph = GRCV4Graph((0, 1), (OrientedEdge("a", 0, 1), OrientedEdge("b", 0, 1)))
        witness = ((1.0, 0.1), (0.1, 0.010000000000000002))
        self.assertGreater(Fraction(witness[1][1]) - Fraction(witness[0][1]) ** 2, 0)
        for scale in (-400, 0, 400):
            for signs in ((1, 1), (1, -1)):
                hodge = tuple(
                    tuple(
                        math.ldexp(x * signs[i] * signs[j], scale)
                        for j, x in enumerate(row)
                    )
                    for i, row in enumerate(witness)
                )
                inputs = current_fixture(
                    graph=graph,
                    weights={"a": 1, "b": 1},
                    hodge=hodge,
                    changes={
                        "candidate": {"kappa_M_C": 0, "Lambda_C": -1},
                        "solver": {"conditioning_limit": 1e12},
                    },
                )
                before = canonical_json_bytes(inputs.to_payload())
                with (
                    self.subTest(scale=scale, signs=signs),
                    self.assertRaisesRegex(
                        ValueError, "conditioning limit exceeded: structural flat map"
                    ),
                ):
                    CandidateCCurrent(inputs)
                self.assertEqual(canonical_json_bytes(inputs.to_payload()), before)

    def test_seeded_dense_spd_multigraphs_against_independent_equations(self) -> None:
        import numpy as np
        from pygrc.models.grc_v4_candidate_c import CandidateCCurrent

        rng = np.random.default_rng(94242)
        for case in range(12):
            edges = [
                OrientedEdge("a", 0, 1),
                OrientedEdge("b", 1, 2),
                OrientedEdge("c", 2, 0),
            ]
            if case % 2:
                edges.append(OrientedEdge("l", 1, 1))
            graph = GRCV4Graph((0, 1, 2), tuple(edges))
            a = rng.integers(-2, 3, size=(len(edges), len(edges)))
            h = (a.T @ a + np.eye(len(edges))) / 4
            b = np.array(graph.incidence)
            eig = np.linalg.eigvalsh(b @ h @ b.T)
            cutoff = float((eig[1] + eig[2]) / 2)
            # Avoid repeated nonzero clusters for this partial-projector oracle;
            # exact repeated-cluster rotation has its own deterministic test.
            if eig[2] - eig[1] < 0.01:
                cutoff = 0.01
            inputs = current_fixture(
                graph=graph,
                weights={e.edge_id: float(2 ** (i - 1)) for i, e in enumerate(edges)},
                hodge=tuple(tuple(float(x) for x in row) for row in h),
                resource=tuple(float(x) for x in rng.uniform(0, 3, size=3)),
                changes={
                    "candidate": {
                        "Lambda_C": cutoff,
                        "kappa_M_C": float(rng.uniform(-0.8, 0.8)),
                        "chi_C": 0.65,
                        "zeta_C": 0.55,
                        "tau_C": 0.17,
                    }
                },
            )
            actual, expected = CandidateCCurrent(inputs), dense_current_oracle(inputs)
            for label, value in (
                ("projector", actual.algebra.selector.projector),
                ("phi", actual.algebra.potential.values),
                ("j0", actual.algebra.baseline.values),
                ("current", actual.current.values),
                ("read", actual.read.flux.values),
            ):
                with self.subTest(case=case, field=label):
                    np.testing.assert_allclose(
                        np.asarray(value, dtype=float),
                        expected[label],
                        atol=2e-11,
                        rtol=2e-11,
                    )

    def test_actual_current_rejects_lost_physical_conditioning_margin(self) -> None:
        import numpy as np
        from pygrc.models.grc_v4_candidate_c import CandidateCCurrent

        graph = GRCV4Graph(
            (0, 1, 2),
            tuple(OrientedEdge(e, i, (i + 1) % 3) for i, e in enumerate("abc")),
        )

        def fixture(limit: float) -> Any:
            return current_fixture(
                graph=graph,
                weights={"a": 1, "b": 1, "c": 1},
                hodge=((9, -6, 4), (-6, 10, -1), (4, -1, 4)),
                resource=(0.02, 0.2, 2),
                changes={
                    "candidate": {
                        "Lambda_C": 100,
                        "kappa_M_C": 2,
                        "zeta_C": 0.999,
                        "chi_C": 1,
                        "tau_C": 0.2,
                    },
                    "solver": {"conditioning_limit": limit},
                },
            )

        inputs = fixture(2000)
        expected = dense_current_oracle(inputs)
        self.assertLess(np.linalg.cond(np.eye(3) - 0.999 * expected["response"]), 1500)
        self.assertGreater(np.linalg.cond(expected["block"]), 390000)
        with self.assertRaisesRegex(
            ValueError, "conditioning limit exceeded: physical total-current block"
        ):
            CandidateCCurrent(inputs)
        # Changing only the serialized bound admits the same regular equation;
        # neither a retained-space certificate nor a repair is substituted.
        admitted = CandidateCCurrent(fixture(1e6))
        np.testing.assert_allclose(
            admitted.current.values, expected["current"], rtol=2e-10, atol=2e-10
        )

    def test_tiny_residuals_cannot_underflow_into_zero_tolerance_success(self) -> None:
        from pygrc.models.grc_v4_candidate_c import _c_residual_pass, _c_solve

        policy = current_fixture().geometry.reference.profile.params_resolved.solver
        zero = replace(policy, absolute_tolerance=0, relative_tolerance=0)
        self.assertFalse(_c_residual_pass((Fraction(1, 10**500),), (Fraction(),), zero))
        self.assertTrue(
            _c_residual_pass(
                (Fraction(1),),
                (Fraction(1),),
                replace(policy, absolute_tolerance=1, relative_tolerance=0),
            )
        )
        self.assertFalse(
            _c_residual_pass(
                (Fraction(1),),
                (Fraction(1),),
                replace(
                    policy,
                    absolute_tolerance=math.nextafter(1, 0),
                    relative_tolerance=0,
                ),
            )
        )
        with self.assertRaisesRegex(ValueError, "residual"):
            _c_solve(((3,),), ((1,),), zero, "one third", [])
        with self.assertRaisesRegex(ValueError, "residual"):
            _c_solve(((3,),), ((5e-324,),), zero, "subnormal rhs", [])

    def test_stage_declarations_reject_unsupported_policies(self) -> None:
        from pygrc.models.grc_v4_candidate_c import CandidateCCurrent

        controls = [
            ("common", "domain_id", "wrong"),
            ("common", "gauge_id", "wrong"),
            ("common", "normalization_id", "wrong"),
            ("candidate", "potential_evaluator_id", "wrong"),
            ("candidate", "current_conditioning_policy_id", "wrong"),
            ("solver", "solver_kind", "newton"),
            ("solver", "residual_norm_id", "wrong"),
            ("identity", "solver_id", "wrong"),
        ]
        for group, key, value in controls:
            changes = {group: {key: value}}
            if group == "common":
                changes["identity"] = {key: value}
            with (
                self.subTest(field=key),
                self.assertRaisesRegex(ValueError, "unimplemented"),
            ):
                CandidateCCurrent(current_fixture(changes=changes))
        with self.assertRaises(TypeError):
            CandidateCCurrent({})  # type: ignore[arg-type]
        from tests.models.test_grc_v4_geometry import stage_inputs_fixture

        with self.assertRaisesRegex(ValueError, "profile"):
            CandidateCCurrent(stage_inputs_fixture(stage_reference_fixture("A")))

    def test_nonfinite_and_underflowed_required_operators_fail_without_repair(
        self,
    ) -> None:
        from pygrc.models.grc_v4_candidate_c import CandidateCCurrent

        for km in (2000, -2000):
            with self.subTest(km=km), self.assertRaises(ValueError):
                CandidateCCurrent(
                    current_fixture(
                        graph=self.edge_graph(),
                        weights={"e": 1},
                        resource=(100, 100),
                        changes={"candidate": {"kappa_M_C": km}},
                    )
                )
        with self.assertRaises(ValueError):
            CandidateCCurrent(
                current_fixture(
                    graph=self.edge_graph(),
                    weights={"e": 5e-324},
                    resource=(0, 0),
                    changes={"candidate": {"kappa_M_C": 0, "tau_C": 0}},
                )
            )
        # Saturated tanh remains well-defined for a finite quotient above the
        # binary64 range; it does not authorize an infinite Hodge or inverse.
        actual = CandidateCCurrent(
            current_fixture(
                graph=self.edge_graph(),
                weights={"e": 1},
                resource=(1, 1),
                changes={"candidate": {"C_ref": 5e-324}},
            )
        )
        self.assertEqual(actual.algebra.deformation, (math.exp(0.25),))

    def test_fresh_geometry_and_trial_current_have_distinct_stage_roles(self) -> None:
        from pygrc.models.grc_v4_candidate_c import CandidateCCurrent
        from pygrc.models.grc_v4_geometry import GRCV4Geometry

        inputs = current_fixture(
            realization="CI",
            stage="ci_trial",
            resource=(0.1, 1.5, 2.7),
            changes={"candidate": {"Lambda_C": 4}},
        )
        first = CandidateCCurrent(inputs)
        changed = replace(
            inputs,
            trial_current=PhysicalFlux(inputs.geometry.reference.graph, (12, -4)),
            evaluation_index=7,
        )
        trial = CandidateCCurrent(changed)
        self.assertEqual(first.current, trial.current)
        self.assertEqual(first.algebra.baseline, trial.algebra.baseline)
        self.assertNotEqual(first.identity, trial.identity)
        next_geometry = GRCV4Geometry(
            inputs.geometry.reference,
            OneFormHodge(inputs.geometry.reference.graph, ((3, 0.5), (0.5, 2))),
        )
        refreshed = CandidateCCurrent(replace(inputs, geometry=next_geometry))
        self.assertNotEqual(
            first.algebra.selector.projector, refreshed.algebra.selector.projector
        )
        self.assertNotEqual(first.algebra.baseline, refreshed.algebra.baseline)
        self.assertEqual(
            first.algebra.transport.mobility, refreshed.algebra.transport.mobility
        )

    def test_local_evaluation_at_each_declared_stage_is_not_a_complete_beat(
        self,
    ) -> None:
        from pygrc.models.grc_v4_candidate_c import CandidateCCurrent
        from pygrc.models.grc_v4_profile import list_supported_profiles

        for realization, stage in [
            ("OS", "os_predictor"),
            ("OS", "os_corrector"),
            ("CI", "ci_trial"),
            ("CI+PC", "cipc_trial"),
            ("PC", "pc_old_history"),
            ("RG2b", "rg2b_section"),
            ("OS", "post_continuity"),
            ("OS", "reset_readmission"),
            ("OS", "target_readmission"),
        ]:
            with self.subTest(stage=stage):
                inputs = current_fixture(realization=realization, stage=stage)
                before = inputs.to_payload()
                current = CandidateCCurrent(inputs)
                self.assertEqual(inputs.to_payload(), before)
                self.assertEqual(current.inputs.stage, stage)
        self.assertFalse(list_supported_profiles())

    def test_signed_permutation_and_vertex_relabeling_covariance(self) -> None:
        import numpy as np
        from pygrc.models.grc_v4_candidate_c import CandidateCCurrent

        original = current_fixture(
            hodge=((3, 0.75), (0.75, 1.5)),
            resource=(0.2, 1.5, 2.4),
            changes={"candidate": {"Lambda_C": 3}},
        )
        first = CandidateCCurrent(original)
        graph = original.geometry.reference.graph
        edge_order = (1, 0)
        node_order = (2, 0, 1)
        sign = (-1, 1)
        labels = {node: f"relabel-{i}" for i, node in enumerate(graph.live_node_ids)}
        edges = []
        for j, s in zip(edge_order, sign, strict=True):
            e = graph.oriented_edges[j]
            tail, head = e.tail_node_id, e.head_node_id
            if s < 0:
                tail, head = head, tail
            edges.append(OrientedEdge(e.edge_id, labels[tail], labels[head]))
        transformed = GRCV4Graph(
            tuple(labels[graph.live_node_ids[i]] for i in node_order), tuple(edges)
        )
        h = original.geometry.one_form_hodge.matrix
        h2 = tuple(
            tuple(float(sign[i] * sign[j] * h[a][b]) for j, b in enumerate(edge_order))
            for i, a in enumerate(edge_order)
        )
        target = current_fixture(
            graph=transformed,
            weights=dict(original.geometry.reference.edge_weights),
            hodge=h2,
            resource=tuple(original.current.C[i] for i in node_order),
            changes={"candidate": {"Lambda_C": 3}},
        )
        second = CandidateCCurrent(target)
        np.testing.assert_allclose(
            second.algebra.potential.values,
            np.array(first.algebra.potential.values)[list(node_order)],
            atol=2e-12,
        )
        np.testing.assert_allclose(
            second.current.values,
            np.array(first.current.values)[list(edge_order)] * sign,
            atol=2e-12,
        )
        np.testing.assert_allclose(
            second.read.flux.values,
            np.array(first.read.flux.values)[list(edge_order)] * sign,
            atol=2e-12,
        )

    def test_input_reconstruction_immutability_and_no_derived_authority(self) -> None:
        from pygrc.models.grc_v4_candidate_c import CandidateCCurrent

        inputs = current_fixture()
        raw = inputs.to_payload()
        before = deepcopy(raw)
        current = CandidateCCurrent(inputs)
        payload = current.to_payload()
        restored = CandidateCCurrent.from_canonical_bytes(current.to_canonical_bytes())
        self.assertEqual(restored.current, current.current)
        self.assertEqual(restored.identity, current.identity)
        self.assertEqual(raw, before)
        self.assertEqual(set(payload), {"descriptor_version", "numerics", "inputs"})
        for key in (
            "current",
            "selector",
            "retained_hodge",
            "response",
            "baseline",
            "history",
        ):
            with self.subTest(key=key), self.assertRaises(ValueError):
                CandidateCCurrent.from_payload({**payload, key: []})
        mutable: Any = payload
        mutable["inputs"]["current"]["C"][0] = 99
        self.assertEqual(current.inputs.current.C, inputs.current.C)
        with self.assertRaises(FrozenInstanceError):
            current.current = PhysicalFlux(inputs.geometry.reference.graph, (0, 0))  # type: ignore[misc]
        with self.assertRaises(TypeError):
            current.algebra.certificates[0]["limit"] = 1  # type: ignore[index]

    def test_rejected_evaluation_preserves_full_stage_preimage(self) -> None:
        from pygrc.models.grc_v4_candidate_c import CandidateCCurrent
        from tests.models.test_grc_v4_step import preservation_snapshot

        for changes in (
            {"candidate": {"Lambda_C": 0}},
            {"candidate": {"tau_C": 0, "zeta_C": 0.5, "chi_C": 2}},
            {"solver": {"conditioning_limit": 0.5}},
            {"solver": {"absolute_tolerance": 0, "relative_tolerance": 0}},
        ):
            inputs = current_fixture(changes=changes)
            before = preservation_snapshot(inputs.to_payload())
            with self.assertRaises(ValueError):
                CandidateCCurrent(inputs)
            self.assertEqual(preservation_snapshot(inputs.to_payload()), before)


class CandidateCCaptureTests(unittest.TestCase):
    """Synthetic gate controls; these do not substitute for numeric leaf tests."""

    @contextmanager
    def fixture(
        self,
    ) -> Iterator[tuple[Path, dict[str, ModuleType], Callable[[], dict[str, str]]]]:
        from importlib.machinery import ModuleSpec
        import tempfile
        from unittest.mock import patch

        names = (
            "pygrc.models.grc_v4_geometry",
            "pygrc.models.grc_v4_transport",
            "tests.models.test_grc_v4_geometry",
            "tests.models.test_grc_v4_transport",
            "pygrc.models.grc_v4_candidate_c",
            "tests.models.test_grc_v4_candidate_c",
        )
        source = (
            "from dataclasses import dataclass\n"
            "def mobility(eta, weight):\n    return eta * weight\n"
            "class Probe:\n"
            "    @staticmethod\n    def static():\n        return 1\n"
            "    @classmethod\n    def cls(cls):\n        return 2\n"
            "    @property\n    def value(self):\n        return 3\n"
            "@dataclass(frozen=True)\nclass Generated:\n    value: int\n"
        )
        with tempfile.TemporaryDirectory(prefix="p941-capture-") as folder:
            root = Path(folder).resolve()
            modules = {}
            paths = []
            for name in names:
                prefix = "src/" if name.startswith("pygrc.") else ""
                path = root / (prefix + name.replace(".", "/") + ".py")
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(source)
                paths.append(path)
                module = ModuleType(name)
                module.__file__ = str(path)
                module.__spec__ = ModuleSpec(name, loader=None, origin=str(path))
                modules[name] = module
            main = ModuleType("__main__")
            leaf = modules[names[-1]]
            main.__file__, main.__spec__ = leaf.__file__, leaf.__spec__
            modules["__main__"] = main
            kept = {
                n: m
                for n, m in sys.modules.items()
                if n not in {"pygrc", "tests", "__main__"}
                and not n.startswith(("tests.", "pygrc.", "grcv4_explorer."))
            }

            def hashes() -> dict[str, str]:
                return {
                    str(path.relative_to(root)): hashlib.sha256(
                        path.read_bytes()
                    ).hexdigest()
                    for path in paths
                }

            with patch.dict(sys.modules, {**kept, **modules}, clear=True):
                for module in modules.values():
                    exec(
                        compile(
                            source, str(module.__file__), "exec", dont_inherit=True
                        ),
                        module.__dict__,
                    )
                yield root, modules, hashes

    def execute(
        self,
        root: Path,
        hashes: Callable[[], dict[str, str]],
        action: Callable[[], None] = lambda: None,
    ) -> dict[str, Any]:
        case = unittest.FunctionTestCase(action)
        return _p941_execute(
            root, hashes(), {case.id()}, unittest.TestSuite([case]), hashes
        )

    def test_matching_live_sources_and_main_alias_pass(self) -> None:
        with self.fixture() as (root, modules, hashes):
            result = self.execute(root, hashes)
            self.assertEqual(result["status"], "passed", result)
            self.assertEqual(result["results"]["tests_run"], 1)
            self.assertEqual(
                result["loaded_sources_before"], result["loaded_sources_after"]
            )
            self.assertEqual(set(result["loaded_sources_before"]), set(modules))
            self.assertEqual(
                result["loaded_sources_before"]["__main__"][
                    "source_declared_code_objects_checked"
                ],
                4,
            )

    def test_same_path_stale_code_and_main_alias_reject(self) -> None:
        for name in (
            "pygrc.models.grc_v4_candidate_c",
            "tests.models.test_grc_v4_candidate_c",
            "__main__",
        ):
            with self.subTest(module=name), self.fixture() as (root, modules, hashes):
                module = modules[name]
                stale = "def mobility(eta, weight):\n    return weight\n"
                exec(
                    compile(stale, str(module.__file__), "exec", dont_inherit=True),
                    module.__dict__,
                )
                self.assertEqual(module.mobility(3, 2), 2)
                result = self.execute(root, hashes)
                self.assertEqual(result["status"], "failed")
                self.assertIn("code differs", result["capture_error"])
                self.assertTrue(result["source_unchanged"])
                self.assertNotIn("results", result)  # no test execution or reload
                self.assertEqual(module.mobility(3, 2), 2)

    def test_foreign_wrong_local_and_missing_origins_reject(self) -> None:
        from importlib.machinery import ModuleSpec

        for mode in (
            "foreign",
            "wrong_local",
            "wrong_spec",
            "no_spec",
            "no_file",
            "missing_leaf",
            "main_no_spec",
        ):
            with self.subTest(mode=mode), self.fixture() as (root, modules, hashes):
                name = "pygrc.models.grc_v4_candidate_c"
                module = modules[name]
                if mode == "main_no_spec":
                    modules["__main__"].__spec__ = None
                elif mode == "foreign":
                    module.__file__ = str(root.parent / "foreign.py")
                elif mode == "wrong_local":
                    module.__file__ = modules["pygrc.models.grc_v4_transport"].__file__
                    module.__spec__ = ModuleSpec(name, None, origin=module.__file__)
                elif mode == "wrong_spec":
                    module.__spec__ = ModuleSpec(
                        name, None, origin=str(root / "wrong.py")
                    )
                elif mode == "no_spec":
                    module.__spec__ = None
                elif mode == "no_file":
                    del module.__file__
                else:
                    del sys.modules[name]
                result = self.execute(root, hashes)
                self.assertEqual(result["status"], "failed")
                self.assertNotIn("results", result)
                self.assertIn(
                    "mismatch" if mode != "missing_leaf" else "not loaded",
                    result["capture_error"],
                )

    def test_replaced_declared_slots_cannot_hide_as_generated_or_foreign(self) -> None:
        for mode in (
            "generated_filename",
            "foreign_owner",
            "deleted",
            "property_getter",
        ):
            with self.subTest(mode=mode), self.fixture() as (root, modules, hashes):
                module = modules["pygrc.models.grc_v4_candidate_c"]
                if mode == "generated_filename":
                    module.mobility.__code__ = module.mobility.__code__.replace(
                        co_filename="<string>"
                    )
                elif mode == "foreign_owner":
                    module.mobility.__module__ = "foreign"
                elif mode == "deleted":
                    del module.mobility
                else:
                    module.Probe.value = property()
                result = self.execute(root, hashes)
                self.assertEqual(result["status"], "failed")
                self.assertIn("code differs", result["capture_error"])

    def test_disk_change_during_execution_fails(self) -> None:
        for mode in ("edited", "deleted"):
            with self.subTest(mode=mode), self.fixture() as (root, modules, hashes):
                path = Path(str(modules["pygrc.models.grc_v4_candidate_c"].__file__))

                def change() -> None:
                    if mode == "deleted":
                        path.unlink()
                    else:
                        path.write_bytes(
                            path.read_bytes() + b"\n# changed during test\n"
                        )

                result = self.execute(root, hashes, change)
                self.assertEqual(result["results"]["tests_run"], 1)
                self.assertEqual(result["status"], "failed")
                self.assertFalse(result["source_unchanged"])
                if mode == "deleted":
                    self.assertIn("FileNotFoundError", result["source_snapshot_error"])

    def test_postrun_live_changes_and_late_imports_are_checked(self) -> None:
        from importlib.machinery import ModuleSpec

        for mode in ("changed_code", "removed_module", "late_good", "late_stale"):
            with self.subTest(mode=mode), self.fixture() as (root, modules, hashes):
                name = "pygrc.models.grc_v4_candidate_c"
                module = modules[name]
                extra = root / "src/pygrc/models/late_probe.py"
                extra.write_text("def value():\n    return 2\n")

                def snapshot() -> dict[str, str]:
                    return {
                        **hashes(),
                        str(extra.relative_to(root)): hashlib.sha256(
                            extra.read_bytes()
                        ).hexdigest(),
                    }

                def change() -> None:
                    if mode == "changed_code":
                        exec(
                            compile(
                                "def mobility(eta, weight):\n    return weight\n",
                                str(module.__file__),
                                "exec",
                                dont_inherit=True,
                            ),
                            module.__dict__,
                        )
                    elif mode == "removed_module":
                        del sys.modules[name]
                    else:
                        late = ModuleType("pygrc.models.late_probe")
                        late.__file__ = str(extra)
                        late.__spec__ = ModuleSpec(
                            late.__name__, None, origin=str(extra)
                        )
                        source = (
                            extra.read_bytes()
                            if mode == "late_good"
                            else b"def value():\n    return 1\n"
                        )
                        exec(
                            compile(source, str(extra), "exec", dont_inherit=True),
                            late.__dict__,
                        )
                        sys.modules[late.__name__] = late

                result = self.execute(root, snapshot, change)
                self.assertEqual(result["results"]["tests_run"], 1)
                self.assertTrue(result["source_unchanged"])
                self.assertEqual(
                    result["status"],
                    "passed" if mode == "late_good" else "failed",
                    result,
                )
                if mode == "late_good":
                    self.assertNotIn(
                        "pygrc.models.late_probe", result["loaded_sources_before"]
                    )
                    self.assertIn(
                        "pygrc.models.late_probe", result["loaded_sources_after"]
                    )

    def test_roster_and_nonpassing_outcomes_still_reject(self) -> None:
        with self.fixture() as (root, _, hashes):
            for mode in ("empty", "missing", "duplicate", "skip", "failure", "subtest"):
                with self.subTest(mode=mode):

                    class Probe(unittest.TestCase):
                        def test_case(self) -> None:
                            if mode == "skip":
                                self.skipTest("ordinary test_case name")
                            if mode == "failure":
                                self.fail("intentional failure")
                            if mode == "subtest":
                                with self.subTest():
                                    self.fail("intentional subtest failure")

                    case = Probe("test_case")
                    required = (
                        {case.id(), "missing"} if mode == "missing" else {case.id()}
                    )
                    cases = (
                        []
                        if mode == "empty"
                        else [case, Probe("test_case")]
                        if mode == "duplicate"
                        else [case]
                    )
                    result = _p941_execute(
                        root, hashes(), required, unittest.TestSuite(cases), hashes
                    )
                    self.assertEqual(result["status"], "failed", result)
                    self.assertFalse(result["coverage"]["passed"])


_P941_CAPTURE_METHODS = (
    "test_matching_live_sources_and_main_alias_pass",
    "test_same_path_stale_code_and_main_alias_reject",
    "test_foreign_wrong_local_and_missing_origins_reject",
    "test_replaced_declared_slots_cannot_hide_as_generated_or_foreign",
    "test_disk_change_during_execution_fails",
    "test_postrun_live_changes_and_late_imports_are_checked",
    "test_roster_and_nonpassing_outcomes_still_reject",
)


_P941_METHODS = (
    "test_exact_siblings_and_typed_operator_actions",
    "test_equal_matrices_still_have_separate_constructor_identities",
    "test_gain_changes_only_mobility_constructor",
    "test_map_value_and_stable_id_are_identity_inputs",
    "test_unrelated_profile_controls_do_not_condition_reference_constructors",
    "test_all_five_declarations_bind_without_advertising_execution",
    "test_units_declaration_is_part_of_each_typed_constructor_identity",
    "test_complete_reference_geometry_agrees_with_sibling_hodge",
    "test_reference_hodge_mismatch_rejects_even_with_reidentified_profile",
    "test_map_must_cover_exact_target_edges_without_copy_or_resize",
    "test_map_domain_and_gain_reject_without_repair",
    "test_transport_and_constructor_policy_ids_cannot_be_substituted",
    "test_complete_profile_and_map_identity_tampering_rejects",
    "test_binary64_positive_extremes_and_product_boundaries",
    "test_random_scalar_rational_oracle_across_wide_exponents",
    "test_graph_outliers_and_signed_permutation_covariance",
    "test_unicode_and_numeric_looking_edge_ids_roundtrip",
    "test_noncanonical_duplicate_or_extra_wire_authority_rejects",
    "test_no_mutable_source_or_output_aliases",
    "test_wrong_candidate_bare_params_and_graph_duplicates_reject",
)


def _p941_loaded_sources(root: Path, hashes: dict[str, str]) -> dict[str, Any]:
    """Check origins and live source code; not hostile-interpreter attestation."""
    import inspect
    from types import CodeType

    leaf_modules = {
        "pygrc.models.grc_v4_candidate_c",
        "tests.models.test_grc_v4_candidate_c",
    }
    # A local file can still be the wrong module. Bind names to their actual
    # package paths, including the second instance created by `python -m`.
    aliases = {}
    for name, module in tuple(sys.modules.items()):
        spec = getattr(module, "__spec__", None)
        canonical = getattr(spec, "name", None) if name == "__main__" else name
        if name == "__main__" and (
            getattr(module, "__file__", None)
            == str(root / "tests/models/test_grc_v4_candidate_c.py")
            or __name__ == "__main__"
        ):
            canonical = "tests.models.test_grc_v4_candidate_c"
        if not isinstance(canonical, str) or not (
            canonical in {"pygrc", "tests"}
            or canonical.startswith(("pygrc.", "tests.", "grcv4_explorer."))
        ):
            continue
        prefix = "src/" if canonical.split(".")[0] == "pygrc" else ""
        if canonical.startswith("grcv4_explorer."):
            prefix = (
                "implementation/investigations/grc9v4-constitutive-design/"
                "tools/exploratory-side-tool/tool/src/"
            )
        stem = prefix + canonical.replace(".", "/")
        file = getattr(module, "__file__", None)
        path = Path(file).resolve() if file else None
        if path not in {root / (stem + ".py"), root / stem / "__init__.py"}:
            raise RuntimeError("loaded module path mismatch: " + name)
        if spec is None or spec.name != canonical or spec.origin is None:
            raise RuntimeError("loaded module origin mismatch: " + name)
        if Path(spec.origin).resolve() != path:
            raise RuntimeError("loaded module origin mismatch: " + name)
        relative = str(path.relative_to(root))
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if hashes.get(relative) != digest:
            raise RuntimeError("loaded source bytes not in snapshot: " + name)
        if canonical not in leaf_modules and canonical != "pygrc":
            continue

        # Audit source-declared slots, including properties and class/static
        # methods. Generated dataclass methods have no source declaration and
        # are not treated as fresh-compiled source. Nested function code is
        # compared recursively as part of its enclosing function's code object.
        codes: list[CodeType] = []

        def collect(code: CodeType) -> None:
            if "<" not in code.co_qualname:
                codes.append(code)
            for item in code.co_consts:
                if isinstance(item, CodeType):
                    collect(item)

        collect(compile(data, str(path), "exec", dont_inherit=True))
        checked = 0
        for code in codes:
            obj: Any = module
            for part in code.co_qualname.split("."):
                obj = inspect.getattr_static(obj, part, None)
            if inspect.isclass(obj):
                if obj.__module__ != name:
                    raise RuntimeError("loaded class owner mismatch: " + name)
                continue
            if isinstance(obj, (classmethod, staticmethod)):
                obj = obj.__func__
            candidates = (
                (obj.fget, obj.fset, obj.fdel) if isinstance(obj, property) else (obj,)
            )
            if not any(
                callable(candidate)
                and inspect.isfunction(live := inspect.unwrap(candidate))
                and live.__module__ == name
                and live.__code__.co_filename == str(path)
                and live.__code__.co_qualname == code.co_qualname
                and live.__code__ == code
                for candidate in candidates
            ):
                raise RuntimeError(
                    "loaded code differs from snapshot: "
                    + name
                    + "."
                    + code.co_qualname
                )
            checked += 1
        aliases[name] = {
            "path": relative,
            "sha256": digest,
            "source_declared_code_objects_checked": checked,
        }
    loaded = _p934_loaded_sources(root, hashes)
    for name in leaf_modules:
        if name not in loaded:
            raise RuntimeError("required leaf module not loaded: " + name)
    loaded.update(aliases)
    return loaded


def _p941_execute(
    root: Path,
    before: dict[str, str],
    required: set[str],
    suite: unittest.TestSuite,
    source_hashes: Callable[[], dict[str, str]],
) -> dict[str, Any]:
    """The same before/run/after gate serves full and explicitly focused runs."""
    import io
    import time
    from typing import cast

    record: dict[str, Any] = {"status": "failed"}
    stream = io.StringIO()
    start = time.monotonic()
    try:
        names = _p934_ids(suite)
        record["coverage"] = _p934_coverage(required, names)
        if not record["coverage"]["passed"]:
            raise RuntimeError("discovery differs from the independently pinned roster")
        record["loaded_sources_before"] = _p941_loaded_sources(root, before)
        result = cast(
            _P934Result,
            unittest.TextTestRunner(stream=stream, resultclass=_P934Result).run(suite),
        )
        record["coverage"] = _p934_coverage(required, names, result.rows)
        record["results"] = {
            "tests_run": result.testsRun,
            "failures": len(result.failures),
            "errors": len(result.errors),
            "skips": len(result.skipped),
            "nonpassing_methods": [r for r in result.rows if r["status"] != "passed"],
            "executed_ids_sha256": hashlib.sha256(
                canonical_json_bytes(sorted(r["test"] for r in result.rows))
            ).hexdigest(),
        }
        record["loaded_sources_after"] = _p941_loaded_sources(root, before)
        if any(
            record["loaded_sources_after"].get(name) != row
            for name, row in record["loaded_sources_before"].items()
        ):
            raise RuntimeError("loaded sources disappeared or changed during execution")
        if (
            result.wasSuccessful()
            and not result.skipped
            and result.testsRun == len(names)
            and record["coverage"]["passed"]
        ):
            record["status"] = "passed"
    except Exception as exc:
        record["capture_error"] = type(exc).__name__ + ": " + str(exc)
    finally:
        try:
            record["source_unchanged"] = before == source_hashes()
        except Exception as exc:
            record["source_unchanged"] = False
            record["source_snapshot_error"] = type(exc).__name__ + ": " + str(exc)
        if not record["source_unchanged"]:
            record["status"] = "failed"
        record["elapsed_seconds"] = round(time.monotonic() - start, 3)
    if record["status"] != "passed":
        record["failure_output"] = stream.getvalue().replace(str(root), "<checkout>")
    return record


_P942_METHODS = (
    "test_scalar_chain_has_literal_independent_solution",
    "test_scalar_random_controls_against_closed_formula",
    "test_frozen_weighted_three_node_algebra_vector",
    "test_dense_nonreference_hodge_matches_literal_equations",
    "test_selector_ties_zero_and_exterior_strata",
    "test_exact_inertia_handles_zero_diagonal_pivots",
    "test_selector_pair_permutation_sign_and_repeated_cluster_rotations",
    "test_selector_rejects_unresolved_or_malformed_decomposition",
    "test_disconnected_isolated_parallel_and_loop_coordinates",
    "test_offdiagonal_loop_and_cycle_modes_match_oracle",
    "test_only_loop_graph_has_full_selector_and_harmonic_response",
    "test_one_chi_gate_linearity_and_zero_input",
    "test_zero_controls_are_independent_current_equations",
    "test_singular_current_and_zero_rhs_do_not_get_a_fallback",
    "test_conditioning_bounds_are_checked_in_actual_euclidean_coordinates",
    "test_exact_current_singularity_is_not_hidden_by_rounded_resolvent",
    "test_positive_pairing_audit_witness_reaches_current_conditioning_guard",
    "test_seeded_dense_spd_multigraphs_against_independent_equations",
    "test_actual_current_rejects_lost_physical_conditioning_margin",
    "test_tiny_residuals_cannot_underflow_into_zero_tolerance_success",
    "test_stage_declarations_reject_unsupported_policies",
    "test_nonfinite_and_underflowed_required_operators_fail_without_repair",
    "test_fresh_geometry_and_trial_current_have_distinct_stage_roles",
    "test_local_evaluation_at_each_declared_stage_is_not_a_complete_beat",
    "test_signed_permutation_and_vertex_relabeling_covariance",
    "test_input_reconstruction_immutability_and_no_derived_authority",
    "test_rejected_evaluation_preserves_full_stage_preimage",
)


def _capture_candidate_c(output: str, *, scope: str) -> int:
    """One manifest; source is recovered from Git, without copying source blobs.

    The inherited pinned method roster and audited result collector detect
    omission, duplicates, skips and subtest failures. All source bytes are
    observed before/after, with only this leaf's two overrides over its base.
    """
    from datetime import datetime, timezone
    import importlib.metadata
    import os
    import platform
    import subprocess
    from tests.models.test_grc_v4_step import p935_required

    if scope not in {"full", "focused", "current"}:
        raise ValueError("unknown capture scope")
    root = Path(__file__).resolve().parents[2]
    destination = (root / output).resolve()
    if not destination.is_relative_to(
        root
        / "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/generated"
    ):
        raise ValueError(
            "capture destination must be inside the side tool generated directory"
        )
    wheelhouse = (root / os.environ.get("GRCV4_WHEELHOUSE", "<missing>")).resolve()
    if scope == "full" and (
        os.environ.get("GRCV4_PACKAGE_TESTS") != "1"
        or not wheelhouse.is_relative_to(root)
        or not wheelhouse.is_dir()
    ):
        raise ValueError(
            "full capture requires enabled package tests and repository-local dependency wheels"
        )
    base = subprocess.check_output(
        ["git", "rev-parse", "94a079d" if scope == "current" else "2e90398"],
        cwd=root,
        text=True,
    ).strip()
    scopes = [
        "src",
        "tests",
        "specs",
        "pyproject.toml",
        "uv.lock",
        "implementation/investigations/grc9v4-constitutive-design/drafts/2026-09-GRC-V4.md",
    ]
    overrides = {
        "src/pygrc/models/grc_v4_candidate_c.py",
        "tests/models/test_grc_v4_candidate_c.py",
    }

    def source_hashes() -> dict[str, str]:
        names = set(
            subprocess.check_output(
                [
                    "git",
                    "ls-files",
                    "--cached",
                    "--others",
                    "--exclude-standard",
                    "--",
                    *scopes,
                ],
                cwd=root,
                text=True,
            ).splitlines()
        )
        return {
            name: hashlib.sha256((root / name).read_bytes()).hexdigest()
            for name in sorted(names)
        }

    iteration = "P9-4.2" if scope == "current" else "P9-4.1"
    before = source_hashes()
    # Git diff also sees staged changes, while the explicit overrides cover
    # this leaf's new files before they have been staged.
    changed = set(
        subprocess.check_output(
            ["git", "diff", "--name-only", base, "--", *scopes], cwd=root, text=True
        ).splitlines()
    )
    untracked = set(
        subprocess.check_output(
            ["git", "ls-files", "--others", "--exclude-standard", "--", *scopes],
            cwd=root,
            text=True,
        ).splitlines()
    )
    if (changed | untracked) != overrides:
        raise ValueError(
            "capture source differs from the two reviewed " + iteration + " overrides"
        )
    inherited = p935_required(root)
    if scope == "focused":
        inherited = {
            name
            for name in inherited
            if name.startswith(
                (
                    "tests.models.test_grc_v4_geometry.CaptureIntegrityTests.",
                    "tests.models.test_grc_v4_transport.MobilityTests.",
                )
            )
        }
    if scope == "current":
        inherited = {
            name
            for name in inherited
            if name.startswith(
                (
                    "tests.models.test_grc_v4_geometry.CaptureIntegrityTests.",
                    "tests.models.test_grc_v4_geometry.PairingTests.",
                    "tests.models.test_grc_v4_geometry.ExactPositiveDomainTests.",
                    "tests.models.test_grc_v4_geometry.GeometryAdmissionTests.",
                    "tests.models.test_grc_v4_geometry.StageCacheTests.",
                    "tests.models.test_grc_v4_transport.MobilityTests.",
                )
            )
        } | {
            "tests.models.test_grc_v4_geometry.NumericalEnvelopeTests.test_exact_positive_matrix_can_have_nonpositive_computed_self_pairing"
        }
    required = (
        inherited
        | {
            "tests.models.test_grc_v4_candidate_c.CandidateCReferenceTests." + name
            for name in _P941_METHODS
        }
        | {
            "tests.models.test_grc_v4_candidate_c.CandidateCCaptureTests." + name
            for name in _P941_CAPTURE_METHODS
        }
    )
    if scope == "current":
        required |= {
            "tests.models.test_grc_v4_candidate_c.CandidateCCurrentTests." + name
            for name in _P942_METHODS
        }
    suite = (
        unittest.defaultTestLoader.discover(
            str(root / "tests"), top_level_dir=str(root)
        )
        if scope == "full"
        else unittest.defaultTestLoader.loadTestsFromNames(sorted(required))
    )
    destination.mkdir(parents=True, exist_ok=False)
    record: dict[str, Any] = {
        "schema": "phase9_leaf_run_v1",
        "iteration_id": iteration,
        "scope": scope,
        "status": "running",
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "source": {
            "base_commit": base,
            "scopes": scopes,
            "overrides_sha256": {n: before[n] for n in sorted(overrides)},
            "manifest_sha256": hashlib.sha256(canonical_json_bytes(before)).hexdigest(),
            "file_count": len(before),
            "reconstruction": "Recover the two override files from the Git commit containing this record (or a later commit with matching hashes), overlay on base_commit, and verify the manifest hash. No uncommitted source blob is preserved separately.",
        },
        "python": platform.python_version(),
        "platform": platform.platform(),
        "dependencies": sorted(
            f"{d.metadata['Name']}=={d.version}"
            for d in importlib.metadata.distributions()
        ),
        "environment": {
            "GRCV4_PACKAGE_TESTS": os.environ.get("GRCV4_PACKAGE_TESTS"),
            "GRCV4_WHEELHOUSE": str(wheelhouse.relative_to(root))
            if wheelhouse.is_relative_to(root) and wheelhouse.is_dir()
            else None,
            **{
                key: os.environ.get(key)
                for key in ["PYTHONHASHSEED", "OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS"]
            },
        },
        "wheel_requirements": sorted(p.name for p in wheelhouse.glob("*.whl"))
        if scope == "full"
        else [],
        "replay_command": [
            ".venv/bin/python",
            "-m",
            "tests.models.test_grc_v4_candidate_c",
            "--capture-p942"
            if scope == "current"
            else "--capture-p941"
            if scope == "full"
            else "--capture-p941-focused",
            "<fresh-repository-relative-generated-directory>",
        ],
        "claim_ceiling": (
            "Fixed-stage Candidate C selector, potential, baseline, typed read and regular current solve; no complete beat, lifecycle, profile conformance or cross-platform bitwise numerical claim."
            if scope == "current"
            else "Reference transport constructors only; no selector, baseline flux, solve, beat, lifecycle or runtime conformance."
        ),
    }
    record["required_ids"] = sorted(required)
    record.update(_p941_execute(root, before, required, suite, source_hashes))
    passed = record["status"] == "passed"
    if passed:
        loaded_before = record.pop("loaded_sources_before")
        loaded_after = record.pop("loaded_sources_after")
        record["loaded_sources"] = {
            "before": loaded_before,
            "added_after": {
                name: row
                for name, row in loaded_after.items()
                if name not in loaded_before
            },
            "before_rechecked_after": True,
        }
    record["live_source_check_limits"] = (
        "Before/after source, origin and applicable live-code checks detect stale or "
        "wrong local code. They do not attest a hostile interpreter, transient "
        "changes restored between checkpoints, arbitrary globals/default values, "
        "generated dataclass methods, or native dependency internals. Source-declared "
        "leaf slots and the python -m alias are checked explicitly."
    )
    record["completed_utc"] = datetime.now(timezone.utc).isoformat()
    (destination / "run.json").write_text(
        json.dumps(record, indent=2, allow_nan=False) + "\n"
    )
    print(
        json.dumps(
            {
                "status": record["status"],
                **record.get("results", {}),
                "capture_error": record.get("capture_error"),
                "source_unchanged": record["source_unchanged"],
            }
        )
    )
    return 0 if passed else 1


def capture_p941(output: str, *, scope: str = "full") -> int:
    if scope not in {"full", "focused"}:
        raise ValueError("unknown P9-4.1 capture scope")
    return _capture_candidate_c(output, scope=scope)


def capture_p942(output: str) -> int:
    return _capture_candidate_c(output, scope="current")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--capture-p942":
        raise SystemExit(capture_p942(sys.argv[2]))
    if len(sys.argv) == 3 and sys.argv[1] in {
        "--capture-p941",
        "--capture-p941-focused",
    }:
        raise SystemExit(
            capture_p941(
                sys.argv[2],
                scope="focused" if sys.argv[1].endswith("-focused") else "full",
            )
        )
    unittest.main()

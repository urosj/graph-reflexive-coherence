"""P9-4.1/P9-4.2 construction and P9-4.3 derivative/control pressure.

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
        self.assertEqual(list_supported_profiles(), frozenset({'grcv4-profile-sha256:a6b853ee382895eb78b1a7955a0df22f95d68b27cb0f762503e8c424c2f59b6d', 'grcv4-profile-sha256:e4c04a83240a33d77c50a26ca6effbb6ce142774bd01f0966861dd517a94e2c4', 'grcv4-profile-sha256:16ed65f7f65d4716e1be3e384f6fa0f957d26dd7b7a3f7e1b43ad1aa3f250946', 'grcv4-profile-sha256:a56ef981821478cc50a3551a914dd6240e0dc62c9ca69d52305bd59a3405f69e', 'grcv4-profile-sha256:058ae6b1f923c85952ffdfa083af74e3b56dd450f309190f307c3ea56ac2aa75'}))

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
        self.assertEqual(list_supported_profiles(), frozenset({'grcv4-profile-sha256:a6b853ee382895eb78b1a7955a0df22f95d68b27cb0f762503e8c424c2f59b6d', 'grcv4-profile-sha256:e4c04a83240a33d77c50a26ca6effbb6ce142774bd01f0966861dd517a94e2c4', 'grcv4-profile-sha256:16ed65f7f65d4716e1be3e384f6fa0f957d26dd7b7a3f7e1b43ad1aa3f250946', 'grcv4-profile-sha256:a56ef981821478cc50a3551a914dd6240e0dc62c9ca69d52305bd59a3405f69e', 'grcv4-profile-sha256:058ae6b1f923c85952ffdfa083af74e3b56dd450f309190f307c3ea56ac2aa75'}))

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


def p943_fixture(**candidate: float) -> Any:
    """Nonreference SPD partial-selector point, with dyadic resource inputs."""
    graph = GRCV4Graph((0, 1, 2), (OrientedEdge("a", 0, 1), OrientedEdge("b", 1, 2)))
    return current_fixture(
        graph=graph,
        weights={"a": 2, "b": 3},
        hodge=((2, 0.5), (0.5, 1.5)),
        resource=(0.5, 1.25, 2.25),
        changes={
            "candidate": {
                "Lambda_C": 3,
                "kappa_M_C": 1.1,
                "chi_C": 1,
                "zeta_C": 0.4,
                "tau_C": 0.3,
                **candidate,
            }
        },
    )


def p943_arrays(current: Any) -> dict[str, Any]:
    import numpy as np

    a = current.algebra
    return {
        key: np.asarray(value, dtype=float)
        for key, value in {
            "projector": a.selector.projector,
            "sector": a.selector.selected.values,
            "deformation": a.deformation,
            "hm": a.retained_hodge.matrix,
            "phi": a.potential.values,
            "j0": a.baseline.values,
        }.items()
    }


def p943_direction(inputs: Any, dc: Any, dh: Any) -> dict[str, Any]:
    """Independent analytic chain; no production selector or linear-solve helper.

    H0, B, reference mobility and the complete profile are fixed. Spectral
    divided differences occur only across selected/unselected clusters.
    The derivative is of the real constitutive equations, not a derivative of
    the discontinuous map that rounds every input/output to binary64.
    """
    import numpy as np

    ref = inputs.geometry.reference
    p = ref.profile.params_resolved.candidate
    b = np.asarray(ref.graph.incidence)
    c, h = (
        np.asarray(inputs.current.C),
        np.asarray(inputs.geometry.one_form_hodge.matrix),
    )
    dc, dh = np.asarray(dc, dtype=float), np.asarray(dh, dtype=float)
    if (
        p.potential_evaluator_id != "quadratic_site_potential_zero_derivative_v1"
        or inputs.context.contract_id != "constant_zero_context_v1"
        or dict(inputs.context.value)
        or not np.array_equal(inputs.geometry.pairings.vertex.matrix, np.eye(len(c)))
    ):
        raise ValueError(
            "derivative oracle requires the supported zero-potential/context and unit-measure declarations"
        )
    if (
        dc.shape != c.shape
        or dh.shape != h.shape
        or not np.array_equal(dh, dh.T)
        or not np.all(np.isfinite(dc))
        or not np.all(np.isfinite(dh))
    ):
        raise ValueError("invalid derivative direction")
    values, vectors = np.linalg.eigh(b @ h @ b.T)
    if min(abs(values - p.Lambda_C)) == 0:
        raise ValueError("oracle cutoff tie")
    selected = values < p.Lambda_C
    projector = vectors[:, selected] @ vectors[:, selected].T
    perturbation = vectors.T @ (b @ dh @ b.T) @ vectors
    divided = np.zeros_like(perturbation)
    for i in range(len(c)):
        for j in range(len(c)):
            if selected[i] != selected[j]:
                divided[i, j] = (
                    (int(selected[i]) - int(selected[j]))
                    * perturbation[i, j]
                    / (values[i] - values[j])
                )
    dp = vectors @ divided @ vectors.T
    # The spectral proposal remains binary64; carry the nonlinear/product chain
    # in an explicit Decimal context so a small intermediate can be amplified
    # before final binary64 rounding. This is a bounded numerical oracle, not
    # an arbitrary-range spectral or transcendental proof.
    from decimal import (
        Context,
        Decimal,
        DecimalException,
        DivisionByZero,
        InvalidOperation,
        Overflow,
        ROUND_HALF_EVEN,
        Underflow,
        localcontext,
    )

    context = Context(
        prec=90,
        Emin=-999999,
        Emax=999999,
        rounding=ROUND_HALF_EVEN,
        traps=[InvalidOperation, DivisionByZero, Overflow, Underflow],
    )
    decimal_array = np.vectorize(
        lambda value: Decimal.from_float(float(value)), otypes=[object]
    )
    try:
        with localcontext(context):
            b, c, h, dc, dh, pd, dpd = map(
                decimal_array, (b, c, h, dc, dh, projector, dp)
            )
            cref, km, kphi, eta = map(
                Decimal.from_float,
                map(float, (p.C_ref, p.kappa_M_C, p.kappa_Phi_C, p.eta_C)),
            )
            t = pd @ c
            dt = dpd @ c + pd @ dc
            ratios = t / cref
            tails = [(-2 * abs(x)).exp() for x in ratios]
            rho = np.array(
                [
                    (1 - q) / (1 + q) * (-1 if x < 0 else 1)
                    for x, q in zip(ratios, tails, strict=True)
                ],
                dtype=object,
            )
            drho = np.array(
                [
                    4 * q * v / (cref * (1 + q) ** 2)
                    for q, v in zip(tails, dt, strict=True)
                ],
                dtype=object,
            )
            ends = [
                (
                    ref.graph.node_index(e.tail_node_id),
                    ref.graph.node_index(e.head_node_id),
                )
                for e in ref.graph.oriented_edges
            ]
            average = np.array([(rho[i] + rho[j]) / 2 for i, j in ends], dtype=object)
            daverage = np.array(
                [(drho[i] + drho[j]) / 2 for i, j in ends], dtype=object
            )
            d = np.array([(km * a / 2).exp() for a in average], dtype=object)
            dd = km * d * daverage / 2
            diag, ddiag = np.diag(d), np.diag(dd)
            hm = diag @ h @ diag
            left, middle, right = ddiag @ h @ diag, diag @ dh @ diag, diag @ h @ ddiag
            dhm = left + middle + right
            geometry_term = kphi * b @ dhm @ b.T @ c
            resource_term = kphi * b @ hm @ b.T @ dc
            dphi = geometry_term + resource_term  # V''=0 and delta_U=0 by declaration.
            mobility = eta * np.diag(
                [
                    Decimal.from_float(float(p.W_C_tr[e]))
                    for e in ref.graph.live_edge_ids
                ]
            )
            wide = dict(
                sector=dt,
                deformation=dd,
                hm=dhm,
                phi=dphi,
                j0=-mobility @ b.T @ dphi,
                left=left,
                middle=middle,
                right=right,
                geometry_term=geometry_term,
                resource_term=resource_term,
            )
            rounded = {
                key: np.asarray(value, dtype=float) for key, value in wide.items()
            }
            if any(not np.all(np.isfinite(value)) for value in rounded.values()):
                raise ValueError("derivative oracle final binary64 range exceeded")
            representation = []
            for key in ("sector", "deformation", "hm", "phi", "j0"):
                for index in np.ndindex(wide[key].shape):
                    value = wide[key][index]
                    binary = float(rounded[key][index])
                    if value and abs(binary) < sys.float_info.min:
                        representation.append(
                            dict(
                                output=key,
                                index=list(index),
                                decimal_sign=1 if value > 0 else -1,
                                log_abs_decimal=str(abs(value).ln()),
                                binary64_hex=binary.hex(),
                                status="rounded_to_zero"
                                if binary == 0
                                else "subnormal",
                            )
                        )
    except DecimalException as failure:
        raise ValueError(
            "derivative oracle Decimal operation/exponent range exceeded; "
            "no zero or NaN derivative is certified"
        ) from failure
    return dict(
        projector=dp,
        **rounded,
        representation=representation,
        base_projector=projector,
        rank=int(np.count_nonzero(selected)),
    )


def p943_perturb(inputs: Any, dc: Any, dh: Any, epsilon: float) -> Any:
    import numpy as np
    from pygrc.models.grc_v4_state import GRCV4AuthoritativeState

    c = np.asarray(inputs.current.C) + epsilon * np.asarray(dc)
    h = np.asarray(inputs.geometry.one_form_hodge.matrix) + epsilon * np.asarray(dh)
    return replace(
        inputs,
        current=GRCV4AuthoritativeState(
            tuple(float(x) for x in c), None, inputs.current.Z_4
        ),
        geometry=GRCV4Geometry(
            inputs.geometry.reference,
            OneFormHodge(
                inputs.geometry.reference.graph,
                tuple(tuple(float(x) for x in row) for row in h),
            ),
        ),
    )


def p943_centered(inputs: Any, dc: Any, dh: Any, epsilon: float) -> dict[str, Any]:
    """Differentiate actual fresh current evaluations only within the same stratum."""
    from pygrc.models.grc_v4_candidate_c import CandidateCCurrent

    if epsilon <= 0 or not math.isfinite(epsilon):
        raise ValueError("positive finite difference step required")
    plus, minus = (
        p943_perturb(inputs, dc, dh, epsilon),
        p943_perturb(inputs, dc, dh, -epsilon),
    )
    if plus.current == minus.current and plus.geometry == minus.geometry:
        raise ValueError("finite difference step is unresolvable in binary64")
    actual, left, right = (
        CandidateCCurrent(inputs),
        CandidateCCurrent(plus),
        CandidateCCurrent(minus),
    )
    if (
        not actual.algebra.selector.rank
        == left.algebra.selector.rank
        == right.algebra.selector.rank
    ):
        raise ValueError("finite difference crosses a selector stratum")
    a, b = p943_arrays(left), p943_arrays(right)
    return {key: (a[key] - b[key]) / (2 * epsilon) for key in a}


class CandidateCControlDerivativeTests(unittest.TestCase):
    observations: list[dict[str, Any]] = []

    def check_direction(
        self, inputs: Any, dc: Any, dh: Any, *, label: str, tolerance: float = 2e-6
    ) -> None:
        import numpy as np

        expected = p943_direction(inputs, dc, dh)
        if expected["representation"]:
            raise ValueError(
                "finite-difference comparison cannot certify subnormal or rounded-zero derivatives"
            )
        observed = p943_centered(inputs, dc, dh, 2**-12)
        errors = {}
        for key in observed:
            error = float(
                np.max(abs(observed[key] - expected[key]))
                / max(1, float(np.max(abs(expected[key]))))
            )
            errors[key] = error
            self.assertLess(error, tolerance, (label, key, error))
        self.observations.append(
            dict(case=label, normalized_max_errors=errors, tolerance=tolerance)
        )

    def test_exact_path_projector_and_geometry_derivative_oracle(self) -> None:
        import numpy as np
        from pygrc.models.grc_v4_candidate_c import CandidateCCurrent

        graph = p943_fixture().geometry.reference.graph
        # Path spectrum 0,1,3. Cutoff 2 retains constant and antisymmetric modes.
        inputs = current_fixture(
            graph=graph,
            weights={"a": 2, "b": 3},
            hodge=((1, 0), (0, 1)),
            resource=(0.5, 1.25, 2.25),
            changes={"candidate": {"Lambda_C": 2, "kappa_M_C": 1.1}},
        )
        expected_p = np.array([[5, 2, -1], [2, 2, 2], [-1, 2, 5]]) / 6
        expected_dp = np.array([[-1, 1, 0], [1, 0, -1], [0, -1, 1]]) / 2
        direction = p943_direction(inputs, (0, 0, 0), ((1, 0), (0, -1)))
        np.testing.assert_allclose(
            direction["base_projector"], expected_p, atol=1e-15, rtol=0
        )
        np.testing.assert_allclose(
            direction["projector"], expected_dp, atol=1e-15, rtol=0
        )
        np.testing.assert_allclose(
            CandidateCCurrent(inputs).algebra.selector.projector,
            expected_p,
            atol=1e-15,
            rtol=0,
        )
        self.check_direction(
            inputs, (0, 0, 0), ((1, 0), (0, -1)), label="literal_path_projector"
        )

    def test_complete_resource_geometry_and_joint_derivatives(self) -> None:
        inputs = p943_fixture()
        for label, dc, dh in [
            ("resource", (0.25, -0.5, 0.25), ((0, 0), (0, 0))),
            ("geometry", (0, 0, 0), ((0.25, -0.5), (-0.5, 0.125))),
            ("joint", (0.25, -0.5, 0.25), ((0.25, -0.5), (-0.5, 0.125))),
        ]:
            with self.subTest(direction=label):
                self.check_direction(inputs, dc, dh, label=label)

    def test_joint_difference_converges_at_second_order(self) -> None:
        import numpy as np

        inputs, dc, dh = (
            p943_fixture(kappa_M_C=1.7),
            (0.5, -0.75, 0.25),
            ((0.5, -0.25), (-0.25, 0.25)),
        )
        expected = p943_direction(inputs, dc, dh)
        errors = []
        for step in (2**-5, 2**-7, 2**-9):
            actual = p943_centered(inputs, dc, dh, step)
            errors.append(float(np.linalg.norm(actual["j0"] - expected["j0"])))
        self.assertLess(errors[1], errors[0] / 8)
        self.assertLess(errors[2], errors[1] / 8)
        self.observations.append(
            dict(
                case="second_order_convergence",
                steps=[2**-5, 2**-7, 2**-9],
                errors=errors,
            )
        )

    def test_every_hodge_product_and_resource_term_is_load_bearing(self) -> None:
        import numpy as np

        inputs, dc, dh = (
            p943_fixture(),
            (0.25, -0.5, 0.25),
            ((0.25, -0.5), (-0.5, 0.125)),
        )
        derivative = p943_direction(inputs, dc, dh)
        observed = p943_centered(inputs, dc, dh, 2**-12)
        for term in ("left", "middle", "right"):
            with self.subTest(term=term):
                self.assertGreater(np.linalg.norm(derivative[term]), 0.01)
                self.assertGreater(
                    np.linalg.norm(
                        observed["hm"] - (derivative["hm"] - derivative[term])
                    ),
                    0.01,
                )
        for term in ("geometry_term", "resource_term"):
            with self.subTest(term=term):
                self.assertGreater(
                    np.linalg.norm(
                        observed["phi"] - (derivative["phi"] - derivative[term])
                    ),
                    0.01,
                )
        # Freezing P when h changes gives the wrong selected-content derivative.
        fixed_selector = derivative["base_projector"] @ np.array(dc)
        self.assertGreater(np.linalg.norm(observed["sector"] - fixed_selector), 0.01)

    def test_directional_linearity_and_zero_direction(self) -> None:
        import numpy as np

        inputs = p943_fixture()
        a = p943_direction(inputs, (0.25, -0.5, 0.25), ((0.25, 0), (0, -0.125)))
        b = p943_direction(inputs, (-0.5, 0.25, 0.25), ((0, 0.25), (0.25, 0.125)))
        combined = p943_direction(
            inputs, (0.75, -0.9375, 0.1875), ((0.375, -0.1875), (-0.1875, -0.28125))
        )
        zero = p943_direction(inputs, (0, 0, 0), ((0, 0), (0, 0)))
        for key in ("projector", "sector", "deformation", "hm", "phi", "j0"):
            np.testing.assert_allclose(
                combined[key], 1.5 * a[key] - 0.75 * b[key], atol=3e-14, rtol=2e-14
            )
            np.testing.assert_array_equal(zero[key], np.zeros_like(zero[key]))

    def test_zero_controls_are_separate_full_chains_on_nonreference_hodge(self) -> None:
        import numpy as np
        from pygrc.models.grc_v4_candidate_c import CandidateCCurrent

        baseline = CandidateCCurrent(p943_fixture())
        controls = {
            key: CandidateCCurrent(p943_fixture(**{key: 0}))
            for key in ("kappa_M_C", "chi_C", "zeta_C", "tau_C")
        }
        for key, point in controls.items():
            source = point.inputs.geometry.reference.profile.params_resolved.candidate.to_payload()
            original = baseline.inputs.geometry.reference.profile.params_resolved.candidate.to_payload()
            self.assertEqual(
                {name for name in source if source[name] != original[name]}, {key}
            )
            self.assertEqual(
                point.algebra.transport.mobility.matrix,
                baseline.algebra.transport.mobility.matrix,
            )
            self.assertEqual(
                point.algebra.transport.mobility_constructor_identity,
                baseline.algebra.transport.mobility_constructor_identity,
            )
            self.assertEqual(
                point.algebra.transport.mobility.apply(
                    OneForm(point.algebra.transport.graph, (1, -2))
                ),
                baseline.algebra.transport.mobility.apply(
                    OneForm(baseline.algebra.transport.graph, (1, -2))
                ),
            )
            self.assertEqual(point.algebra.selector, baseline.algebra.selector)
        km, chi, zeta, tau = (
            controls[k] for k in ("kappa_M_C", "chi_C", "zeta_C", "tau_C")
        )
        self.assertEqual(km.algebra.retained_hodge, km.inputs.geometry.one_form_hodge)
        self.assertEqual(km.algebra.deformation, (1, 1))
        self.assertNotEqual(
            km.algebra.retained_hodge, km.algebra.transport.structural_hodge
        )
        self.assertNotEqual(km.algebra.baseline, baseline.algebra.baseline)
        self.assertNotEqual(km.read.flux.values, (0, 0))
        for point in (chi, zeta, tau):
            self.assertEqual(
                point.algebra.retained_hodge, baseline.algebra.retained_hodge
            )
            self.assertEqual(point.algebra.baseline, baseline.algebra.baseline)
        self.assertEqual(chi.current, chi.algebra.baseline)
        self.assertEqual(chi.read.flux.values, (0, 0))
        self.assertNotEqual(chi.read.ungated_flat.values, (0, 0))
        self.assertEqual(zeta.current, zeta.algebra.baseline)
        self.assertNotEqual(zeta.read.flux.values, (0, 0))
        self.assertEqual(tau.algebra.response, ((1, 0), (0, 1)))
        self.assertEqual(tau.read.flux, tau.current)
        np.testing.assert_allclose(
            tau.current.values, np.array(tau.algebra.baseline.values) / 0.6, rtol=2e-14
        )
        self.assertNotEqual(
            tau.algebra.retained_hodge, tau.inputs.geometry.one_form_hodge
        )
        self.assertNotEqual(tau.algebra.physical_identification, ((1, 0), (0, 1)))
        self.assertNotEqual(tau.current, baseline.current)

    def test_derivatives_under_each_zero_control_remain_distinct(self) -> None:
        import numpy as np

        dc, dh = (0.25, -0.5, 0.25), ((0.25, -0.5), (-0.5, 0.125))
        original = p943_direction(p943_fixture(), dc, dh)
        for key in ("kappa_M_C", "chi_C", "zeta_C", "tau_C"):
            inputs = p943_fixture(**{key: 0})
            self.check_direction(inputs, dc, dh, label="zero_" + key)
            derived = p943_direction(inputs, dc, dh)
            if key == "kappa_M_C":
                np.testing.assert_array_equal(derived["deformation"], (0, 0))
                np.testing.assert_array_equal(derived["hm"], dh)
                self.assertGreater(np.linalg.norm(derived["j0"] - original["j0"]), 0.01)
            else:
                np.testing.assert_array_equal(derived["j0"], original["j0"])

    def test_reference_reduction_has_closed_resource_and_hodge_derivatives(
        self,
    ) -> None:
        import numpy as np
        from pygrc.models.grc_v4_candidate_c import CandidateCCurrent

        inputs = p943_fixture(kappa_M_C=0)
        inputs = replace(inputs, geometry=inputs.geometry.reference.geometry())
        actual = CandidateCCurrent(inputs)
        b = np.asarray(inputs.geometry.reference.graph.incidence)
        w = np.diag((2, 3))
        p = actual.algebra.transport.params
        c, dc, dh = (
            np.array(inputs.current.C),
            np.array((0.25, -0.5, 0.25)),
            np.array(((0.25, 0.125), (0.125, -0.125))),
        )
        phi = p.kappa_Phi_C * b @ w @ b.T @ c
        np.testing.assert_array_equal(actual.algebra.potential.values, phi)
        expected = (
            -p.eta_C * w @ b.T @ (p.kappa_Phi_C * b @ (dh @ b.T @ c + w @ b.T @ dc))
        )
        np.testing.assert_allclose(
            p943_direction(inputs, dc, dh)["j0"], expected, atol=1e-14
        )
        self.check_direction(inputs, dc, dh, label="reference_kappa_zero")

    def test_vertex_signed_edge_covariance_of_values_and_directions(self) -> None:
        import numpy as np
        from pygrc.models.grc_v4_candidate_c import CandidateCCurrent

        inputs, dc, dh = (
            p943_fixture(),
            np.array((0.25, -0.5, 0.25)),
            np.array(((0.25, -0.5), (-0.5, 0.125))),
        )
        graph = inputs.geometry.reference.graph
        base = CandidateCCurrent(inputs)
        derivative = p943_direction(inputs, dc, dh)
        h = np.asarray(inputs.geometry.one_form_hodge.matrix)
        rng = random.Random(943)
        for case in range(12):
            nodes, order = list(range(3)), list(range(2))
            rng.shuffle(nodes)
            rng.shuffle(order)
            signs = np.array([rng.choice((-1, 1)) for _ in order])
            labels = {i: f"node-{case}-{i}" for i in range(3)}
            edges = []
            for j, sign in zip(order, signs, strict=True):
                edge = graph.oriented_edges[j]
                tail, head = edge.tail_node_id, edge.head_node_id
                if sign < 0:
                    tail, head = head, tail
                edges.append(OrientedEdge(edge.edge_id, labels[tail], labels[head]))
            moved = GRCV4Graph(tuple(labels[i] for i in nodes), tuple(edges))
            h2 = h[np.ix_(order, order)] * np.outer(signs, signs)
            target = current_fixture(
                graph=moved,
                weights={"a": 2, "b": 3},
                hodge=tuple(map(tuple, h2)),
                resource=tuple(inputs.current.C[i] for i in nodes),
                changes={
                    "candidate": {
                        "Lambda_C": 3,
                        "kappa_M_C": 1.1,
                        "chi_C": 1,
                        "zeta_C": 0.4,
                        "tau_C": 0.3,
                    }
                },
            )
            current = CandidateCCurrent(target)
            tangent = p943_direction(
                target, dc[nodes], dh[np.ix_(order, order)] * np.outer(signs, signs)
            )
            for original, transformed in [
                (p943_arrays(base), p943_arrays(current)),
                (derivative, tangent),
            ]:
                np.testing.assert_allclose(
                    transformed["projector"],
                    original["projector"][np.ix_(nodes, nodes)],
                    atol=2e-12,
                    rtol=2e-12,
                )
                np.testing.assert_allclose(
                    transformed["sector"],
                    original["sector"][nodes],
                    atol=2e-12,
                    rtol=2e-12,
                )
                np.testing.assert_allclose(
                    transformed["deformation"],
                    original["deformation"][order],
                    atol=2e-12,
                    rtol=2e-12,
                )
                np.testing.assert_allclose(
                    transformed["phi"], original["phi"][nodes], atol=2e-12, rtol=2e-12
                )
                np.testing.assert_allclose(
                    transformed["j0"],
                    original["j0"][order] * signs,
                    atol=2e-12,
                    rtol=2e-12,
                )
                np.testing.assert_allclose(
                    transformed["hm"],
                    original["hm"][np.ix_(order, order)] * np.outer(signs, signs),
                    atol=2e-12,
                    rtol=2e-12,
                )
            self.check_direction(
                target,
                dc[nodes],
                dh[np.ix_(order, order)] * np.outer(signs, signs),
                label=f"signed_covariance_{case}",
            )

    def test_repeated_cluster_derivative_is_basis_independent_and_finite(self) -> None:
        import numpy as np
        from unittest.mock import patch

        graph = GRCV4Graph(
            tuple(range(4)),
            tuple(OrientedEdge(str(i), i, (i + 1) % 4) for i in range(4)),
        )
        inputs = current_fixture(
            graph=graph,
            weights={str(i): 1 for i in range(4)},
            resource=(0.5, 1, 1.5, 2),
            changes={"candidate": {"Lambda_C": 3, "kappa_M_C": 0.8}},
        )
        dc = np.array((0.25, -0.5, 0.5, -0.25))
        dh = np.diag((0.25, -0.25, 0.5, -0.5))
        expected = p943_direction(inputs, dc, dh)
        real = np.linalg.eigh

        def varied(matrix: Any) -> Any:
            values, vectors = real(matrix)
            if abs(values[1] - values[2]) < 1e-12:
                rotation = np.array([[0.6, -0.8], [0.8, 0.6]])
                vectors[:, 1:3] = vectors[:, 1:3] @ rotation
            order = [3, 1, 0, 2]
            return values[order], vectors[:, order] * np.array((-1, 1, -1, 1))

        with patch.object(np.linalg, "eigh", side_effect=varied):
            actual = p943_direction(inputs, dc, dh)
            for key in ("projector", "sector", "hm", "phi", "j0"):
                np.testing.assert_allclose(
                    actual[key], expected[key], atol=3e-14, rtol=3e-14
                )
            self.check_direction(inputs, dc, dh, label="repeated_cluster_rotation")

    def test_near_gap_growth_and_crossing_are_not_hidden(self) -> None:
        import numpy as np

        # Complete 3-node graph with Laplacian on the nonconstant plane:
        # diag(lambda-gap/2,lambda+gap/2). An off-diagonal edge
        # perturbation couples the sectors; sensitivity grows like 1/gap.
        graph = GRCV4Graph(
            (0, 1, 2),
            (OrientedEdge("a", 0, 1), OrientedEdge("b", 1, 2), OrientedEdge("c", 2, 0)),
        )
        b = np.array(graph.incidence)
        q1 = np.array((1, -1, 0)) / math.sqrt(2)
        q2 = np.array((1, 1, -2)) / math.sqrt(6)
        norms = []
        for gap in (2**-4, 2**-8, 2**-12):
            laplacian = (
                3 * np.eye(3)
                - np.ones((3, 3))
                + 0.5 * gap * (np.outer(q2, q2) - np.outer(q1, q1))
            )
            h = (
                np.eye(3)
                + b.T @ (laplacian - (3 * np.eye(3) - np.ones((3, 3)))) @ b / 9
            )
            # h(t)=h+t*dh, with lambda gap about the cutoff 3.
            dh = b.T @ (np.outer(q1, q2) + np.outer(q2, q1)) @ b / 9
            inputs = current_fixture(
                graph=graph,
                weights={e: 1 for e in "abc"},
                hodge=tuple(map(tuple, h)),
                resource=(0.5, 1.25, 2.25),
                changes={"candidate": {"Lambda_C": 3, "kappa_M_C": 0.7}},
            )
            expected = p943_direction(inputs, (0, 0, 0), dh)
            norms.append(float(np.linalg.norm(expected["projector"])))
            observed = p943_centered(inputs, (0, 0, 0), dh, gap / 1024)
            for key in ("projector", "sector", "hm", "phi", "j0"):
                np.testing.assert_allclose(
                    observed[key], expected[key], rtol=2e-5, atol=2e-6
                )
        self.assertAlmostEqual(norms[1] / norms[0], 16, delta=1e-8)
        self.assertAlmostEqual(norms[2] / norms[1], 16, delta=1e-7)
        self.observations.append(
            dict(
                case="near_gap_sensitivity",
                gaps=[2**-4, 2**-8, 2**-12],
                projector_derivative_norms=norms,
            )
        )
        # Endpoint evaluations in different ranks are locally admissible, but
        # their quotient cannot certify a fixed-stratum derivative.
        inputs = p943_fixture(Lambda_C=3)
        with self.assertRaisesRegex(ValueError, "stratum|spectrum"):
            p943_centered(inputs, (0, 0, 0), ((2, 0), (0, 2)), 0.5)

    def test_disconnected_loop_parallel_and_exterior_sector_derivatives(self) -> None:
        import numpy as np

        graph = GRCV4Graph(
            (0, 1, 2),
            (OrientedEdge("a", 0, 1), OrientedEdge("b", 1, 0), OrientedEdge("l", 0, 0)),
        )
        for cutoff in (-1, 0.5, 100):
            inputs = current_fixture(
                graph=graph,
                weights={e: 1 for e in ("a", "b", "l")},
                hodge=((2, 0.25, 0.125), (0.25, 1, 0.25), (0.125, 0.25, 1.5)),
                resource=(0.5, 1.5, 2),
                changes={"candidate": {"Lambda_C": cutoff, "kappa_M_C": 0.9}},
            )
            dc = (0.25, -0.25, 0)
            dh = ((0.25, 0.125, 0), (0.125, -0.25, 0.125), (0, 0.125, 0.5))
            expected = p943_direction(inputs, dc, dh)
            np.testing.assert_allclose(
                expected["projector"], np.zeros((3, 3)), atol=1e-14
            )
            self.check_direction(inputs, dc, dh, label=f"multigraph_cutoff_{cutoff}")
            # A loop has zero direct gradient/baseline, even with offdiagonal H.
            self.assertEqual(expected["j0"][2], 0)
            self.assertEqual(expected["phi"][2], 0)

    def test_trial_current_and_metadata_do_not_become_baseline_directions(self) -> None:
        from pygrc.models.grc_v4_candidate_c import CandidateCCurrent
        from tests.models.test_grc_v4_geometry import stage_inputs_fixture

        inputs = p943_fixture()
        ref = stage_reference_fixture(
            "C",
            "CI",
            graph=inputs.geometry.reference.graph,
            weights={"a": 2, "b": 3},
            changes={
                "solver": {"absolute_tolerance": 1e-11, "relative_tolerance": 1e-11},
                "candidate": {"Lambda_C": 3, "kappa_M_C": 1.1, "tau_C": 0.3},
            },
        )
        inputs = stage_inputs_fixture(ref, stage="ci_trial")
        first = CandidateCCurrent(inputs)
        for values in ((0, 0), (1e6, -1e6)):
            current = CandidateCCurrent(
                replace(
                    inputs,
                    trial_current=PhysicalFlux(ref.graph, values),
                    evaluation_index=9,
                    time=7,
                )
            )
            self.assertNotEqual(current.identity, first.identity)
            self.assertEqual(current.algebra.baseline, first.algebra.baseline)
            self.assertEqual(current.current, first.current)

    def test_eta_profile_family_variation_has_the_declared_delta_m_term(self) -> None:
        import numpy as np
        from pygrc.models.grc_v4_candidate_c import CandidateCCurrent

        base = CandidateCCurrent(p943_fixture(eta_C=1))
        h = 2**-10
        plus, minus = (
            CandidateCCurrent(p943_fixture(eta_C=1 + s * h)) for s in (1, -1)
        )
        self.assertNotEqual(
            base.inputs.geometry.reference.profile.complete_profile_id,
            plus.inputs.geometry.reference.profile.complete_profile_id,
        )
        self.assertEqual(base.algebra.potential, plus.algebra.potential)
        self.assertEqual(base.algebra.retained_hodge, plus.algebra.retained_hodge)
        expected = (
            -np.diag((2, 3))
            @ np.array(base.inputs.geometry.reference.graph.incidence).T
            @ np.array(base.algebra.potential.values)
        )
        np.testing.assert_allclose(
            (
                np.array(plus.algebra.baseline.values)
                - np.array(minus.algebra.baseline.values)
            )
            / (2 * h),
            expected,
            rtol=1e-12,
            atol=1e-12,
        )
        # This is explicitly an adjacent-profile parameter study, not ordinary
        # same-profile delta_M=0 or a lawful lifecycle migration.

    def test_resource_boundary_uses_admitted_one_sided_direction(self) -> None:
        import numpy as np
        from pygrc.models.grc_v4_candidate_c import CandidateCCurrent
        from pygrc.models.grc_v4_state import GRCV4AuthoritativeState

        inputs = p943_fixture()
        inputs = replace(inputs, current=GRCV4AuthoritativeState((0, 1, 2), None, None))
        dc, dh = (1, -1, 0), ((0, 0), (0, 0))
        step = 2**-12
        with self.assertRaises(ValueError):
            p943_centered(inputs, dc, dh, step)
        points = [
            p943_arrays(CandidateCCurrent(p943_perturb(inputs, dc, dh, t * step)))
            for t in (0, 1, 2)
        ]
        expected = p943_direction(inputs, dc, dh)
        for key in ("sector", "hm", "phi", "j0"):
            estimate = (-3 * points[0][key] + 4 * points[1][key] - points[2][key]) / (
                2 * step
            )
            np.testing.assert_allclose(estimate, expected[key], rtol=3e-6, atol=3e-6)

    def test_difference_probe_rejects_unresolvable_steps_and_domain_loss(self) -> None:
        inputs = p943_fixture()
        before = canonical_json_bytes(inputs.to_payload())
        for step in (0, -1, float("inf"), 5e-324):
            with self.subTest(step=step), self.assertRaises(ValueError):
                p943_centered(inputs, (0.25, -0.5, 0.25), ((0.25, 0), (0, 0.25)), step)
        with self.assertRaises(ValueError):
            p943_centered(inputs, (0, 0, 0), ((4, 0), (0, 4)), 1)
        self.assertEqual(canonical_json_bytes(inputs.to_payload()), before)

    def test_literal_scalar_derivative_and_saturation_tail(self) -> None:
        from decimal import Decimal, localcontext
        from pygrc.models.grc_v4_candidate_c import CandidateCCurrent

        graph = CandidateCCurrentTests.edge_graph()
        for mean in (0.5, 4, 20):
            inputs = current_fixture(
                graph=graph,
                weights={"e": 2},
                resource=(mean - 0.25, mean + 0.25),
                changes={
                    "candidate": {
                        "Lambda_C": 1,
                        "kappa_M_C": 0.75,
                        "eta_C": 0.5,
                        "kappa_Phi_C": 1,
                        "C_ref": 1,
                    }
                },
            )
            # Uniform delta_C changes mean, retaining the fixed resource gradient.
            # This is ambient constitutive sensitivity, not charge-preserving motion.
            expected = p943_direction(inputs, (1, 1), ((0,),))
            with localcontext() as ctx:
                ctx.prec = 70
                m = Decimal(str(mean))
                e = (2 * m).exp()
                rho = (e - 1) / (e + 1)
                hm = Decimal(2) * (Decimal(".75") * rho).exp()
                j0 = hm
                dj0 = j0 * Decimal(".75") * (4 * e / (e + 1) ** 2)
                target = float(dj0)
            self.assertGreater(target, 0)
            self.assertAlmostEqual(expected["j0"][0] / target, 1, delta=2e-14)
            self.assertAlmostEqual(
                CandidateCCurrent(inputs).algebra.baseline.values[0] / float(j0),
                1,
                delta=2e-14,
            )
            if mean < 20:
                self.check_direction(
                    inputs, (1, 1), ((0,),), label=f"scalar_mean_{mean}"
                )
            else:
                self.assertEqual(math.tanh(mean), 1)
                rounded = p943_centered(inputs, (1, 1), ((0,),), 2**-12)
                self.assertEqual(rounded["j0"][0], 0)
                self.observations.append(
                    dict(
                        case="saturated_tanh_tail",
                        mean=mean,
                        mathematical_derivative=target,
                        rounded_tanh=1,
                        rounded_current_difference=0,
                        finite_difference_claim=False,
                    )
                )

    def test_constitutive_potential_is_not_total_retained_energy_gradient(self) -> None:
        import numpy as np
        from pygrc.models.grc_v4_candidate_c import CandidateCCurrent

        inputs, dc, dh = p943_fixture(), np.array((0.25, -0.5, 0.25)), np.zeros((2, 2))
        current = CandidateCCurrent(inputs)
        tangent = p943_direction(inputs, dc, dh)
        b = np.asarray(inputs.geometry.reference.graph.incidence)
        gradient = b.T @ np.asarray(inputs.current.C)
        kappa = current.algebra.transport.params.kappa_Phi_C
        frozen = float(np.asarray(current.algebra.potential.values) @ dc)
        extra = float(0.5 * kappa * gradient @ tangent["hm"] @ gradient)
        self.assertGreater(abs(extra), 0.01)

        def energy(epsilon: float) -> float:
            point = CandidateCCurrent(p943_perturb(inputs, dc, dh, epsilon))
            g = b.T @ np.asarray(point.inputs.current.C)
            return float(
                0.5 * kappa * g @ np.asarray(point.algebra.retained_hodge.matrix) @ g
            )

        step = 2**-12
        observed = (energy(step) - energy(-step)) / (2 * step)
        self.assertAlmostEqual(observed, frozen + extra, delta=1e-7)
        self.assertGreater(abs(observed - frozen), 0.01)
        self.observations.append(
            dict(
                case="constitutive_potential_not_energy_gradient",
                frozen_potential_action=frozen,
                retained_energy_chain_term=extra,
                energy_difference=observed,
            )
        )

    def test_zero_context_and_potential_declarations_bound_derivative_scope(
        self,
    ) -> None:
        from pygrc.models.grc_v4_candidate_c import CandidateCCurrent
        from pygrc.models.grc_v4_geometry import GRCV4Context
        from pygrc.models.grc_v4_state import FrozenJSONMap

        unknown = current_fixture(
            changes={
                "candidate": {
                    "potential_evaluator_id": "unimplemented_nonzero_potential"
                }
            }
        )
        with self.assertRaisesRegex(ValueError, "oracle requires"):
            p943_direction(unknown, (1, -1, 0), ((0, 0), (0, 0)))
        with self.assertRaisesRegex(ValueError, "unimplemented C site potential"):
            CandidateCCurrent(unknown)
        inputs = p943_fixture()
        before = canonical_json_bytes(inputs.to_payload())
        with self.assertRaises(ValueError):
            replace(
                inputs,
                context=GRCV4Context(
                    "constant_zero_context_v1", FrozenJSONMap({"U": 1})
                ),
            )
        for dc, dh in [
            ((float("inf"), 0, 0), ((0, 0), (0, 0))),
            ((0, 0, 0), ((0, 1), (0, 0))),
        ]:
            with self.assertRaisesRegex(ValueError, "invalid derivative direction"):
                p943_direction(inputs, dc, dh)
        self.assertEqual(canonical_json_bytes(inputs.to_payload()), before)

    def test_seeded_spd_mixed_directions_match_actual_baseline(self) -> None:
        import numpy as np

        rng = np.random.default_rng(943)
        graph = GRCV4Graph(
            (0, 1, 2),
            (OrientedEdge("a", 0, 1), OrientedEdge("b", 1, 2), OrientedEdge("c", 2, 0)),
        )
        b = np.array(graph.incidence)
        for case in range(8):
            a = rng.integers(-2, 3, size=(3, 3))
            h = (a.T @ a + np.eye(3)) / 4
            values = np.linalg.eigvalsh(b @ h @ b.T)
            cutoff = float((values[1] + values[2]) / 2)
            if values[2] - values[1] < 0.01:
                cutoff = 0.01
            inputs = current_fixture(
                graph=graph,
                weights={"a": 0.5, "b": 2, "c": 4},
                hodge=tuple(map(tuple, h)),
                resource=(0.75, 1.25, 2),
                changes={
                    "candidate": {
                        "Lambda_C": cutoff,
                        "kappa_M_C": float(rng.uniform(-1, 1)),
                    }
                },
            )
            a = rng.integers(-2, 3, size=(3, 3))
            dh = (a + a.T) / 16
            dc = rng.integers(-2, 3, size=3) / 8
            dc[-1] = -sum(dc[:-1])
            self.check_direction(
                inputs, dc, dh, label=f"seeded_spd_{case}", tolerance=1e-5
            )

    @staticmethod
    def saturation_fixture(cref: float, *, km: float = 0.75, gain: float = 1) -> Any:
        return current_fixture(
            graph=CandidateCCurrentTests.edge_graph(),
            weights={"e": 2},
            resource=(0.75, 1.25),
            changes={
                "candidate": {
                    "Lambda_C": 1,
                    "kappa_M_C": km,
                    "eta_C": 0.5 * gain,
                    "kappa_Phi_C": 1,
                    "C_ref": cref,
                }
            },
        )

    @staticmethod
    def scalar_saturation_derivative(
        cref: float, km: float, direction: float, gain: float = 1
    ) -> Any:
        """Independent one-edge closed form using the positive exponential.

        C=(.75,1.25), Hpre=W=2, eta=gain/2, uniform delta_C.
        T=1 exactly; no spectral routine or production/derivative helper is used.
        The callers keep this witness within its stated Decimal exponent range.
        """
        from decimal import Context, Decimal, localcontext

        with localcontext(Context(prec=120)):
            cf, k, v, g = map(
                Decimal.from_float, map(float, (cref, km, direction, gain))
            )
            e = (2 / cf).exp()
            rho = (e - 1) / (e + 1)
            return 2 * g * k * v * (k * rho).exp() * (4 * e / (e + 1) ** 2) / cf

    def test_extreme_saturation_preserves_representable_subnormal(self) -> None:
        from pygrc.models.grc_v4_candidate_c import CandidateCCurrent

        for cf in (
            math.nextafter(1 / 373, 0),
            1 / 373,
            math.nextafter(1 / 373, math.inf),
        ):
            for km in (0.75, -0.75):
                inputs = self.saturation_fixture(cf, km=km)
                self.assertTrue(
                    math.isfinite(CandidateCCurrent(inputs).algebra.baseline.values[0])
                )
                for direction in (1, -1):
                    with self.subTest(cref=cf, km=km, direction=direction):
                        expected = self.scalar_saturation_derivative(cf, km, direction)
                        actual = p943_direction(inputs, (direction, direction), ((0,),))
                        self.assertNotEqual(float(expected), 0)
                        self.assertEqual(actual["j0"][0].hex(), float(expected).hex())
                        row = next(
                            r for r in actual["representation"] if r["output"] == "j0"
                        )
                        self.assertEqual(row["status"], "subnormal")
                        self.assertEqual(row["decimal_sign"], 1 if expected > 0 else -1)
        expected = self.scalar_saturation_derivative(1 / 373, 0.75, 1)
        self.assertEqual(float(expected).hex(), "0x0.00000000003e4p-1022")
        self.observations.append(
            dict(
                case="audit_representable_subnormal",
                C_ref=1 / 373,
                independent_decimal=str(expected),
                binary64_hex=float(expected).hex(),
            )
        )

    def test_subnormal_intermediates_are_not_rounded_before_mobility(self) -> None:
        inputs = self.saturation_fixture(1 / 400, gain=1e100)
        expected = self.scalar_saturation_derivative(1 / 400, 0.75, 1, 1e100)
        actual = p943_direction(inputs, (1, 1), ((0,),))
        self.assertGreater(actual["j0"][0], 0)
        self.assertAlmostEqual(actual["j0"][0] / float(expected), 1, delta=2e-12)
        self.assertEqual(actual["deformation"][0], 0)
        row = next(r for r in actual["representation"] if r["output"] == "deformation")
        self.assertEqual(row["status"], "rounded_to_zero")
        self.assertEqual(row["decimal_sign"], 1)
        # Rounding delta_D or delta_Hm to float before multiplying by mobility
        # loses this representable final derivative. An absolute FD tolerance
        # must not turn the unresolved zero quotient into a claimed check.
        with self.assertRaisesRegex(ValueError, "cannot certify"):
            self.check_direction(inputs, (1, 1), ((0,),), label="unresolved_saturation")
        difference = p943_centered(inputs, (1, 1), ((0,),), 2**-12)
        self.assertEqual(difference["j0"][0], 0)
        self.observations.append(
            dict(
                case="later_mobility_amplifies_tail",
                C_ref=1 / 400,
                gain=1e100,
                independent_decimal=str(expected),
                observed_j0=float(actual["j0"][0]),
                deformation_representation=row,
                rounded_current_difference=0,
                finite_difference_claim=False,
            )
        )

    def test_negative_selected_content_keeps_saturation_derivative_sign(self) -> None:
        from decimal import Context, Decimal, localcontext
        import numpy as np
        from pygrc.models.grc_v4_candidate_c import CandidateCCurrent

        graph = p943_fixture().geometry.reference.graph
        inputs = current_fixture(
            graph=graph,
            weights={"a": 1, "b": 1},
            resource=(0, 1, 8),
            changes={
                "candidate": {
                    "Lambda_C": 2,
                    "kappa_M_C": 0.75,
                    "eta_C": 1e100,
                    "C_ref": 1 / 373,
                }
            },
        )
        point = CandidateCCurrent(inputs)
        self.assertLess(point.algebra.selector.selected.values[0], 0)
        actual = p943_direction(inputs, (1, 1, 1), ((0, 0), (0, 0)))
        # Literal path projector gives T=(-1,3,7), delta_T=(1,1,1).
        # Hpre=I: delta_h_e = kappa/2 * h_e * (delta_rho_i+delta_rho_j).
        # Differentiating Phi and -eta B^T Phi yields these two scalar formulas.
        with localcontext(Context(prec=120)):
            cf, eta, km = (
                Decimal.from_float(1 / 373),
                Decimal.from_float(1e100),
                Decimal(".75"),
            )
            rho, drho = [], []
            for t in (-1, 3, 7):
                e = (2 * abs(t) / cf).exp()
                rho.append((e - 1) / (e + 1) * (-1 if t < 0 else 1))
                drho.append(4 * e / (e + 1) ** 2 / cf)
            a, b = (
                km
                / 2
                * (km * (rho[i] + rho[i + 1]) / 2).exp()
                * (drho[i] + drho[i + 1])
                for i in (0, 1)
            )
            expected = np.array(
                [float(eta * (2 * a - 7 * b)), float(eta * (-a + 14 * b))]
            )
        np.testing.assert_allclose(actual["j0"], expected, rtol=3e-12, atol=0)
        self.assertGreater(actual["j0"][0], 0)
        self.assertLess(actual["j0"][1], 0)

    def test_extreme_saturation_range_rejection_has_independent_log_witness(
        self,
    ) -> None:
        from decimal import Context, Decimal, ROUND_CEILING, ROUND_FLOOR, localcontext
        import warnings
        from pygrc.models.grc_v4_candidate_c import CandidateCCurrent

        tiny = math.ulp(0.0)
        inputs = self.saturation_fixture(tiny)
        before = canonical_json_bytes(inputs.to_payload())
        with warnings.catch_warnings(record=True) as messages:
            warnings.simplefilter("always")
            with self.assertRaisesRegex(ValueError, "Decimal operation/exponent range"):
                p943_direction(inputs, (1, 1), ((0,),))
        self.assertEqual(messages, [])
        self.assertTrue(
            math.isfinite(CandidateCCurrent(inputs).algebra.baseline.values[0])
        )
        self.assertEqual(canonical_json_bytes(inputs.to_payload()), before)
        self.assertEqual(p943_centered(inputs, (1, 1), ((0,),), 2**-12)["j0"][0], 0)
        # For this exact scalar equation, dJ0>0 and
        # 1.5 exp(-.75-2/cf)/cf <= dJ0 <= 6 exp(.75-2/cf)/cf.
        # Bound logs without attempting exp(-2/cf). ln is correctly rounded;
        # widen its endpoints and use directed arithmetic for the interval.
        with localcontext(Context(prec=110)) as ctx:
            cf = Decimal.from_float(tiny)
            ctx.rounding = ROUND_FLOOR
            x_lower = 1 / cf
            ctx.rounding = ROUND_CEILING
            x_upper = 1 / cf
            log_cf_lower, log_cf_upper = cf.ln().next_minus(), cf.ln().next_plus()
            ctx.rounding = ROUND_FLOOR
            lower = (
                -Decimal(2) * x_upper
                + Decimal("1.5").ln().next_minus()
                - Decimal(".75")
                - log_cf_upper
            )
            half_min_log_lower = -Decimal(1075) * Decimal(2).ln().next_plus()
            ctx.rounding = ROUND_CEILING
            upper = (
                -Decimal(2) * x_lower
                + Decimal(6).ln().next_plus()
                + Decimal(".75")
                - log_cf_lower
            )
            self.assertTrue(lower.is_finite() and upper.is_finite())
            self.assertLess(lower, upper)
            self.assertLess(upper, half_min_log_lower)
        self.observations.append(
            dict(
                case="minimum_positive_C_ref_log_witness",
                C_ref=tiny,
                mathematical_sign=1,
                mathematical_nonzero=True,
                log_abs_lower=str(lower),
                log_abs_upper=str(upper),
                final_binary64_hex=(0.0).hex(),
                rounding_reason="below_half_min_subnormal",
                generic_oracle="explicit_range_rejection",
                rounded_current_difference=0,
                finite_difference_claim=False,
            )
        )

    def test_decimal_context_and_final_binary64_range_are_explicit(self) -> None:
        from decimal import Inexact, ROUND_DOWN, localcontext
        import numpy as np
        from pygrc.models.grc_v4_candidate_c import CandidateCCurrent
        from pygrc.models.grc_v4_state import GRCV4AuthoritativeState

        inputs = self.saturation_fixture(1 / 373)
        expected = p943_direction(inputs, (1, 1), ((0,),))
        with localcontext() as ctx:
            ctx.prec, ctx.Emin, ctx.Emax, ctx.rounding = 6, -20, 20, ROUND_DOWN
            ctx.traps[Inexact] = True
            actual = p943_direction(inputs, (1, 1), ((0,),))
            for key in ("sector", "deformation", "hm", "phi", "j0"):
                np.testing.assert_array_equal(actual[key], expected[key])
            self.assertEqual(actual["representation"], expected["representation"])
            self.assertEqual(ctx.prec, 6)
            self.assertTrue(ctx.traps[Inexact])
        zero = p943_direction(inputs, (0, 0), ((0,),))
        self.assertEqual(zero["representation"], [])
        self.assertEqual(zero["j0"][0], 0)
        # At T=0 and the minimum C_ref the exponential fits, but delta_D does
        # not fit binary64. This is a different, explicitly rejected range.
        extreme = self.saturation_fixture(math.ulp(0.0))
        extreme = replace(extreme, current=GRCV4AuthoritativeState((0, 0), None, None))
        self.assertEqual(CandidateCCurrent(extreme).algebra.baseline.values, (0,))
        with self.assertRaisesRegex(ValueError, "final binary64 range"):
            p943_direction(extreme, (1, 1), ((0,),))


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

    def test_namespace_packages_keep_local_paths_and_child_source_checks(self) -> None:
        from importlib.machinery import ModuleSpec

        for mode in (
            "local", "foreign_spec_path", "foreign_module_path", "extra_path",
            "empty_path", "wrong_name", "unbound_child", "wrong_child_origin",
            "forged_child_hash", "regular_package_disguised_as_namespace",
        ):
            with self.subTest(mode=mode), self.fixture() as (root, _, hashes):
                folder = root / "tests/fixtures"
                folder.mkdir()
                child_path = folder / "probe.py"
                child_path.write_text("value = 7\n")
                namespace = ModuleType("tests.fixtures")
                namespace.__spec__ = ModuleSpec(namespace.__name__, None, is_package=True)
                namespace.__spec__.submodule_search_locations = [str(folder)]
                namespace.__path__ = [str(folder)]
                child = ModuleType("tests.fixtures.probe")
                child.__file__ = str(child_path)
                child.__spec__ = ModuleSpec(child.__name__, None, origin=str(child_path))
                exec(compile(child_path.read_bytes(), str(child_path), "exec"), child.__dict__)
                sys.modules[namespace.__name__] = namespace
                sys.modules[child.__name__] = child
                if mode == "foreign_spec_path":
                    namespace.__spec__.submodule_search_locations = [str(root.parent)]
                elif mode == "foreign_module_path":
                    namespace.__path__ = [str(root.parent)]
                elif mode == "extra_path":
                    namespace.__path__.append(str(root.parent))
                elif mode == "empty_path":
                    namespace.__path__ = []
                elif mode == "wrong_name":
                    namespace.__spec__.name = "tests.another"
                elif mode == "wrong_child_origin":
                    child.__spec__.origin = str(folder / "another.py")
                elif mode == "regular_package_disguised_as_namespace":
                    (folder / "__init__.py").write_text("")

                def snapshot() -> dict[str, str]:
                    extra = {} if mode == "unbound_child" else {
                        "tests/fixtures/probe.py": (
                            "0" * 64 if mode == "forged_child_hash"
                            else hashlib.sha256(child_path.read_bytes()).hexdigest()
                        )
                    }
                    return {**hashes(), **extra}

                result = self.execute(root, snapshot)
                self.assertEqual(result["status"], "passed" if mode == "local" else "failed", result)
                if mode == "local":
                    self.assertIn(child.__name__, result["loaded_sources_after"])
                else:
                    self.assertNotIn("results", result)

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


def _p941_loaded_sources(
    root: Path, hashes: dict[str, str], *, extra_modules: frozenset[str] = frozenset()
) -> dict[str, Any]:
    """Check origins and live source code; not hostile-interpreter attestation."""
    import inspect
    from types import CodeType

    leaf_modules = {
        "pygrc.models.grc_v4_candidate_c",
        "tests.models.test_grc_v4_candidate_c",
    } | extra_modules
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
        if file is None and spec is not None and spec.origin is None:
            # A namespace owns no executable file. Admit only its one actual,
            # source-bound local directory; inspect every loaded child normally.
            expected = root / stem
            locations = tuple(Path(p).resolve() for p in (spec.submodule_search_locations or ()))
            module_locations = tuple(Path(p).resolve() for p in getattr(module, "__path__", ()))
            if (
                canonical in leaf_modules
                or spec.name != canonical
                or locations != (expected,)
                or module_locations != (expected,)
                or not expected.is_dir()
                or (expected / "__init__.py").exists()
                or not any(p.startswith(stem + "/") for p in hashes)
            ):
                raise RuntimeError("loaded namespace path mismatch: " + name)
            continue
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
    *,
    extra_modules: frozenset[str] = frozenset(),
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
        record["loaded_sources_before"] = _p941_loaded_sources(
            root, before, extra_modules=extra_modules
        )
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
        record["loaded_sources_after"] = _p941_loaded_sources(
            root, before, extra_modules=extra_modules
        )
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


_P943_METHODS = (
    "test_exact_path_projector_and_geometry_derivative_oracle",
    "test_complete_resource_geometry_and_joint_derivatives",
    "test_joint_difference_converges_at_second_order",
    "test_every_hodge_product_and_resource_term_is_load_bearing",
    "test_directional_linearity_and_zero_direction",
    "test_zero_controls_are_separate_full_chains_on_nonreference_hodge",
    "test_derivatives_under_each_zero_control_remain_distinct",
    "test_reference_reduction_has_closed_resource_and_hodge_derivatives",
    "test_vertex_signed_edge_covariance_of_values_and_directions",
    "test_repeated_cluster_derivative_is_basis_independent_and_finite",
    "test_near_gap_growth_and_crossing_are_not_hidden",
    "test_disconnected_loop_parallel_and_exterior_sector_derivatives",
    "test_trial_current_and_metadata_do_not_become_baseline_directions",
    "test_eta_profile_family_variation_has_the_declared_delta_m_term",
    "test_resource_boundary_uses_admitted_one_sided_direction",
    "test_difference_probe_rejects_unresolvable_steps_and_domain_loss",
    "test_literal_scalar_derivative_and_saturation_tail",
    "test_constitutive_potential_is_not_total_retained_energy_gradient",
    "test_zero_context_and_potential_declarations_bound_derivative_scope",
    "test_seeded_spd_mixed_directions_match_actual_baseline",
)


_P943_AUDIT_METHODS = (
    "test_extreme_saturation_preserves_representable_subnormal",
    "test_subnormal_intermediates_are_not_rounded_before_mobility",
    "test_negative_selected_content_keeps_saturation_derivative_sign",
    "test_extreme_saturation_range_rejection_has_independent_log_witness",
    "test_decimal_context_and_final_binary64_range_are_explicit",
)


def _capture_candidate_c(output: str, *, scope: str) -> int:
    """One manifest; source is recovered from Git, without copying source blobs.

    The inherited pinned method roster and audited result collector detect
    omission, duplicates, skips and subtest failures. All source bytes are
    observed before/after, with only this leaf's listed overrides over its base.
    """
    from datetime import datetime, timezone
    import importlib.metadata
    import os
    import platform
    import subprocess
    from tests.models.test_grc_v4_step import p935_required

    if scope not in {"full", "focused", "current", "derivative", "derivative_audit"}:
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
        [
            "git",
            "rev-parse",
            "39cfe6a"
            if scope == "derivative_audit"
            else "ac3a7cf"
            if scope == "derivative"
            else "94a079d"
            if scope == "current"
            else "2e90398",
        ],
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

    if scope in {"derivative", "derivative_audit"}:
        overrides = {"tests/models/test_grc_v4_candidate_c.py"}

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

    iteration = (
        "P9-4.3"
        if scope in {"derivative", "derivative_audit"}
        else "P9-4.2"
        if scope == "current"
        else "P9-4.1"
    )
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
            "capture source differs from the reviewed " + iteration + " overrides"
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
    if scope in {"current", "derivative", "derivative_audit"}:
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
    if scope in {"current", "derivative", "derivative_audit"}:
        required |= {
            "tests.models.test_grc_v4_candidate_c.CandidateCCurrentTests." + name
            for name in _P942_METHODS
        }
    if scope in {"derivative", "derivative_audit"}:
        required |= {
            "tests.models.test_grc_v4_candidate_c.CandidateCControlDerivativeTests."
            + name
            for name in _P943_METHODS
        }
    if scope == "derivative_audit":
        required |= {
            "tests.models.test_grc_v4_candidate_c.CandidateCControlDerivativeTests."
            + name
            for name in _P943_AUDIT_METHODS
        }
    suite = (
        unittest.defaultTestLoader.discover(
            str(root / "tests"), top_level_dir=str(root)
        )
        if scope == "full"
        else unittest.defaultTestLoader.loadTestsFromNames(sorted(required))
    )
    if scope in {"derivative", "derivative_audit"}:
        from tests.models import test_grc_v4_candidate_c as leaf

        leaf.CandidateCControlDerivativeTests.observations = []
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
            "reconstruction": "Recover the listed override files from the Git commit containing this record (or a later commit with matching hashes), overlay on base_commit, and verify the manifest hash. No uncommitted source blob is preserved separately.",
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
            "--capture-p943-audit"
            if scope == "derivative_audit"
            else "--capture-p943"
            if scope == "derivative"
            else "--capture-p942"
            if scope == "current"
            else "--capture-p941"
            if scope == "full"
            else "--capture-p941-focused",
            "<fresh-repository-relative-generated-directory>",
        ],
        "claim_ceiling": (
            "Candidate C supported-profile smooth-stratum baseline derivative/covariance and independent zero controls; no production derivative API, complete beat, lifecycle, runtime conformance or cross-platform bitwise numerical claim."
            if scope in {"derivative", "derivative_audit"}
            else "Fixed-stage Candidate C selector, potential, baseline, typed read and regular current solve; no complete beat, lifecycle, profile conformance or cross-platform bitwise numerical claim."
            if scope == "current"
            else "Reference transport constructors only; no selector, baseline flux, solve, beat, lifecycle or runtime conformance."
        ),
    }
    if scope == "derivative_audit":
        record["audit_followup"] = {
            "subject_commit": base,
            "finding": "Test-only saturation oracle intermediate underflow and 0*infinity NaN; no production defect.",
            "oracle_policy": "NumPy spectral proposal; 90-digit Decimal nonlinear/product chain with explicit exponent traps; outputs rounded once, subnormal/rounded-zero coordinates labeled and excluded from ordinary finite-difference certification.",
            "range_limit": "Generic Decimal exponent/operation and final binary64 overflow reject. Minimum-positive C_ref uses a separate scalar sign/log bound, not a returned general derivative. Working precision is not a general cancellation or spectral error certificate.",
        }
    record["required_ids"] = sorted(required)
    record.update(_p941_execute(root, before, required, suite, source_hashes))
    passed = record["status"] == "passed"
    if scope in {"derivative", "derivative_audit"}:
        record["control_derivative_observations"] = (
            leaf.CandidateCControlDerivativeTests.observations
        )
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


def capture_p943(output: str) -> int:
    return _capture_candidate_c(output, scope="derivative")


def capture_p943_audit(output: str) -> int:
    return _capture_candidate_c(output, scope="derivative_audit")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--capture-p943-audit":
        raise SystemExit(capture_p943_audit(sys.argv[2]))
    if len(sys.argv) == 3 and sys.argv[1] == "--capture-p943":
        raise SystemExit(capture_p943(sys.argv[2]))
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

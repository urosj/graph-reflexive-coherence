"""Independent P9-3.1 candidate-factor ownership and covariance witnesses."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import json
from pathlib import Path
from typing import Any
import unittest

from pygrc.models.grc_v4_geometry import (
    GRCV4Graph,
    OneForm,
    OneFormHodge,
    PhysicalFlux,
    PhysicalFluxFlatMap,
)
from pygrc.models.grc_v4_profile import (
    CandidateAParams,
    CandidateCParams,
    list_supported_profiles,
)
from pygrc.models.grc_v4_transport import (
    CandidateAMobility,
    CandidateCMobility,
    candidate_c_structural_hodge,
)
from tests.models.test_grc_v4_geometry import (
    coordinate_action,
    graph_payload,
    independent_ascii_id,
)


def a_params(**updates: Any) -> CandidateAParams:
    return CandidateAParams.from_payload(
        {
            "schema_version": "grcv4-candidate-a-params-v1",
            "eta": 2,
            "kappa_c": 0,
            "site_potential_id": "test_site_v1",
            "W_floor": 0.5,
            "alpha": 1,
            "beta": 1,
            "gamma": 1,
            "kappa_Ah": 0,
            "chi_A": 1,
            "zeta_A": 1,
            "tau_A": 1,
            "descriptor_backend_id": "test_descriptor_v1",
            "conductance_evaluator_id": "curvature_disabled_G_W_v1",
            **updates,
        }
    )


def c_payload(weights: dict[str, Any] | None = None, **updates: Any) -> dict[str, Any]:
    # Reuse only the accepted declaration fixture; expected numerical results
    # and reference identities use the independent scalar/ASCII oracle.
    vectors = json.loads(
        (
            Path(__file__).resolve().parents[2]
            / "specs/grc-v4-conformance-vectors.json"
        ).read_text()
    )
    value: dict[str, Any] = vectors["identity_vectors"][0]["payload"]["candidate"]
    reference = {"a": 5, "z": 2} if weights is None else weights
    value.update(
        W_C_tr=reference,
        W_C_tr_content_digest=independent_ascii_id(
            "grcv4-wctr-sha256",
            {"schema_version": "grcv4-wctr-identity-v1", "W_C_tr": reference},
        ),
        eta_C=3,
    )
    value.update(updates)
    return value


class MobilityTests(unittest.TestCase):
    graph: GRCV4Graph
    a: CandidateAParams
    c: CandidateCParams

    @classmethod
    def setUpClass(cls) -> None:
        cls.graph = GRCV4Graph.from_payload(graph_payload())
        cls.a = a_params()
        cls.c = CandidateCParams.from_payload(c_payload())

    def test_a_reads_retained_authority_with_its_own_gain(self) -> None:
        mobility = CandidateAMobility(self.graph, self.a, (3, 7))
        self.assertEqual(mobility.diagonal, (6, 14))
        self.assertEqual(mobility.matrix, ((6, 0), (0, 14)))
        self.assertEqual(mobility.apply(OneForm(self.graph, (2, -3))).values, (12, -42))
        self.assertEqual(mobility.SOURCE, "candidate_A_retained_W_A")
        self.assertNotEqual(
            mobility.identity, CandidateAMobility(self.graph, self.a, (3, 8)).identity
        )

    def test_c_reads_reference_by_edge_id_in_live_order(self) -> None:
        # Profile map insertion order a,z differs from live edge order z,a.
        mobility = CandidateCMobility(self.graph, self.c)
        self.assertEqual(mobility.diagonal, (6, 15))
        self.assertEqual(mobility.apply(OneForm(self.graph, (2, -3))).values, (12, -45))
        self.assertEqual(mobility.SOURCE, "candidate_C_profile_W_C_tr")
        self.assertEqual(
            mobility.identity,
            CandidateCMobility(
                self.graph, CandidateCParams.from_payload(c_payload({"z": 2, "a": 5}))
            ).identity,
        )

    def test_c_structural_and_mobility_embeddings_are_siblings(self) -> None:
        hodge = candidate_c_structural_hodge(self.graph, self.c)
        mobility = CandidateCMobility(self.graph, self.c)
        self.assertEqual(hodge.matrix, ((2, 0), (0, 5)))
        self.assertEqual(mobility.matrix, ((6, 0), (0, 15)))
        self.assertEqual(
            PhysicalFluxFlatMap(hodge).flat(PhysicalFlux(self.graph, (4, 10))).values,
            (2, 2),
        )
        changed_gain = replace(self.c, eta_C=1)
        same_numbers = CandidateCMobility(self.graph, changed_gain)
        self.assertEqual(same_numbers.matrix, hodge.matrix)
        self.assertNotEqual(same_numbers, hodge)
        self.assertNotEqual(same_numbers.identity, hodge.identity)
        with self.assertRaises(TypeError):
            PhysicalFluxFlatMap(same_numbers)  # type: ignore[arg-type]

    def test_geometry_cannot_supply_mobility_authority(self) -> None:
        hodge = OneFormHodge(self.graph, ((3, 1), (1, 7)))
        for constructor, args in [
            (CandidateCMobility, (self.graph, hodge)),
            (CandidateAMobility, (self.graph, hodge, (3, 7))),
            (CandidateAMobility, (self.graph, self.a, hodge)),
        ]:
            with self.assertRaises(TypeError):
                constructor(*args)

    def test_candidate_authority_is_not_interchangeable(self) -> None:
        with self.assertRaises(TypeError):
            CandidateCMobility(self.graph, self.a)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            CandidateAMobility(self.graph, self.c, (2, 5))  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            candidate_c_structural_hodge(self.graph, self.a)  # type: ignore[arg-type]
        a = CandidateAMobility(self.graph, replace(self.a, eta=3), (2, 5))
        c = CandidateCMobility(self.graph, self.c)
        self.assertEqual(a.matrix, c.matrix)
        self.assertNotEqual(a.identity, c.identity)

    def test_c_reference_exact_coverage_and_positive_values(self) -> None:
        for weights in [{"z": 2}, {"a": 5, "z": 2, "extra": 1}]:
            params = CandidateCParams.from_payload(c_payload(weights))
            for constructor in [CandidateCMobility, candidate_c_structural_hodge]:
                with self.assertRaisesRegex(ValueError, "exactly"):
                    constructor(self.graph, params)
        for weights in [{"z": 0, "a": 5}, {"z": -1, "a": 5}]:
            with self.assertRaises(ValueError):
                CandidateCParams.from_payload(c_payload(weights))

    def test_a_retained_values_shape_and_positive_domain(self) -> None:
        for values in [(1,), (0, 1), (-1, 1), (float("inf"), 1), (True, 1), (2**53, 1)]:
            with (
                self.subTest(values=values),
                self.assertRaises((TypeError, ValueError)),
            ):
                CandidateAMobility(self.graph, self.a, values)

    def test_a_foundation_does_not_run_candidate_write_or_floor(self) -> None:
        # Positive retained authority is consumed verbatim, never clamped or
        # regenerated from a candidate conductance evaluator here.
        self.assertEqual(
            CandidateAMobility(self.graph, self.a, (0.25, 1)).diagonal, (0.5, 2)
        )

    def test_mobility_factors_reject_overflow_and_underflow(self) -> None:
        for gain, weights in [(1e308, (2, 1)), (1e-308, (1e-308, 1))]:
            with self.assertRaises(ValueError):
                CandidateAMobility(self.graph, replace(self.a, eta=gain), weights)
        with self.assertRaises(ValueError):
            CandidateCMobility(self.graph, replace(self.c, eta_C=1e308))
        with self.assertRaises(ValueError):
            CandidateAMobility(self.graph, self.a, (1e307, 1)).apply(
                OneForm(self.graph, (100, 1))
            )

    def test_c_ownership_excludes_selector_and_geometry_inputs(self) -> None:
        # Perturb the selector-only parameters; no T_C/h input can even enter
        # the C factor constructor. Complete stage derivative tests are later.
        baseline = CandidateCMobility(self.graph, self.c)
        mutations: list[dict[str, Any]] = [
            {"Lambda_C": 9},
            {"kappa_M_C": 7},
            {"kappa_Phi_C": 8},
        ]
        for updates in mutations:
            self.assertEqual(
                baseline.matrix,
                CandidateCMobility(self.graph, replace(self.c, **updates)).matrix,
            )

    def test_mutable_authority_inputs_are_detached(self) -> None:
        retained: Any = [3, 7]
        a = CandidateAMobility(self.graph, self.a, retained)
        payload = c_payload()
        c = CandidateCMobility(self.graph, CandidateCParams.from_payload(payload))
        identities = a.identity, c.identity
        retained[0] = 100
        payload["W_C_tr"]["z"] = 100
        self.assertEqual((a.identity, c.identity), identities)
        self.assertEqual(a.retained_W_A, (3, 7))
        with self.assertRaises(FrozenInstanceError):
            setattr(c, "diagonal", (100, 100))

    def test_wrong_typed_or_foreign_driving_form_rejected(self) -> None:
        mobility = CandidateCMobility(self.graph, self.c)
        with self.assertRaises(TypeError):
            mobility.apply(PhysicalFlux(self.graph, (2, 3)))  # type: ignore[arg-type]
        other = replace(self.graph, oriented_edges=self.graph.oriented_edges[::-1])
        with self.assertRaises(ValueError):
            mobility.apply(OneForm(other, (2, 3)))

    def test_signed_candidate_mobility_covariance(self) -> None:
        action = coordinate_action(self.graph)
        target_c = CandidateCParams.from_payload(c_payload({"new-a": 5, "new-z": 2}))
        source_form = OneForm(self.graph, (2, -3))
        for original, transformed in [
            (
                CandidateCMobility(self.graph, self.c),
                CandidateCMobility(action.target, target_c),
            ),
            (
                CandidateAMobility(self.graph, self.a, (3, 7)),
                CandidateAMobility(action.target, self.a, (7, 3)),
            ),
        ]:
            self.assertEqual(
                transformed.apply(action.one_form(source_form)),
                action.physical_flux(original.apply(source_form)),
            )
        self.assertEqual(
            candidate_c_structural_hodge(action.target, target_c),
            action.one_form_hodge(candidate_c_structural_hodge(self.graph, self.c)),
        )

    def test_reconstruction_preserves_candidate_identity_and_output(self) -> None:
        graph = GRCV4Graph.from_payload(json.loads(json.dumps(graph_payload())))
        c = CandidateCMobility(
            graph, CandidateCParams.from_payload(json.loads(json.dumps(c_payload())))
        )
        self.assertEqual(c.identity, CandidateCMobility(self.graph, self.c).identity)
        a = CandidateAMobility(
            graph, CandidateAParams.from_payload(self.a.to_payload()), (3, 7)
        )
        self.assertEqual(
            a.identity, CandidateAMobility(self.graph, self.a, (3, 7)).identity
        )
        self.assertEqual(a.apply(OneForm(graph, (2, -3))).values, (12, -42))
        self.assertEqual(c.apply(OneForm(graph, (2, -3))).values, (12, -45))

    def test_subnormal_positive_factors_and_arithmetic_underflow(self) -> None:
        smallest = float.fromhex("0x0.0000000000001p-1022")
        mobility = CandidateCMobility(self.graph, replace(self.c, eta_C=smallest))
        self.assertEqual(
            mobility.diagonal,
            (
                float.fromhex("0x0.0000000000002p-1022"),
                float.fromhex("0x0.0000000000005p-1022"),
            ),
        )
        output = mobility.apply(OneForm(self.graph, (smallest, -smallest)))
        self.assertEqual(output.values, (0.0, 0.0))
        import math

        self.assertEqual([math.copysign(1, v) for v in output.values], [1, 1])
        # IEEE-754 product underflow is explicit here. The strictly positive
        # mobility factor itself may never underflow to zero at construction.

    def test_extreme_finite_a_factor_keeps_retained_authority(self) -> None:
        retained = (2.0**400, 2.0**-400)
        mobility = CandidateAMobility(
            self.graph, replace(self.a, eta=2.0**500), retained
        )
        self.assertEqual(mobility.diagonal, (2.0**900, 2.0**100))
        self.assertEqual(
            mobility.apply(OneForm(self.graph, (-1, 2))).values, (-(2.0**900), 2.0**101)
        )
        self.assertEqual(mobility.retained_W_A, retained)

    def test_construction_does_not_advertise_runtime_support(self) -> None:
        CandidateCMobility(self.graph, self.c)
        self.assertEqual(list_supported_profiles(), frozenset())
        import pygrc.models as models

        self.assertFalse(hasattr(models, "GRCV4"))


if __name__ == "__main__":
    unittest.main()

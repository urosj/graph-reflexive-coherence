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
        self.assertEqual(list_supported_profiles(), frozenset({'grcv4-profile-sha256:a6b853ee382895eb78b1a7955a0df22f95d68b27cb0f762503e8c424c2f59b6d', 'grcv4-profile-sha256:e4c04a83240a33d77c50a26ca6effbb6ce142774bd01f0966861dd517a94e2c4', 'grcv4-profile-sha256:16ed65f7f65d4716e1be3e384f6fa0f957d26dd7b7a3f7e1b43ad1aa3f250946'}))
        import pygrc.models as models

        self.assertTrue(hasattr(models, "GRCV4"))


def charge_profile(**changes: float) -> Any:
    from tests.models.test_grc_v4_geometry import stage_reference_fixture

    return stage_reference_fixture(changes={"charge": changes}).profile


def padded_charge_oracle(values: tuple[float, ...]) -> float:
    """Exact rational internal nodes in an independently padded recursive tree."""
    from fractions import Fraction

    n = 1 << max(0, (len(values) - 1).bit_length())
    leaves = values + (0.0,) * (n - len(values))

    def reduce(left: int, right: int) -> float:
        if right - left == 1:
            return leaves[left]
        middle = (left + right) // 2
        return float(Fraction(reduce(left, middle)) + Fraction(reduce(middle, right)))

    return reduce(0, n)


class ChargeTests(unittest.TestCase):
    def test_literal_tree_ties_odd_lengths_and_empty_space(self) -> None:
        from pygrc.models.grc_v4_geometry import VertexScalar
        from pygrc.models.grc_v4_transport import unit_charge

        large = float(2**53)
        for values, expected in [
            ((), 0.0),
            ((5e-324,), 5e-324),
            ((large, 1.0, 1.0), large),
            ((large, 1.0, 1.0, 1.0), large + 2),
            ((1.0, 1.0, large), large + 2),
            ((0.5, 1.0, 1.5), 3.0),
        ]:
            with self.subTest(values=values):
                graph = GRCV4Graph(tuple(range(len(values))), ())
                self.assertEqual(unit_charge(VertexScalar(graph, values)), expected)

    def test_seeded_scale_trees_against_padded_rational_oracle(self) -> None:
        import math
        import random
        from pygrc.models.grc_v4_geometry import VertexScalar
        from pygrc.models.grc_v4_transport import unit_charge

        rng = random.Random(933)
        for case in range(160):
            values = tuple(
                math.ldexp(rng.choice((0.0, 1.0, 1.5)), rng.randint(-1074, 1022))
                for _ in range(case % 19)
            )
            graph = GRCV4Graph(tuple(range(len(values))), ())
            scalar = VertexScalar(graph, values)
            with self.subTest(case=case):
                try:
                    expected = padded_charge_oracle(values)
                except OverflowError:
                    with self.assertRaisesRegex(ValueError, "nonfinite"):
                        unit_charge(scalar)
                else:
                    self.assertEqual(unit_charge(scalar), expected)

    def test_charge_rejects_nonresource_roles_negative_and_overflow(self) -> None:
        from pygrc.models.grc_v4_geometry import VertexScalar
        from pygrc.models.grc_v4_transport import unit_charge

        graph = GRCV4Graph.from_payload(graph_payload())
        for other in (PhysicalFlux(graph, (1, 2)), OneForm(graph, (1, 2)), [1, 2, 3]):
            with self.assertRaises(TypeError):
                unit_charge(other)  # type: ignore[arg-type]
        for values in ((-5e-324, 1.0, 2.0), (1e308, 1e308, 0.0)):
            with self.assertRaises(ValueError):
                unit_charge(VertexScalar(graph, values))

    def test_tolerance_inclusive_edges_and_signed_receipt_values(self) -> None:
        import math
        from pygrc.models.grc_v4_geometry import VertexScalar
        from pygrc.models.grc_v4_transport import ChargeEvaluation

        graph = GRCV4Graph(("u",), ())
        profile = charge_profile(absolute_tolerance=0.25)
        for actual, admitted in [
            (1.25, True),
            (math.nextafter(1.25, math.inf), False),
            (0.75, True),
            (math.nextafter(0.75, 0), False),
        ]:
            with self.subTest(actual=actual):
                resource = VertexScalar(graph, (actual,))
                check = ChargeEvaluation(resource, 1.0, profile)
                self.assertEqual(check.admitted, admitted)
                self.assertEqual(check.residual, actual - 1.0)
                self.assertEqual(
                    check.receipt_values(),
                    {
                        "target_charge": 1.0,
                        "admitted_charge": actual,
                        "residual": actual - 1.0,
                    },
                )
                self.assertEqual(check.resource, resource)
                self.assertIsNone(check.remainder)

    def test_relative_scale_floor_and_exact_threshold_no_rounded_enlargement(
        self,
    ) -> None:
        import math
        from fractions import Fraction
        from pygrc.models.grc_v4_geometry import VertexScalar
        from pygrc.models.grc_v4_transport import ChargeEvaluation

        graph = GRCV4Graph(("u",), ())
        profile = charge_profile(relative_tolerance=0.25)
        self.assertTrue(
            ChargeEvaluation(VertexScalar(graph, (0.75,)), 0.5, profile).admitted
        )
        self.assertTrue(
            ChargeEvaluation(VertexScalar(graph, (5.0,)), 4.0, profile).admitted
        )
        relative = float.fromhex("0x1.5555555555555p-53")
        actual = math.nextafter(3.0, math.inf)
        self.assertEqual(relative * 3.0, actual - 3.0)
        self.assertLess(Fraction(relative) * 3, Fraction(actual) - 3)
        self.assertFalse(
            ChargeEvaluation(
                VertexScalar(graph, (actual,)),
                3.0,
                charge_profile(relative_tolerance=relative),
            ).admitted
        )
        self.assertTrue(
            ChargeEvaluation(
                VertexScalar(graph, (actual,)),
                3.0,
                charge_profile(relative_tolerance=math.nextafter(relative, math.inf)),
            ).admitted
        )

    def test_extreme_tolerance_and_unrepresentable_residual_are_distinct(self) -> None:
        from pygrc.models.grc_v4_geometry import VertexScalar
        from pygrc.models.grc_v4_transport import ChargeEvaluation

        graph = GRCV4Graph(("u",), ())
        huge = charge_profile(relative_tolerance=1e308)
        check = ChargeEvaluation(VertexScalar(graph, (0.0,)), 1e308, huge)
        self.assertTrue(check.admitted)
        self.assertEqual(check.residual, -1e308)
        with self.assertRaisesRegex(ValueError, "nonfinite"):
            ChargeEvaluation(VertexScalar(graph, (1e308,)), -1e308, huge)
        # Frozen target schema is finite, not nonnegative; apply its inequality.
        check = ChargeEvaluation(
            VertexScalar(graph, (0.0,)), -0.25, charge_profile(absolute_tolerance=0.25)
        )
        self.assertTrue(check.admitted)
        self.assertEqual(check.residual, 0.25)

    def test_policy_and_measure_declarations_cannot_be_rehashed_aliases(self) -> None:
        from tests.models.test_grc_v4_profile import reidentify
        from pygrc.models.grc_v4_profile import resolve_profile
        from pygrc.models.grc_v4_geometry import VertexScalar
        from pygrc.models.grc_v4_transport import ChargeEvaluation

        graph = GRCV4Graph(("u",), ())
        base = charge_profile().to_payload()
        for field in ("charge_profile_id", "measure_profile_id"):
            params = json.loads(json.dumps(base["params_resolved"]))
            identity = json.loads(json.dumps(base["identity_payload"]))
            (identity if field == "charge_profile_id" else params["common"])[field] = (
                "unimplemented_v1"
            )
            reidentify(params, identity)
            with self.assertRaisesRegex(ValueError, "charge/measure"):
                ChargeEvaluation(
                    VertexScalar(graph, (1.0,)), 1.0, resolve_profile(params, identity)
                )
        for target in (True, float("nan"), float("inf"), -0.0):
            with self.assertRaises((TypeError, ValueError)):
                ChargeEvaluation(VertexScalar(graph, (1.0,)), target, charge_profile())

    def test_charge_has_no_geometry_or_candidate_resource_ledger(self) -> None:
        from tests.models.test_grc_v4_geometry import stage_reference_fixture
        from pygrc.models.grc_v4_geometry import VertexScalar
        from pygrc.models.grc_v4_transport import ChargeEvaluation

        for candidate in ("A", "C"):
            for gain in (0.0, 0.5, 1e308):
                ref = stage_reference_fixture(candidate, gain=gain)
                check = ChargeEvaluation(
                    VertexScalar(ref.graph, (1, 2, 3)), 6.0, ref.profile
                )
                self.assertEqual(check.actual, 6.0)
                self.assertTrue(check.admitted)


class ContinuityTests(unittest.TestCase):
    def test_repeated_primitive_transfers_can_hide_exact_stored_sum_growth(
        self,
    ) -> None:
        from fractions import Fraction
        from pygrc.models.grc_v4_geometry import OrientedEdge, VertexScalar
        from pygrc.models.grc_v4_transport import (
            ChargeEvaluation,
            provisional_continuity,
        )
        from tests.models.test_grc_v4_geometry import stage_reference_fixture

        graph = GRCV4Graph(("rich", "small"), (OrientedEdge("e", "rich", "small"),))
        ref = stage_reference_fixture(
            graph=graph,
            changes={"charge": {"absolute_tolerance": 0.0, "relative_tolerance": 0.0}},
        )
        current = PhysicalFlux(graph, (1.0,))
        original = VertexScalar(graph, (1e20, 0.0))
        value = original
        # These are primitive compositions, not full beats: no current solve,
        # histories, clock, final readmission or commit is executed here.
        for count in range(1, 101):
            value = provisional_continuity(
                value, current, 1.0, differential=ref.differential
            )
            self.assertEqual(value.values, (1e20, float(count)))
            self.assertEqual(
                sum(map(Fraction, value.values)) - sum(map(Fraction, original.values)),
                Fraction(count),
            )
        check = ChargeEvaluation(value, 1e20, ref.profile)
        self.assertTrue(check.admitted)
        self.assertEqual(check.residual, 0.0)
        self.assertIsNone(check.remainder)

    def test_charge_alone_cannot_detect_wrong_sign_or_duplicate_update(self) -> None:
        from pygrc.models.grc_v4_geometry import VertexScalar
        from pygrc.models.grc_v4_transport import provisional_continuity, unit_charge
        from tests.models.test_grc_v4_geometry import stage_reference_fixture

        ref = stage_reference_fixture()
        original = VertexScalar(ref.graph, (8.0, 6.0, 4.0))
        forward = provisional_continuity(
            original,
            PhysicalFlux(ref.graph, (1.0, 0.5)),
            0.25,
            differential=ref.differential,
        )
        reverse = provisional_continuity(
            original,
            PhysicalFlux(ref.graph, (-1.0, -0.5)),
            0.25,
            differential=ref.differential,
        )
        twice = provisional_continuity(
            forward,
            PhysicalFlux(ref.graph, (1.0, 0.5)),
            0.25,
            differential=ref.differential,
        )
        # Literal per-vertex expectations distinguish three equal-charge flows.
        self.assertEqual(forward.values, (7.75, 6.125, 4.125))
        self.assertEqual(reverse.values, (8.25, 5.875, 3.875))
        self.assertEqual(twice.values, (7.5, 6.25, 4.25))
        self.assertEqual(
            tuple(unit_charge(x) for x in (forward, reverse, twice)), (18.0,) * 3
        )

    def test_seeded_multigraphs_against_independent_exact_edge_scatter(self) -> None:
        from fractions import Fraction
        import random
        from pygrc.models.grc_v4_geometry import (
            GRCV4Differential,
            OrientedEdge,
            VertexScalar,
        )
        from pygrc.models.grc_v4_transport import provisional_continuity, unit_charge
        from tests.models.test_grc_v4_geometry import stage_reference_fixture

        common = stage_reference_fixture().profile.params_resolved.common
        randomizer = random.Random(933)
        for case in range(100):
            count = randomizer.randint(1, 8)
            vertices = tuple(f"v-{i}" for i in range(count))
            edges = tuple(
                OrientedEdge(
                    f"e-{i}", randomizer.choice(vertices), randomizer.choice(vertices)
                )
                for i in range(randomizer.randint(0, 14))
            )
            graph = GRCV4Graph(vertices, edges)
            current = tuple(float(randomizer.randint(-8, 8)) for _ in edges)
            resource = tuple(float(randomizer.randint(40, 80)) for _ in vertices)
            dt = Fraction(randomizer.choice((0, 1, 2, 3)), 8)
            expected: dict[str | int, Fraction] = {
                v: Fraction(c) for v, c in zip(vertices, resource, strict=True)
            }
            for edge, flux in zip(edges, current, strict=True):
                expected[edge.tail_node_id] -= dt * Fraction(flux)
                expected[edge.head_node_id] += dt * Fraction(flux)
            result = provisional_continuity(
                VertexScalar(graph, resource),
                PhysicalFlux(graph, current),
                float(dt),
                differential=GRCV4Differential(graph, common),
            )
            with self.subTest(case=case):
                self.assertEqual(
                    result.values, tuple(float(expected[v]) for v in vertices)
                )
                self.assertEqual(unit_charge(result), sum(resource))

    def test_continuity_all_48_exact_signed_coordinate_actions(self) -> None:
        import itertools
        from pygrc.models.grc_v4_geometry import (
            GRCV4Differential,
            GraphCoordinateAction,
            OrientedEdge,
            VertexScalar,
        )
        from pygrc.models.grc_v4_transport import provisional_continuity, unit_charge
        from tests.models.test_grc_v4_geometry import stage_reference_fixture

        ref = stage_reference_fixture()
        graph = ref.graph
        resource = VertexScalar(graph, (4.0, 5.0, 6.0))
        current = PhysicalFlux(graph, (3.0, -2.0))
        baseline = provisional_continuity(
            resource, current, 0.25, differential=ref.differential
        )
        ids = ("renamed", "", 2**53 - 1)
        for p in itertools.permutations(range(3)):
            mapping = {old: ids[new] for new, old in enumerate(p)}
            for u in itertools.permutations(range(2)):
                for signs in itertools.product((-1, 1), repeat=2):
                    edges = []
                    for i, old in enumerate(u):
                        edge = graph.oriented_edges[old]
                        tail, head = (
                            graph.node_index(edge.tail_node_id),
                            graph.node_index(edge.head_node_id),
                        )
                        if signs[i] < 0:
                            tail, head = head, tail
                        edges.append(
                            OrientedEdge(f"new-{i}", mapping[tail], mapping[head])
                        )
                    target = GRCV4Graph(ids, tuple(edges))
                    action = GraphCoordinateAction(graph, target, p, u, signs)
                    result = provisional_continuity(
                        action.vertex_scalar(resource),
                        action.physical_flux(current),
                        0.25,
                        differential=GRCV4Differential(
                            target, ref.profile.params_resolved.common
                        ),
                    )
                    self.assertEqual(result, action.vertex_scalar(baseline))
                    self.assertEqual(unit_charge(result), 15.0)

    def test_literal_mixed_graph_and_single_simultaneous_update(self) -> None:
        from tests.models.test_grc_v4_geometry import stage_reference_fixture
        from pygrc.models.grc_v4_geometry import OrientedEdge, VertexScalar
        from pygrc.models.grc_v4_transport import provisional_continuity

        graph = GRCV4Graph(
            ("u", "v", "isolated"),
            (
                OrientedEdge("p", "u", "v"),
                OrientedEdge("q", "v", "u"),
                OrientedEdge("loop", "u", "u"),
            ),
        )
        ref = stage_reference_fixture(graph=graph)
        resource = VertexScalar(graph, (4, 5, 6))
        flux = PhysicalFlux(graph, (3, -1, 1e308))
        actual = provisional_continuity(
            resource, flux, 0.5, differential=ref.differential
        )
        self.assertEqual(actual.values, (2.0, 7.0, 6.0))
        self.assertEqual(resource.values, (4, 5, 6))
        self.assertEqual(flux.values, (3, -1, 1e308))

    def test_negative_candidate_is_not_repaired_by_continuity(self) -> None:
        from tests.models.test_grc_v4_geometry import stage_reference_fixture
        from pygrc.models.grc_v4_geometry import VertexScalar
        from pygrc.models.grc_v4_transport import provisional_continuity

        ref = stage_reference_fixture()
        result = provisional_continuity(
            VertexScalar(ref.graph, (0, 2, 3)),
            PhysicalFlux(ref.graph, (1, 0)),
            1.0,
            differential=ref.differential,
        )
        self.assertEqual(result.values, (-1.0, 3.0, 3.0))

    def test_zero_underflow_overflow_duration_and_operand_roles(self) -> None:
        from tests.models.test_grc_v4_geometry import stage_reference_fixture
        from pygrc.models.grc_v4_geometry import VertexScalar
        from pygrc.models.grc_v4_transport import provisional_continuity

        ref = stage_reference_fixture()
        resource = VertexScalar(ref.graph, (1, 2, 3))
        flux = PhysicalFlux(ref.graph, (0.5, 0))
        for dt in (0.0, 5e-324):
            self.assertEqual(
                provisional_continuity(
                    resource, flux, dt, differential=ref.differential
                ),
                resource,
            )
        for dt in (-1.0, -0.0, float("inf"), True):
            with self.assertRaises((TypeError, ValueError)):
                provisional_continuity(
                    resource, flux, dt, differential=ref.differential
                )
        with self.assertRaisesRegex(ValueError, "nonfinite"):
            provisional_continuity(
                resource,
                PhysicalFlux(ref.graph, (2, 0)),
                1e308,
                differential=ref.differential,
            )
        with self.assertRaises(TypeError):
            provisional_continuity(
                resource,
                OneForm(ref.graph, (1, 0)),  # type: ignore[arg-type]
                1.0,
                differential=ref.differential,
            )
        foreign = replace(ref.graph, live_node_ids=ref.graph.live_node_ids[::-1])
        with self.assertRaises(ValueError):
            provisional_continuity(
                resource,
                PhysicalFlux(foreign, (1, 0)),
                1.0,
                differential=ref.differential,
            )


class ChargePrecisionEnvelopeTests(unittest.TestCase):
    """Independent stored-coordinate diagnostics; no replacement charge rule."""

    observations: list[dict[str, Any]] = []

    def test_half_ulp_and_subnormal_transfer_grid(self) -> None:
        from fractions import Fraction
        import math
        from pygrc.models.grc_v4_geometry import (
            GRCV4Differential,
            OrientedEdge,
            VertexScalar,
        )
        from pygrc.models.grc_v4_transport import (
            ChargeEvaluation,
            provisional_continuity,
            unit_charge,
        )
        from tests.models.test_grc_v4_geometry import common_payload
        from pygrc.models.grc_v4_profile import GRCV4CommonParams

        graph = GRCV4Graph(("rich", "small"), (OrientedEdge("e", "rich", "small"),))
        differential = GRCV4Differential(
            graph, GRCV4CommonParams.from_payload(common_payload())
        )
        profile = charge_profile(absolute_tolerance=0.0, relative_tolerance=0.0)
        cases = 0
        for magnitude in (5e-324, 2.0**-1022, 1.0, float(2**53), 1e20, 1e150):
            ulp = math.ulp(magnitude)
            for rate, dt in (
                (0.5, 5e-324),
                (1.0, 5e-324),
                (1.0, 0.25 * ulp),
                (1.0, 0.5 * ulp),
                (1.0, ulp),
                (1.0, 0.5),
                (1.0, 1.0),
            ):
                initial = VertexScalar(graph, (magnitude, 0.0))
                result = provisional_continuity(
                    initial, PhysicalFlux(graph, (rate,)), dt, differential=differential
                )
                rounded_transfer = float(Fraction(rate) * Fraction(dt))
                oracle = (
                    float(Fraction(magnitude) - Fraction(rounded_transfer)),
                    rounded_transfer,
                )
                self.assertEqual(result.values, oracle)
                drift = sum(map(Fraction, result.values)) - Fraction(magnitude)
                if min(result.values) < 0:
                    with self.assertRaises(ValueError):
                        unit_charge(result)
                    admitted = False
                else:
                    gate = ChargeEvaluation(result, magnitude, profile)
                    self.assertEqual(gate.actual, padded_charge_oracle(oracle))
                    self.assertEqual(gate.admitted, gate.actual == magnitude)
                    self.assertIsNone(gate.remainder)
                    admitted = gate.admitted
                self.observations.append(
                    dict(
                        case="transfer_precision",
                        magnitude=magnitude,
                        rate=rate,
                        dt=dt,
                        result=list(result.values),
                        exact_stored_drift=str(drift),
                        admitted=admitted,
                    )
                )
                cases += 1
        self.assertEqual(cases, 42)

    def test_repeated_primitive_compositions_have_exact_diagnostic_drift(self) -> None:
        from fractions import Fraction
        from pygrc.models.grc_v4_geometry import (
            GRCV4Differential,
            OrientedEdge,
            VertexScalar,
        )
        from pygrc.models.grc_v4_transport import (
            ChargeEvaluation,
            provisional_continuity,
        )
        from pygrc.models.grc_v4_profile import GRCV4CommonParams
        from tests.models.test_grc_v4_geometry import common_payload

        graph = GRCV4Graph(("a", "b"), (OrientedEdge("e", "a", "b"),))
        differential = GRCV4Differential(
            graph, GRCV4CommonParams.from_payload(common_payload())
        )
        profile = charge_profile(absolute_tolerance=0.0, relative_tolerance=0.0)
        resource = VertexScalar(graph, (1e20, 0.0))
        for k in range(1, 101):
            resource = provisional_continuity(
                resource, PhysicalFlux(graph, (1.0,)), 1.0, differential=differential
            )
            gate = ChargeEvaluation(resource, 1e20, profile)
            self.assertTrue(gate.admitted)
            self.assertEqual(gate.residual, 0)
            self.assertEqual(resource.values, (1e20, float(k)))
            self.assertEqual(sum(map(Fraction, resource.values)) - Fraction(1e20), k)
        self.observations.append(
            dict(
                case="primitive_compositions",
                compositions=100,
                exact_stored_drift="100",
                rounded_charge_residual=0.0,
                complete_beats=False,
            )
        )

    def test_exact_conservative_transfer_all_vertex_orders(self) -> None:
        from fractions import Fraction
        import itertools
        from pygrc.models.grc_v4_geometry import (
            GRCV4Differential,
            OrientedEdge,
            VertexScalar,
        )
        from pygrc.models.grc_v4_transport import (
            ChargeEvaluation,
            provisional_continuity,
            unit_charge,
        )
        from pygrc.models.grc_v4_profile import GRCV4CommonParams
        from tests.models.test_grc_v4_geometry import common_payload

        profile = charge_profile(absolute_tolerance=0.0, relative_tolerance=0.0)
        residuals: set[float] = set()
        for order in itertools.permutations(("a", "b", "c", "d")):
            for sign in (-1, 1):
                graph = GRCV4Graph(
                    order,
                    (
                        OrientedEdge(
                            "e", "a" if sign == 1 else "d", "d" if sign == 1 else "a"
                        ),
                    ),
                )
                differential = GRCV4Differential(
                    graph, GRCV4CommonParams.from_payload(common_payload())
                )
                values = {"a": float(2**53), "b": 1.0, "c": 1.0, "d": 1.0}
                initial = VertexScalar(graph, tuple(values[x] for x in order))
                result = provisional_continuity(
                    initial,
                    PhysicalFlux(graph, (float(sign),)),
                    1.0,
                    differential=differential,
                )
                self.assertEqual(
                    sum(map(Fraction, result.values)),
                    sum(map(Fraction, initial.values)),
                )
                gate = ChargeEvaluation(result, unit_charge(initial), profile)
                expected = padded_charge_oracle(result.values) - padded_charge_oracle(
                    initial.values
                )
                self.assertEqual(gate.residual, expected)
                self.assertEqual(gate.admitted, expected == 0)
                residuals.add(expected)
        self.assertIn(2.0, residuals)
        self.assertIn(0.0, residuals)
        self.observations.append(
            dict(
                case="conservative_coordinate_permutations",
                cases=48,
                residuals=sorted(residuals),
                exact_stored_drift="0",
            )
        )

    def test_high_degree_cancellation_and_safe_order_controls(self) -> None:
        from fractions import Fraction
        from pygrc.models.grc_v4_geometry import GRCV4Differential, OrientedEdge
        from pygrc.models.grc_v4_profile import GRCV4CommonParams
        from tests.models.test_grc_v4_geometry import common_payload, pressure_action

        for degree in (4, 16, 64, 256):
            graph = GRCV4Graph(
                ("a", "b", "isolated"),
                tuple(OrientedEdge(str(i), "a", "b") for i in range(degree)),
            )
            differential = GRCV4Differential(
                graph, GRCV4CommonParams.from_payload(common_payload())
            )
            for magnitude in (1.0, 1e100, 1e308):
                grouped = (magnitude,) * (degree // 2) + (-magnitude,) * (degree // 2)
                alternating = (magnitude, -magnitude) * (degree // 2)
                for label, values in (
                    ("grouped", grouped),
                    ("alternating", alternating),
                ):
                    self.assertEqual(sum(map(Fraction, values)), 0)
                    flux = PhysicalFlux(graph, values)
                    overflows = magnitude == 1e308 and label == "grouped"
                    if overflows:
                        with self.assertRaisesRegex(ValueError, "nonfinite"):
                            differential.divergence(flux)
                    else:
                        result = differential.divergence(flux)
                        self.assertEqual(result.values, (0, 0, 0))
                        action = pressure_action(
                            graph,
                            tuple(reversed(range(degree))),
                            tuple((-1) ** i for i in range(degree)),
                        )
                        moved = GRCV4Differential(
                            action.target, differential.common
                        ).divergence(action.physical_flux(flux))
                        self.assertEqual(moved, action.vertex_scalar(result))
                    self.observations.append(
                        dict(
                            case="high_degree_divergence",
                            degree=degree,
                            magnitude=magnitude,
                            order=label,
                            rejected_nonfinite=overflows,
                            exact_divergence="0",
                        )
                    )

    def test_normwise_accuracy_does_not_promise_cancellation_relative_accuracy(
        self,
    ) -> None:
        from fractions import Fraction
        import random
        from pygrc.models.grc_v4_geometry import GRCV4Differential, OrientedEdge
        from pygrc.models.grc_v4_profile import GRCV4CommonParams
        from tests.models.test_grc_v4_geometry import common_payload

        rng = random.Random(93402)
        for degree in (3, 17, 65, 257):
            graph = GRCV4Graph(
                ("a", "b"), tuple(OrientedEdge(str(i), "a", "b") for i in range(degree))
            )
            differential = GRCV4Differential(
                graph, GRCV4CommonParams.from_payload(common_payload())
            )
            for scale in (2.0**-400, 1.0, 2.0**400):
                values = [rng.uniform(-1, 1) * scale for _ in range(degree // 2)]
                values += [-x for x in values]
                values.append(scale * 2.0**-52)
                rng.shuffle(values)
                exact = sum(map(Fraction, values))
                actual = differential.divergence(
                    PhysicalFlux(graph, tuple(values))
                ).values[0]
                bound = Fraction(4 * degree, 2**53) * sum(
                    abs(Fraction(x)) for x in values
                )
                error = abs(Fraction(actual) - exact)
                self.assertLessEqual(error, bound)
                self.observations.append(
                    dict(
                        case="cancellation_accuracy",
                        degree=degree,
                        scale=scale,
                        exact_sum=str(exact),
                        absolute_error=float(error),
                        normwise_bound=float(bound),
                    )
                )


if __name__ == "__main__":
    unittest.main()

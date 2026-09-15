"""P9-5.1: independent scalar/Decimal initialization and authority pressure."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import FrozenInstanceError, replace
from decimal import Decimal, DefaultContext, ROUND_UP, getcontext, localcontext
from fractions import Fraction
import json
import math
import random
import unittest
from unittest.mock import patch

from pygrc.models.grc_v4_candidate_a import (
    BACKEND,
    HISTORY_POLICY,
    A_SITE_POTENTIAL,
    CandidateACurrent,
    CandidateADifferentialReference,
    CandidateAInitialization,
    CandidateAInitializationStage,
    CandidateARetainedAuthority,
    CandidateAStageError,
    CandidateAWriter,
    candidate_a_log_interpolation,
)
from pygrc.models.grc_v4_codec import canonical_json_bytes
from pygrc.models.grc_v4_geometry import (
    GRCV4Graph,
    GRCV4Geometry,
    GeometryStageInputs,
    H_profile,
    OneForm,
    OneFormHodge,
    OrientedEdge,
    PhysicalFlux,
    VertexScalar,
)
from pygrc.models.grc_v4_profile import (
    get_supported_profile,
    list_supported_profiles,
    resolve_profile,
)
from pygrc.models.grc_v4_state import FrozenJSONMap, GRCV4AuthoritativeState
from pygrc.models.grc_v4_step import (
    CurrentSelection,
    ProvisionalResourceStep,
    ResourceBoundaryError,
)
from tests.models.test_grc_v4_geometry import stage_reference_fixture
from tests.models.test_grc_v4_profile import reidentify


def fixture(
    *,
    graph=None,
    positions=None,
    weights=None,
    ridge=1.0,
    dimension=1,
    realization="OS",
    **candidate,
):
    graph = (
        graph
        if graph is not None
        else GRCV4Graph(("u", "v"), (OrientedEdge("e", "u", "v"),))
    )
    positions = (
        positions
        if positions is not None
        else tuple((float(i),) for i in range(len(graph.live_node_ids)))
    )
    weights = weights if weights is not None else {e: 1.0 for e in graph.live_edge_ids}
    backend = CandidateADifferentialReference(
        graph, dimension, positions, weights, ridge
    )
    reference = stage_reference_fixture(
        "A",
        realization,
        graph=graph,
        weights=weights,
        changes={
            "candidate": {
                "descriptor_backend_id": backend.identity,
                "W_floor": 1e-12,
                **candidate,
            },
            "lifecycle": {"history_policy_id": HISTORY_POLICY},
        },
    )
    return reference, backend


def stage(reference, backend, C=(1.0, 3.0), J=(0.0,)):
    return CandidateAInitializationStage(
        reference,
        backend,
        VertexScalar(reference.graph, C),
        PhysicalFlux(reference.graph, J),
    )


def scalar_oracle(reference, backend, C, J):
    """One-dimensional WLS as independent Decimal scalar normal equations.

    No runtime differential, conductance, mobility or solve helper is called.
    Round each declared gradient once; evaluate the physical law at 100 digits.
    This exact-exponent oracle is used only in the modest cases below; their
    tolerances are not a global bound for the runtime's rounded-exponent exp.
    """
    with localcontext() as ctx:
        ctx.prec = 100
        D = Decimal.from_float
        gradients = []
        graph = reference.graph
        for i, node in enumerate(graph.live_node_ids):
            numerator, denominator = Decimal(0), D(float(backend.regularization))
            for edge in graph.oriented_edges:
                if node not in (edge.tail_node_id, edge.head_node_id):
                    continue
                other = (
                    edge.head_node_id
                    if node == edge.tail_node_id
                    else edge.tail_node_id
                )
                j = graph.node_index(other)
                dx = D(float(backend.positions[j][0])) - D(
                    float(backend.positions[i][0])
                )
                weight = D(float(backend.reference_weights[edge.edge_id]))
                numerator += weight * dx * (D(float(C[j])) - D(float(C[i])))
                denominator += weight * dx * dx
            gradients.append(float(numerator / denominator))
        params = reference.profile.params_resolved.candidate
        result = []
        for edge, flux in zip(graph.oriented_edges, J, strict=True):
            u, v = (
                graph.node_index(edge.tail_node_id),
                graph.node_index(edge.head_node_id),
            )
            exponent = (
                -(
                    D(float(params.alpha)) * (D(float(C[u])) + D(float(C[v])))
                    + D(float(params.beta)) * (D(gradients[u]) - D(gradients[v])) ** 2
                    + D(float(params.gamma)) * D(float(flux)) ** 2
                )
                / 2
            )
            result.append(float(max(D(float(params.W_floor)), exponent.exp())))
        return tuple((x,) for x in gradients), tuple(result)


class CandidateAInitializationTests(unittest.TestCase):
    def test_exact_gradient_and_separate_positive_mobility_authority(self) -> None:
        ref, backend = fixture(eta=2.0, alpha=0.0, beta=1.0, gamma=0.0)
        result = stage(ref, backend)
        self.assertEqual(result.descriptors, ((1.0,), (1.0,)))
        self.assertEqual(result.authority.state.W_A, (1.0,))
        self.assertEqual(result.authority.mobility.diagonal, (2.0,))
        self.assertEqual(
            result.authority.mobility.apply(OneForm(ref.graph, (3.0,))).values, (6.0,)
        )
        self.assertEqual(result.authority.mobility.SOURCE, "candidate_A_retained_W_A")

    def test_nontrivial_all_channels_against_decimal(self) -> None:
        graph = GRCV4Graph(
            ("a", "b", "c"),
            (OrientedEdge("ab", "a", "b"), OrientedEdge("bc", "b", "c")),
        )
        ref, backend = fixture(graph=graph, alpha=0.25, beta=0.5, gamma=0.75)
        result = stage(ref, backend, (1.0, 3.0, 2.0), (0.5, -1.0))
        gradients, expected = scalar_oracle(
            ref, backend, result.C.values, result.reference_current.values
        )
        self.assertEqual(result.descriptors, gradients)
        for actual, oracle in zip(result.authority.state.W_A, expected, strict=True):
            self.assertAlmostEqual(actual, oracle, delta=4 * math.ulp(oracle))

    def test_two_dimensional_cross_terms_have_independent_closed_form(self) -> None:
        graph = GRCV4Graph(
            (0, 1, 2), (OrientedEdge("a", 0, 1), OrientedEdge("b", 0, 2))
        )
        ref, backend = fixture(
            graph=graph, dimension=2, positions=((0.0, 0.0), (1.0, 0.0), (1.0, 1.0))
        )
        result = stage(ref, backend, (1.0, 3.0, 4.0), (0.0, 0.0))
        # At node 0: M=[[3,1],[1,2]], rhs=[5,3], det=5.
        self.assertEqual(result.descriptors[0], (7 / 5, 4 / 5))
        self.assertEqual(result.descriptors[1], (1.0, 0.0))
        self.assertEqual(result.descriptors[2], (1.0, 1.0))

    def test_random_one_dimensional_paths_and_signed_coefficients(self) -> None:
        rng = random.Random(951)
        for _ in range(40):
            n = rng.randrange(2, 7)
            graph = GRCV4Graph(
                tuple(range(n)),
                tuple(OrientedEdge(str(i), i, i + 1) for i in range(n - 1)),
            )
            ref, backend = fixture(
                graph=graph,
                positions=tuple((rng.randrange(-8, 9) / 4,) for _ in range(n)),
                weights={e: rng.randrange(1, 9) / 4 for e in graph.live_edge_ids},
                ridge=rng.randrange(1, 5) / 4,
                alpha=rng.randrange(-2, 3) / 4,
                beta=rng.randrange(-2, 3) / 4,
                gamma=rng.randrange(-2, 3) / 4,
            )
            C = tuple(rng.randrange(0, 9) / 4 for _ in range(n))
            J = tuple(rng.randrange(-8, 9) / 4 for _ in range(n - 1))
            result = stage(ref, backend, C, J)
            gradients, expected = scalar_oracle(ref, backend, C, J)
            self.assertEqual(result.descriptors, gradients)
            for actual, oracle in zip(
                result.authority.state.W_A, expected, strict=True
            ):
                self.assertTrue(math.isclose(actual, oracle, rel_tol=3e-15, abs_tol=0))

    def test_current_and_reset_rebuild_separately(self) -> None:
        ref, backend = fixture(alpha=1.0, beta=0.0, gamma=1.0)
        result = CandidateAInitialization.construct(
            ref,
            backend,
            current_C=VertexScalar(ref.graph, (1.0, 3.0)),
            current_reference_current=PhysicalFlux(ref.graph, (0.0,)),
            reset_C=VertexScalar(ref.graph, (2.0, 6.0)),
            reset_reference_current=PhysicalFlux(ref.graph, (1.0,)),
        )
        self.assertEqual(result.current.authority.state.C, (1.0, 3.0))
        self.assertEqual(result.reset.authority.state.C, (2.0, 6.0))
        self.assertEqual(result.current.authority.state.W_A, (math.exp(-2),))
        self.assertEqual(result.reset.authority.state.W_A, (math.exp(-4.5),))
        self.assertEqual(result.reset.descriptors, ((2.0,), (2.0,)))
        self.assertNotEqual(result.current.identity, result.reset.identity)

    def test_reset_only_failure_does_not_change_current_or_reference(self) -> None:
        ref, backend = fixture(alpha=-1.0, beta=0.0, gamma=0.0)
        current = stage(ref, backend)
        before = canonical_json_bytes(current.to_payload())
        with self.assertRaisesRegex(ValueError, "overflows"):
            CandidateAInitialization.construct(
                ref,
                backend,
                current_C=current.C,
                current_reference_current=current.reference_current,
                reset_C=VertexScalar(ref.graph, (1e308, 1e308)),
                reset_reference_current=current.reference_current,
            )
        self.assertEqual(canonical_json_bytes(current.to_payload()), before)

    def test_missing_reference_current_is_not_a_zero_seed(self) -> None:
        ref, backend = fixture(alpha=0.0, beta=0.0, gamma=1.0)
        with self.assertRaises(TypeError):
            CandidateAInitializationStage(
                ref, backend, VertexScalar(ref.graph, (1.0, 3.0))
            )
        zero, nonzero = stage(ref, backend, J=(0.0,)), stage(ref, backend, J=(1.0,))
        self.assertNotEqual(zero.identity, nonzero.identity)
        self.assertEqual(zero.authority.state.W_A, (1.0,))
        self.assertEqual(nonzero.authority.state.W_A, (math.exp(-0.5),))

    def test_orientation_permutation_and_host_rigid_frame_covariance(self) -> None:
        graph = GRCV4Graph(
            ("a", "b", "c"), (OrientedEdge("x", "a", "b"), OrientedEdge("y", "b", "c"))
        )
        ref, backend = fixture(
            graph=graph, dimension=2, positions=((0.0, 0.0), (1.0, 0.0), (1.0, 1.0))
        )
        original = stage(ref, backend, (1.0, 3.0, 2.0), (0.5, -1.0))
        changed = GRCV4Graph(
            ("c", "a", "b"), (OrientedEdge("y", "c", "b"), OrientedEdge("x", "b", "a"))
        )
        # Node permutation plus rigid quarter-turn/translation, both edge signs.
        ref2, backend2 = fixture(
            graph=changed, dimension=2, positions=((3.0, 4.0), (4.0, 3.0), (4.0, 4.0))
        )
        transformed = stage(ref2, backend2, (2.0, 1.0, 3.0), (1.0, -0.5))
        self.assertEqual(
            transformed.authority.state.W_A, original.authority.state.W_A[::-1]
        )
        self.assertNotEqual(transformed.identity, original.identity)

    def test_empty_isolated_disconnected_and_coincident_host_positions(self) -> None:
        for graph, positions, C in [
            (GRCV4Graph((), ()), (), ()),
            (GRCV4Graph(("i",), ()), ((0.0,),), (7.0,)),
        ]:
            backend = CandidateADifferentialReference(graph, 1, positions, {}, 1.0)
            self.assertEqual(
                backend.rebuild(VertexScalar(graph, C)), ((0.0,),) * len(C)
            )
            # The frozen complete-profile reference-Hodge schema excludes an
            # empty edge map. A vacuous differential is not target admission.
            with self.assertRaisesRegex(ValueError, "non-empty"):
                fixture(graph=graph, positions=positions)
        graph = GRCV4Graph((0, 1, 2), (OrientedEdge("e", 0, 1),))
        ref, backend = fixture(graph=graph, positions=((0.0,), (0.0,), (5.0,)))
        result = stage(ref, backend, (1.0, 3.0, 9.0), (0.0,))
        self.assertEqual(result.descriptors, ((0.0,),) * 3)
        self.assertEqual(len(result.authority.state.W_A), 1)

    def test_floor_is_exact_normative_floor_including_subnormal(self) -> None:
        tiny = math.nextafter(0.0, 1.0)
        for floor in (tiny, 0.25, 2.0):
            ref, backend = fixture(W_floor=floor, alpha=1.0, beta=0.0, gamma=0.0)
            result = stage(ref, backend, (1e308, 1e308))
            self.assertEqual(result.authority.state.W_A, (floor,))
        ref, backend = fixture(W_floor=1.0, alpha=0.0, beta=0.0, gamma=0.0)
        self.assertEqual(stage(ref, backend).authority.state.W_A, (1.0,))

    def test_exp_boundary_and_large_signed_channel_cancellation(self) -> None:
        # All inputs and the final answer are representable; naive C_u+C_v
        # and gamma*J**2 overflow before their exact cancellation.
        ref, backend = fixture(alpha=1.0, beta=0.0, gamma=-2.0)
        c = math.ldexp(1.0, 1000)
        j = math.ldexp(1.0, 500)
        result = stage(ref, backend, (c, c), (j,))
        self.assertEqual(result.authority.state.W_A, (1.0,))
        ref, backend = fixture(alpha=0.0, beta=0.0, gamma=0.0)
        self.assertEqual(
            stage(ref, backend, (1e308, 1e308), (1e308,)).authority.state.W_A, (1.0,)
        )
        ref, backend = fixture(alpha=-1.0, beta=0.0, gamma=0.0)
        value = stage(ref, backend, (709.0, 709.0)).authority.state.W_A[0]
        self.assertTrue(math.isfinite(value) and value > 0)
        with self.assertRaisesRegex(ValueError, "overflows"):
            stage(ref, backend, (710.0, 710.0))

    def test_large_exponent_rounding_against_decimal_at_rounded_input(self) -> None:
        # With beta=gamma=0 and equal endpoints, E = -alpha*C exactly.
        # Decimal's correctly rounded exp supplies an independent oracle at
        # E64. It also exposes the separate effect of rounding E before exp.
        for alpha in (-0.1, 0.1):
            with self.subTest(alpha=alpha), localcontext() as ctx:
                ctx.prec = 160
                ref, backend = fixture(
                    alpha=alpha,
                    beta=0.0,
                    gamma=0.0,
                    W_floor=math.nextafter(0.0, 1.0),
                    eta=1.0,
                )
                actual = stage(ref, backend, (7001.0, 7001.0)).authority.state.W_A[0]
                exact_exponent = -Decimal.from_float(alpha) * Decimal(7001)
                rounded_exponent = Decimal.from_float(float(exact_exponent))
                rounded_oracle = float(rounded_exponent.exp())
                exact_oracle = float(exact_exponent.exp())
                self.assertNotEqual(exact_exponent, rounded_exponent)
                self.assertAlmostEqual(
                    actual, rounded_oracle, delta=math.ulp(rounded_oracle)
                )
                # This is a witness against a global four-ULP exact-exponent
                # claim, not a platform-specific expected ULP-distance count.
                self.assertGreater(
                    abs(actual - exact_oracle), 4 * math.ulp(exact_oracle)
                )

    def test_gradient_subnormal_rounding_ties_and_canonical_zero(self) -> None:
        tiny = math.nextafter(0.0, 1.0)
        normal = math.ldexp(1.0, -1022)
        # For x=(0,1), w=1, the exact gradient is +/-C/(1+ridge)
        # at both nodes. Expected values follow binary64 ties-to-even by hand.
        for ridge, cases in (
            (4.0, [(tiny, 0.0), (2 * tiny, 0.0), (3 * tiny, tiny), (5 * tiny, tiny)]),
            (
                1.0,
                [
                    (tiny, 0.0),
                    (2 * tiny, tiny),
                    (3 * tiny, 2 * tiny),
                    (5 * tiny, 2 * tiny),
                    (7 * tiny, 4 * tiny),
                    (2 * normal - tiny, normal),
                    (2 * normal - 2 * tiny, normal - tiny),
                    (2 * normal - 3 * tiny, normal - 2 * tiny),
                ],
            ),
        ):
            ref, backend = fixture(ridge=ridge, alpha=0.0, beta=1.0, gamma=0.0, eta=1.0)
            for c, magnitude in cases:
                for sign in (1.0, -1.0):
                    with self.subTest(ridge=ridge, C=c, sign=sign):
                        C = (0.0, c) if sign > 0 else (c, 0.0)
                        result = stage(ref, backend, C)
                        expected = sign * magnitude if magnitude else 0.0
                        self.assertEqual(result.descriptors, ((expected,), (expected,)))
                        for gradient in result.descriptors:
                            self.assertEqual(
                                math.copysign(1.0, gradient[0]),
                                sign if magnitude else 1.0,
                            )
                        # A rounded-zero gradient does not relax the strict
                        # positivity requirement for retained W_A or mobility.
                        self.assertEqual(result.authority.state.W_A, (1.0,))
                        self.assertEqual(result.authority.mobility.diagonal, (1.0,))

    def test_parallel_edges_self_loop_and_isolate_in_typed_stage(self) -> None:
        graph = GRCV4Graph(
            ("u", "v", "isolated"),
            (
                OrientedEdge("a", "u", "v"),
                OrientedEdge("b", "v", "u"),
                OrientedEdge("loop", "u", "u"),
            ),
        )
        ref, backend = fixture(
            graph=graph,
            positions=((0.0,), (1.0,), (8.0,)),
            weights={"a": 1.0, "b": 3.0, "loop": 1e308},
            alpha=0.0,
            beta=1.0,
            gamma=1.0,
            eta=1.0,
        )
        result = stage(ref, backend, (1.0, 3.0, 9.0), (0.5, -1.0, 2.0))
        # Both parallel edges contribute: ((1+3)*2)/(1+1+3) = 8/5.
        # The loop has zero displacement even at an extreme reference weight;
        # the isolate has only its declared ridge and zero right-hand side.
        self.assertEqual(result.descriptors, ((8 / 5,), (8 / 5,), (0.0,)))
        with localcontext() as ctx:
            ctx.prec = 100
            for actual, exponent in zip(
                result.authority.state.W_A,
                (Decimal("-0.125"), Decimal("-0.5"), Decimal(-2)),
                strict=True,
            ):
                expected = float(exponent.exp())
                self.assertAlmostEqual(actual, expected, delta=math.ulp(expected))
        self.assertEqual(result.authority.mobility.diagonal, result.authority.state.W_A)
        rebuilt = CandidateAInitializationStage.from_payload(result.to_payload())
        self.assertEqual(rebuilt.identity, result.identity)
        self.assertEqual(rebuilt.descriptors, result.descriptors)
        self.assertEqual(rebuilt.authority.state.W_A, result.authority.state.W_A)

    def test_rational_wls_avoids_overflowing_normal_equations(self) -> None:
        ref, backend = fixture(
            positions=((0.0,), (1e308,)), alpha=0.0, beta=0.0, gamma=0.0
        )
        result = stage(ref, backend, (0.0, 1e308))
        self.assertEqual(result.descriptors, ((1.0,), (1.0,)))
        self.assertEqual(result.authority.state.W_A, (1.0,))

    def test_unrepresentable_fresh_differential_is_not_hidden_by_zero_beta(
        self,
    ) -> None:
        ref, backend = fixture(
            positions=((0.0,), (1e-161,)),
            ridge=math.nextafter(0.0, 1.0),
            alpha=0.0,
            beta=0.0,
            gamma=0.0,
        )
        with self.assertRaisesRegex(ValueError, "not representable"):
            stage(ref, backend, (0.0, 1e308))

    def test_same_value_initialization_does_not_claim_formation_or_history(
        self,
    ) -> None:
        ref, backend = fixture(alpha=0.0, beta=0.0, gamma=0.0)
        original = stage(ref, backend)
        result = CandidateAInitialization(original, original)
        existing = GRCV4AuthoritativeState((1.0, 3.0), (1.0,), None)
        self.assertEqual(result.current.authority.state, existing)
        self.assertFalse(result.to_payload()["source_history_preserved"])
        self.assertFalse(result.to_payload()["native_formation_claimed"])
        self.assertFalse(result.to_payload()["lifecycle_committed"])
        other_ref, other_backend = fixture(ridge=2.0, alpha=0.0, beta=0.0, gamma=0.0)
        with self.assertRaisesRegex(ValueError, "same declared target recipe"):
            CandidateAInitialization(original, stage(other_ref, other_backend))

    def test_existing_positive_history_below_drive_floor_is_not_clamped(self) -> None:
        ref, backend = fixture(W_floor=0.5, eta=2.0)
        state = GRCV4AuthoritativeState((1.0, 3.0), (0.125,), None)
        authority = CandidateARetainedAuthority(ref.graph, ref.profile, state)
        self.assertEqual(authority.state.W_A, (0.125,))
        self.assertEqual(authority.mobility.diagonal, (0.25,))
        self.assertNotEqual(
            authority.state.W_A, stage(ref, backend).authority.state.W_A
        )

    def test_positive_mobility_overflow_underflow_and_bad_history_fail(self) -> None:
        for eta, W in [(1e308, (1e308,)), (1e-308, (1e-308,))]:
            ref, _ = fixture(eta=eta)
            with self.assertRaises(ValueError):
                CandidateARetainedAuthority(
                    ref.graph, ref.profile, GRCV4AuthoritativeState((1.0, 3.0), W, None)
                )
        ref, _ = fixture()
        for W in [None, (), (1.0, 2.0)]:
            with self.assertRaises(ValueError):
                CandidateARetainedAuthority(
                    ref.graph, ref.profile, GRCV4AuthoritativeState((1.0, 3.0), W, None)
                )
        for W in [(0.0,), (-1.0,), (True,), (math.nan,), (math.inf,)]:
            with self.assertRaises((TypeError, ValueError)):
                GRCV4AuthoritativeState((1.0, 3.0), W, None)

    def test_backend_preimages_bind_profile_and_geometry(self) -> None:
        ref, backend = fixture()
        for changed in [
            replace(backend, regularization=2.0),
            replace(backend, positions=((0.0,), (2.0,))),
            replace(backend, reference_weights=FrozenJSONMap({"e": 2.0})),
        ]:
            with self.assertRaisesRegex(ValueError, "mismatch"):
                stage(ref, changed)
        other_ref, other_backend = fixture(weights={"e": 4.0})
        self.assertNotEqual(
            other_ref.profile.complete_profile_id, ref.profile.complete_profile_id
        )
        self.assertNotEqual(other_backend.identity, backend.identity)

    def test_bad_input_types_shapes_signs_and_coordinate_domains(self) -> None:
        ref, backend = fixture()
        for kwargs in [
            dict(dimension=True),
            dict(dimension=0),
            dict(positions=((0.0,),)),
            dict(positions=((False,), (1.0,))),
            dict(regularization=0.0),
            dict(regularization=-1.0),
            dict(reference_weights={}),
            dict(reference_weights={"e": 1.0, "extra": 2.0}),
            dict(reference_weights={"e": 0.0}),
            dict(positions=((math.inf,), (0.0,))),
        ]:
            with self.assertRaises((TypeError, ValueError)):
                replace(backend, **kwargs)
        for C, J in [
            (VertexScalar(ref.graph, (-1.0, 3.0)), PhysicalFlux(ref.graph, (0.0,))),
            (VertexScalar(ref.graph, (1.0, 3.0)), OneForm(ref.graph, (0.0,))),
        ]:
            with self.assertRaises((TypeError, ValueError)):
                CandidateAInitializationStage(ref, backend, C, J)
        reversed_graph = GRCV4Graph(("u", "v"), (OrientedEdge("e", "v", "u"),))
        with self.assertRaises(ValueError):
            CandidateAInitializationStage(
                ref,
                backend,
                VertexScalar(ref.graph, (1.0, 3.0)),
                PhysicalFlux(reversed_graph, (0.0,)),
            )

    def test_unsupported_candidate_realization_and_history_policy_fail(self) -> None:
        ref, backend = fixture(realization="PC")
        with self.assertRaisesRegex(ValueError, "A_OS"):
            stage(ref, backend)
        c = stage_reference_fixture("C", graph=backend.graph)
        with self.assertRaisesRegex(TypeError, "Candidate A"):
            stage(c, backend)
        ref, backend = fixture()
        # A genuine newly identified unsupported declaration is still rejected.
        params = ref.profile.params_resolved.to_payload()
        ident = ref.profile.identity_payload.to_payload()
        params["lifecycle"]["history_policy_id"] = "undeclared_seed_policy"
        reidentify(params, ident)
        ref = replace(ref, profile=resolve_profile(params, ident))
        with self.assertRaisesRegex(ValueError, "history policy"):
            stage(ref, backend)

    def test_roundtrip_rebuilds_and_rejects_cached_outputs_or_claim_promotions(
        self,
    ) -> None:
        ref, backend = fixture()
        original = CandidateAInitialization(
            stage(ref, backend), stage(ref, backend, (2.0, 6.0), (1.0,))
        )
        payload = json.loads(canonical_json_bytes(original.to_payload()))
        rebuilt = CandidateAInitialization.from_payload(payload)
        self.assertEqual(rebuilt.identity, original.identity)
        self.assertEqual(
            rebuilt.current.authority.state, original.current.authority.state
        )
        for field, value in [
            ("source_history_preserved", True),
            ("native_formation_claimed", True),
            ("lifecycle_committed", True),
            ("whole_target_readmission", "passed"),
        ]:
            forged = deepcopy(payload)
            forged[field] = value
            with self.assertRaises(ValueError):
                CandidateAInitialization.from_payload(forged)
        for field, value in [
            ("W_A", [1.0]),
            ("descriptors", [[1.0], [1.0]]),
            ("reference_current_role", "committed_A_current"),
        ]:
            forged = deepcopy(payload)
            forged["current"][field] = value
            with self.assertRaises(ValueError):
                CandidateAInitialization.from_payload(forged)
        forged = deepcopy(payload)
        forged["current"]["differential_reference"]["backend"] = BACKEND + "-other"
        with self.assertRaises(ValueError):
            CandidateAInitialization.from_payload(forged)

    def test_inputs_outputs_detach_and_no_runtime_support_is_advertised(self) -> None:
        positions = [[0.0], [1.0]]
        weights = {"e": 1.0}
        ref, backend = fixture(positions=positions, weights=weights)
        result = stage(ref, backend)
        before = result.identity
        positions[0][0] = 9.0
        weights["e"] = 10.0
        payload = result.to_payload()
        payload["C"][0] = 100.0
        self.assertEqual(result.identity, before)
        with self.assertRaises(FrozenInstanceError):
            result.authority.state.W_A = (10.0,)
        self.assertEqual(len(list_supported_profiles()), 9)
        self.assertTrue(
            all(
                get_supported_profile(p).identity_payload.candidate in ("A", "C")
                for p in list_supported_profiles()
            )
        )


def current_fixture(*, C=(3.0, 1.0), W=(2.0,), dt=0.125, changes=None, **kwargs):
    candidate = dict(
        site_potential_id=A_SITE_POTENTIAL,
        kappa_c=0.5,
        eta=0.25,
        alpha=0.0,
        beta=0.0,
        gamma=0.0,
        chi_A=0.5,
        zeta_A=0.75,
    )
    candidate.update(kwargs)
    ref, backend = fixture(**candidate)
    params, identity = (
        ref.profile.params_resolved.to_payload(),
        ref.profile.identity_payload.to_payload(),
    )
    params["solver"].update(absolute_tolerance=1e-12, relative_tolerance=1e-12)
    params["charge"].update(absolute_tolerance=1e-12)
    for group, values in (changes or {}).items():
        params[group].update(values)
    reidentify(params, identity)
    ref = replace(ref, profile=resolve_profile(params, identity))
    state = GRCV4AuthoritativeState(C, W, None)
    inputs = GeometryStageInputs(
        ref.geometry(),
        ref.context,
        state,
        state,
        "operation:p952",
        float(sum(C)),
        (),
        0,
        0.0,
        dt,
        "pre_read",
        0,
        None,
    )
    return inputs, backend


def write_fixture(**kwargs):
    before, backend = current_fixture(**kwargs)
    point = CandidateACurrent(replace(before, stage="os_corrector"), backend)
    resource = ProvisionalResourceStep(
        before, CurrentSelection(point.inputs, "valid_root", point.current)
    )
    return point, resource


def log_writer_oracle(old, target, dt, tau):
    """Independent 240-digit multiplicative powers, not the runtime log increment."""
    with localcontext() as ctx:
        ctx.prec = 240
        a = (-Decimal.from_float(float(dt)) / Decimal.from_float(float(tau))).exp()
        return tuple(
            float(
                Decimal.from_float(float(w)) ** a
                * Decimal.from_float(float(d)) ** (1 - a)
            )
            for w, d in zip(old, target, strict=True)
        )


class CandidateACurrentWriterTests(unittest.TestCase):
    def test_reference_baseline_and_regular_read_have_closed_form(self):
        inputs, backend = current_fixture()
        result = CandidateACurrent(inputs, backend)
        self.assertEqual(result.reference_potential_exact, (2.0, -2.0))
        self.assertEqual(result.geometry_potential_increment_exact, (0.0, 0.0))
        self.assertEqual(result.baseline.values, (-2.0,))
        self.assertEqual(result.W_hat_A, (1.0,))
        self.assertEqual(result.contrast_exact, (Fraction(1, 3),))
        self.assertEqual(result.denominator_exact, (Fraction(7, 8),))
        self.assertEqual(result.current.values, (-16 / 7,))
        self.assertAlmostEqual(
            result.read.flux.values[0], -8 / 21, delta=math.ulp(8 / 21)
        )
        self.assertEqual(result.read.causal_flat.values, result.read.flux.values)

    def test_nonreference_geometry_changes_potential_without_mobility_transfer(self):
        before, backend = current_fixture(kappa_Ah=0.25)
        ref = before.geometry.reference
        point = CandidateACurrent(
            replace(
                before,
                geometry=GRCV4Geometry(ref, OneFormHodge(ref.graph, ((3.0,),))),
                stage="os_corrector",
            ),
            backend,
        )
        self.assertEqual(point.geometry_potential_increment_exact, (1.0, -1.0))
        self.assertEqual(point.potential.values, (3.0, -3.0))
        self.assertEqual(point.baseline.values, (-3.0,))
        self.assertEqual(point.authority.mobility.diagonal, (0.5,))
        self.assertAlmostEqual(
            point.read.causal_flat.values[0], point.read.flux.values[0] / 3, delta=1e-16
        )
        source = point.structural_source()
        self.assertAlmostEqual(
            source.increment[0][0],
            0.75 * point.read.causal_flat.values[0] ** 2,
            delta=1e-16,
        )

    def test_explicit_gate_and_structural_gain_controls_preserve_direct_history(self):
        points = []
        for options in ({}, dict(chi_A=0.0), dict(zeta_A=0.0)):
            inputs, backend = current_fixture(**options)
            points.append(CandidateACurrent(inputs, backend))
        self.assertEqual({p.baseline.values for p in points}, {(-2.0,)})
        self.assertEqual(points[1].current, points[1].baseline)
        self.assertEqual(points[1].read.flux.values, (0.0,))
        self.assertEqual(points[2].current, points[2].baseline)
        self.assertNotEqual(points[2].read.flux.values, (0.0,))
        self.assertEqual(points[2].structural_source().increment, ((0.0,),))
        inputs, backend = current_fixture(chi_A=0.0, W=(1.0,))
        self.assertNotEqual(
            CandidateACurrent(inputs, backend).baseline, points[1].baseline
        )

    def test_exact_contrast_avoids_overflow_and_false_endpoint_singularities(self):
        for w, target, zeta, expected in (
            (1e308, 5e307, 0.5, Fraction(1, 3)),
            (1e308, 1.0, 1.0, None),
            (math.nextafter(0.0, 1.0), 1e308, -1.0, None),
        ):
            with self.subTest(w=w, target=target):
                inputs, backend = current_fixture(
                    C=(0.0, 0.0),
                    W=(w,),
                    eta=1.0,
                    W_floor=target,
                    kappa_c=0.0,
                    chi_A=1.0,
                    zeta_A=zeta,
                )
                point = CandidateACurrent(inputs, backend)
                if expected is not None:
                    self.assertEqual(point.contrast_exact, (expected,))
                else:
                    self.assertEqual(abs(point.contrast[0]), 1.0)
                    self.assertLess(abs(point.contrast_exact[0]), 1)
                self.assertGreater(point.denominator_exact[0], 0)
                self.assertEqual(point.current.values, (0.0,))

    def test_singular_and_exact_conditioning_boundaries_fail_closed(self):
        for C in ((0.0, 0.0), (3.0, 1.0)):
            inputs, backend = current_fixture(C=C, W=(3.0,), chi_A=1.0, zeta_A=2.0)
            with self.assertRaises(CandidateAStageError) as error:
                CandidateACurrent(inputs, backend)
            self.assertEqual(error.exception.disposition, "singular")
        graph = GRCV4Graph(
            (0, 1, 2, 3), (OrientedEdge("a", 0, 1), OrientedEdge("b", 2, 3))
        )
        for limit, valid in ((4.0, True), (math.nextafter(4.0, 0.0), False)):
            inputs, backend = current_fixture(
                graph=graph,
                C=(0.0,) * 4,
                W=(3.0, 1.0),
                chi_A=1.0,
                zeta_A=1.5,
                changes={"solver": {"conditioning_limit": limit}},
            )
            if valid:
                self.assertEqual(
                    CandidateACurrent(inputs, backend).denominator_exact,
                    (Fraction(1, 4), Fraction(1)),
                )
            else:
                with self.assertRaises(CandidateAStageError) as error:
                    CandidateACurrent(inputs, backend)
                self.assertEqual(error.exception.disposition, "conditioning_failure")

    def test_signed_regular_gain_outside_sufficient_uniform_region(self):
        inputs, backend = current_fixture(W=(3.0,), chi_A=1.0, zeta_A=3.0)
        point = CandidateACurrent(inputs, backend)
        self.assertEqual(point.denominator_exact, (Fraction(-1, 2),))
        self.assertEqual(point.current.values, (-2 * point.baseline.values[0],))

    def test_strict_residual_rejects_unrepresentable_root_and_typed_flat_failure(self):
        inputs, backend = current_fixture(
            changes={"solver": {"absolute_tolerance": 0.0, "relative_tolerance": 0.0}}
        )
        with self.assertRaises(CandidateAStageError) as error:
            CandidateACurrent(inputs, backend)
        self.assertEqual(error.exception.disposition, "no_admitted_root")
        graph = GRCV4Graph(
            (0, 1, 2), (OrientedEdge("a", 0, 1), OrientedEdge("b", 1, 2))
        )
        inputs, backend = current_fixture(
            graph=graph,
            C=(0.0, 0.0, 0.0),
            W=(1.0, 1.0),
            changes={"solver": {"conditioning_limit": 2.0}},
        )
        ref = inputs.geometry.reference
        with self.assertRaises(CandidateAStageError) as error:
            CandidateACurrent(
                replace(
                    inputs,
                    geometry=GRCV4Geometry(
                        ref, OneFormHodge(graph, ((1.0, 0.0), (0.0, 4.0)))
                    ),
                ),
                backend,
            )
        self.assertEqual(error.exception.disposition, "conditioning_failure")

    def test_dense_geometry_multigraph_and_all_conductance_channels(self):
        graph = GRCV4Graph(
            ("u", "v", "w", "i"),
            (
                OrientedEdge("a", "u", "v"),
                OrientedEdge("b", "v", "u"),
                OrientedEdge("c", "v", "w"),
                OrientedEdge("loop", "u", "u"),
            ),
        )
        inputs, backend = current_fixture(
            graph=graph,
            C=(3.0, 1.0, 2.0, 7.0),
            W=(2.0, 0.5, 1.0, 3.0),
            kappa_Ah=0.25,
            alpha=0.125,
            beta=0.25,
            gamma=0.0625,
        )
        ref = inputs.geometry.reference
        h = (
            (2.0, 0.25, 0.0, 0.25),
            (0.25, 3.0, 0.5, 0.0),
            (0.0, 0.5, 2.0, 0.0),
            (0.25, 0.0, 0.0, 4.0),
        )
        point = CandidateACurrent(
            replace(
                inputs,
                geometry=GRCV4Geometry(ref, OneFormHodge(graph, h)),
                stage="os_corrector",
            ),
            backend,
        )
        # Independent literal incidence/matrix oracle at small exact inputs.
        import numpy as np

        B = np.array(
            ((1, -1, 0, 0), (-1, 1, 1, 0), (0, 0, -1, 0), (0, 0, 0, 0)), dtype=float
        )
        C = np.array(inputs.current.C)
        expected_phi = 0.5 * (B @ np.diag(inputs.current.W_A) @ B.T @ C) + 0.25 * (
            B @ (np.array(h) - np.eye(4)) @ B.T @ C
        )
        self.assertEqual(point.potential.values, tuple(expected_phi))
        self.assertEqual(
            point.baseline.values,
            tuple(-0.25 * np.array(inputs.current.W_A) * (B.T @ expected_phi)),
        )
        D, hat = scalar_oracle(ref, backend, inputs.current.C, point.baseline.values)
        self.assertEqual(point.descriptors, D)
        for w, expected in zip(point.W_hat_A, hat, strict=True):
            self.assertAlmostEqual(w, expected, delta=4 * math.ulp(expected))
        self.assertEqual(point.baseline.values[-1], 0.0)
        self.assertNotEqual(point.read.causal_flat.values[-1], 0.0)
        self.assertEqual(point.potential.values[-1], 0.0)
        np.testing.assert_allclose(
            np.array(h) @ np.array(point.read.causal_flat.values),
            point.read.flux.values,
            rtol=1e-14,
            atol=1e-14,
        )

    def test_current_reconstruction_and_rejection_of_unknown_or_cached_inputs(self):
        inputs, backend = current_fixture()
        point = CandidateACurrent(inputs, backend)
        self.assertEqual(CandidateACurrent.from_payload(point.to_payload()), point)
        for field, value in (
            ("current", [1.0]),
            ("W_hat_A", [1.0]),
            ("contrast", [0.0]),
            ("numerics", "invented"),
        ):
            payload = deepcopy(point.to_payload())
            payload[field] = value
            with self.assertRaises(ValueError):
                CandidateACurrent.from_payload(payload)
        for options in (
            dict(site_potential_id="test_site_potential_v1"),
            dict(changes={"solver": {"solver_kind": "newton"}}),
        ):
            x, b = current_fixture(**options)
            with self.assertRaises(ValueError):
                CandidateACurrent(x, b)
        with self.assertRaises(ValueError):
            CandidateACurrent(replace(inputs, trial_current=point.current), backend)
        with self.assertRaises(ValueError):
            CandidateACurrent(inputs, replace(backend, regularization=2.0))
        with self.assertRaises(TypeError):
            point.read_back(OneForm(point.current.graph, (1.0,)))

    def test_current_orientation_permutation_and_resource_shift_covariance(self):
        graph = GRCV4Graph(
            ("u", "v", "w"), (OrientedEdge("a", "u", "v"), OrientedEdge("b", "v", "w"))
        )
        x, b = current_fixture(
            graph=graph, C=(3.0, 1.0, 2.0), W=(2.0, 0.5), gamma=0.125, beta=0.25
        )
        point = CandidateACurrent(x, b)
        changed = GRCV4Graph(
            ("w", "u", "v"), (OrientedEdge("b", "w", "v"), OrientedEdge("a", "v", "u"))
        )
        y, b2 = current_fixture(
            graph=changed,
            positions=((2.0,), (0.0,), (1.0,)),
            C=(2.0, 3.0, 1.0),
            W=(0.5, 2.0),
            gamma=0.125,
            beta=0.25,
        )
        moved = CandidateACurrent(y, b2)
        self.assertEqual(moved.W_hat_A, point.W_hat_A[::-1])
        self.assertEqual(
            moved.current.values, tuple(-v for v in point.current.values[::-1])
        )
        shifted = CandidateACurrent(
            replace(
                x, current=GRCV4AuthoritativeState((5.0, 3.0, 4.0), (2.0, 0.5), None)
            ),
            b,
        )
        self.assertEqual(
            shifted.current, point.current
        )  # alpha=0, zero site derivative

    def test_predictor_corrector_rebuilds_baseline_reference_and_contrast(self):
        before, backend = current_fixture(kappa_Ah=0.25, gamma=0.25)
        predictor = CandidateACurrent(replace(before, stage="os_predictor"), backend)
        ref = before.geometry.reference
        geometry = H_profile(
            predictor.structural_source(),
            reference=ref,
            context=ref.context,
            profile=ref.profile,
        )
        corrector = CandidateACurrent(
            replace(before, stage="os_corrector", geometry=geometry), backend
        )
        self.assertNotEqual(corrector.baseline, predictor.baseline)
        self.assertNotEqual(corrector.W_hat_A, predictor.W_hat_A)
        self.assertNotEqual(corrector.contrast_exact, predictor.contrast_exact)
        self.assertEqual(corrector.authority.state.W_A, predictor.authority.state.W_A)

    def test_log_writer_small_ratio_and_extreme_endpoints_against_powers(self):
        tiny = math.nextafter(0.0, 1.0)
        large = math.nextafter(math.inf, 0.0)
        cases = [
            (1.0, 16.0, math.log(2.0), 1.0),
            (tiny, large, 1.0, 1.0),
            (large, tiny, 1.0, 1.0),
            (1.0, 1e308, 1e-17, 1.0),
            (1e308, tiny, 1e-17, 1.0),
            (tiny, 2 * tiny, 1.0, 1.0),
            (large, large, 1.0, 1.0),
            (1.0, 2.0, tiny, 1e308),
        ]
        for w, d, dt, tau in cases:
            with self.subTest(old=w, target=d, dt=dt, tau=tau):
                actual = candidate_a_log_interpolation((w,), (d,), dt, tau)[0]
                expected = log_writer_oracle((w,), (d,), dt, tau)[0]
                self.assertAlmostEqual(actual, expected, delta=math.ulp(expected))
                self.assertGreater(actual, 0.0)
                self.assertLessEqual(min(w, d), actual)
                self.assertLessEqual(actual, max(w, d))
        self.assertNotEqual(
            candidate_a_log_interpolation((1.0,), (1e308,), 1e-17, 1.0), (1.0,)
        )

    def test_log_writer_endpoints_validation_and_decimal_context_independence(self):
        tiny = math.nextafter(0.0, 1.0)
        for dt, tau in ((1000.0, 1.0), (1e308, tiny)):
            self.assertEqual(
                candidate_a_log_interpolation((tiny,), (1e308,), dt, tau), (1e308,)
            )
        self.assertEqual(
            candidate_a_log_interpolation((tiny,), (1.0,), 0.0, 1.0), (tiny,)
        )
        expected = candidate_a_log_interpolation((0.125,), (7.0,), 0.125, 0.7)
        with localcontext() as ctx:
            ctx.prec = 3
            self.assertEqual(
                candidate_a_log_interpolation((0.125,), (7.0,), 0.125, 0.7), expected
            )
        for old, target, dt, tau in (
            ((0.0,), (1.0,), 1.0, 1.0),
            ((1.0,), (-1.0,), 1.0, 1.0),
            ((1.0,), (), 1.0, 1.0),
            ((1.0,), (1.0,), -1.0, 1.0),
            ((1.0,), (1.0,), 1.0, 0.0),
            ((True,), (1.0,), 1.0, 1.0),
            ((1.0,), (1.0,), math.inf, 1.0),
        ):
            with self.assertRaises((TypeError, ValueError)):
                candidate_a_log_interpolation(old, target, dt, tau)

    def test_seeded_log_interpolation_with_independent_multiplicative_oracle(self):
        rng = random.Random(952)
        for _ in range(40):
            w, d = (
                math.ldexp(rng.uniform(1.0, 2.0), rng.randrange(-1074, 1023))
                for _ in range(2)
            )
            dt, tau = (
                math.ldexp(rng.uniform(1.0, 2.0), rng.randrange(-20, 20))
                for _ in range(2)
            )
            actual = candidate_a_log_interpolation((w,), (d,), dt, tau)[0]
            expected = log_writer_oracle((w,), (d,), dt, tau)[0]
            self.assertAlmostEqual(actual, expected, delta=math.ulp(expected))

    def test_writer_rebuilds_final_differential_and_reads_selected_total_current(self):
        graph = GRCV4Graph(
            (0, 1, 2), (OrientedEdge("a", 0, 1), OrientedEdge("b", 1, 2))
        )
        point, resource = write_fixture(
            graph=graph,
            C=(2.0, 1.0, 3.0),
            W=(2.0, 0.5),
            kappa_c=0.05,
            eta=0.1,
            alpha=0.25,
            beta=0.5,
            gamma=1.0,
            chi_A=1.0,
            zeta_A=0.5,
        )
        before = canonical_json_bytes(point.to_payload())
        original = CandidateADifferentialReference.rebuild
        with patch.object(
            CandidateADifferentialReference,
            "rebuild",
            autospec=True,
            side_effect=original,
        ) as rebuild:
            writer = CandidateAWriter(point, resource)
        self.assertEqual(rebuild.call_count, 1)
        self.assertEqual(rebuild.call_args.args[1].values, resource.provisional_state.C)
        D, drive = scalar_oracle(
            point.inputs.geometry.reference,
            point.differential_reference,
            resource.provisional_state.C,
            point.current.values,
        )
        self.assertEqual(writer.descriptors, D)
        self.assertNotEqual(writer.descriptors, point.descriptors)
        for actual, expected in zip(writer.W_drv_A, drive, strict=True):
            self.assertAlmostEqual(actual, expected, delta=4 * math.ulp(expected))
        expected = log_writer_oracle(
            point.inputs.current.W_A, writer.W_drv_A, point.inputs.dt, 1.0
        )
        self.assertEqual(writer.authority.state.W_A, expected)
        self.assertEqual(resource.continuity_evaluations, 1)
        self.assertEqual(canonical_json_bytes(point.to_payload()), before)
        self.assertNotEqual(writer.W_drv_A, point.W_hat_A)
        hold = replace(
            point.inputs,
            current=GRCV4AuthoritativeState(
                writer.authority.state.C, point.inputs.current.W_A, None
            ),
        )
        next_point = CandidateACurrent(
            replace(hold, current=writer.authority.state), point.differential_reference
        )
        self.assertNotEqual(
            next_point.baseline,
            CandidateACurrent(hold, point.differential_reference).baseline,
        )

    def test_writer_rejects_wrong_current_stage_operation_and_duration(self):
        point, resource = write_fixture(gamma=0.25)
        for flux in (point.baseline, point.read.flux):
            forged = ProvisionalResourceStep(
                resource.prestate, CurrentSelection(point.inputs, "valid_root", flux)
            )
            with self.assertRaises(ResourceBoundaryError):
                CandidateAWriter(point, forged)
        for changes in (dict(operation_id="another"), dict(dt=0.25)):
            foreign = CandidateACurrent(
                replace(point.inputs, **changes), point.differential_reference
            )
            with self.assertRaises(ResourceBoundaryError):
                CandidateAWriter(foreign, resource)
        for stage_name in ("os_predictor", "pre_read", "post_continuity"):
            wrong = CandidateACurrent(
                replace(point.inputs, stage=stage_name), point.differential_reference
            )
            with self.assertRaises(ValueError):
                CandidateAWriter(wrong, resource)
        zero = CandidateACurrent(
            replace(point.inputs, dt=0.0), point.differential_reference
        )
        with self.assertRaises(ValueError):
            CandidateAWriter(zero, resource)

    def test_resource_failure_prevents_writer_and_final_mobility_failure_preserves_inputs(
        self,
    ):
        inputs, backend = current_fixture(C=(0.0, 1.0), dt=1.0)
        point = CandidateACurrent(replace(inputs, stage="os_corrector"), backend)
        with patch("pygrc.models.grc_v4_candidate_a._conductance") as target:
            with self.assertRaises(ResourceBoundaryError):
                resource = ProvisionalResourceStep(
                    inputs, CurrentSelection(point.inputs, "valid_root", point.current)
                )
                CandidateAWriter(point, resource)
            target.assert_not_called()
        point, resource = write_fixture(
            C=(500.0, 500.0),
            W=(1e-308,),
            eta=1e308,
            kappa_c=0.0,
            alpha=-1.0,
            chi_A=0.0,
            zeta_A=0.0,
            dt=1000.0,
        )
        before = canonical_json_bytes(resource.to_payload())
        with self.assertRaises(CandidateAStageError) as error:
            CandidateAWriter(point, resource)
        self.assertEqual(error.exception.disposition, "nonfinite")
        self.assertEqual(canonical_json_bytes(resource.to_payload()), before)

    def test_writer_roundtrip_recomputes_outputs_and_rejects_claim_promotions(self):
        point, resource = write_fixture(gamma=0.25)
        writer = CandidateAWriter(point, resource)
        rebuilt = CandidateAWriter.from_payload(writer.to_payload())
        self.assertEqual(rebuilt.identity, writer.identity)
        self.assertEqual(rebuilt.authority.state, writer.authority.state)
        for field, value in (
            ("W_A", [1.0]),
            ("W_drv_A", [1.0]),
            ("lifecycle_committed", True),
            ("native_formation_claimed", True),
        ):
            payload = deepcopy(writer.to_payload())
            payload[field] = value
            with self.assertRaises(ValueError):
                CandidateAWriter.from_payload(payload)
        with self.assertRaises(FrozenInstanceError):
            writer.authority.state.W_A = (1.0,)
        self.assertEqual(len(list_supported_profiles()), 9)

    def test_current_range_failures_and_exact_potential_cancellation(self):
        inputs, backend = current_fixture(
            C=(1.0, 0.0),
            W=(1.0,),
            eta=1.0,
            kappa_c=1e308,
            kappa_Ah=-1e308,
        )
        ref = inputs.geometry.reference
        point = CandidateACurrent(
            replace(
                inputs, geometry=GRCV4Geometry(ref, OneFormHodge(ref.graph, ((2.0,),)))
            ),
            backend,
        )
        self.assertEqual(point.potential.values, (0.0, 0.0))
        self.assertEqual(point.baseline.values, (0.0,))
        inputs, backend = current_fixture(
            C=(0.25, 0.75),
            W=(1e308,),
            eta=1.0,
            kappa_c=1e-308,
            chi_A=1.0,
            zeta_A=1.0,
        )
        with self.assertRaises(CandidateAStageError) as error:
            CandidateACurrent(inputs, backend)
        self.assertEqual(error.exception.disposition, "nonfinite")
        inputs, backend = current_fixture(
            C=(0.0, 1e308),
            W=(1.0,),
            kappa_c=0.0,
            positions=((0.0,), (1e-161,)),
            ridge=math.nextafter(0.0, 1.0),
        )
        with self.assertRaises(CandidateAStageError) as error:
            CandidateACurrent(inputs, backend)
        self.assertEqual(error.exception.disposition, "nonfinite")

    def test_writer_preserves_subnormal_below_floor_history_and_checks_policy(self):
        point, resource = write_fixture(
            C=(0.0, 0.0),
            W=(math.nextafter(0.0, 1.0),),
            eta=1.0,
            kappa_c=0.0,
            W_floor=0.5,
            dt=0.01,
        )
        writer = CandidateAWriter(point, resource)
        self.assertGreater(writer.authority.state.W_A[0], 0.0)
        self.assertLess(writer.authority.state.W_A[0], 0.5)
        point, resource = write_fixture(
            changes={"lifecycle": {"history_policy_id": "unknown_writer"}}
        )
        with self.assertRaisesRegex(ValueError, "writer policy"):
            CandidateAWriter(point, resource)

    def test_predictor_reached_corrector_retains_unbounded_exact_diagnostics(self):
        s = math.ldexp(1.0, 1023)
        # Signed gains, edge reversal and node-order permutation must preserve
        # this reachable cancellation, including its exact diagnostic meaning.
        for sign, reverse, permute in (
            (1, False, False),
            (-1, False, False),
            (1, True, False),
            (1, False, True),
        ):
            with self.subTest(sign=sign, reverse=reverse, permute=permute):
                nodes = ("v", "u") if permute else ("u", "v")
                edge = (
                    OrientedEdge("e", "v", "u")
                    if reverse
                    else OrientedEdge("e", "u", "v")
                )
                before, backend = current_fixture(
                    graph=GRCV4Graph(nodes, (edge,)),
                    C=tuple(1.0 if node == "u" else 0.0 for node in nodes),
                    W=(2.0,),
                    eta=math.ldexp(1.0, -1024),
                    kappa_c=sign * math.ldexp(1.0, 1022),
                    kappa_Ah=-sign * 3 * math.ldexp(1.0, 1021),
                    chi_A=1.0,
                    zeta_A=1.5,
                    changes={"geometry": {"kappa_H": 1.125}},
                )
                original = canonical_json_bytes(before.to_payload())
                ref = before.geometry.reference
                predictor = CandidateACurrent(
                    replace(before, stage="os_predictor"), backend
                )
                edge_sign = -sign if reverse else sign
                self.assertEqual(predictor.baseline.values, (-2.0 * edge_sign,))
                self.assertEqual(predictor.current.values, (-4.0 * edge_sign,))
                geometry = H_profile(
                    predictor.structural_source(),
                    reference=ref,
                    context=ref.context,
                    profile=ref.profile,
                )
                self.assertEqual(geometry.one_form_hodge.matrix, ((4.0,),))
                point = CandidateACurrent(
                    replace(before, stage="os_corrector", geometry=geometry), backend
                )
                phi0 = tuple(
                    Fraction(sign * s) * (1 if node == "u" else -1) for node in nodes
                )
                delta = tuple(-Fraction(9, 4) * x for x in phi0)
                self.assertEqual(point.reference_potential_exact, phi0)
                self.assertEqual(point.geometry_potential_increment_exact, delta)
                self.assertTrue(
                    all(
                        type(x) is Fraction
                        for x in point.geometry_potential_increment_exact
                    )
                )
                with self.assertRaises(OverflowError):
                    float(delta[0])
                self.assertEqual(
                    point.potential.values,
                    tuple(float(-Fraction(5, 4) * x) for x in phi0),
                )
                self.assertEqual(point.baseline.values, (2.5 * edge_sign,))
                self.assertEqual(point.denominator_exact, (Fraction(1, 2),))
                self.assertEqual(point.current.values, (5.0 * edge_sign,))
                rebuilt = CandidateACurrent.from_payload(point.to_payload())
                self.assertEqual(rebuilt, point)
                self.assertEqual(canonical_json_bytes(before.to_payload()), original)

    def test_both_potential_components_can_overflow_but_consumed_values_must_fit(self):
        for sign in (1, -1):
            before, backend = current_fixture(
                C=(1.0, 0.0),
                W=(2.0,),
                eta=0.25,
                kappa_c=sign * 1e308,
                kappa_Ah=-sign * 1e308,
            )
            ref = before.geometry.reference
            point = CandidateACurrent(
                replace(
                    before,
                    geometry=GRCV4Geometry(ref, OneFormHodge(ref.graph, ((3.0,),))),
                ),
                backend,
            )
            expected = Fraction(sign * 1e308) * 2
            self.assertEqual(point.reference_potential_exact, (expected, -expected))
            self.assertEqual(
                point.geometry_potential_increment_exact, (-expected, expected)
            )
            for value in (
                point.reference_potential_exact[0],
                point.geometry_potential_increment_exact[0],
            ):
                with self.assertRaises(OverflowError):
                    float(value)
            self.assertEqual(point.potential.values, (0.0, 0.0))
            self.assertEqual(point.baseline.values, (0.0,))
            self.assertEqual(point.current.values, (0.0,))
            # Reference geometry has no cancelling increment: its consumed
            # total is truly outside binary64 and must still reject.
            with self.assertRaises(CandidateAStageError) as caught:
                CandidateACurrent(before, backend)
            self.assertEqual(caught.exception.disposition, "nonfinite")
        # Here the potential fits but its consumed baseline does not.
        before, backend = current_fixture(
            C=(1.0, 0.0), W=(2.0,), eta=1.0, kappa_c=5e307
        )
        with self.assertRaises(CandidateAStageError) as caught:
            CandidateACurrent(before, backend)
        self.assertEqual(caught.exception.disposition, "nonfinite")

    def test_log_writer_isolates_all_decimal_defaults_and_current_context_fields(self):
        fields = (
            "prec",
            "rounding",
            "Emin",
            "Emax",
            "capitals",
            "clamp",
            "traps",
            "flags",
        )

        def snapshot(ctx):
            return {
                name: dict(getattr(ctx, name))
                if name in ("traps", "flags")
                else getattr(ctx, name)
                for name in fields
            }

        cases = [
            ((0.125,), (7.0,), 0.125, 0.7),
            ((7.0,), (0.125,), 2.0, 0.7),
            ((math.nextafter(0.0, 1.0),), (1e308,), 0.125, 1.0),
            ((0.125,), (7.0,), 0.0, 0.7),
            ((0.125,), (7.0,), 1000.0, 0.7),
            ((7.0,), (7.0,), 1.0, 0.7),
            ((), (), 1.0, 0.7),
        ]
        expected = [log_writer_oracle(*case) for case in cases]
        self.assertEqual(expected[0], (0.2414355139455957,))
        point, resource = write_fixture(gamma=0.25)
        expected_writer = CandidateAWriter(point, resource).authority.state
        saved_default, saved_current = snapshot(DefaultContext), snapshot(getcontext())
        try:
            for mode in ("current", "default", "both"):
                for flags_set in (False, True):
                    with (
                        self.subTest(mode=mode, flags_set=flags_set),
                        localcontext() as current,
                    ):
                        for name, value in saved_default.items():
                            setattr(DefaultContext, name, value)
                        contexts = {
                            "current": (current,),
                            "default": (DefaultContext,),
                            "both": (current, DefaultContext),
                        }[mode]
                        for ctx in contexts:
                            ctx.prec, ctx.rounding, ctx.Emin, ctx.Emax = (
                                2,
                                ROUND_UP,
                                -2,
                                2,
                            )
                            ctx.capitals, ctx.clamp = 0, 1
                            ctx.traps = dict.fromkeys(ctx.traps, True)
                            ctx.flags = dict.fromkeys(ctx.flags, flags_set)
                        hostile_default, hostile_current = (
                            snapshot(DefaultContext),
                            snapshot(current),
                        )
                        for case, value in zip(cases, expected, strict=True):
                            self.assertEqual(
                                candidate_a_log_interpolation(*case), value
                            )
                        self.assertEqual(
                            CandidateAWriter(point, resource).authority.state,
                            expected_writer,
                        )
                        with self.assertRaises(ValueError):
                            candidate_a_log_interpolation((0.0,), (1.0,), 1.0, 1.0)
                        self.assertEqual(snapshot(DefaultContext), hostile_default)
                        self.assertEqual(snapshot(current), hostile_current)
        finally:
            for name, value in saved_default.items():
                setattr(DefaultContext, name, value)
        self.assertEqual(snapshot(getcontext()), saved_current)

    def test_positive_writer_can_require_singular_poststate_readmission(self):
        # P9-5.3/full lifecycle must reject the complete transaction atomically;
        # the provisional writer must not feed new W into this beat's solve.
        point, resource = write_fixture(
            C=(0.0, 0.0),
            W=(4.0,),
            kappa_c=0.0,
            chi_A=1.0,
            zeta_A=3.0,
            tau_A=1.0,
            dt=math.log(2.0),
        )
        original = canonical_json_bytes(resource.to_payload())
        self.assertEqual(point.denominator_exact, (Fraction(-4, 5),))
        self.assertEqual(point.current.values, (0.0,))
        writer = CandidateAWriter(point, resource)
        self.assertEqual(writer.W_drv_A, (1.0,))
        self.assertEqual(writer.authority.state.W_A, (2.0,))
        self.assertEqual(writer.authority.state.C, point.inputs.current.C)
        with self.assertRaises(CandidateAStageError) as caught:
            CandidateACurrent(
                replace(point.inputs, current=writer.authority.state),
                point.differential_reference,
            )
        self.assertEqual(caught.exception.disposition, "singular")
        self.assertEqual(canonical_json_bytes(resource.to_payload()), original)
        self.assertEqual(point.current.values, (0.0,))


if __name__ == "__main__":
    unittest.main()

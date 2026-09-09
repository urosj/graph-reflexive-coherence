"""P9-5.1: independent scalar/Decimal initialization and authority pressure."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import FrozenInstanceError, replace
from decimal import Decimal, localcontext
import json
import math
import random
import unittest

from pygrc.models.grc_v4_candidate_a import (
    BACKEND,
    HISTORY_POLICY,
    CandidateADifferentialReference,
    CandidateAInitialization,
    CandidateAInitializationStage,
    CandidateARetainedAuthority,
)
from pygrc.models.grc_v4_codec import canonical_json_bytes
from pygrc.models.grc_v4_geometry import (
    GRCV4Graph,
    OneForm,
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
        self.assertEqual(len(list_supported_profiles()), 1)
        self.assertTrue(
            all(
                get_supported_profile(p).identity_payload.candidate == "C"
                for p in list_supported_profiles()
            )
        )


if __name__ == "__main__":
    unittest.main()

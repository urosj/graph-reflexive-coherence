"""Matrix reuse preserves numerical proofs, per-RHS checks and scope isolation."""

import math
import unittest
from concurrent.futures import ThreadPoolExecutor
from dataclasses import FrozenInstanceError, replace
from fractions import Fraction
from threading import Barrier
from unittest.mock import patch

from pygrc.models import _grc_v4_matrix as arithmetic
from pygrc.models import grc_v4_codec as codec
from pygrc.models import grc_v4_numerics as numerics
from pygrc.models.grc_v4_candidate_a import CandidateACurrent
from pygrc.models.grc_v4_ci import (
    CIStageError,
    _analytic_residual,
    _iinverse,
    _Interval,
)
from pygrc.models.grc_v4_geometry import GRCV4Graph, OrientedEdge
from pygrc.models.grc_v4_linear import _MAX_MATRIX_FACTS
from tests.models.test_grc_v4_candidate_c import current_fixture
from tests.models.test_grc_v4_ci import fixture as ci_fixture

MATRIX = ((3.0, 1.0), (1.0, 3.0))
RHS = ((1.0,), (2.0,))


class MatrixPreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy = current_fixture().geometry.reference.profile.params_resolved.solver

    def test_equal_matrices_reuse_proof_with_new_rhs_and_stage_labels(self):
        expected = []
        for rhs, label in ((RHS, "predictor"), (((2.0,), (1.0,)), "corrector")):
            certificates = []
            expected.append(
                (
                    numerics.solve(MATRIX, rhs, self.policy, label, certificates),
                    certificates,
                )
            )
        same_matrix = tuple(tuple(value for value in row) for row in MATRIX)
        self.assertIsNot(same_matrix, MATRIX)
        with (
            codec._operation_contract_assets(),
            patch.object(arithmetic, "inverse", wraps=arithmetic.inverse
            ) as inverse,
            patch.object(arithmetic, "condition_bound", wraps=arithmetic.condition_bound
            ) as condition,
            patch.object(numerics, "residual_pass", wraps=numerics.residual_pass
            ) as residual,
        ):
            for matrix, rhs, label, reference in (
                (MATRIX, RHS, "predictor", expected[0]),
                (same_matrix, ((2.0,), (1.0,)), "corrector", expected[1]),
            ):
                certificates = []
                actual = numerics.solve(
                    matrix, rhs, self.policy, label, certificates
                )
                self.assertEqual((actual, certificates), reference)
                self.assertEqual(certificates[0]["block"], label)
            self.assertEqual(inverse.call_count, 1)
            self.assertEqual(condition.call_count, 1)
            self.assertEqual(residual.call_count, 2)

    def test_changed_coefficient_and_conditioning_limit_require_fresh_proof(self):
        admitted = replace(self.policy, conditioning_limit=2.0)
        strict = replace(self.policy, conditioning_limit=math.nextafter(2.0, 0.0))
        with (
            codec._operation_contract_assets(),
            patch.object(arithmetic, "condition_bound", wraps=arithmetic.condition_bound
            ) as condition,
        ):
            numerics.solve(MATRIX, RHS, admitted, "admitted", [])
            for label in ("strict stage", "retry strict stage"):
                with self.assertRaisesRegex(
                    ValueError, "conditioning limit exceeded: " + label
                ):
                    numerics.solve(MATRIX, RHS, strict, label, [])
            changed = ((math.nextafter(3.0, math.inf), 1.0), (1.0, 3.0))
            numerics.solve(changed, RHS, self.policy, "changed coefficient", [])
            self.assertEqual(condition.call_count, 4)

    def test_warm_preparation_retains_zero_tolerance_and_subnormal_residual_failures(
        self,
    ):
        zero = replace(self.policy, absolute_tolerance=0.0, relative_tolerance=0.0)
        with (
            codec._operation_contract_assets(),
            patch.object(arithmetic, "inverse", wraps=arithmetic.inverse
            ) as inverse,
            patch.object(numerics, "residual_pass", wraps=numerics.residual_pass
            ) as residual,
        ):
            numerics.solve(((3.0,),), ((1.0,),), self.policy, "warm", [])
            for rhs, label in ((((1.0,),), "one third"), (((5e-324,),), "subnormal")):
                certificates = []
                with self.assertRaisesRegex(
                    ValueError, "residual tolerance failed: " + label
                ):
                    numerics.solve(((3.0,),), rhs, zero, label, certificates)
                self.assertEqual(certificates[0]["block"], label)
            numerics.solve(((3.0,),), ((3.0,),), zero, "exact RHS", [])
            self.assertEqual(inverse.call_count, 1)
            self.assertEqual(residual.call_count, 4)

    def test_singular_and_nonfinite_inputs_never_reuse_success_or_cache_failure(self):
        with (
            codec._operation_contract_assets(),
            patch.object(arithmetic, "inverse", wraps=arithmetic.inverse
            ) as inverse,
        ):
            numerics.solve(MATRIX, RHS, self.policy, "valid", [])
            for label in ("singular", "singular retry"):
                with self.assertRaisesRegex(ValueError, "singular"):
                    numerics.solve(
                        ((1.0, 1.0), (1.0, 1.0)), RHS, self.policy, label, []
                    )
            with self.assertRaises(ValueError):
                numerics.solve(
                    ((float("nan"), 1.0), (1.0, 3.0)), RHS, self.policy, "nonfinite", []
                )
            numerics.solve(MATRIX, RHS, self.policy, "valid again", [])
            self.assertEqual(inverse.call_count, 3)

    def test_direct_inverse_and_condition_checks_share_solve_facts(self):
        exact = numerics.exact_matrix(MATRIX)
        expected = numerics.inverse(exact)
        direct_certificate = numerics.condition(
            MATRIX, self.policy.conditioning_limit, "direct condition"
        )
        with (
            codec._operation_contract_assets(),
            patch.object(arithmetic, "inverse", wraps=arithmetic.inverse
            ) as inverse,
            patch.object(arithmetic, "condition_bound",
                wraps=arithmetic.condition_bound,
            ) as condition,
        ):
            # First callers are direct primitives, not the solve helper.
            self.assertEqual(numerics.inverse(exact), expected)
            self.assertEqual(
                numerics.condition(
                    MATRIX, self.policy.conditioning_limit, "direct condition"
                ),
                direct_certificate,
            )
            numerics.solve(MATRIX, RHS, self.policy, "solve", [])
            self.assertEqual(numerics.inverse(exact), expected)
            other = numerics.condition(
                MATRIX, self.policy.conditioning_limit, "another stage"
            )
            self.assertEqual(other["block"], "another stage")
            self.assertEqual(
                other["condition_upper_squared"],
                direct_certificate["condition_upper_squared"],
            )
            self.assertEqual(inverse.call_count, 1)
            self.assertEqual(condition.call_count, 1)

    def test_analytic_residual_reuses_the_current_points_exact_hodge_inverse(self):
        graph = GRCV4Graph(
            ("a", "b", "c"),
            (OrientedEdge("ab", "a", "b"), OrientedEdge("bc", "b", "c")),
        )
        before, backend = ci_fixture(
            "A", graph=graph, C=(3.0, 1.0, 2.0), W=(1.1, 0.7)
        )
        cold_point = CandidateACurrent(before, backend)
        expected = _analytic_residual(cold_point, cold_point.current)
        exact_hodge = numerics.exact_matrix(before.geometry.one_form_hodge.matrix)
        ordinary_inverse = arithmetic.inverse
        hodge_calls = []

        def inverse(matrix):
            if matrix == exact_hodge:
                hodge_calls.append(matrix)
            return ordinary_inverse(matrix)

        with (
            codec._operation_contract_assets() as operation,
            patch.object(arithmetic, "inverse", side_effect=inverse),
        ):
            point = CandidateACurrent(before, backend)
            self.assertIsNotNone(operation.matrix_facts.find(exact_hodge))
            self.assertEqual(len(hodge_calls), 1)
            for _ in range(2):
                self.assertEqual(_analytic_residual(point, point.current), expected)
            self.assertEqual(len(hodge_calls), 1)

    def test_inverse_reuse_never_adds_a_conditioning_policy(self):
        # Exact elimination also serves non-SPD proof blocks and blocks whose
        # condition number exceeds a physical solver's declared limit.
        matrices = (
            ((0.0, 1.0), (1.0, 0.0)),
            ((1.0, 2.0), (0.0, 1.0)),
            ((1.0, 0.0), (0.0, 1e-100)),
        )
        expected = [numerics.inverse(numerics.exact_matrix(m)) for m in matrices]
        with (
            codec._operation_contract_assets(),
            patch.object(arithmetic, "inverse", wraps=arithmetic.inverse
            ) as inverse,
            patch.object(arithmetic, "condition_bound",
                wraps=arithmetic.condition_bound,
            ) as condition,
        ):
            for matrix, reference in zip(matrices, expected, strict=True):
                exact = numerics.exact_matrix(matrix)
                self.assertEqual(numerics.inverse(exact), reference)
                self.assertEqual(numerics.inverse(exact), reference)
            self.assertEqual(inverse.call_count, len(matrices))
            self.assertEqual(condition.call_count, 0)
            for label in ("strict direct", "strict direct retry"):
                with self.assertRaisesRegex(
                    ValueError, "conditioning limit exceeded: " + label
                ):
                    numerics.condition(matrices[-1], 2.0, label)
            self.assertEqual(condition.call_count, 2)
            self.assertEqual(inverse.call_count, len(matrices))

    def test_interval_midpoint_reuse_keeps_enclosure_admission_fresh(self):
        narrow = ((_Interval(Fraction(7, 4), Fraction(9, 4)),),)
        wide = ((_Interval(Fraction(1), Fraction(3)),),)
        unresolved = ((_Interval(Fraction(0), Fraction(4)),),)
        expected_narrow, expected_wide = _iinverse(narrow), _iinverse(wide)
        with (
            codec._operation_contract_assets(),
            patch.object(arithmetic, "inverse", wraps=arithmetic.inverse
            ) as inverse,
        ):
            self.assertEqual(_iinverse(narrow), expected_narrow)
            self.assertEqual(_iinverse(wide), expected_wide)
            self.assertLess(expected_wide[0][0].lo, expected_narrow[0][0].lo)
            self.assertGreater(expected_wide[0][0].hi, expected_narrow[0][0].hi)
            for _ in range(2):
                with self.assertRaisesRegex(CIStageError, "enclosure is unresolved"):
                    _iinverse(unresolved)
            self.assertEqual(inverse.call_count, 1)

    def test_condition_facts_do_not_supply_an_inverse(self):
        with (
            codec._operation_contract_assets() as operation,
            patch.object(arithmetic, "inverse", wraps=arithmetic.inverse
            ) as inverse,
        ):
            exact = numerics.exact_matrix(MATRIX)
            numerics.condition(MATRIX, self.policy.conditioning_limit, "only proof")
            self.assertIsNone(operation.matrix_facts.find(exact))
            numerics.inverse(exact)
            numerics.inverse(exact)
            self.assertEqual(inverse.call_count, 1)

    def test_facts_are_immutable_and_inverse_storage_is_bounded(self):
        with (
            codec._operation_contract_assets() as operation,
            patch.object(arithmetic, "inverse", wraps=arithmetic.inverse
            ) as inverse,
        ):
            exact = ((Fraction(1),),)
            result = numerics.inverse(exact)
            fact = operation.matrix_facts.find(exact)
            with self.assertRaises(FrozenInstanceError):
                fact.inverse = ()
            with self.assertRaises(TypeError):
                result[0][0] = 0
            for coefficient in range(2, _MAX_MATRIX_FACTS + 2):
                numerics.inverse(((Fraction(coefficient),),))
            numerics.inverse(((Fraction(_MAX_MATRIX_FACTS + 1),),))
            self.assertEqual(inverse.call_count, _MAX_MATRIX_FACTS + 1)
            numerics.inverse(exact)
            self.assertEqual(inverse.call_count, _MAX_MATRIX_FACTS + 2)

    def test_inverse_and_condition_facts_share_one_eviction_budget(self):
        with (
            codec._operation_contract_assets() as operation,
            patch.object(arithmetic, "inverse", wraps=arithmetic.inverse
            ) as inverse,
            patch.object(arithmetic, "condition_bound",
                wraps=arithmetic.condition_bound,
            ) as condition,
        ):
            count = _MAX_MATRIX_FACTS // 2
            for coefficient in range(1, count + 1):
                exact = ((Fraction(coefficient),),)
                numerics.inverse(exact)
                numerics.condition_bound(exact, 2.0, "proof")
            first = ((Fraction(1),),)
            numerics.inverse(((Fraction(count + 1),),))
            self.assertIsNone(operation.matrix_facts.find(first))
            fact = operation.matrix_facts.find(first, Fraction(2))
            with self.assertRaises(FrozenInstanceError):
                fact.condition_upper_squared = Fraction(0)
            # A surviving conditioning proof does not imply an inverse is cached.
            numerics.condition_bound(first, 2.0, "same condition")
            self.assertEqual(condition.call_count, count)
            numerics.inverse(first)
            self.assertEqual(inverse.call_count, count + 2)

    def test_nested_failed_and_unscoped_calls_have_independent_lifetimes(self):
        with patch.object(arithmetic, "inverse", wraps=arithmetic.inverse
        ) as inverse:
            with codec._operation_contract_assets() as outer:
                numerics.solve(MATRIX, RHS, self.policy, "outer", [])
                with (
                    self.assertRaisesRegex(RuntimeError, "abort"),
                    codec._operation_contract_assets(),
                ):
                    numerics.solve(MATRIX, RHS, self.policy, "inner", [])
                    raise RuntimeError("abort")
                self.assertIs(codec._OPERATION_CONTEXT.get(), outer)
                numerics.solve(MATRIX, RHS, self.policy, "outer again", [])
            self.assertIsNone(codec._OPERATION_CONTEXT.get())
            with codec._operation_contract_assets():
                numerics.solve(MATRIX, RHS, self.policy, "new operation", [])
            numerics.solve(MATRIX, RHS, self.policy, "unscoped", [])
            numerics.solve(MATRIX, RHS, self.policy, "unscoped again", [])
            self.assertEqual(inverse.call_count, 5)

    def test_threads_do_not_share_preparations(self):
        barrier = Barrier(2)

        def prepare(_):
            with codec._operation_contract_assets():
                first = numerics.inverse(numerics.exact_matrix(MATRIX))
                barrier.wait(timeout=10)
                second = numerics.inverse(numerics.exact_matrix(MATRIX))
                self.assertIs(first, second)
                return first

        with (
            patch.object(arithmetic, "inverse", wraps=arithmetic.inverse
            ) as inverse,
            ThreadPoolExecutor(max_workers=2) as pool,
        ):
            first, second = pool.map(prepare, range(2))
        self.assertIsNot(first, second)
        self.assertEqual(inverse.call_count, 2)
        self.assertIsNone(codec._OPERATION_CONTEXT.get())


if __name__ == "__main__":
    unittest.main()

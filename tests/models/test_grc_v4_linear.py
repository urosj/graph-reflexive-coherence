"""Matrix reuse preserves numerical proofs, per-RHS checks and scope isolation."""

import math
import unittest
from concurrent.futures import ThreadPoolExecutor
from dataclasses import FrozenInstanceError, replace
from threading import Barrier
from unittest.mock import patch

from pygrc.models import grc_v4_candidate_c as numerical
from pygrc.models import grc_v4_codec as codec
from tests.models.test_grc_v4_candidate_c import current_fixture

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
                    numerical._c_solve(MATRIX, rhs, self.policy, label, certificates),
                    certificates,
                )
            )
        same_matrix = tuple(tuple(value for value in row) for row in MATRIX)
        self.assertIsNot(same_matrix, MATRIX)
        with (
            codec._operation_contract_assets(),
            patch.object(
                numerical, "_c_inverse", wraps=numerical._c_inverse
            ) as inverse,
            patch.object(
                numerical, "_c_condition_bound", wraps=numerical._c_condition_bound
            ) as condition,
            patch.object(
                numerical, "_c_residual_pass", wraps=numerical._c_residual_pass
            ) as residual,
        ):
            for matrix, rhs, label, reference in (
                (MATRIX, RHS, "predictor", expected[0]),
                (same_matrix, ((2.0,), (1.0,)), "corrector", expected[1]),
            ):
                certificates = []
                actual = numerical._c_solve(
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
            patch.object(
                numerical, "_c_condition_bound", wraps=numerical._c_condition_bound
            ) as condition,
        ):
            numerical._c_solve(MATRIX, RHS, admitted, "admitted", [])
            for label in ("strict stage", "retry strict stage"):
                with self.assertRaisesRegex(
                    ValueError, "conditioning limit exceeded: " + label
                ):
                    numerical._c_solve(MATRIX, RHS, strict, label, [])
            changed = ((math.nextafter(3.0, math.inf), 1.0), (1.0, 3.0))
            numerical._c_solve(changed, RHS, self.policy, "changed coefficient", [])
            self.assertEqual(condition.call_count, 4)

    def test_warm_preparation_retains_zero_tolerance_and_subnormal_residual_failures(
        self,
    ):
        zero = replace(self.policy, absolute_tolerance=0.0, relative_tolerance=0.0)
        with (
            codec._operation_contract_assets(),
            patch.object(
                numerical, "_c_inverse", wraps=numerical._c_inverse
            ) as inverse,
            patch.object(
                numerical, "_c_residual_pass", wraps=numerical._c_residual_pass
            ) as residual,
        ):
            numerical._c_solve(((3.0,),), ((1.0,),), self.policy, "warm", [])
            for rhs, label in ((((1.0,),), "one third"), (((5e-324,),), "subnormal")):
                certificates = []
                with self.assertRaisesRegex(
                    ValueError, "residual tolerance failed: " + label
                ):
                    numerical._c_solve(((3.0,),), rhs, zero, label, certificates)
                self.assertEqual(certificates[0]["block"], label)
            numerical._c_solve(((3.0,),), ((3.0,),), zero, "exact RHS", [])
            self.assertEqual(inverse.call_count, 1)
            self.assertEqual(residual.call_count, 4)

    def test_singular_and_nonfinite_inputs_never_reuse_success_or_cache_failure(self):
        with (
            codec._operation_contract_assets(),
            patch.object(
                numerical, "_c_inverse", wraps=numerical._c_inverse
            ) as inverse,
        ):
            numerical._c_solve(MATRIX, RHS, self.policy, "valid", [])
            for label in ("singular", "singular retry"):
                with self.assertRaisesRegex(ValueError, "singular"):
                    numerical._c_solve(
                        ((1.0, 1.0), (1.0, 1.0)), RHS, self.policy, label, []
                    )
            with self.assertRaises(ValueError):
                numerical._c_solve(
                    ((float("nan"), 1.0), (1.0, 3.0)), RHS, self.policy, "nonfinite", []
                )
            numerical._c_solve(MATRIX, RHS, self.policy, "valid again", [])
            self.assertEqual(inverse.call_count, 3)

    def test_preparations_are_immutable_and_storage_is_bounded(self):
        with (
            codec._operation_contract_assets(),
            patch.object(
                numerical, "_c_inverse", wraps=numerical._c_inverse
            ) as inverse,
        ):
            first = numerical._c_prepare_matrix(
                ((1.0,),), self.policy.conditioning_limit, "first"
            )
            with self.assertRaises(FrozenInstanceError):
                first.condition_upper_squared = 0
            with self.assertRaises(TypeError):
                first.inverse[0][0] = 0
            for coefficient in range(2, 10):
                numerical._c_prepare_matrix(
                    ((float(coefficient),),), self.policy.conditioning_limit, "trial"
                )
            numerical._c_prepare_matrix(
                ((9.0,),), self.policy.conditioning_limit, "recent"
            )
            self.assertEqual(inverse.call_count, 9)
            numerical._c_prepare_matrix(
                ((1.0,),), self.policy.conditioning_limit, "evicted"
            )
            self.assertEqual(inverse.call_count, 10)

    def test_nested_failed_and_unscoped_calls_have_independent_lifetimes(self):
        with patch.object(
            numerical, "_c_inverse", wraps=numerical._c_inverse
        ) as inverse:
            with codec._operation_contract_assets() as outer:
                numerical._c_solve(MATRIX, RHS, self.policy, "outer", [])
                with (
                    self.assertRaisesRegex(RuntimeError, "abort"),
                    codec._operation_contract_assets(),
                ):
                    numerical._c_solve(MATRIX, RHS, self.policy, "inner", [])
                    raise RuntimeError("abort")
                self.assertIs(codec._OPERATION_CONTEXT.get(), outer)
                numerical._c_solve(MATRIX, RHS, self.policy, "outer again", [])
            self.assertIsNone(codec._OPERATION_CONTEXT.get())
            with codec._operation_contract_assets():
                numerical._c_solve(MATRIX, RHS, self.policy, "new operation", [])
            numerical._c_solve(MATRIX, RHS, self.policy, "unscoped", [])
            numerical._c_solve(MATRIX, RHS, self.policy, "unscoped again", [])
            self.assertEqual(inverse.call_count, 5)

    def test_threads_do_not_share_preparations(self):
        barrier = Barrier(2)

        def prepare(_):
            with codec._operation_contract_assets():
                first = numerical._c_prepare_matrix(
                    MATRIX, self.policy.conditioning_limit, "thread"
                )
                barrier.wait(timeout=10)
                second = numerical._c_prepare_matrix(
                    MATRIX, self.policy.conditioning_limit, "thread again"
                )
                self.assertIs(first, second)
                return first

        with (
            patch.object(
                numerical, "_c_inverse", wraps=numerical._c_inverse
            ) as inverse,
            ThreadPoolExecutor(max_workers=2) as pool,
        ):
            first, second = pool.map(prepare, range(2))
        self.assertIsNot(first, second)
        self.assertEqual(inverse.call_count, 2)
        self.assertIsNone(codec._OPERATION_CONTEXT.get())


if __name__ == "__main__":
    unittest.main()

"""The matrix API owns preparation, policy, and strict arithmetic boundaries."""

import ast
import unittest
from dataclasses import replace
from fractions import Fraction
from pathlib import Path
from random import Random
from types import SimpleNamespace
from unittest.mock import patch

from pygrc.models import _grc_v4_matrix as arithmetic
from pygrc.models import grc_v4_codec as codec
from pygrc.models import grc_v4_numerics as numerics
from pygrc.models.grc_v4_candidate_c import CandidateCStageError
from pygrc.models.grc_v4_linear import _MatrixContinuation
from tests.models.test_grc_v4_candidate_c import current_fixture
from tests.models.test_grc_v4_generic_lifecycle import FAMILIES, fixture, model
from tests.models.test_grc_v4_lifecycle import request

MATRIX = ((3.0, 1.0), (1.0, 3.0))
RHS = ((1.0,), (2.0,))


class MatrixAPITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy = current_fixture().geometry.reference.profile.params_resolved.solver

    def test_exact_psd_certificate_matches_full_inertia_at_boundaries(self):
        # Exact zero pivots, near-boundary negatives, and arbitrary symmetric
        # rationals must have the same PSD decision as full signed inertia.
        epsilon = Fraction(1, 2**80)
        matrices = (
            ((Fraction(), Fraction()), (Fraction(), Fraction())),
            ((Fraction(1), Fraction(1)), (Fraction(1), Fraction(1))),
            ((Fraction(1), Fraction(1)), (Fraction(1), 1 - epsilon)),
            ((Fraction(), Fraction(1)), (Fraction(1), Fraction())),
            ((Fraction(), Fraction(), Fraction()),
             (Fraction(), Fraction(1), Fraction()),
             (Fraction(), Fraction(), Fraction())),
        )
        for matrix in matrices:
            self.assertEqual(
                arithmetic._positive_semidefinite(matrix),
                arithmetic.inertia(matrix)[0] == 0,
            )
        rng = Random(711)
        for n in range(1, 7):
            for _ in range(100):
                rows = [[Fraction() for _ in range(n)] for _ in range(n)]
                for i in range(n):
                    for j in range(i, n):
                        value = Fraction(rng.randrange(-3, 4), rng.randrange(1, 5))
                        rows[i][j] = rows[j][i] = value
                matrix = tuple(map(tuple, rows))
                self.assertEqual(
                    arithmetic._positive_semidefinite(matrix),
                    arithmetic.inertia(matrix)[0] == 0,
                )

    def test_automatic_and_fresh_modes_keep_rhs_and_certificates_fresh(self):
        for reuse, count in (
            (numerics.MatrixReuse.AUTOMATIC, 1),
            (numerics.MatrixReuse.FRESH, 2),
        ):
            with (
                self.subTest(reuse=reuse),
                numerics.matrix_operation(reuse=reuse),
                patch.object(
                    arithmetic, "inverse", wraps=arithmetic.inverse
                ) as inverse,
                patch.object(
                    arithmetic, "condition_bound", wraps=arithmetic.condition_bound
                ) as condition,
                patch.object(
                    numerics, "residual_pass", wraps=numerics.residual_pass
                ) as residual,
                patch.object(
                    numerics,
                    "_condition_certificate",
                    wraps=numerics._condition_certificate,
                ) as certificate,
            ):
                certificates = []
                first = numerics.solve(MATRIX, RHS, self.policy, "first", certificates)
                second = numerics.solve(
                    MATRIX, ((2.0,), (1.0,)), self.policy, "second", certificates
                )
                self.assertNotEqual(first, second)
                self.assertEqual(
                    (inverse.call_count, condition.call_count), (count, count)
                )
                self.assertEqual((residual.call_count, certificate.call_count), (2, 2))
                self.assertEqual(
                    [c["block"] for c in certificates], ["first", "second"]
                )

    def test_policy_inherits_across_scopes_without_sharing_facts(self):
        exact = numerics.exact_matrix(MATRIX)
        with numerics.matrix_operation(reuse=numerics.MatrixReuse.FRESH):
            outer = codec._OPERATION_CONTEXT.get()
            with numerics.matrix_operation():
                inner = codec._OPERATION_CONTEXT.get()
                self.assertIsNot(inner, outer)
                self.assertIs(inner.matrix_facts.reuse, numerics.MatrixReuse.FRESH)
                self.assertIsNot(numerics.inverse(exact), numerics.inverse(exact))
            self.assertIs(codec._OPERATION_CONTEXT.get(), outer)
            with numerics.matrix_operation(reuse=numerics.MatrixReuse.AUTOMATIC):
                self.assertIs(numerics.inverse(exact), numerics.inverse(exact))
            self.assertIs(outer.matrix_facts.reuse, numerics.MatrixReuse.FRESH)
        self.assertIsNone(codec._OPERATION_CONTEXT.get())

    def test_fresh_policy_cannot_use_seeded_facts_or_retain_history(self):
        exact = numerics.exact_matrix(MATRIX)
        with numerics.matrix_operation():
            numerics.solve(MATRIX, RHS, self.policy, "warm", [])
            continuation = codec._OPERATION_CONTEXT.get().matrix_facts.retain(
                exact, exact, Fraction(self.policy.conditioning_limit)
            )
        self.assertEqual(len(continuation.facts), 2)
        with (
            numerics.matrix_operation(reuse=numerics.MatrixReuse.FRESH),
            patch.object(arithmetic, "inverse", wraps=arithmetic.inverse) as inverse,
        ):
            store = codec._OPERATION_CONTEXT.get().matrix_facts
            store.seed(continuation)
            for _ in range(2):
                numerics.solve(MATRIX, RHS, self.policy, "fresh", [])
            self.assertEqual(inverse.call_count, 2)
            self.assertEqual(
                store.retain(exact, exact, Fraction(self.policy.conditioning_limit)),
                _MatrixContinuation(),
            )

    def test_explicit_policy_rejects_booleans_and_unknown_modes(self):
        for invalid in (True, False, "fresh", object()):
            with (
                self.subTest(invalid=invalid),
                self.assertRaisesRegex(TypeError, "MatrixReuse"),
                numerics.matrix_operation(reuse=invalid),
            ):
                self.fail("invalid policy entered a scope")
        self.assertIsNone(codec._OPERATION_CONTEXT.get())

    def test_positive_solve_shares_inverse_but_checks_new_rhs_and_domain(self):
        exact = numerics.exact_matrix(MATRIX)
        rhs = (Fraction(1), Fraction(2))
        with (
            numerics.matrix_operation(),
            patch.object(arithmetic, "inverse", wraps=arithmetic.inverse) as inverse,
        ):
            result = numerics.solve_positive(exact, rhs)
            numerics.solve(MATRIX, RHS, self.policy, "physical", [])
            other = numerics.solve_positive(exact, tuple(reversed(rhs)))
            self.assertNotEqual(result, other)
            self.assertEqual(inverse.call_count, 1)
            for invalid in (((Fraction(-1),),), ((Fraction(0),),)):
                with self.assertRaisesRegex(numerics.MatrixError, "not positive"):
                    numerics.solve_positive(invalid, (Fraction(1),))
            with self.assertRaisesRegex(ValueError, "symmetric"):
                numerics.solve_positive(
                    ((Fraction(1), Fraction(1)), (Fraction(0), Fraction(1))), rhs
                )

    def test_warm_positive_solve_does_not_bypass_exact_rhs_check(self):
        exact = numerics.exact_matrix(MATRIX)
        rhs = (Fraction(1), Fraction(2))
        with numerics.matrix_operation():
            numerics.solve_positive(exact, rhs)
            with (
                patch.object(numerics, "inverse", return_value=exact),
                self.assertRaisesRegex(numerics.MatrixError, "residual failed"),
            ):
                numerics.solve_positive(exact, rhs)

    def test_fresh_mode_preserves_strict_limit_and_zero_tolerance_failures(self):
        with numerics.matrix_operation(reuse=numerics.MatrixReuse.FRESH):
            numerics.solve(MATRIX, RHS, self.policy, "admitted", [])
            with self.assertRaisesRegex(numerics.MatrixError, "conditioning limit"):
                numerics.solve(
                    MATRIX,
                    RHS,
                    replace(self.policy, conditioning_limit=1.5),
                    "strict",
                    [],
                )
            with self.assertRaisesRegex(numerics.MatrixError, "residual tolerance"):
                numerics.solve(
                    ((3.0,),),
                    ((1.0,),),
                    replace(
                        self.policy, absolute_tolerance=0.0, relative_tolerance=0.0
                    ),
                    "strict RHS",
                    [],
                )
        self.assertIs(CandidateCStageError, numerics.MatrixError)

    def test_all_ten_public_realizations_match_explicit_fresh_calculation(self):
        for family in FAMILIES:
            with self.subTest(family=family):
                warm, fresh = model(family), model(family)
                for index in range(2):
                    command = request(fixture(family)[0].dt, f"matrix-api-{index}")
                    actual = warm.step_v4_input(command)
                    with numerics.matrix_operation(reuse=numerics.MatrixReuse.FRESH):
                        expected = fresh.step_v4_input(command)
                    self.assertTrue(actual.committed, actual.failure)
                    self.assertEqual(
                        actual.to_canonical_bytes(), expected.to_canonical_bytes()
                    )
                    self.assertEqual(warm.snapshot(), fresh.snapshot())
                    self.assertFalse(fresh._operation._owned.matrix_continuation.facts)


class MatrixAPIBoundaryTests(unittest.TestCase):
    def test_only_matrix_api_imports_arithmetic_implementation(self):
        root = Path(__file__).resolve().parents[2] / "src" / "pygrc" / "models"
        offenders = []
        for path in root.glob("*.py"):
            if path.name == "grc_v4_numerics.py":
                continue
            for node in ast.walk(ast.parse(path.read_text())):
                if isinstance(node, ast.ImportFrom):
                    backend_import = (node.module or "").endswith("_grc_v4_matrix")
                    backend_import |= any(
                        alias.name == "_grc_v4_matrix" for alias in node.names
                    )
                    if backend_import:
                        offenders.append((path.name, node.lineno))
                elif isinstance(node, ast.Import):
                    if any(
                        alias.name.endswith("_grc_v4_matrix") for alias in node.names
                    ):
                        offenders.append((path.name, node.lineno))
        self.assertEqual(
            offenders, [], "arithmetic must be reached through the matrix API"
        )

    def test_new_realization_cannot_silently_receive_no_continuation_policy(self):
        from pygrc.models.grc_v4_lifecycle import _step_matrix_continuation

        reference = SimpleNamespace(
            profile=SimpleNamespace(
                identity_payload=SimpleNamespace(realization="unhandled_realization")
            )
        )
        step = SimpleNamespace(
            inputs=SimpleNamespace(geometry=SimpleNamespace(reference=reference))
        )
        with numerics.matrix_operation(), self.assertRaises(AssertionError):
            _step_matrix_continuation(step)

    def test_old_candidate_matrix_entry_points_are_removed(self):
        from pygrc.models import grc_v4_candidate_c as candidate

        for name in (
            "_c_inverse",
            "_c_inverse_uncached",
            "_c_solve",
            "_c_condition",
            "_c_condition_bound",
            "_c_condition_bound_uncached",
        ):
            self.assertFalse(hasattr(candidate, name), name)
        self.assertNotIn("_backend", numerics.__all__)
        self.assertNotIn("_condition_certificate", numerics.__all__)


if __name__ == "__main__":
    unittest.main()

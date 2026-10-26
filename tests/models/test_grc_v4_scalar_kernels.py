"""Exact scalar reuse must not reuse rounding/admission decisions."""
from contextlib import contextmanager
from fractions import Fraction
import math
import unittest
from unittest.mock import patch

from pygrc.models import grc_v4_certification as cert
from pygrc.models import _grc_v4_matrix as matrix
from pygrc.models.grc_v4_exact import ExactBackend, exact_backend, exact_number, exact_rows


@contextmanager
def uncached_kernels():
    naive = lambda rows: tuple(tuple(exact_number(x) for x in row) for row in rows)
    original = cert._round_interval
    with patch.object(matrix, 'exact_rows', naive), patch.object(cert, 'exact_rows', naive), \
         patch.object(cert, '_round_interval', lambda lo, hi, cells: original(lo, hi, None)):
        yield


class ScalarKernelTests(unittest.TestCase):
    def test_exact_conversion_backends_mixed_types_and_changed_operands(self):
        for backend in ExactBackend:
            with self.subTest(backend=backend), exact_backend(backend):
                values = (0., -0., 1., 1, True, Fraction(1, 3),
                          math.nextafter(1., 2.), 2**-1074, -2**-1074,
                          float.fromhex('0x1.fffffffffffffp+1023'))
                for row in (values, tuple(reversed(values)), tuple(float(i) for i in range(5000))):
                    self.assertEqual(exact_rows((row,)), (tuple(exact_number(x) for x in row),))
                for value in (math.nan, math.inf, -math.inf):
                    with self.assertRaises((ValueError, OverflowError)):
                        exact_rows(((value,),))
                self.assertEqual(exact_rows(()), ())

    def test_conversion_is_bounded_and_discarded_per_call(self):
        import pygrc.models.grc_v4_exact as exact
        with exact_backend(ExactBackend.FLINT):
            with patch.object(exact, 'exact_number', wraps=exact.exact_number) as convert:
                exact_rows(((0., 1.) * 100,))
                self.assertEqual(convert.call_count, 2)
                exact_rows(((0., 1.),))
                self.assertEqual(convert.call_count, 4)
            with patch.object(exact, 'exact_number', wraps=exact.exact_number) as convert:
                exact_rows((tuple(range(4096)) + (4096, 4096, 0),))
                self.assertEqual(convert.call_count, 4098)

    def test_cells_ties_subnormals_overflow_and_fresh_containment(self):
        for backend in ExactBackend:
            with self.subTest(backend=backend), exact_backend(backend):
                q = exact_number
                cells = {}
                values = (0., 2**-1074, -2**-1074, 2**-1022,
                          1., math.nextafter(1., 2.), -1.,
                          float.fromhex('0x1.fffffffffffffp+1023'))
                for value in values:
                    x = q(value)
                    self.assertEqual(cert._round_interval(x, x, cells), value)
                    lo, hi, even = cert._rounding_cell(value)
                    for endpoint in (lo, hi):
                        # At odd cells, the shared boundary belongs to the even neighbour.
                        try:
                            expected = cert.round_interval(endpoint, endpoint)
                        except cert.CertificationInconclusive:
                            with self.assertRaises(cert.CertificationInconclusive):
                                cert._round_interval(endpoint, endpoint, cells)
                        else:
                            self.assertEqual(cert._round_interval(endpoint, endpoint, cells), expected)
                midpoint = q(1) + q(2)**-53
                for lo, hi in ((midpoint-q(2)**-200, midpoint+q(2)**-200),
                               (q(2)**1024, q(2)**1024)):
                    with self.assertRaises(cert.CertificationInconclusive):
                        cert._round_interval(lo, hi, cells)
                with self.assertRaises(ValueError):
                    cert._round_interval(q(2), q(1), cells)
                for i in range(5000):
                    cert._round_interval(q(i), q(i), cells)
                self.assertEqual(len(cells), 4096)

    def test_changed_dense_rhs_matches_exact_fraction_and_flint(self):
        a = ((2., .125), (.25, 3.))
        for rhs in (((1., 2.), (-3., .5)), ((1.25, 2.), (-3., .25))):
            with exact_backend(ExactBackend.PYTHON):
                expected = matrix.binary64_matrix(matrix.matmul(
                    matrix.inverse(matrix.exact_matrix(a)), matrix.exact_matrix(rhs)))
            with exact_backend(ExactBackend.FLINT):
                self.assertEqual(cert.rounded_solve(a, rhs), expected)
                with uncached_kernels():
                    self.assertEqual(cert.rounded_solve(a, rhs), expected)

    def test_two_changing_native_steps_match_uncached_kernels(self):
        from tests.models.test_grc_v4_os_pass_probe import before, compare_point
        from pygrc.models.grc_v4_step import ProvisionalCandidateCOSStep
        from pygrc.models.grc_v4_numerics import matrix_operation
        with exact_backend(ExactBackend.FLINT), cert.numerical_policy(cert.NumericalPolicy.CERTIFIED_ARB_256):
            expected_before = actual_before = before()
            for _ in range(2):
                with uncached_kernels(), matrix_operation():
                    expected = ProvisionalCandidateCOSStep(expected_before)
                with matrix_operation():
                    actual = ProvisionalCandidateCOSStep(actual_before)
                self.assertEqual(actual.next_inputs, expected.next_inputs)
                self.assertNotEqual(actual_before.current.C, actual.next_inputs.current.C)
                for field in ('predictor', 'corrector'):
                    compare_point(self, getattr(actual.os_pass, field), getattr(expected.os_pass, field))
                compare_point(self, actual.final, expected.final)
                self.assertEqual(actual.os_pass.residual, expected.os_pass.residual)
                expected_before, actual_before = expected.next_inputs, actual.next_inputs


if __name__ == '__main__':
    unittest.main()

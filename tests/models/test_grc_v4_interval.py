"""Certified CI interval kernels: enclosure, policy, and no-fallback pressure."""
from contextlib import contextmanager
from fractions import Fraction as Q
from itertools import product
import unittest
import importlib.util
from unittest.mock import patch
from pygrc.models import grc_v4_interval as iv
from pygrc.models import grc_v4_ci as ci
from pygrc.models.grc_v4_numerics import exact_backend, ExactBackend, numerical_policy, NumericalPolicy
from pygrc.models.grc_v4_certification import CertificationInconclusive
from pygrc.models.grc_v4_exact import exact_number

def rational(x):
    return Q(int(x.numerator),int(x.denominator))


@contextmanager
def selected():
    with exact_backend(ExactBackend.FLINT), numerical_policy(NumericalPolicy.CERTIFIED_ARB_256):
        yield


@unittest.skipUnless(importlib.util.find_spec('flint'), 'optional python-flint required')
class IntervalKernels(unittest.TestCase):
    def test_policy_and_dimensions_are_explicit(self):
        with self.assertRaises(ValueError):iv.inverse((((1,1),),))
        with selected():
            self.assertEqual(iv.inverse(()),())
            self.assertEqual(iv.matmul((),()),())
            with self.assertRaises(ValueError):iv.inverse((((1,1),(0,0)),))
            with self.assertRaises(ValueError):iv.matmul((((1,1),),),())
            with self.assertRaises(ValueError):iv.inverse((((2,1),),))

    def test_signed_interval_products_enclose_all_corners(self):
        a=(((Q(-2),Q(-1)),(Q(1,3),Q(1,2))),((Q(0),Q(1)),(Q(-1,7),Q(1,9))))
        b=(((Q(-1),Q(1)),),((Q(2),Q(3)),))
        with selected():out=iv.matmul(a,b)
        for choices in product((0,1),repeat=6):
            aa=[[a[i][j][choices[2*i+j]] for j in range(2)] for i in range(2)]
            bb=[b[i][0][choices[4+i]] for i in range(2)]
            for i in range(2):
                expected=sum(aa[i][j]*bb[j] for j in range(2))
                self.assertLessEqual(rational(out[i][0][0]),expected);self.assertGreaterEqual(rational(out[i][0][1]),expected)

    def test_inverse_contains_exact_points_without_exact_inverse_fallback(self):
        matrix=(((Q(2),Q(2)),(Q(1,10),Q(1,5))),((Q(-1,5),Q(-1,10)),(Q(3),Q(3))))
        with selected(),patch.object(ci.numerics,'inverse',side_effect=AssertionError('exact fallback')):
            out=ci._iinverse(tuple(tuple(ci._Interval(exact_number(lo),exact_number(hi)) for lo,hi in row) for row in matrix))
        for b,c in product(matrix[0][1],matrix[1][0]):
            det=6-b*c;expected=((3/det,-b/det),(-c/det,2/det))
            for i,j in product(range(2),repeat=2):
                self.assertLessEqual(rational(out[i][j].lo),expected[i][j]);self.assertGreaterEqual(rational(out[i][j].hi),expected[i][j])

    def test_singularity_and_uncertainty_fail_explicitly(self):
        with selected(),patch.object(ci.numerics,'inverse',side_effect=AssertionError('fallback')):
            for matrix in ((((0,0),),),(((0,1),),),(((1,1),(1,1)),((1,1),(1,1)))):
                with self.assertRaises(CertificationInconclusive):iv.inverse(matrix)

    def test_exact_legacy_route_remains_exact(self):
        point=((Q(2),Q(3)),(Q(-1),Q(4)))
        out=ci._iinverse(ci._im(point))
        self.assertEqual([[(x.lo,x.hi) for x in row] for row in out],
            [[(Q(4,11),Q(4,11)),(Q(-3,11),Q(-3,11))],[(Q(1,11),Q(1,11)),(Q(2,11),Q(2,11))]])

    def test_extreme_scale_and_signed_cancellation(self):
        for scale in (Q(1,2**1074),Q(1),Q(2**1023)):
            with selected():
                out=iv.matmul((((scale,scale),(-scale,-scale)),),(((1,1),),((1,1),)))
            self.assertLessEqual(out[0][0][0],0);self.assertGreaterEqual(out[0][0][1],0)

    def test_small_a_c_native_roots_preserve_selected_physical_values(self):
        from tests.models.test_grc_v4_ci import fixture
        for candidate in ('A','C'):
            before,backend=fixture(candidate)
            legacy=ci.CandidateCIRoot(before,backend)
            with selected():
                actual=ci.CandidateCIRoot(before,backend)
                residual=rational(actual.selected.residual_squared)
            self.assertEqual(actual.current,legacy.current)
            self.assertEqual(actual.selected.inputs.geometry,legacy.selected.inputs.geometry)
            self.assertEqual(actual.evaluations,legacy.evaluations)
            self.assertEqual(actual.identity,legacy.identity)
            self.assertLessEqual(residual,Q(1,10**22))


if __name__=='__main__':unittest.main()

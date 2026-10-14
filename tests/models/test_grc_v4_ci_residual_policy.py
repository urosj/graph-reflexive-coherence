"""CI analytic Hodge policy and nonlinear interval-image regressions."""
from dataclasses import replace
from fractions import Fraction as Q
import unittest
from unittest.mock import patch
from pygrc.models import grc_v4_ci as ci
from pygrc.models.grc_v4_candidate_a import CandidateACurrent
from pygrc.models.grc_v4_geometry import PhysicalFlux
from pygrc.models.grc_v4_exact import exact_number
from pygrc.models.grc_v4_certification import CertificationInconclusive
from tests.models.test_grc_v4_interval import selected, rational
from tests.models.test_grc_v4_ci import fixture


class ResidualPolicy(unittest.TestCase):
    def test_square_contains_signed_and_zero_crossing_images(self):
        with selected():
            for lo,hi in ((-3,2),(-3,-2),(2,3),(0,0),(-2,-2),(Q(-1,3),Q(2,7))):
                result=ci._isquare(ci._Interval(exact_number(lo),exact_number(hi)))
                for x in (lo,hi,(lo+hi)/2,0 if lo<=0<=hi else lo):
                    self.assertLessEqual(rational(result.lo),Q(x)**2)
                    self.assertGreaterEqual(rational(result.hi),Q(x)**2)
                if lo<=0<=hi:self.assertEqual(result.lo,0)

    def test_floor_boundary_and_underflow_tail(self):
        with selected():
            for lo,hi,floor in ((-2,0,1.),(-2,0,.5),(-1001,-999,2**-1074),(-2000,-1001,.5)):
                result=ci._ifloored_exp(ci._Interval(exact_number(lo),exact_number(hi)),floor)
                if hi < -999:self.assertEqual((result.lo,result.hi),(exact_number(floor),exact_number(floor)))
                else:
                    for x in (max(-1000,lo),hi):
                        lower,upper=ci._exp_bounds(exact_number(x))
                        self.assertLessEqual(result.lo,max(exact_number(floor),lower))
                        self.assertGreaterEqual(result.hi,max(exact_number(floor),upper))
            with self.assertRaises(ci.CIStageError):ci._ifloored_exp(ci._iv(0),0.)
            with self.assertRaises(ci.CIStageError):ci._ifloored_exp(ci._iv(1025),.5)

    def test_conservative_widening_cannot_lose_exact_residual(self):
        before,backend=fixture('A',C=(2.,2.),W=(1.,),changes={'candidate':
            {'alpha':0.,'beta':0.,'gamma':1.,'chi_A':.25,'zeta_A':.5}})
        with selected():
            point=CandidateACurrent(before,backend);j=PhysicalFlux(before.geometry.reference.graph,(1.,))
            original=ci._imm;calls=0
            def broader(a,b):
                nonlocal calls
                result=original(a,b);calls+=1
                if calls==4:
                    self.assertEqual((result[0][0].lo,result[0][0].hi),(0,0))
                    return ((ci._Interval(exact_number(-1),exact_number(1)),),)
                return result
            true=ci._analytic_residual(point,j)[1][0][0]
            with patch.object(ci,'_imm',broader):wide=ci._analytic_residual(point,j)[1][0][0]
            self.assertEqual((true.lo,true.hi),(0,0));self.assertLessEqual(wide.lo,0);self.assertGreaterEqual(wide.hi,0)

    def test_selected_hodge_dispatch_does_not_use_exact_inverse(self):
        # C avoids A's legitimate small WLS descriptor inverses; spy on the
        # actual common Hodge dispatch, not just on its standalone helper.
        before,_=fixture('C')
        with selected():
            point=ci._point(before,None)
            with patch.object(ci.numerics,'inverse',side_effect=AssertionError('exact Hodge fallback')):
                fj,fh=ci._analytic_residual(point,point.current)
            self.assertTrue(fj and fh)
            with (patch('pygrc.models.grc_v4_interval.inverse',side_effect=CertificationInconclusive('injected')),
                  self.assertRaises(CertificationInconclusive)):
                ci._analytic_residual(point,point.current)


if __name__=='__main__':unittest.main()

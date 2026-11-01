"""Finite, non-infinitesimal pressure on the Lipschitz proof; no D Gamma oracle."""
from pathlib import Path
import sys,unittest
from fractions import Fraction as F
ROOT=Path(__file__).resolve().parents[4];INV=ROOT/'implementation/investigations/grc9v4-constitutive-design'
sys.path[:0]=[str(ROOT/'src'),str(INV/'research'),str(INV/'evidence/spark-completion/review/constructive-candidate')]
from flint import arb,arb_mat,fmpq,ctx
from spark_completion_c_rg2b import CRG2bReference,trap_certificate,ball,maxnorm,PRECISION,TRAP_RADIUS
from spark_completion_positive import fixture,norm_upper

class FiniteDifferences(unittest.TestCase):
    def test_duration_32_uniform_inverse_obstruction_for_this_completion(self):
        # This concerns the auxiliary completed base map for the admissible
        # constant section gamma=I, not the physical trajectory or all possible
        # completions. At uniform C=a*1, its derivative on a Laplacian mode is
        # 1 - h*alpha(lambda)*(3*(a-2)^2-1-lambda/64), where
        # alpha(lambda)=lambda*(1+1/(3+4*lambda)). At duration 32, h=1/32.
        # Rayleigh(e_v-1/n) bounds lambda_max below; ||B^T B||inf bounds it
        # above. The exact bounds below put a zero derivative strictly inside
        # the retraction agreement box, ruling out a uniformly Lipschitz inverse
        # there. A zero derivative alone does not prove non-injectivity.
        with ctx.workprec(PRECISION):
            source,_,targets=fixture()
            for role,g in [('source',source),('target',targets['1']['graph'])]:
                m=CRG2bReference(g);degree=m.algebra['b'];ell=m.algebra['ell']
                low=degree*F(m.n,m.n-1);high=ell
                alpha=lambda x:x*(1+1/(3+4*x))
                curvature_low=32/alpha(high)+low/64
                curvature_high=32/alpha(low)+high/64
                u=max(abs(m.lo-2),abs(m.hi-2));maximum=3*u*u-1
                self.assertTrue(0<low<=high)
                self.assertTrue(0<curvature_low<=curvature_high<maximum)
                left=2+ball((curvature_low+1)/3).sqrt()
                right=2+ball((curvature_high+1)/3).sqrt()
                self.assertTrue(ball(m.lo)<left and right<ball(m.hi))
                print(role,'duration-32 critical uniform-resource interval',left.str(9),right.str(9),flush=True)

    def test_whole_trap_physical_segments_and_section_differences(self):
        # The norm is evaluated directly by its exact rational matrix. The
        # endpoints are at 90% of the declared ball, not infinitesimal probes.
        with ctx.workprec(PRECISION):
            _,_,targets=fixture();proof,_=trap_certificate(targets);m=CRG2bReference(targets['1']['graph'])
            c=m.vector(proof['center']);r=ball(TRAP_RADIUS);s=m.section(c)
            q,parts=m.return_lipschitz(c,r,s);max_ratio=arb(0)
            for k in range(m.n-1):
                v=arb_mat([[int(i==k)-int(i==m.n-1)]for i in range(m.n)])
                length=(v.transpose()*m.P*v)[0,0].sqrt().upper()
                scalar=F(str((r*9/10/length).lower().fmpq()));scale=2**160
                amplitude=F((scalar.numerator*scale)//scalar.denominator,scale)
                for sign in (-1,1):
                    delta=sign*ball(amplitude)*v;point=c+delta
                    dist=(delta.transpose()*m.P*delta)[0,0].sqrt()
                    self.assertGreater(dist,ball(F(89,100))*r);self.assertLess(dist,r)
                    t=m.section(point);difference=delta+t['read']['increment']-s['read']['increment']
                    after=(difference.transpose()*m.P*difference)[0,0].sqrt()
                    self.assertLess(after.upper(),q*dist.lower())
                    geometry=maxnorm(t['geometry']-s['geometry'])
                    self.assertLess(geometry,parts['section_lipschitz']*maxnorm(delta))
                    max_ratio=max(max_ratio,(after/dist).upper())
            print('Finite-segment maximum return ratio:',max_ratio.str(12),'proved bound:',q.str(12),flush=True)

if __name__=='__main__':unittest.main(verbosity=2)

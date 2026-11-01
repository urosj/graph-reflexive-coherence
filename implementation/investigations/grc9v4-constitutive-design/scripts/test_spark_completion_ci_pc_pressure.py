"""Additional nonstationary C_CI_PC controls independent of the campaign sources."""
import unittest
from unittest.mock import patch
import check_spark_completion_applicability_ci_pc as pc
from flint import arb, fmpq, ctx
from spark_completion_ci_pc import CCIPCReference, trap_certificate
from spark_completion_positive import fixture
from spark_completion_ci_campaign import retained


class NonstationaryPressure(unittest.TestCase):
    def setUp(self):
        self.prec=ctx.workprec(512);self.prec.__enter__()
        _,_,self.targets=fixture();self.m=CCIPCReference(self.targets['1']['graph']);m=self.m
        self.C=m.matrix([[m.q(1)+m.q(i,32) for _ in range(1)] for i in range(m.n)])
        self.Z=m.zero()
        for i,j in m.pairs:
            self.Z[i,j]=m.q((-1)**(i+j),2**16);self.Z[j,i]=self.Z[i,j]

    def tearDown(self): self.prec.__exit__(None,None,None)

    def test_all_derivative_directions_at_nonzero_carrier_and_current(self):
        m=self.m;C,Z=self.C,self.Z;h=m.q(1,2**35)
        box=m.matrix([[arb(C[i,0].fmpq(),fmpq(1,2**25))] for i in range(m.n)])
        zb=m.zero()
        for i,j in m.pairs:
            zb[i,j]=arb(Z[i,j].fmpq(),fmpq(1,2**25));zb[j,i]=zb[i,j]
        p=m.partials(box,zb);start=m.ccipc_step(C,Z)
        self.assertGreater(max(abs(x).lower() for x in start['read']['selected']['current'].entries()),0)
        for k in range(m.n-1):
            v=m.matrix([[int(i==k)-int(i==m.n-1)] for i in range(m.n)])
            end=m.ccipc_step(C+h*v,Z);quotient=(end['after']-start['after'])/h
            predicted=p['CC']*v
            self.assertTrue(all(predicted[i,0].contains(quotient[i,0]) for i in range(m.n)))
            dz=(end['carrier_after']-start['carrier_after'])/h
            predicted=(1-m.decay)*p['SC']*v
            self.assertTrue(all(predicted[k,0].contains(dz[i,j]*(1 if i==j else arb(2).sqrt()))
                                for k,(i,j) in enumerate(m.pairs)))
        for k,(i,j) in enumerate(m.pairs):
            v=m.zero();v[i,j]=1;v[j,i]=1;scale=1 if i==j else arb(2).sqrt()
            end=m.ccipc_step(C,Z+h*v);quotient=(end['after']-start['after'])/h
            self.assertTrue(all((p['CZ'][r,k]*scale).contains(quotient[r,0]) for r in range(m.n)))
            dz=(end['carrier_after']-start['carrier_after'])/h
            for r,(a,b) in enumerate(m.pairs):
                predicted=(1-m.decay)*p['SZ'][r,k]*scale+(m.decay*scale if r==k else 0)
                self.assertTrue(predicted.contains(dz[a,b]*(1 if a==b else arb(2).sqrt())))

    def test_wrong_writer_stage_and_frozen_geometry_have_strict_separation(self):
        m=self.m;C,Z=self.C,self.Z;step=m.ccipc_step(C,Z)
        correct=step['read'];wrong=m.ccipc_read(step['after'],Z)
        separation=lambda A,B:max(abs(x-y).lower() for x,y in zip(A.entries(),B.entries()))
        self.assertGreater(separation(correct['source'],wrong['source']),0)
        fixed=m.ccipc_read(C,m.zero())
        self.assertGreater(separation(correct['selected']['current'],fixed['selected']['current']),0)
        H=correct['geometry']
        j0=-m.q(1,1024)*m.Bt*(m.q(1,64)*m.B*m.Bt*C-m.site(C))
        y=(m.q(3,4)*m.I+H*m.Le).solve(j0)
        self.assertGreater(separation(correct['selected']['current'],j0+y/4),0)

    def test_unweighted_carrier_bound_does_not_pass_the_declared_proof(self):
        old=retained('SC2PositiveCandidate.json.xz')['checks']['trap']
        with patch('spark_completion_ci_pc.TRAP_WEIGHT',1),self.assertRaises(ValueError):
            trap_certificate({**self.targets['1'],'charts':self.targets},old)

    def test_composition_discriminates_ci_pc_and_wrong_half_gain(self):
        from spark_completion_pc import CPCReference
        from spark_completion_ci import CCIReference
        m=self.m;C,Z=self.C,self.Z;root=m.ccipc_read(C,Z)
        separated=lambda A,B:any(not x.overlaps(y)for x,y in zip(A.entries(),B.entries()))
        pc=CPCReference(self.targets['1']['graph']).pc_read(C,Z)
        ci=CCIReference(self.targets['1']['graph']).root(C)
        self.assertTrue(separated(root['selected']['current'],pc['selected']['current']))
        self.assertTrue(separated(root['selected']['current'],ci['selected']['current']))
        wrong=m.I+Z/2+root['source']/4
        self.assertTrue(separated(root['geometry'],wrong))
        zero=m.ccipc_read(C,m.zero())
        self.assertFalse(separated(zero['selected']['current'],ci['selected']['current']))
        self.assertGreater(max(abs(x).lower()for x in zero['source'].entries()),0)
        self.assertTrue(separated(m.advance(C,m.zero(),zero)[1],m.zero()))
        with patch('spark_completion_ci_pc.ROOT_NEWTON_LIMIT',1),self.assertRaises(ValueError):
            m.ccipc_read(C,Z)


if __name__=='__main__': unittest.main()

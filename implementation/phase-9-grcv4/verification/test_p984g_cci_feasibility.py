"""Focused allocation, operator, domain and first-step pressure."""
from copy import deepcopy
import unittest
from unittest.mock import patch
from flint import arb, arb_mat
import p984g_cci_feasibility as p


class FeasibilityMath(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old,cls.target,cls.transfer,cls.declaration=p.companion()

    def test_exact_constraints_and_maximin_choice(self):
        expected=[('core','18',['-16','-16','-16']),
            ('extra/1/1','6',['-12','0','0']),('extra/2/1','6',['0','-12','0']),
            ('extra/3/1','6',['0','0','-14']),('extra/3/2','0',['0','0','2'])]
        for role in ('current','reset'):
            rows=p.leading_constraints(self.target,role)
            self.assertEqual([(r['node'],r['offset'],r['coefficients']) for r in rows],expected)
            def margin(shares):
                return min(p.q(r['offset'])+sum((p.q(a)*p.q(b) for a,b in zip(r['coefficients'],shares)),p.q(0)) for r in rows)
            self.assertEqual(margin(p.SHARES),p.q(3)/4)
            self.assertEqual(margin(('1/2','1/4','1/4')),0)
            self.assertLess(margin(('9/16','3/16','1/4')),0)
            for a3 in (p.q(0),p.q(1)/4,p.q(3)/8,p.q(1)/2,p.q(1)):
                self.assertLessEqual(min(6-14*a3,2*a3),p.q(3)/4)

    def test_lawful_transfer_and_new_identity(self):
        self.assertNotEqual(self.declaration['event_id'],self.old['event_id'])
        self.assertNotEqual(self.declaration['target_graph_digest'],self.old['target']['graph']['graph_digest'])
        self.assertEqual(self.old['source'],p.read(p.prior.PREPARED)['source'])
        self.assertEqual([sum(col,p.q(0)) for col in zip(*self.transfer)],[p.q(1)]*100)
        for role in ('current','reset'):
            c=self.target['roles'][role]['C']
            self.assertEqual(sum((p.q(x) for x in c),p.q(0)),200)
            self.assertEqual(c[99:104],[0]*5)
            self.assertEqual(c[104:],[.625,.625,.75])
        for shares in (('1/2','1/2','1/2'),('-1','1','1'),('1',)):
            with self.assertRaises(ValueError):
                p.transfer_matrix([0],['x/satellite/'+str(i) for i in (1,2,3)],'x',0,shares)
        with self.assertRaises(ValueError):
            p.transfer_matrix([0,1],['x/satellite/'+str(i) for i in (1,2,3)],'x',0,p.SHARES)

    def test_full_edge_current_matches_vertex_formula_not_baseline(self):
        # Nonzero Read-Back and a cyclic nonuniform graph; amplified legal beta
        # makes omitting response or reversing continuity sign distinguishable.
        with p.staged.ctx.workprec(p.iv.BITS):
            b=p.iv.matrix([[1,0,-1,1],[ -1,1,0,0],[0,-1,1,0],[0,0,0,-1]])
            c=p.iv.matrix([[2],[3],[1],[4]]);t=p.iv.a('11/10')
            cp=dict(eta_C=1,kappa_Phi_C=1,zeta_C=.125,chi_C=2,tau_C=.5)
            d=b.transpose()*b; ident=p.iv.eye(4)
            j0=-t*d*b.transpose()*c
            response=(ident+p.iv.a(cp['tau_C'])*t*d).inv()
            full=(ident-p.iv.a('1/4')*response).solve(j0)
            rate=p.reference_divergence(b,c,cp,t)
            for i in range(4):self.assertTrue(rate[i,0].overlaps((b*full)[i,0]))
            self.assertTrue(any(not rate[i,0].overlaps((b*j0)[i,0]) for i in range(4)))
            self.assertTrue(any(not rate[i,0].overlaps(-(b*full)[i,0]) for i in range(4)))

    def test_bad_resource_envelope_and_uncertified_gradient_rejected(self):
        with p.staged.ctx.workprec(p.iv.BITS):
            c=self.target['roles']['current']['C']
            with self.assertRaisesRegex(ValueError,'conserved-200'):
                p.step_bound(self.target,'current',[p.iv.a(x+1) for x in c])
            # Conserve mass but exceed the predeclared 5/4 gradient envelope.
            changed=[p.iv.a(x) for x in c];changed[0]+=100;changed[1]=p.iv.a(0)
            changed[2]-=98
            with self.assertRaises(ValueError):p.step_bound(self.target,'current',changed,p.q(5)/4)
            concentrated=[p.iv.a(0) for _ in c];concentrated[0]=p.iv.a(200)
            with self.assertRaisesRegex(ValueError,'gradient envelope'):
                p.step_bound(self.target,'current',concentrated,p.q(5)/4)

    def test_old_boundary_is_not_silently_a_positive_witness(self):
        with p.staged.ctx.workprec(p.iv.BITS):
            result=p.step_bound(self.old['target'],'current')
        self.assertFalse(result['all_positive'])
        self.assertLess(p.q(result['minimum_lower']),0)


class RetainedFeasibility(unittest.TestCase):
    def test_recomputed_bounds_and_fail_closed_record(self):
        value=p.check()
        p.check_retained(value)
        self.assertFalse(value['event_pair']['reset_evolves'])
        for role in ('current','reset'):
            before=p.read(p.prior.PREPARED)['source']['roles'][role]['C']
            after=value['companion']['source_roles'][role]['C']
            self.assertEqual([i for i,(x,y) in enumerate(zip(before,after)) if x!=y],[0,60])
            self.assertEqual(sum((p.q(x) for x in after),p.q(0)),200)
        for row in value['cases']:
            for stage in ('initial_transfer','fresh_postbeat_transfer'):
                self.assertTrue(row[stage]['all_positive'])
                self.assertGreater(p.q(row[stage]['minimum_lower']),0)
                self.assertTrue(all(p.q(x['outward_rate_upper'])<0 for x in row[stage]['zero_resource_vertices']))
            self.assertTrue(row['source_postbeat_trigger']['small_gradient'])
            self.assertTrue(row['source_postbeat_trigger']['strict_hessian_condition'])
            self.assertTrue(row['rounded_exact_postbeat_control']['strict_hessian_condition'])
        for row in value['allocation_only_diagnostic']['cases']:
            self.assertTrue(row['exact_postbeat_trigger']['strict_hessian_condition'])
            self.assertFalse(row['retained_staged_postbeat_trigger']['strict_hessian_condition'])
        for edit in (lambda r:r.update(native_steps=1),lambda r:r['companion'].update(shares=['1/2','1/4','1/4']),
                     lambda r:r['cases'][0]['fresh_postbeat_transfer'].update(minimum_lower='1')):
            mutant=deepcopy(value);edit(mutant)
            with patch.object(p,'calculate',return_value=value),self.assertRaises(ValueError):p.check(p.seal(mutant))
        for edit in (lambda r:r.update(native_steps=1),lambda r:r['event_pair'].update(reset_evolves=True),
                     lambda r:r['cases'][0]['initial_transfer']['resource_bounds'][0].update(lower='-1')):
            mutant=deepcopy(value);edit(mutant)
            with self.assertRaises(ValueError):p.check_retained(p.seal(mutant))


if __name__=='__main__':unittest.main()

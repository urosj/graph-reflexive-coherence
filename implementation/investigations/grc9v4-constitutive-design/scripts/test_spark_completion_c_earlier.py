"""Pressure full C/carrier directions, continuous domains and short-prefix claims."""
from copy import deepcopy
import inspect,unittest
from unittest.mock import patch
import check_spark_completion_c_earlier as check
e=check.e


class EarlierCTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.domain=e.read_json(e.EARLIER+'CEarlierDomain.json')
        cls.saved=e.read_json(e.EARLIER+'CEarlierProofs.json')
        cls.proofs={f:e.certificate(f,cls.domain)for f in e.FAMILIES}

    def test_complete_domain_and_prefix_recomputation(self):
        result=check.check();self.assertEqual(result['retained_states'],3012)
        for key,value in result['decisions'].items():
            self.assertEqual((value['entry'],value['completion']),(374,376)if key.endswith('/current')else(375,377))
        for family,(p,o)in self.proofs.items():
            self.assertEqual(p['full_dimension'],60 if family in ('C_PC','C_CI_PC') else 14)
            self.assertLess(e.F(p['contraction'][1]),1);self.assertGreater(e.F(p['strict_image_margin'][0]),0)
            self.assertEqual(p['trajectory_inputs_to_domain_checker'],0)

    def test_secants_in_all_148_independent_directions_both_signs(self):
        with e.ctx.workprec(e.PRECISION):
            h=e.arb(e.fmpq(1,256))
            for family,(p,o)in self.proofs.items():
                m=o['model'];S=e.arb_mat(o['S']);U=e.arb_mat(o['U']);C=o['C'];d=m.n-1
                persistent=p['carrier_dimension']>0;Z=m.zero()if persistent else None
                a,b=e.state_step(family,m,C,Z)
                def output(c,z):
                    resource=U*(c-a)
                    history=[]if z is None else [[(z[i,j]-b[i,j])*(1 if i==j else e.arb(2).sqrt())/e.arb(o['zrad'])]for i,j in m.pairs]
                    return e.arb_mat(resource.tolist()+history)
                if persistent:
                    P=o['partials'];CZ=U*P['CZ']*e.arb(o['zrad'])
                    ZC=(1-m.decay)*P['SC']*S/e.arb(o['zrad'])
                    ZZ=m.decay*e.arb_mat([[int(i==j)for j in range(len(m.pairs))]for i in range(len(m.pairs))])+(1-m.decay)*P['SZ']
                    D=e.arb_mat([[o['derivative'][i,j]for j in range(d)]+[CZ[i,j]for j in range(CZ.ncols())]for i in range(d)]+
                        [[ZC[i,j]for j in range(d)]+[ZZ[i,j]for j in range(ZZ.ncols())]for i in range(ZZ.nrows())])
                else:D=o['derivative']
                for k in range(p['full_dimension']):
                    for sign in (-1,1):
                        dc=e.arb_mat([[S[i,k]*sign if k<d else 0]for i in range(m.n)])
                        dz=m.zero()if persistent else None
                        if persistent and k>=d:
                            i,j=m.pairs[k-d];dz[i,j]=e.arb(o['zrad'])*sign/(1 if i==j else e.arb(2).sqrt());dz[j,i]=dz[i,j]
                        aa,bb=e.state_step(family,m,C+h*dc,Z+h*dz if persistent else None)
                        secant=output(aa,bb)/h
                        self.assertTrue(all((D[i,k]*sign).contains(secant[i,0])for i in range(D.nrows())),(family,k,sign))

    def test_correlated_OS_split_bound_preserves_original_tolerance(self):
        p,o=self.proofs['C_OS'];m=o['model']
        with e.ctx.workprec(e.PRECISION):
            tolerance=e.arb(e.fmpq(e.PARAMETERS['OS_split_tolerance']))
            naive=e.norm_upper(m.step(o['Cbox'],eta=m.q(1,1024),dt=m.q(32))['defect'])
            bound,operands=e.split_bound(m,o['Cbox'])
            self.assertGreater(naive,tolerance);self.assertLess(bound,tolerance)
            self.assertEqual(operands['norm'],'Frobenius')
            for k in range(14):
                for sign in (-1,1):
                    C=o['C']+e.arb_mat([[e.arb(o['S'][i,k])*sign]for i in range(m.n)])
                    direct=m.step(C,eta=m.q(1,1024),dt=m.q(32))
                    self.assertLess(e.norm_upper(direct['defect']),bound)
                    self.assertLess(e.infnorm(direct['predictor']['causal_flat']-direct['corrector']['causal_flat']).upper(),
                                    e.arb(e.fmpq(operands['flat_difference'][1])))

    def test_rank_radius_graph_law_and_scope_controls(self):
        for defect in ('rank','radius','carrier','duration','graph','center','scope','sources'):
            v=deepcopy(self.domain)
            if defect=='rank':
                for row in v['basis']:row[-1]=row[-2]
            if defect=='radius':v['axis_radii'][0]='0'
            if defect=='carrier':v['carrier_radius']='0'
            if defect=='duration':v['parameters']['duration']='16'
            if defect=='graph':v['graphs']['1']['edges'][0]['tail']['port']=99
            if defect=='center':
                nodes=list(v['center']);v['center'][nodes[0]]=str(e.F(v['center'][nodes[0]])+1);v['center'][nodes[1]]=str(e.F(v['center'][nodes[1]])-1)
            if defect=='scope':v['accepted_authority']=True
            if defect=='sources':v['sources'][0]['sha256']='0'*64
            v=e.sealed(v)
            with self.subTest(defect=defect),self.assertRaises((ValueError,ZeroDivisionError)):
                if defect=='sources':e.bound_sources(v)
                else:e.certificate('C_PC',v)

    def test_all_carrier_directions_affect_membership_and_are_not_frozen(self):
        with e.ctx.workprec(e.PRECISION):
            for family in ('C_PC','C_CI_PC'):
                p,o=self.proofs[family];m=o['model']
                for i,j in m.pairs:
                    Z=m.zero();Z[i,j]=2*e.arb(o['zrad'])/(1 if i==j else e.arb(2).sqrt());Z[j,i]=Z[i,j]
                    lower,upper=e.membership(m,o['C'],Z,o);self.assertGreater(lower,1)
                saved=e.read_json(self.saved['prefixes'][family+'/current']['path']);row=deepcopy(saved['observations'][0]);del row['Z']
                with self.assertRaisesRegex(ValueError,'history omitted'):
                    e.select_prefix(family,'current',[row],self.domain,o,origin=saved['origin'])

    def test_domain_support_and_tail_independence(self):
        self.assertEqual(list(inspect.signature(e.certificate).parameters),['family','declaration'])
        for family,(p,o)in self.proofs.items():
            S=o['S'];nodes=o['model'].nodes
            for a,b in o['model'].edges:
                i,j=nodes.index(a),nodes.index(b);coeff=[S[i,k]-S[j,k]for k in range(14)]
                self.assertEqual(sum(x*(1 if x>=0 else -1)for x in coeff),sum(map(abs,coeff)))
            value=e.read_json(self.saved['prefixes'][family+'/current']['path'])
            # An invalid unused tail must never be consulted to certify closure.
            rows=value['observations']+[{'step':value['completion']+1,'poison':True}]
            self.assertEqual(e.select_prefix(family,'current',rows,self.domain,o,origin=value['origin']),value)
            bad=deepcopy(self.domain);bad['axis_radii']=[str(1000*e.F(x))for x in bad['axis_radii']]
            with self.assertRaises(ValueError):e.certificate(family,e.sealed(bad))

    def test_fresh_COS_prefixes_replay_and_cache_preflights(self):
        _,o=self.proofs['C_OS']
        for role in ('current','reset'):
            preflight=e.preflight_cos(self.domain,role);self.assertEqual(preflight['cached_fixed_I_reads'],8)
            self.assertTrue(preflight['exact_inverse_identity']);self.assertGreater(preflight['graph_cache']['hits'],0)
            actual=e.fresh_cos_prefix(self.domain,role,o)
            saved=e.read_json(self.saved['prefixes']['C_OS/'+role]['path'])
            for key in ('observations','membership_checks','entry','completion','last_executed_step'):
                self.assertEqual(actual[key],saved[key])
            self.assertEqual(actual['origin']['original_checkpoint_overlaps'],saved['origin']['original_checkpoint_overlaps'])
            self.assertTrue({1,42,128} <= set(actual['origin']['original_checkpoint_overlaps']))
            self.assertEqual(actual['origin']['cached_fixed_I_reads'],actual['completion'])

    def test_accepted_ancestors_and_existing_AOS_result_preserved(self):
        _,sources=e.original_runs();self.assertEqual(sources,self.saved['original_sources'])
        for family in ('C_CI','C_PC','C_CI_PC'):
            for role,old_end,end in [('current',851,376),('reset',819,377)]:
                value=e.read_json(self.saved['prefixes'][family+'/'+role]['path'])
                self.assertEqual(value['last_executed_step'],old_end)
                self.assertEqual(value['last_retained_step'],end)
                self.assertEqual(value['last_required_execution_step'],end)
                self.assertEqual(value['supporting_trajectory_steps_after_completion'],0)
        aos=e.read_json(e.EARLIER+'AOSEarlierResearch.json');e.need_seal(aos)
        self.assertEqual(aos['record_digest'],'dec3d7189532bd937d7d3cf65084bb01f78107ea0e18dd325c2a713649e0f5a3')
        self.assertEqual(aos['decisions']['current']['anisotropic_window_end'],377)
        self.assertEqual(aos['decisions']['reset']['anisotropic_window_end'],374)
        self.assertFalse(aos['accepted_authority'])


if __name__=='__main__':unittest.main(verbosity=2)

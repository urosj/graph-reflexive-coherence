"""Focused science/edge-case pressure, no larger native trajectory campaign."""
from copy import deepcopy
from types import SimpleNamespace as NS
import unittest
import numpy as np

import p984g_cos as p


class LargerCOSPrerequisites(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prepared=p.read(p.PREPARED)
        cls.result=p.calculate()

    def test_literal_dense_crosscheck_all_four_points(self):
        import prepare_p983_all_realizations as original
        from tests.models.test_grc_v4_candidate_c import dense_current_oracle
        with original.exact_backend(original.ExactBackend.FLINT):
            for graph in ('source','target'):
                native=original.materialize(self.prepared,graph).inputs
                b,params=p.graph_data(self.prepared[graph])
                for case in (c for c in self.result['cases'] if c['graph']==graph):
                    h=p.generated_h(b,case['predictor']['causal_flat'],params)
                    for stage,matrix in (('predictor',np.eye(b.shape[1])),('corrector',h)):
                        inputs=NS(geometry=NS(reference=native.geometry.reference,
                            one_form_hodge=NS(matrix=matrix)),current=getattr(native,case['role']))
                        other=dense_current_oracle(inputs)
                        for key,foreign in (('current','current'),('read_flux','read'),
                                            ('baseline','j0'),('sector','sector')):
                            with self.subTest(graph=graph,role=case['role'],stage=stage,key=key):
                                np.testing.assert_allclose(case[stage][key],other[foreign],atol=2e-11,rtol=2e-11)

    def test_graph_and_exact_boundary_pressure(self):
        source=self.prepared['source']; b,params=p.graph_data(source)
        for change in ('loop','duplicate','disconnected','weights'):
            mutated=deepcopy(source)
            if change=='loop':mutated['graph']['edges'][0]['head']=deepcopy(mutated['graph']['edges'][0]['tail'])
            if change=='duplicate':mutated['graph']['edges'].append(deepcopy(mutated['graph']['edges'][0]))
            if change=='disconnected':mutated['graph']['live_node_ids'].append('isolated')
            if change=='weights':mutated['profile']['params_resolved']['candidate']['W_C_tr']['foreign']=1
            with self.subTest(change=change),self.assertRaises(ValueError):p.graph_data(mutated)
        h=np.eye(b.shape[1]); altered=h.copy();altered[0,0]+=2**-20
        self.assertFalse(p.exact_bounds(b,h,altered,params)['split_within_tolerance'])
        threshold=deepcopy(params);threshold['candidate']['Lambda_C']=1
        self.assertFalse(p.exact_bounds(b,h,h,threshold)['selector_path_separated'])
        for entry in (float('nan'),float('inf'),1.):
            bad=h.copy();bad[0,1]=entry
            with self.assertRaises(ValueError):p.exact_bounds(b,bad,h,params)
        singular=h.copy();singular[0,0]=0
        self.assertFalse(p.exact_bounds(b,singular,singular,params)['spd'])

    def test_stage_gain_and_continuity_discrimination(self):
        for case in self.result['cases']:
            subject=self.prepared[case['graph']]; b,params=p.graph_data(subject)
            h=p.generated_h(b,case['predictor']['causal_flat'],params)
            self.assertGreater(np.max(abs(h-np.eye(len(h)))),0)
            off=deepcopy(params);off['candidate']['zeta_C']=0
            np.testing.assert_array_equal(p.generated_h(b,case['predictor']['causal_flat'],off),np.eye(len(h)))
            wrong=p.generated_h(b,case['predictor']['current'],params)
            self.assertNotEqual(p.digest(h.tolist()),p.digest(wrong.tolist()))
            c=np.array(subject['roles'][case['role']]['C']); dt=self.prepared['selected_configuration']['ordinary_dt']
            # Outward-tail incidence and C-dt*B*J, not its opposite.
            expected=c-dt*b@np.array(case['corrector']['current'])
            np.testing.assert_allclose(case['continuity_proposal'],expected,atol=2e-15,rtol=2e-15)
            self.assertGreater(np.max(abs(c+dt*b@np.array(case['corrector']['current'])-expected)),1e-8)

    def test_retained_scope_and_mutations(self):
        manifest=p.make_manifest()
        p.check(manifest,self.result)
        for change in ('scope','count','bound','continuity'):
            result=deepcopy(self.result)
            if change=='scope':result['native_admission']=True
            if change=='count':result['cases'].pop()
            if change=='bound':result['cases'][0]['bounds']['split_norm_upper']='0'
            if change=='continuity':result['cases'][0]['continuity_proposal'][0]+=1
            with self.subTest(change=change),self.assertRaises(ValueError):p.check(manifest,p.seal(result))


if __name__=='__main__':unittest.main()

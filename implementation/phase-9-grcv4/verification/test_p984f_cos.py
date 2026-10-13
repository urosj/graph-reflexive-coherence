"""Full chart, phase and role normalization pressure, separate from native count."""
from copy import deepcopy
from dataclasses import replace
import unittest
from unittest.mock import patch
import p984f_cos as f


class ChartTests(unittest.TestCase):
    def test_literal_generators_and_frozen_pairs(self):
        ds=f.declarations();rot,ref=ds[1],ds[3]
        self.assertEqual(list(rot['ports'].values()),[5,6,4,8,9,7,2,3,1])
        self.assertEqual(list(ref['ports'].values()),list(range(9,0,-1)))
        self.assertEqual(len(f.frozen_pairs(execute=True)),2)
        for d,order in ((rot,3),(ref,2)):
            for p in range(1,10):
                x=p
                for _ in range(order):x=d['ports'][str(x)]
                self.assertEqual(x,p)
        self.assertEqual(f.label('old/extra/1/2',rot,'old','new'),'new/extra/2/2')
        bad=deepcopy(rot);bad['ports']={str(p):1+(p-1)%3+3*((1+(p-1)//3)%3) for p in range(1,10)}
        with self.assertRaisesRegex(ValueError,'partial or foreign'):f.validate_transform(bad)

    def test_source_operands_and_nonuniform_reference_transport(self):
        p=f.b.read(f.consumer.INPUTS)['initial_inputs'];old=f.b.GeometryStageInputs.from_payload(p)
        for d in f.declarations():
            q=f.transform(p,d);new=f.b.GeometryStageInputs.from_payload(q)
            ni,ei,sign=f.mapping(p['reference']['graph'],q['reference']['graph'],d)
            self.assertTrue(f.b.np.array_equal(new.geometry.reference.graph.incidence,
                f.b.np.array(old.geometry.reference.graph.incidence)[f.b.np.ix_(ni,ei)]))
            self.assertTrue(all(x==1 for x in sign))
            for role in f.ROLES:self.assertEqual(q[role]['C'],[p[role]['C'][i] for i in ni])
        # Algebra-only probe, not an admitted numerical fixture.
        p['reference']['profile']['params_resolved']['candidate']['W_C_tr']={f'e{i}':float(i) for i in range(1,10)}
        p['reference']['reference_hodge']['edge_weights']={f'e{i}':float(i) for i in range(1,10)}
        f.reidentify(p['reference'])
        ref=f.b.GRCV4ReferenceGeometry.from_payload(p['reference'])
        p=replace(old,geometry=ref.geometry()).to_payload()
        d=f.declarations()[1];q=f.transform(p,d)
        weights=q['reference']['profile']['params_resolved']['candidate']['W_C_tr']
        for i in range(1,10):self.assertEqual(weights[f.label('e'+str(i),d)],float(i))
        q['reference']['profile']=p['reference']['profile']
        with self.assertRaises(ValueError):f.b.GeometryStageInputs.from_payload(q)

    def test_retained_chart_history_and_coverage_mutations(self):
        if not (f.b.ROOT/f.RESULTS).exists():self.skipTest('capture required')
        m=f.b.read(f.INPUTS);record=f.b.read(f.RESULTS);f.check_manifest(m)
        with patch.object(f,'check_manifest'),patch.object(f.b,'ProvisionalCandidateCOSStep',side_effect=AssertionError('native rerun')):
            self.assertEqual(f.check(m,record)['passing_pending_cells'],24)
            for mutation in ('phase','chirality','shares','port','resource','sign','role','frozen','acceptance'):
                bad=deepcopy(record);data=f.prior.previous.expand(bad['execution'])
                row=next(x for x in data['cases'] if 'D52' in x['layout'] and x['kind']=='reflect')
                if mutation=='phase':row['request']['growth_phase']=1
                elif mutation=='chirality':row['request']['module_chirality']*=-1
                elif mutation=='shares':row['request']['resource_distribution']=[1.,0.,0.]
                elif mutation=='port':
                    endpoint=row['target']['inputs']['reference']['graph']['edges'][0]['head']
                    endpoint['port']=1+endpoint['port']%9
                elif mutation=='resource':row['roles']['reset']['steps'][0]['pass']['inputs']['current']['C'].reverse()
                elif mutation=='sign':row['roles']['current']['steps'][0]['pass']['corrector']['current'][0]+=0.01
                elif mutation=='role':del row['roles']['reset']
                elif mutation=='frozen':bad['frozen_plan_execution']['plans_executed']=0
                else:bad['user_accepted']=True
                bad['execution']=f.prior.previous.compact(data);bad=f.b.seal(bad)
                with self.subTest(mutation=mutation),self.assertRaises((ValueError,TypeError)):
                    f.check(m,bad)


if __name__=='__main__':unittest.main()

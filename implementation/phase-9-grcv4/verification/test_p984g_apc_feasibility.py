"""PC allocation/chronology, input enclosures and mechanical parity pressure."""
from copy import deepcopy
import unittest
import p984g_apc_feasibility as p


class APCFeasibility(unittest.TestCase):
    def test_selection_exclusion_and_trigger_separation(self):
        v=p.check_retained();old=p.prior.read(p.prior.RESULTS)
        constraints={c['role']:c['leading_empty_node_constraints'] for c in old['cases'] if c['graph']=='target'}
        self.assertEqual(v['selection'],p.select(constraints))
        self.assertEqual(v['selection']['denominator'],8)
        self.assertEqual(v['selection']['shares'],['1/4','3/8','3/8'])
        self.assertLess(p.q(old['cases'][-1]['first_resource_minimum_upper']),0)
        for c in v['cases']:
            self.assertGreater(p.q(c['postbeat_transfer_target']['minimum_resource_lower']),0)
            self.assertLess(p.q(c['source_trigger']['minimum_signed_hessian_upper']),-p.q('1/2048'))
        with self.assertRaises(ValueError):p.select({'current':[],'reset':[]})

    def test_histories_and_source_charge_preserved(self):
        v=p.read();original=p.prior.read(p.prior.PREPARED)
        self.assertNotEqual(v['companion']['event_id'],original['event_id'])
        for role in ('current','reset'):
            before=original['source']['roles'][role];after=v['source']['roles'][role]
            self.assertEqual(before['W_A'],after['W_A']);self.assertEqual(before['Z_4'],after['Z_4'])
            self.assertEqual(sum(map(p.q,before['C']),p.q(0)),sum(map(p.q,after['C']),p.q(0)))
            changed=[original['source']['graph']['live_node_ids'][i] for i,(x,y) in enumerate(zip(before['C'],after['C'])) if x!=y]
            self.assertEqual(changed,[0,29])
            self.assertEqual(v['target']['roles'][role]['Z_4'],{'recipe':'zero_v1'})
        self.assertFalse(v['event_pair']['reset_evolves'])

    def test_interval_input_includes_small_point_controls(self):
        s=deepcopy(p.prior.read(p.prior.PREPARED)['source'])
        s['graph']['live_node_ids']=['a','b','c'];s['graph']['edges']=[dict(edge_id=str(i),
            tail=dict(node_id=u,port=1),head=dict(node_id=v,port=4)) for i,(u,v) in enumerate((('a','b'),('b','c'),('c','a')))]
        s['roles']['current'].update(C=[2.25,2,1.75],W_A=[1.00001,.99999,1])
        with p.ctx.workprec(p.BITS):
            c=[p.prior.scalar.inflate(p.a(x),p.q('1/1048576')) for x in s['roles']['current']['C']]
            w=[p.prior.scalar.inflate(p.a(x),p.q('1/16777216')) for x in s['roles']['current']['W_A']]
            boxed=p.state_box(s,'current',c,w)
            for sign in (-1,1):
                cc=[p.a(p.lo(x) if sign<0 else p.hi(x)) for x in c]
                ww=[p.a(p.hi(x) if sign<0 else p.lo(x)) for x in w]
                point=p.state_box(s,'current',cc,ww)
                self.assertTrue(all(x.contains(y) for x,y in zip(boxed['J'],point['J'])))
                self.assertTrue(all(x.contains(y) for x,y in zip(boxed['flat'],point['flat'])))
            bad=list(w);bad[0]=p.a(0).union(p.a(1))
            with self.assertRaises(ValueError):p.state_box(s,'current',c,bad)

    def test_pure_mechanical_transfer_parity(self):
        with p.mechanical.exact_backend(p.mechanical.ExactBackend.FLINT):
            self.mechanical_transfer_parity()

    def mechanical_transfer_parity(self):
        v=p.read();d=p.mechanical;s=v['source']
        graph=d.GRC9V4PortGraph.from_envelope(s['graph'])
        profile=d.GRCV4Profile.from_canonical_bytes(d.canonical_json_bytes(s['profile']))
        original=p.prior.read(p.prior.PREPARED)
        spec=d.native.GRC9V4Specialization(d.FrozenJSONMap(original['specialization']['resolved']),d.FrozenJSONMap(original['specialization']['identity_payload']))
        roles={r:d.authority(x,len(graph.edges)) for r,x in s['roles'].items()}
        state=d.make_state(graph,profile,spec,roles,'A_PC')
        self.assertEqual(state.scientific_digest,s['scientific_digest'])
        plan=d.expansion.GRC9V4ExpansionPlan(graph,state.scientific_digest,
            d.expansion.GRC9V4ExpansionRequestInput.from_payload(v['companion']['request']),
            d.expansion.GRC9ExpansionPolicy.from_payload(original['specialization']['resolved']['expansion']))
        transfer=d.expansion.GRC9V4APCExpansion(plan,state.inputs.geometry.reference,roles['current'],roles['reset'])
        self.assertEqual(transfer.target.profile.to_payload(),v['target']['profile'])
        for r,state in roles.items():
            actual=transfer.transfer(state);expected=v['target']['roles'][r]
            self.assertEqual(list(actual.C),expected['C']);self.assertEqual(list(actual.W_A),expected['W_A'])
            self.assertTrue(all(x==0 for x in actual.Z_4))

    def test_retained_scope_and_stages(self):
        original=p.read()
        for mutate in (lambda v:v.update(native_steps=1),lambda v:v.update(ready_for_8_4h=True),
            lambda v:v['event_pair'].update(reset_evolves=True),
            lambda v:v['cases'][0]['initial_target'].update(minimum_resource_lower='-1'),
            lambda v:v['cases'][0]['source_postbeat'].update(poststate_read_executed=True),
            lambda v:v['companion'].update(compensation_node=60),
            lambda v:v['selection'].update(shares=['1/2','1/4','1/4'])):
            value=deepcopy(original);mutate(value)
            with self.assertRaises(ValueError):p.check_retained(p.prior.seal(value))


if __name__=='__main__':unittest.main()

"""A-specific allocation, interval-input root and chronology pressure."""
from copy import deepcopy
import math
import unittest
from unittest.mock import patch
import p984g_aci_feasibility as p


class ACIFeasibility(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old,cls.target,cls.matrix,cls.identity=p.companion(source_deficit=p.DEFICIT)

    def test_full_recomputation_and_first_failures_preserved(self):
        value=p.check()
        self.assertFalse(value['ready_for_8_4h'])
        self.assertTrue(value['original_reset_exclusion_preserved'])
        for c in value['cases']:
            self.assertLess(float(p.q(c['source_trigger']['minimum_signed_hessian_upper'])),-.001)
            for name in ('initial_target','postbeat_transfer_target'):
                self.assertGreater(float(p.q(c[name]['minimum_resource_lower'])),.00018)
        for c in value['allocation_only']['cases']:
            self.assertGreater(p.q(c['initial_target_minimum_lower']),0)
            self.assertFalse(c['source_trigger']['strict_hessian_condition'])
            self.assertFalse(c['rounded_exact_postbeat_control']['strict_hessian_condition'])

    def test_exact_source_history_and_affine_constraints(self):
        original=p.prior.read(p.prior.PREPARED)
        self.assertNotEqual(self.identity['event_id'],original['event_id'])
        for role in ('current','reset'):
            before=original['source']['roles'][role];after=self.old['source']['roles'][role]
            self.assertEqual(before['W_A'],after['W_A'])
            self.assertEqual(sum(map(p.q,before['C']),p.q(0)),sum(map(p.q,after['C']),p.q(0)))
            diff=[i for i,(a,b) in enumerate(zip(before['C'],after['C'])) if a!=b]
            self.assertEqual([original['source']['graph']['live_node_ids'][i] for i in diff],[0,60])
            rows=p.leading_constraints(original['target'],role)
            self.assertEqual(len(rows),5)
            self.assertTrue(all(p.q(x['selected_rate'])>0 for x in rows))
        # The declared max-min balance is derived at unit W, not fitted to a
        # successful numerical root. Both limiting rates are exactly 3/4.
        self.assertEqual(6-14*p.q(p.SHARES[2]),2*p.q(p.SHARES[2]))

    def test_pure_mechanical_adapter_parity(self):
        d=p.prepared;old=self.old
        graph=d.GRC9V4PortGraph.from_envelope(old['source']['graph'])
        profile=d.GRCV4Profile.from_canonical_bytes(d.canonical_json_bytes(old['source']['profile']))
        spec=d.native.GRC9V4Specialization(d.FrozenJSONMap(old['specialization']['resolved']),d.FrozenJSONMap(old['specialization']['identity_payload']))
        roles={r:d.authority(s,len(graph.edges)) for r,s in old['source']['roles'].items()}
        state=d.make_state(graph,profile,spec,roles,'A_CI')
        plan=d.expansion.GRC9V4ExpansionPlan(graph,state.scientific_digest,
            d.expansion.GRC9V4ExpansionRequestInput.from_payload(self.identity['request']),
            d.expansion.GRC9ExpansionPolicy.from_payload(old['specialization']['resolved']['expansion']))
        # This adapter is pure transfer, not trigger/readmission or an event.
        transfer=d.expansion.GRC9V4ACIExpansion(plan,state.inputs.geometry.reference,roles['current'],roles['reset'])
        self.assertEqual(transfer.target.profile.to_payload(),self.target['profile'])
        for r,s in roles.items():
            actual=transfer.transfer(s);expected=self.target['roles'][r]
            self.assertEqual(list(actual.C),expected['C']);self.assertEqual(list(actual.W_A),expected['W_A'])

    def test_square_zero_crossing_and_log_writer(self):
        with p.ctx.workprec(p.prior.BITS):
            for left,right in ((-2,3),(0,0),(-3,-2),(1,2)):
                square=p.square(p.a(left).union(p.a(right)))
                for point in (left,(left+right)/2,right):self.assertTrue(square.contains(p.a(point)**2))
            result=p.log_writer([p.a(4)],[p.a(1)],1,1)[0]
            expected=(p.a(-1).exp()*p.a(4).log()).exp()
            self.assertTrue(result.overlaps(expected))
            self.assertFalse(result.contains(1+3/math.e)) # not linear W mixing
            with self.assertRaises(ValueError):p.log_writer([p.a(0)],[p.a(1)],1,1)

    def test_interval_operands_not_just_nominal_current(self):
        s=deepcopy(self.old['source']);s['graph']['live_node_ids']=['a','b','c']
        s['graph']['edges']=[dict(edge_id=str(i),tail=dict(node_id=u,port=1),head=dict(node_id=v,port=4))
            for i,(u,v) in enumerate((('a','b'),('b','c'),('c','a')))]
        s['roles']['current'].update(C=[2.25,2,1.75],W_A=[1.00001,.99999,1])
        with p.ctx.workprec(p.prior.BITS):
            c=[p.inflate(p.a(x),p.q('1/1048576')) for x in s['roles']['current']['C']]
            w=[p.inflate(p.a(x),p.q('1/16777216')) for x in s['roles']['current']['W_A']]
            boxed=p.joint_box(s,'current',c,w)
            for sign in (-1,1):
                cc=[p.a(p.lo(x) if sign<0 else p.hi(x)) for x in c]
                ww=[p.a(p.lo(x) if sign<0 else p.hi(x)) for x in w]
                point=p.joint_box(s,'current',cc,ww)
                self.assertTrue(all(x.contains(y) for x,y in zip(boxed['J'],point['Jref'])))
            bad=list(w);bad[0]=p.a(0).union(p.a(1))
            with self.assertRaises(ValueError):p.joint_box(s,'current',c,bad)

    def test_retained_scope_and_chronology_pressure(self):
        value=p.check_retained()
        for mutate in (lambda v:v.update(native_steps=1),lambda v:v.update(ready_for_8_4h=True),
                lambda v:v['event_pair'].update(reset_evolves=True),
                lambda v:v['cases'][0]['initial_target'].update(minimum_resource_lower='-1')):
            x=deepcopy(value);mutate(x)
            with self.assertRaises(ValueError):p.check_retained(p.prior.seal(x))
        for shares in (('1','1','1'),('-1','1','1')):
            with self.assertRaises(ValueError):p.companion(shares)


if __name__=='__main__':unittest.main()

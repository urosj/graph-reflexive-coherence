"""A-specific admission/geometry/history preflight, without native roots."""
from copy import deepcopy
from dataclasses import replace
import unittest
from unittest.mock import patch
import p984h_aci_campaign as m


class CampaignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seed, cls.source = m.baseline_source()
        cls.initial, cls.operand, _ = m.p.seed()
        cls.old = m.p.accepted_source()['result']

    def retained_root(self):
        old = deepcopy(self.old['roots']['current'])
        expected = next(c['result'] for c in m.oracle.read()['cases'] if (c['graph'],c['role'])==('source','current'))
        before=self.initial.inputs; h=m.generated(before,expected['reference']['flat'])[1]
        src,out=m.generated(before,expected['confirming']['flat'])
        old.update(oracle=expected,joint=dict(H=h,source=src,generated=out,
            recipe='grc9v4_ci_fixed_rows_confirmed_joint_residual_v1',
            domain_id=before.geometry.reference.profile.params_resolved.realization.contraction_domain_id))
        return old

    def test_joint_checker_accepts_retained_operand_not_native_reexecution(self):
        with patch.object(m.ci,'CandidateCIRoot',side_effect=AssertionError('native forbidden')):
            m.check_root(self.retained_root(),self.initial.inputs)

    def test_joint_geometry_domain_and_stopping_mutations(self):
        original=self.retained_root()
        for field in ('H','source','generated','domain_id','recipe'):
            with self.subTest(field=field):
                bad=deepcopy(original)
                if field in ('domain_id','recipe'): bad['joint'][field]='wrong'
                else: bad['joint'][field][0][0]+=1e-4
                with self.assertRaises(ValueError):m.check_root(bad,self.initial.inputs)
        bad=deepcopy(original);bad['evaluations']=1
        with self.assertRaisesRegex(ValueError,'two-pass'):m.check_root(bad,self.initial.inputs)

    def test_fresh_target_transfers_both_histories_without_event(self):
        with patch.object(m.p.native,'GRC9V4ACIOperation',side_effect=AssertionError('event forbidden')):
            plan,target=m.expected_event(self.seed,self.source['execution']['request'])
        self.assertEqual((len(plan.target_graph.live_node_ids),len(plan.target_graph.edges)),(107,407))
        self.assertEqual(target.time,self.seed.inputs.time)
        self.assertEqual(target.step_index,self.seed.inputs.step_index)
        self.assertNotEqual(target.current,target.reset)
        old_edges=set(self.seed.inputs.geometry.reference.graph.live_edge_ids)
        for role in m.ROLES:
            incoming=getattr(self.seed.inputs,role);out=getattr(target,role)
            lineage=dict(zip(self.seed.inputs.geometry.reference.graph.live_edge_ids,incoming.W_A))
            for edge,w in zip(plan.target_graph.edges,out.W_A):
                self.assertEqual(w,lineage[edge.edge_id] if edge.edge_id in old_edges else plan.policy.bond_seed)
            self.assertTrue(all(w>0 for w in out.W_A))
        bad=deepcopy(self.source['execution']['request'])
        bad['history_policy']=m.p.aos_history_policy(self.initial.inputs.current,self.initial.inputs.reset)
        with self.assertRaisesRegex(ValueError,'actual old-edge lineage'):
            m.expected_event(self.seed,bad)


if __name__=='__main__':unittest.main()

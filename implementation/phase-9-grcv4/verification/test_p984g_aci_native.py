"""Small native writer parity and retained larger-case mutation pressure."""
from copy import deepcopy
from dataclasses import replace
import json
import lzma
import unittest
from unittest.mock import patch
import p984g_aci_native_check as c
import p984g_pre_aci_residual_sources as history
from test_p984g_aci_staged import small


class ACINative(unittest.TestCase):
    def assess_historical(self,value,companion,oracle):
        with history.native_sources(c.run):return c.assess(value,companion,oracle)

    def test_small_whole_step_writer_and_final_root(self):
        from pygrc.models.grc_v4_ci import ProvisionalCandidateCIStep
        from pygrc.models.grc_v4_numerics import exact_backend,ExactBackend,numerical_policy,NumericalPolicy,matrix_operation
        p=c.run.f.prepared;s=small();old=c.run.f.prior.read(c.run.f.prior.PREPARED)
        graph=p.GRC9V4PortGraph.from_payload({k:v for k,v in s['graph'].items() if k!='graph_digest'})
        profile=p.profile_for(graph,'A_CI',old['selected_configuration'])
        s['graph']=graph.to_envelope();s['profile']=profile.to_payload()
        spec=p.native.GRC9V4Specialization(p.FrozenJSONMap(old['specialization']['resolved']),p.FrozenJSONMap(old['specialization']['identity_payload']))
        roles={r:p.authority(s['roles'][r],3) for r in ('current','reset')}
        before=replace(p.make_state(graph,profile,spec,roles,'A_CI').inputs,Q_target=6.,dt=2**-12)
        backend=p.GRC9V4CandidateADifferentialReference(graph)
        with exact_backend(ExactBackend.FLINT),numerical_policy(NumericalPolicy.CERTIFIED_ARB_256),matrix_operation():
            step=ProvisionalCandidateCIStep(before,backend)
        w=c.run.writer_oracle(s,'current',step.next_inputs.current.C,step.root.current.values,before.dt)
        self.assertEqual(w['W_A'],list(step.next_inputs.current.W_A))
        self.assertEqual(w['drive'],list(step.writer.W_drv_A))
        self.assertEqual([r.evaluations for r in (step.reset_root,step.root,step.restart)],[2,2,2])
        self.assertEqual(step.restart.inputs.current,step.next_inputs.current)
        self.assertEqual(step.next_inputs.reset,before.reset)
        self.assertNotEqual(w['drive'],c.run.writer_oracle(s,'current',before.current.C,step.root.current.values,before.dt)['drive'])

    def test_retained_scope_and_full_joint_mutations(self):
        raw=(c.ROOT/c.run.case_path('source','current')).read_bytes();original=json.loads(lzma.decompress(raw))
        companion=c.run.f.check_retained();oracle=history.check_staged()
        with patch.object(c.run,'execute',side_effect=AssertionError('native rerun')),patch.object(c.run.oracle,'analyze',side_effect=AssertionError('interval root rerun')):
            row=self.assess_historical(original,companion,oracle)
        # A bounded attempt may expose an implementation hold. Such a record
        # must remain inspectable but cannot earn successful-root/step credit.
        if original['outcome']=='incomplete':
            self.assertEqual(row['native_steps'],0)
            for key in ('native_events','ready_for_8_4h','user_accepted'):
                changed=deepcopy(original);changed[key]=1
                with self.subTest(key=key),self.assertRaises(ValueError):self.assess_historical(c.seal(changed),companion,oracle)
            return
        self.assertEqual(row['native_steps'],1)
        edits=[lambda v:v.update(native_events=1),lambda v:v.update(ready_for_8_4h=True),
            lambda v:v['result']['roots']['current'].update(evaluations=1),
            lambda v:v['result']['roots']['current'].update(selected_joint_point_digest='wrong'),
            lambda v:v['result']['roots']['final'].update(state_digest='wrong'),
            lambda v:v['result']['roots']['final']['certificate'].update(contraction_upper='1'),
            lambda v:v['result'].update(reset_unchanged=False),
            lambda v:v['result']['after_W_A'].__setitem__(0,1.1),
            lambda v:v['result']['after_C'].__setitem__(0,1.1),
            lambda v:v['result'].update(exact_resource_sum_delta='1'),
            lambda v:v['result']['roots']['current']['independent_stages'][0]['joint_root_bridge'].update(current_error_upper='0')]
        for i,edit in enumerate(edits):
            changed=deepcopy(original);edit(changed)
            with self.subTest(i=i),self.assertRaises(ValueError):self.assess_historical(c.seal(changed),companion,oracle)

    def test_incomplete_has_no_completion_credit(self):
        original=json.loads(lzma.decompress((c.ROOT/c.run.case_path('source','current')).read_bytes()))
        original.update(outcome='incomplete',result=None,error=dict(type='TimeoutError'),timed_out=True)
        row=self.assess_historical(c.seal(original),None,None)
        self.assertEqual(row['native_steps'],0);self.assertEqual(row['native_roots'],0)

    def test_corrected_analytic_enclosure_under_conservative_widening(self):
        """The old expected failure now passes under the corrected runtime.

        A valid interval product may be wider than the exact point product.
        Widening zero to [-1,1] must not lose the exact geometry residual zero.
        The original failure record remains historical, not relabeled as passed.
        """
        from tests.models.test_grc_v4_ci import fixture
        from pygrc.models import grc_v4_ci as ci
        from pygrc.models.grc_v4_candidate_a import CandidateACurrent
        from pygrc.models.grc_v4_geometry import PhysicalFlux
        from pygrc.models.grc_v4_numerics import exact_backend,ExactBackend,numerical_policy,NumericalPolicy
        from pygrc.models.grc_v4_exact import exact_number
        before,backend=fixture('A',C=(2.,2.),W=(1.,),changes={'candidate':
            {'alpha':0.,'beta':0.,'gamma':1.,'chi_A':.25,'zeta_A':.5}})
        with exact_backend(ExactBackend.FLINT),numerical_policy(NumericalPolicy.CERTIFIED_ARB_256):
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
            self.assertEqual((true.lo,true.hi),(0,0))
            self.assertTrue(wide.lo<=0<=wide.hi,'A nonlinear enclosure lost its exact interior operand')


if __name__=='__main__':unittest.main()

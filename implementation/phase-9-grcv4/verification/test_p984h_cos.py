"""Focused event-operand and retained-oracle pressure, no native campaign."""

from copy import deepcopy
from fractions import Fraction
import unittest
from unittest.mock import patch

import p984h_cos as run


class EventOperands(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.subject = run.fresh_subject()

    def test_actual_postbeat_both_roles_and_fresh_namespace(self):
        declaration, state, request, identity, event, target = self.subject
        self.assertEqual(state.inputs.step_index, 1)
        self.assertNotEqual(state.scientific_digest, declaration['source']['scientific_digest'])
        self.assertNotEqual(event, declaration['event_id'])
        self.assertEqual(request['source_state_digest'], state.scientific_digest)
        self.assertEqual(list(state.inputs.reset.C), declaration['source']['roles']['reset']['C'])
        self.assertNotEqual(list(state.inputs.current.C), declaration['source']['roles']['current']['C'])
        self.assertNotEqual(target['roles']['current']['C'], target['roles']['reset']['C'])
        for role in run.ROLES:
            c=target['roles'][role]['C'];original=getattr(state.inputs,role).C
            self.assertEqual(sum(map(Fraction,c)),sum(map(Fraction,original)))
        self.assertFalse(run.trigger(state)['eligible'])
        self.assertEqual(run.trigger(state)['gradient'],[0.,0.,0.])

    def test_second_beat_does_not_retune_the_source(self):
        declaration,state=run.second_source_input()
        historical=self.subject[1]
        self.assertEqual(state.inputs.current,historical.inputs.current)
        self.assertEqual(state.inputs.reset,historical.inputs.reset)
        self.assertEqual(state.inputs.geometry,historical.inputs.geometry)
        self.assertEqual(state.inputs.step_index,1)
        self.assertEqual(state.inputs.dt,declaration['selected_configuration']['ordinary_dt'])

    def test_independent_graph_reference_transfer_against_native_mechanics(self):
        from pygrc.models.grc_9_v4_expansion import GRC9V4ExpansionPlan, GRC9V4ExpansionRequestInput, GRC9ExpansionPolicy, GRC9V4COSExpansion
        declaration, state, request, identity, event, target = self.subject
        policy=GRC9ExpansionPolicy.from_payload(declaration['specialization']['resolved']['expansion'])
        plan=GRC9V4ExpansionPlan(state.inputs.geometry.reference.graph.port_graph,state.scientific_digest,
                               GRC9V4ExpansionRequestInput.from_payload(request),policy)
        self.assertEqual(plan.event_id,event);self.assertEqual(plan.event_identity_payload(),identity)
        self.assertEqual(plan.target_graph.to_payload(),target['graph'])
        expansion=GRC9V4COSExpansion(plan,state.inputs.geometry.reference)
        self.assertEqual(expansion.target.profile.to_payload(),target['profile'])
        for role in run.ROLES:
            self.assertEqual(list(expansion.transfer(getattr(state.inputs,role)).C),target['roles'][role]['C'])
        bad=deepcopy(request);bad['source_state_digest']=declaration['source']['scientific_digest']
        with self.assertRaises(ValueError):
            GRC9V4ExpansionPlan(plan.source_graph,state.scientific_digest,GRC9V4ExpansionRequestInput.from_payload(bad),policy)

    def test_charge_boundary_and_literal_sum(self):
        params=dict(absolute_tolerance=0.,relative_tolerance=0.)
        self.assertEqual(run.pairwise([1.,2.,3.]),6.)
        self.assertEqual(run.charge([1.],[1.],params,target=1.)['margin'],'0')
        with self.assertRaisesRegex(ValueError,'charge admission'):
            run.charge([1.],[1.+2**-52],params,target=1.)


class RetainedOracle(unittest.TestCase):
    def test_retained_mutation_pressure_without_solves(self):
        if not (run.ROOT/run.RESULTS).exists():self.skipTest('oracle not executed yet')
        m=run.old.read(run.INPUTS);r=run.read_result()
        with patch.object(run,'step',side_effect=AssertionError('numerical rerun')):
            self.assertEqual(run.check(m,r)['oracle_steps'],2)
            mutations=(
                lambda v:v.update(native_events=1),
                lambda v:v.update(user_accepted=True),
                lambda v:v['cases'][0]['steps'].pop(),
                lambda v:v['cases'][0].update(initial_C=v['cases'][1]['initial_C']),
                lambda v:v['cases'][0]['steps'][0]['current'].__setitem__(0,0.),
                lambda v:v['cases'][0]['steps'][0]['after_C'].__setitem__(0,-1.),
                lambda v:v['cases'][0]['steps'][0].update(split_upper='1'),
                lambda v:v['cases'][0]['steps'][0]['charge'].update(margin='0'),
                lambda v:v['cases'][0]['steps'][0]['corrector_domain'].update(selector_gap_lower='1'),
            )
            # Reuse checked reconstruction: these tests target retained semantics,
            # not repeated schema/materialization work.
            _,initial=run.second_source_input()
            state=run.postbeat(initial,r['source_step']['after_C']);subject=run.fresh_subject(state)
            with patch.object(run,'manifest',return_value=m),patch.object(run,'fresh_subject',return_value=subject),patch.object(run,'second_source_input',return_value=(None,initial)):
                for mutate in mutations:
                    v=deepcopy(r);mutate(v)
                    with self.assertRaises(ValueError):run.check(m,run.seal(v))
                bad=deepcopy(m);bad['dt']*=2
                with self.assertRaises(ValueError):run.check(run.seal(bad),r)


if __name__=='__main__':unittest.main()

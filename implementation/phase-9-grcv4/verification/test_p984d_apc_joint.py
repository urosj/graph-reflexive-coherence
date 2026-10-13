"""Coupled selection and unchanged-law witness pressure."""

from copy import deepcopy
from fractions import Fraction as Q
import unittest
from unittest.mock import patch

import p984d_apc_joint as j
from test_p984d_apc_feasibility import literal,overlap


class JointTests(unittest.TestCase):
    def test_interval_decomposition_against_literal_equations(self):
        old=j.b.read(j.h.RESULTS);ctx=j.f.context(old['runtime_manifest'])
        choice=j.b.read(j.DERIVATION)['selection']['shares'];x,y=map(Q,choice[:2])
        for a,z in ((x,y),(Q(0),Q(0)),(Q(1),Q(0))):
            first,second=literal(ctx,a,z)
            bounds=j.f.enclose(ctx,(a,a,z,z))
            for key,truth,err in (('first',first,bounds['first_error']),('second',second,bounds['second_error'])):
                if truth is None:continue
                represented=j.f.affine(ctx[key],j.f.number(a),j.f.number(z))+err
                self.assertTrue(all(overlap(v,w) for v,w in zip(truth,represented)))
        with patch.object(ctx['high'],'write',side_effect=lambda c,w,cur:w):
            wrong=j.f.enclose(ctx,(x,x,y,y))
        _,truth=literal(ctx,x,y)
        frozen=j.f.affine(ctx['second'],j.f.number(x),j.f.number(y))+wrong['second_error']
        self.assertTrue(any(not overlap(v,w) for v,w in zip(truth,frozen)))

    def test_selection_and_scope_mutations(self):
        value=j.b.read(j.DERIVATION)
        checked=j.check_derivation(value)
        self.assertEqual(sum(map(Q,checked['selection']['shares'])),1)
        self.assertGreater(Q(checked['selection']['minimum_share_margin']),0)
        with self.assertRaises(ValueError):j.select([])
        for mutate in (lambda v:v['selection'].update(shares=['1/3']*3),
                lambda v:v.update(uniform_native_domain=True),
                lambda v:v['certificates'].pop(),
                lambda v:v['certificates'][0]['constraints'][0]['affine'].__setitem__(0,'1')):
            wrong=deepcopy(value);mutate(wrong)
            with self.assertRaises(ValueError):j.check_derivation(j.b.seal(wrong))

    def test_event_rebinding_and_both_histories(self):
        declaration=j.b.read(j.INPUTS);old=j.b.read(j.h.RESULTS)['runtime_manifest']
        selected=declaration['runtime_manifest'];case=selected['cases'][0]
        self.assertEqual(selected['expected_source'],old['expected_source'])
        original=next(v for v in old['cases'] if v['case_id']==j.h.c.PILOT)
        self.assertNotEqual(case['oracle']['event_id'],original['oracle']['event_id'])
        self.assertEqual(case['request']['resource_distribution'],case['oracle']['event_identity']['resource_distribution'])
        self.assertEqual(case['request']['history_policy'],original['request']['history_policy'])
        for mutate in (lambda v:v['runtime_manifest']['cases'][0]['request']['resource_distribution'].__setitem__(0,0),
                lambda v:v.update(cases_required=20),lambda v:v.update(source_reused=False)):
            wrong=deepcopy(declaration);mutate(wrong)
            with self.assertRaises(ValueError):j.check_manifest(j.b.seal(wrong))

    def test_retained_runtime_without_execution_and_no_promotion(self):
        m,v=j.b.read(j.INPUTS),j.b.read(j.RESULTS)
        with (patch.object(j.r,'perform_step',side_effect=AssertionError('native step')),
                patch.object(j.r,'event_capture',side_effect=AssertionError('native event'))):
            result=j.check(m,v)
        self.assertEqual(result['accepted_cells'],0)
        self.assertEqual(result['unattempted_cases'],19)
        wrong=deepcopy(v);wrong['user_accepted']=True
        with self.assertRaises(ValueError):j.check(m,j.b.seal(wrong))
        execution=j.h.prior.previous.expand(v['execution'])
        execution['cases'][0]['continuation'][0]['index']=2
        wrong=deepcopy(v);wrong['execution']=j.h.prior.previous.compact(j.b.seal(execution))
        with self.assertRaisesRegex(ValueError,'partial continuation schedule'):
            j.check(m,j.b.seal(wrong))


if __name__=='__main__':unittest.main()

"""Pressure retained summaries without rerunning the native campaign."""
from copy import deepcopy
import json
import lzma
import unittest
from unittest.mock import patch
import p984g_cci_closure_check as c


class NativeClosure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old,cls.target,_,cls.declaration=c.run.f.companion(c.run.f.DEFICIT)
        cls.feasible=c.run.f.check_retained()

    def case(self,graph='source',role='current'):
        return json.loads(lzma.decompress((c.ROOT/c.run.case_path(graph,role)).read_bytes()))

    def assess(self,value):
        subject=self.old['source'] if value['graph']=='source' else self.target
        feasible=next(x for x in self.feasible['cases'] if x['role']==value['role'])
        return c.assess(value,subject,self.declaration,feasible)

    def test_four_cases_retained_only(self):
        with patch.object(c.run,'execute',side_effect=AssertionError('native rerun')):
            value=c.check()
        self.assertEqual(value['native_roots'],12)
        self.assertEqual(value['native_steps'],4)
        self.assertEqual(value['native_events'],0)

    def test_resealed_false_claims_and_wrong_stages_rejected(self):
        original=self.case()
        changes=[lambda v:v.update(outcome='incomplete'),
            lambda v:v.update(native_events=1),
            lambda v:v.update(numerical_policy='legacy_exact_v1'),
            lambda v:v['result'].update(reset_unchanged=False),
            lambda v:v['result']['roots']['final'].update(resource_digest='wrong'),
            lambda v:v['result']['roots']['current'].update(evaluations=2),
            lambda v:v['result']['roots']['current']['point'].update(input_hodge_digest='wrong'),
            lambda v:v['result']['roots']['current']['certificate'].update(contraction_upper='1'),
            lambda v:v['result']['roots']['current'].update(independent_geometry_residual_upper='1'),
            lambda v:v['result']['roots']['current']['joint_root_error'].update(current_error_upper='0'),
            lambda v:v['result']['after_C'].__setitem__(0,v['result']['after_C'][0]+.1),
            lambda v:v['source_bindings'].update({c.run.SELF:'0'*64})]
        for change in changes:
            value=deepcopy(original);change(value)
            with self.subTest(change=changes.index(change)),self.assertRaises((ValueError,AssertionError)):
                self.assess(c.seal(value))

    def test_negative_predecessor_is_not_erased(self):
        import p984g_pre_ci_interval_sources as history
        with history.historical_sources():
            value=c.run.f.continuation.check()
        self.assertEqual(sum(bool(x['certified_negative_vertices']) for x in value['cases']),2)


if __name__=='__main__':unittest.main()

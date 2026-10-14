"""Corrected native records and historical separation, without trajectory replay."""
from copy import deepcopy
import json
import lzma
import unittest
from unittest.mock import patch
import p984g_aci_native_successor_check as c


class NativeSuccessor(unittest.TestCase):
    def test_retained_source_and_mutations(self):
        value=json.loads(lzma.decompress((c.ROOT/c.run.case_path('source','current')).read_bytes()))
        companion=c.run.base.f.check_retained();oracle=c.history.check_staged()
        with patch.object(c.run.base,'execute',side_effect=AssertionError('native replay')),patch.object(c.run.base.oracle,'analyze',side_effect=AssertionError('interval root replay')):
            result=c.assess(value,companion,oracle)
        self.assertEqual(result['native_steps'],1);self.assertEqual(result['root_evaluations'],[2,2,2])
        changes=[lambda v:v.update(native_events=1),lambda v:v.update(ready_for_8_4h=True),
            lambda v:v['result']['roots']['current'].update(evaluations=1),
            lambda v:v['result']['roots']['current'].update(selected_joint_point_digest='bad'),
            lambda v:v['result']['roots']['final'].update(state_digest='bad'),
            lambda v:v['result']['roots']['final']['certificate'].update(contraction_upper='1'),
            lambda v:v['result'].update(reset_unchanged=False),
            lambda v:v['result'].update(exact_resource_sum_delta='1'),
            lambda v:v['result']['after_W_A'].__setitem__(0,1.1),
            lambda v:v['result']['after_C'].__setitem__(0,1.1),
            lambda v:v['result']['roots']['current']['independent_stages'][0]['joint_root_bridge'].update(current_error_upper='0')]
        for i,change in enumerate(changes):
            mutated=deepcopy(value);change(mutated)
            with self.subTest(i=i),self.assertRaises(ValueError):c.assess(c.prior.seal(mutated),companion,oracle)

    def test_historical_binding_is_not_current_runtime_credit(self):
        historical=json.loads(lzma.decompress((c.ROOT/c.run.base.case_path('source','current')).read_bytes()))
        with c.history.native_sources(c.run.base):
            original=c.prior.assess(historical,None,None)
        self.assertEqual(original['native_steps'],0)
        with self.assertRaises(ValueError):c.assess(historical,None,None)
        oracle=c.run.base.oracle.read();bad=deepcopy(oracle)
        key=next(k for k in bad['source_bindings'] if k!=c.history.CI);bad['source_bindings'][key]='0'*64
        with self.assertRaises(ValueError):c.history.check_staged(c.prior.seal(bad))


if __name__=='__main__':unittest.main()

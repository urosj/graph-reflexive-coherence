"""Focused discrimination of composite A root identity and transfer arithmetic."""
from copy import deepcopy
from dataclasses import replace
from fractions import Fraction
import unittest
import p984d_acipc as d
import p984h_acipc_math as math_check
import p9_acipc_targets as targets


class CompositeScienceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before=d.b.GeometryStageInputs.from_payload(d.read(d.r.INPUTS)['initial_inputs'])
        with d.worker():
            root=d.r.CandidateCIRoot(cls.before,d.r.backend(cls.before))
            cls.read=math_check.capture_read(root)

    def test_independent_composite_equations_match_full_native_point(self):
        math_check.check_read(self.before,self.read,numerics=True)
        self.assertGreater(Fraction(self.read['certificate']['local_bounds']['carrier_norm_upper']),0)

    def test_same_current_stale_geometry_is_rejected(self):
        bad=deepcopy(self.read);bad['H'][0][0]+=2**-20
        raw={k:v for k,v in bad.items() if k!='certificate'}
        bad=dict(d.b.seal(raw),certificate=bad['certificate'])
        with self.assertRaisesRegex(ValueError,'whole selected root'):
            math_check.check_read(self.before,bad)

    def test_old_carrier_is_a_separate_bound_operand(self):
        changed=replace(self.before,current=replace(self.before.current,Z_4=(0.,)*len(self.before.current.Z_4)))
        with self.assertRaisesRegex(ValueError,'root input'):
            math_check.check_read(changed,self.read)

    def test_generic_target_matches_existing_independent_small_constructor(self):
        m=d.read(d.INPUTS);case=m['cases'][-1];seed=d.r.state(d.selected_manifest(m,case)['expected_source'])
        self.assertEqual(targets.target(seed,case),d.r.independent_target(seed,case))
        self.assertNotEqual(seed.inputs.current,seed.inputs.reset)

    def test_composite_carrier_symmetry_and_support_fail_closed(self):
        g=math_check.g;operand=math_check.subject(self.before)
        operand['roles']['current']['Z_4'][1]+=1
        with g.ctx.workprec(g.BITS),self.assertRaisesRegex(ValueError,'symmetric carrier'):
            g.local_bounds(operand,'current')


if __name__=='__main__':unittest.main()

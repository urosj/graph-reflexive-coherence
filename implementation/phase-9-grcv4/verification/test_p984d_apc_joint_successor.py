"""Coupled successor source, allocation, scope and partial-evidence pressure."""
from copy import deepcopy
from fractions import Fraction as Q
import unittest
from unittest.mock import patch

import p984d_apc_joint_successor as s


class SuccessorTests(unittest.TestCase):
    def test_independent_source_roles_and_selection(self):
        before=s.initial();old=s.h.initial()
        self.assertEqual(before.reset,old.reset)
        self.assertEqual(before.current.C,old.current.C)
        self.assertEqual(before.current.Z_4,old.current.Z_4)
        self.assertEqual([Q(a)-Q(b) for a,b in zip(before.current.W_A,old.current.W_A)],[-Q(1,64)]*9)
        m=s.b.read(s.INPUTS);s.check_manifest(m)
        self.assertEqual(m['derivation']['selection']['shares'],['47/128','47/128','17/64'])
        self.assertFalse(m['derivation']['uniform_native_domain'])
        self.assertEqual(m['derivation']['represented_sufficient_polygon'],[])

    def test_binding_and_scope_mutations(self):
        m=s.b.read(s.INPUTS)
        for mutate in (lambda v:v.update(initial_history_mean='63/64'),
                lambda v:v['derivation'].update(uniform_native_domain=True),
                lambda v:v['runtime_manifest']['cases'][0]['request'].update(resource_distribution=[0,0,1]),
                lambda v:v['derivation']['certificates'][0]['constraints'][0]['affine'].__setitem__(0,'100')):
            bad=deepcopy(m);mutate(bad)
            with self.assertRaises(ValueError):s.check_manifest(s.b.seal(bad))

    def test_no_native_rerun_or_scope_promotion(self):
        m,v=s.b.read(s.INPUTS),s.b.read(s.RESULTS)
        with (patch.object(s.r,'perform_step',side_effect=AssertionError('native step')),
                patch.object(s.r,'event_capture',side_effect=AssertionError('native event'))):
            result=s.check(m,v)
        self.assertEqual(result['accepted_cells'],0)
        self.assertEqual(result['unattempted_cases'],19)
        bad=deepcopy(v);bad['aggregate_closed']=True
        with self.assertRaises(ValueError):s.check(m,s.b.seal(bad))


if __name__=='__main__':unittest.main()

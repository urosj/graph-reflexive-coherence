"""Bounded source change, retained negative evidence and non-promotion."""

from copy import deepcopy
from fractions import Fraction as Q
import unittest
from unittest.mock import patch

import p984d_apc_companion as c


class CompanionTests(unittest.TestCase):
    def test_charge_preserving_source_not_reset_or_poststate_substitution(self):
        old=c.b.read(c.prior.INPUTS)
        before=c.b.GeometryStageInputs.from_payload(old["initial_inputs"])
        after=c.initial(old)
        self.assertEqual(sum(map(Q,before.current.C)),sum(map(Q,after.current.C)))
        self.assertEqual(after.reset,before.reset)
        self.assertEqual(after.current.W_A,before.current.W_A)
        self.assertEqual(after.current.Z_4,before.current.Z_4)
        self.assertNotEqual(after.current.C,after.reset.C)
        self.assertEqual(after.step_index,0)
        manifest=c.b.read(c.INPUTS)
        c.check_manifest(manifest)
        altered=deepcopy(manifest)
        altered["initial_inputs"]["current"]["C"][0]+=1
        with self.assertRaises(ValueError): c.check_manifest(c.b.seal(altered))

    def test_retained_equations_without_native_and_rehashed_promotion(self):
        manifest,result=c.b.read(c.INPUTS),c.b.read(c.RESULTS)
        with patch.object(c.r,"perform_step",side_effect=AssertionError("native step")), \
                patch.object(c.r,"event_capture",side_effect=AssertionError("native event")):
            c.check(manifest,result,numerics=True)
        for key,value in (("runtime_cells_closed",2),("topology_events",1),
                ("uniform_neighborhood_proved",True),("failures",[{"message":"forged"}]),
                ("status","passed")):
            changed=deepcopy(result)
            changed[key]=value
            with self.assertRaises(ValueError): c.check(manifest,c.b.seal(changed))
        altered=deepcopy(result)
        altered["trajectories"]["current"][0]["input"]["C"][0]+=1
        with self.assertRaises(ValueError): c.check(manifest,c.b.seal(altered))


if __name__=="__main__": unittest.main()

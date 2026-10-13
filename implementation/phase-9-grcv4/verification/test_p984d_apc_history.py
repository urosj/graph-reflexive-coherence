"""History companion scope, source stage and retained lifecycle pressure."""

from copy import deepcopy
from fractions import Fraction as Q
import unittest
from unittest.mock import patch

import p984d_apc_history as h


class HistoryCompanionTests(unittest.TestCase):
    def test_history_only_change_and_declared_neighbors(self):
        original=h.b.GeometryStageInputs.from_payload(h.b.read(h.c.prior.INPUTS)["initial_inputs"])
        for offset in (Q(0),-Q(1,256),Q(1,256)):
            changed=h.initial(offset)
            self.assertEqual(changed.current.C,original.current.C)
            self.assertEqual(changed.current.Z_4,original.current.Z_4)
            self.assertEqual(changed.reset,original.reset)
            self.assertEqual(changed.geometry,original.geometry)
            self.assertEqual([Q(a)-Q(b) for a,b in zip(changed.current.W_A,original.current.W_A)],
                [Q(3,64)+offset]*9)
        with self.assertRaises(ValueError):h.initial(Q(1,128))

    def test_retained_native_evidence_without_execution_and_scope_mutations(self):
        manifest,result=h.b.read(h.INPUTS),h.b.read(h.RESULTS)
        with patch.object(h.r,"perform_step",side_effect=AssertionError("native step")), \
                patch.object(h.r,"event_capture",side_effect=AssertionError("native event")), \
                patch.object(h.prior,"trigger_certificate",side_effect=AssertionError("interval rerun")):
            checked=h.check(manifest,result)
        self.assertEqual(checked["accepted_cells"],0)
        for field,value in (("user_accepted",True),("uniform_neighborhood_proved",True)):
            changed=deepcopy(result);changed[field]=value
            with self.assertRaises(ValueError):h.check(manifest,h.b.seal(changed))
        changed=deepcopy(result)
        changed["source_eligibility"]["native_eligible"]=not changed["source_eligibility"]["native_eligible"]
        with self.assertRaises(ValueError):h.check(manifest,h.b.seal(changed))

    def test_failed_preflight_is_not_native_credit(self):
        manifest,result=h.b.read(h.INPUTS),h.b.read(h.RESULTS)
        changed=deepcopy(result)
        execution=h.prior.previous.expand(changed["execution"])
        execution["cases"][0]["event_committed"]=True
        changed["execution"]=h.prior.previous.compact(h.b.seal(execution))
        with self.assertRaisesRegex(ValueError,"native credit"):
            h.check(manifest,h.b.seal(changed))

    def test_signed_enabled_failure_and_stage_pressure(self):
        manifest,result,pressure=map(h.b.read,(h.INPUTS,h.RESULTS,h.PRESSURE))
        checked=h.check_pressure(manifest,result,pressure)
        self.assertLess(Q(checked["worst"]["interval"][1]),0)
        self.assertLess(checked["worst"]["represented_output"],0)
        self.assertLess(Q(checked["negative_upper_with_budget"]),0)
        self.assertEqual(checked["native_events"],0)
        for mutate in (
            lambda p:p.update(neighbor_probes=2),
            lambda p:p["stages"][0]["input"]["W_A"].__setitem__(0,0.5),
            lambda p:p["stages"][-1].update(resource_intervals=[["0","1"]]*len(p["stages"][-1]["resource_intervals"])),
        ):
            changed=deepcopy(pressure);mutate(changed)
            with self.assertRaises(ValueError):h.check_pressure(manifest,result,h.b.seal(changed))


if __name__=="__main__":unittest.main()

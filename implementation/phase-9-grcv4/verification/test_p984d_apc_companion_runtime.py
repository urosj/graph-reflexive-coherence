"""Native source companion binding and retained lifecycle pressure."""

from copy import deepcopy
import unittest
from unittest.mock import patch

import p984d_apc_companion_runtime as n


class NativeCompanionTests(unittest.TestCase):
    def test_retained_binding_and_lifecycle_without_rerun(self):
        manifest,result=n.b.read(n.INPUTS),n.b.read(n.RESULTS)
        with patch.object(n.r,"perform_step",side_effect=AssertionError("native rerun")), \
                patch.object(n.r,"event_capture",side_effect=AssertionError("native event")):
            value=n.check(manifest,result)
        self.assertEqual(value["accepted_cells"],0)
        self.assertEqual((value["native_event_attempts"],value["committed_events"]),(1,0))
        self.assertFalse(value["uniform_neighborhood_proved"])
        altered=deepcopy(manifest)
        altered["expected_source"]=n.b.read(n.c.prior.INPUTS)["expected_source"]
        with self.assertRaises(ValueError):n.check_manifest(n.b.seal(altered))
        altered=deepcopy(manifest)
        altered["cases"][0]["request"]["resource_distribution"]=[.25,.375,.375]
        with self.assertRaises(ValueError):n.check_manifest(n.b.seal(altered))
        changed=deepcopy(result)
        changed["user_accepted"]=True
        with self.assertRaises(ValueError):n.check(manifest,n.b.seal(changed))

    def test_trigger_equations_and_full_rollback_mutations(self):
        manifest,result=n.b.read(n.INPUTS),n.b.read(n.RESULTS)
        seed=n.r.state(manifest["expected_source"])
        self.assertEqual(result["trigger_certificate"],n.trigger_certificate(seed))
        self.assertTrue(result["trigger_certificate"]["gradient_gate_excluded"])
        for fault in ("published","state","stale_current","charge"):
            changed=deepcopy(result)
            execution=n.previous.expand(changed["execution"])
            event=execution["cases"][0]["event"]
            if fault=="published":event["publication"]=[{}]
            elif fault=="state":event["checkpoint"]["state"]["inputs"]["current"]["C"][0]+=1
            elif fault=="stale_current":event["detections"][0]["current"][0]+=1
            else:event["actual_target"]["inputs"]["Q_target"]+=1
            changed["execution"]=n.previous.compact(n.b.seal(execution))
            with self.assertRaises(ValueError):n.check(manifest,n.b.seal(changed))


if __name__=="__main__":unittest.main()

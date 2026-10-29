from copy import deepcopy
import unittest

import p984h_ccipc as n


class LargeConsumerTests(unittest.TestCase):
    def test_small_step_and_held_source_guard(self):
        with n.compute_worker():
            before=n.b.GeometryStageInputs.from_payload(n.b.read(n.r.INPUTS)['initial_inputs'])
            value,after=n.observe_step(before)
            self.assertEqual(n.check_step(value,numerics=True),after)
            bad=deepcopy(value)
            bad['carrier_calls'][0]['source'][0]+=1e-12
            with self.assertRaises(ValueError):
                n.check_step(bad)

    def test_small_event_and_exact_replay(self):
        with n.compute_worker():
            old=n.b.read(n.r.INPUTS)
            value=n.event(n.r.state(old['expected_source']),old['cases'][0])
            self.assertTrue(value['event']['replay_identical'])
            self.assertEqual(value['native_steps'],0)
            self.assertTrue(value['rollback_exact'])


if __name__=='__main__':
    unittest.main()

"""Non-numerical adapter pressure before any large A_CI .h execution."""
from contextlib import ExitStack
from copy import deepcopy
from dataclasses import replace
import unittest
from unittest.mock import patch

import p984h_aci as m
from pygrc.models import grc_v4_ci as ci


class PreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = m.accepted_source()
        cls.initial, cls.subject, cls.backend = m.seed()

    def test_preflight_cannot_execute_native_or_interval_roots(self):
        with ExitStack() as stack:
            for module, name in ((m.base, 'execute'), (m.base.oracle, 'analyze'),
                    (m.base.f, 'joint_box'), (ci, 'CandidateCIRoot'),
                    (ci, 'ProvisionalCandidateCIStep'), (m.native, 'ProvisionalCandidateCIStep'),
                    (m.native, 'GRC9V4ACIOperation')):
                stack.enter_context(patch.object(module, name, side_effect=AssertionError('numerics forbidden')))
            stack.enter_context(patch.object(m, 'seed', return_value=(self.initial, self.subject, self.backend)))
            value = m.preflight()
        self.assertEqual((value['native_steps'], value['native_events'], value['native_roots']), (0, 0, 0))

    def test_full_joint_comparator_not_current_only(self):
        expected = self.record['result']
        for field in ('represented_geometry_digest', 'selected_joint_point_digest', 'certificate', 'evaluations'):
            with self.subTest(field=field):
                changed = deepcopy(expected)
                changed['roots']['current'][field] = None
                with self.assertRaisesRegex(ValueError, 'whole source result'):
                    m.compare_source_result(changed, expected)
        m.compare_source_result(deepcopy(expected), expected)

    def test_writer_reset_and_clock_mutations_rejected(self):
        for field in ('after_W_A', 'after_C', 'after_time', 'after_step_index'):
            with self.subTest(field=field):
                result = deepcopy(self.record['result'])
                if isinstance(result[field], list):
                    result[field][0] += 0.01
                else:
                    result[field] += 1
                with self.assertRaisesRegex(ValueError, 'source after identity'):
                    m.poststate(self.initial, result)
        swapped = replace(self.initial, inputs=replace(self.initial.inputs,
            current=self.initial.inputs.reset, reset=self.initial.inputs.current))
        with self.assertRaisesRegex(ValueError, 'source before identity'):
            m.poststate(swapped, self.record['result'])

    def test_fresh_policy_binds_both_actual_histories(self):
        post = m.poststate(self.initial, self.record['result'])
        request = m.fresh_request(post)
        self.assertEqual(request['history_policy'], m.aos_history_policy(post.inputs.current, post.inputs.reset))
        self.assertNotEqual(request['history_policy'], m.aos_history_policy(
            self.initial.inputs.current, self.initial.inputs.reset))
        self.assertEqual(request['source_state_digest'], post.scientific_digest)
        self.assertEqual(post.inputs.reset, self.initial.inputs.reset)

    def test_exact_geometry_normalization_and_mutation(self):
        self.assertEqual(m.digest(m.canonical_hodge([[1, 0], [0, 1]])),
                         m.digest(m.canonical_hodge([[1., 0.], [0., 1.]])))
        self.assertNotEqual(m.digest(m.canonical_hodge([[1., 2**-52], [2**-52, 1.]])),
                            m.digest(m.canonical_hodge([[1, 0], [0, 1]])))
        for bad in ([[2**53+1]], [[float('inf')]], [[1, 0]], []):
            with self.subTest(bad=bad), self.assertRaises((ValueError, OverflowError)):
                m.canonical_hodge(bad)

    def test_reference_weight_normalization_does_not_hide_mutation(self):
        payload = dict(H1_form=[[1]], reference=dict(reference_hodge=dict(edge_weights={'e': 1})))
        same = deepcopy(payload)
        same['reference']['reference_hodge']['edge_weights']['e'] = 1.0
        self.assertEqual(m.digest(m.canonical_input_payload(payload)), m.digest(m.canonical_input_payload(same)))
        same['reference']['reference_hodge']['edge_weights']['e'] = 1.0000000000000002
        self.assertNotEqual(m.digest(m.canonical_input_payload(payload)), m.digest(m.canonical_input_payload(same)))

    def test_source_adapter_invokes_current_runner_without_old_code(self):
        expected = self.record['result']
        with patch.object(m.base, 'execute', return_value=deepcopy(expected)) as execute, \
                patch.object(m, 'seed', return_value=(self.initial, self.subject, self.backend)):
            output = m.source_adapter(lambda _: None)
        self.assertEqual(execute.call_args.args[:2], ('source', 'current'))
        self.assertEqual(output['result'], expected)
        self.assertEqual(output['request']['source_state_digest'], output['state']['scientific_digest'])


if __name__ == '__main__':
    unittest.main()

"""Focused non-numerical pressure on the capped source runner's bindings."""
from copy import deepcopy
import unittest
from unittest.mock import patch
import p984h_aci_source as m


class SourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old = m.prep.accepted_source()
        cls.initial, _, _ = m.prep.seed()
        cls.post = m.prep.poststate(cls.initial, cls.old['result'])

    def test_fresh_declaration_no_native_event(self):
        with patch.object(m.prep.native, 'GRC9V4ACIOperation', side_effect=AssertionError('no event')):
            result = m.fresh_binding(self.post, self.old['result'], m.prep.fresh_request(self.post))
        self.assertEqual((result['source_nodes'], result['target_nodes']), (100, 107))
        self.assertEqual((result['source_edges'], result['target_edges']), (400, 407))
        self.assertEqual(result['source_state_digest'], self.post.scientific_digest)

    def test_stale_history_and_wrong_source_rejected(self):
        request = m.prep.fresh_request(self.post)
        for field, bad in (('source_state_digest', self.initial.scientific_digest),
                           ('history_policy', m.prep.aos_history_policy(
                               self.initial.inputs.current, self.initial.inputs.reset))):
            with self.subTest(field=field):
                changed = deepcopy(request); changed[field] = bad
                with self.assertRaisesRegex(ValueError, 'fresh source/history'):
                    m.fresh_binding(self.post, self.old['result'], changed)

    def test_trigger_failure_not_promoted(self):
        for field in ('saturated', 'small_gradient', 'strict_hessian_condition'):
            with self.subTest(field=field):
                changed = deepcopy(self.old['result']); changed['poststep_trigger'][field] = False
                with self.assertRaisesRegex(ValueError, 'trigger prerequisites'):
                    m.fresh_binding(self.post, changed, m.prep.fresh_request(self.post))


if __name__ == '__main__':
    unittest.main()

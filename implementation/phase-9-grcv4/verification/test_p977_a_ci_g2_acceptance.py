"""Exact A_CI G2 decision, immutable evidence and bounded discovery reuse."""

from copy import deepcopy
import unittest
from unittest.mock import patch

import phase9_implementation_policy as p
import profile_g2_registry as g
import g2_source_reuse as reuse


class AcceptanceTests(unittest.TestCase):
    def test_exact_decision_and_discovery_without_initializer_or_parameter_promotion(self):
        from pygrc.models.grc_v4_profile import get_supported_profile, list_supported_profiles, resolve_profile
        rows = g.registry(p.ROOT)['records']
        row = rows[2]
        accepted = g.common_acceptance(p.ROOT,row)
        profile = g.checked_profile(p.ROOT,row)
        self.assertEqual(set(list_supported_profiles()),set(accepted['accepted_generic_runtime_support']))
        self.assertEqual(len(list_supported_profiles()),3)
        self.assertEqual(get_supported_profile(row['complete_profile_id']).to_payload(),profile)
        reviewed = g.bound_record(p.ROOT,row['review'])
        with self.assertRaises(ValueError): get_supported_profile(reviewed['ordered_scope']['initializer_target'])
        different=deepcopy(profile['params_resolved']);different['candidate']['gamma']=0.2
        # Resolution is allowed; it cannot advertise another parameter setting.
        from pygrc.models.grc_v4_codec import payload_identity
        identity=deepcopy(profile['identity_payload'])
        identity['params_hash']=payload_identity('resolved_params',different)
        changed=resolve_profile(different,identity)
        with self.assertRaises(ValueError): get_supported_profile(changed.complete_profile_id)
        self.assertFalse(accepted['G3_accepted'])
        self.assertFalse(accepted['aggregate_closed'])
        self.assertFalse(accepted['all_ordered_pairs_verified'])
        self.assertEqual(accepted['new_runtime_iterations_authorized'],[])

    def test_source_reuse_rejects_unrelated_hashes_and_rehashed_record(self):
        value=reuse.record()
        for name,row in value['changes'].items():
            with self.subTest(path=name):
                self.assertEqual(p.sha((p.ROOT/name).read_bytes()),row['after_sha256'])
                self.assertEqual(reuse.retained_bindings({name:row['after_sha256']}),{name:row['before_sha256']})
                with self.assertRaises(ValueError): reuse.retained_bindings({name:'0'*64})
        target=next(iter(value['changes']))
        bad=deepcopy(value);bad['changes'][target]['after_sha256']='0'*64
        bad['record_digest']=p.digest_record(bad)
        with patch.object(p,'read',return_value=bad):
            with self.assertRaises(ValueError): reuse.record()
        self.assertFalse(reuse.matches({'extra':'0'*64},{}))

    def test_review_execution_and_prior_acceptances_remain_byte_exact(self):
        names=[p.PHASE+'tranche-7/P9-7.7-'+n for n in (
            'A_CI-G2Review.json','A_CI-G2Review.md','A_CI-G2Interface.json',
            'A_CI-LocalProduct.json','A_CI-Crossings.json',
            'A_OS-G2Acceptance.json','A_OS-G2SourceReuse.json')]+[p.G2_ACCEPTANCE]
        for name in names:
            with self.subTest(path=name):
                self.assertEqual((p.ROOT/name).read_bytes(),p.git(p.ROOT,'show','fa94cd2:'+name))


if __name__ == '__main__':
    unittest.main()

"""Exact A_PC decision, unchanged evidence, and finite source-reuse pressure."""

from copy import deepcopy
import unittest
from unittest.mock import patch

import phase9_implementation_policy as p
import profile_g2_registry as g
import a_pc_g2_source_reuse as reuse


class AcceptanceTests(unittest.TestCase):
    def test_exact_discovery_and_no_control_or_target_promotion(self):
        from pygrc.models.grc_v4_profile import get_supported_profile, list_supported_profiles, resolve_profile
        from pygrc.models.grc_v4_codec import payload_identity
        row = next(r for r in g.registry(p.ROOT)['records'] if r['profile_family_id']=='A_PC')
        self.assertEqual(row['profile_family_id'], 'A_PC')
        accepted = g.common_acceptance(p.ROOT, row)
        profile = g.checked_profile(p.ROOT, row)
        self.assertLessEqual(set(accepted['accepted_generic_runtime_support']), set(list_supported_profiles()))
        self.assertEqual(len(list_supported_profiles()), 6)
        self.assertEqual(get_supported_profile(row['complete_profile_id']).to_payload(), profile)
        proposal = g.bound_record(p.ROOT, row['review'])
        for target in ('initializer_target',):
            with self.assertRaises(ValueError): get_supported_profile(proposal['ordered_scope'][target])
        params = deepcopy(profile['params_resolved'])
        params['candidate']['chi_A'] = 0.
        identity = deepcopy(profile['identity_payload'])
        identity['params_hash'] = payload_identity('resolved_params', params)
        control = resolve_profile(params, identity)
        with self.assertRaises(ValueError): get_supported_profile(control.complete_profile_id)
        for flag in ('G3_accepted', 'aggregate_closed', 'all_ordered_pairs_verified'):
            self.assertFalse(accepted[flag])
        self.assertEqual(accepted['new_runtime_iterations_authorized'], [])
        self.assertEqual(accepted['admitted_specialization_support_sets'], [])
        self.assertEqual(g.support_before(p.ROOT, row['complete_profile_id']), accepted['predecessor_support'])

    def test_exact_source_projection_and_drift_rejection(self):
        value = reuse.record()
        for name, row in value['changes'].items():
            with self.subTest(path=name):
                live = p.sha((p.ROOT/name).read_bytes())
                from c_pc_g2_source_reuse import retained_bindings as successor
                self.assertEqual(successor({name:live})[name], row['after_sha256'])
                self.assertEqual(reuse.retained_bindings({name:live}), {name:row['before_sha256']})
                self.assertTrue(p.g2_bindings_match({name:row['before_sha256']}, {name:live}))
                with self.assertRaises(ValueError): reuse.retained_bindings({name:'0'*64})
        target = next(iter(value['changes']))
        bad = deepcopy(value); bad['changes'][target]['after_sha256'] = '0'*64
        bad['record_digest'] = p.digest_record(bad)
        with patch.object(p, 'read', return_value=bad):
            with self.assertRaises(ValueError): reuse.record()
        with patch.object(p, 'sha', return_value='0'*64):
            with self.assertRaises(ValueError): reuse.retained_bindings({target:value['changes'][target]['after_sha256']})
        self.assertFalse(p.g2_bindings_match({'unrelated':'0'*64}, {}))

    def test_review_runs_and_prior_acceptances_unchanged(self):
        prefix = p.PHASE+'tranche-7/P9-7.7-'
        names = [prefix+'A_PC-'+suffix for suffix in (
            'G2Review.json', 'G2Review.md', 'G2Interface.json', 'LocalProduct.json', 'Crossings.json')]
        names += [prefix+family+'-'+suffix for family in ('A_CI', 'A_OS', 'C_CI')
                  for suffix in ('G2Acceptance.json', 'G2SourceReuse.json', 'G2Review.json', 'G2Interface.json')]
        names += [p.G2_ACCEPTANCE]
        for name in names:
            with self.subTest(path=name):
                self.assertEqual((p.ROOT/name).read_bytes(), p.git(p.ROOT, 'show', reuse.BASE+':'+name))


if __name__ == '__main__':
    unittest.main()

"""Shared G2 plumbing pressure; synthetic acceptance is not execution credit."""

import ast
from copy import deepcopy
import json
import subprocess
import sys
import unittest
from unittest.mock import patch

import profile_g2_registry as g
import phase9_implementation_policy as p


class RegistryTests(unittest.TestCase):
    def test_real_legacy_acceptances_and_proposal_remain_distinct(self):
        result = g.checked(p.ROOT)
        self.assertEqual(result['profiles'],[g.view(row) for row in g.registry(p.ROOT)['records']])
        self.assertEqual([(r['profile_family_id'], r['state']) for r in result['profiles'] if r['state']=='accepted'],
                         [('C_OS', 'accepted'), ('A_OS', 'accepted'), ('A_CI', 'accepted'), ('C_CI', 'accepted')])
        for row in result['profiles']:
            if row['state']=='proposed':
                self.assertFalse(row['G2_accepted'])
                self.assertNotIn(row['complete_profile_id'],result['accepted_generic_runtime_support'])
        self.assertEqual(len(result['accepted_generic_runtime_support']), 4)
        self.assertIn(result['profiles'][2]['complete_profile_id'], result['accepted_generic_runtime_support'])
        self.assertEqual(g.support_before(p.ROOT, result['profiles'][2]['complete_profile_id']),
                         sorted(r['complete_profile_id'] for r in result['profiles'][:2]))
        with self.assertRaises(ValueError): g.support_before(p.ROOT, 'unregistered')

    def test_rehashed_untrusted_rosters_cannot_create_authority(self):
        value = g.registry(p.ROOT)
        edits = {
            'demoted_acceptance': lambda v: v['records'][2].update(state='proposed'),
            'changed_review': lambda v: v['records'][2]['review'].update(record_digest='0'*64),
            'invented_acceptance': lambda v: v['records'][2].update(acceptance=v['records'][1]['acceptance']),
            'duplicate': lambda v: v['records'].append(deepcopy(v['records'][0])),
            'missing': lambda v: v['records'].pop(0),
            'alias': lambda v: v['records'][2].update(complete_profile_id='A_CI'),
            'changed_order': lambda v: v['records'].reverse(),
            'unknown_schema': lambda v: v.update(schema='unknown'),
        }
        for label, edit in edits.items():
            with self.subTest(label=label):
                bad = deepcopy(value); edit(bad); bad['record_digest'] = p.digest_record(bad)
                with self.assertRaises(ValueError): g.validate_registry(bad)
        with patch.object(g, 'browser_source', return_value='altered browser roster'):
            with self.assertRaises(ValueError): g.registry(p.ROOT)

    def test_proposal_semantic_ceilings_even_under_rehashed_fixture(self):
        row = deepcopy(g.registry(p.ROOT)['records'][2])
        row.update(state='proposed', acceptance=None)  # historical proposal test fixture
        proposal = g.bound_record(p.ROOT, row['review'])
        edits = {
            'premature_G2': lambda v: v.update(G2_accepted=True),
            'premature_user': lambda v: v.update(user_accepted=True),
            'G3': lambda v: v.update(G3_accepted=True),
            'aggregate': lambda v: v.update(aggregate_closed=True),
            'new_support': lambda v: v.update(new_G2_support=[row['complete_profile_id']]),
            'all_pairs': lambda v: v['ordered_scope'].update(all_ordered_pairs_verified=True),
            'borrowed_target': lambda v: v.update(proposed_additional_support=[v['ordered_scope']['initializer_target']]),
            'declaration': lambda v: v['nomination']['params_resolved']['candidate'].update(gamma=0),
        }
        for label, edit in edits.items():
            with self.subTest(label=label):
                bad = deepcopy(proposal); edit(bad); bad['record_digest'] = p.digest_record(bad)
                with patch.object(g, 'bound_record', return_value=bad):
                    with self.assertRaises((ValueError, KeyError)): g.checked_profile(p.ROOT, row)

    def test_common_acceptance_schema_without_accepting_real_proposal(self):
        """In-memory adapter fixture only; Git/acceptance input is test-supplied."""
        row = deepcopy(g.registry(p.ROOT)['records'][2])
        proposal = g.bound_record(p.ROOT, row['review'])
        review_text = p.PHASE + 'tranche-7/P9-7.7-A_CI-G2Review.md'
        def ref(path):
            return dict(path=path, sha256=p.sha((p.ROOT/path).read_bytes()))
        value = dict(schema=g.ACCEPTANCE_SCHEMA, status='accepted_by_user', gate=row['gate'],
            reviewed_commit='synthetic_adapter_test_only',
            review=dict(ref(row['review']['path']), record_digest=row['review']['record_digest']),
            review_text=ref(review_text), accepted_profile=proposal['nomination'],
            accepted_additional_support=proposal['proposed_additional_support'],
            predecessor_support=proposal['accepted_support_unchanged'], releases=proposal['releases'],
            accepted_generic_runtime_support=sorted(proposal['accepted_support_unchanged']+proposal['proposed_additional_support']),
            G2_accepted=True, G3_accepted=False, aggregate_closed=False, all_ordered_pairs_verified=False,
            admitted_specialization_support_sets=[], new_runtime_iterations_authorized=[])
        row.update(state='accepted', acceptance=dict(path='synthetic-acceptance.json',record_digest='test-only'))
        def check(v):
            def bound(root, reference):
                return v if reference == row['acceptance'] else proposal
            def git(root, *args):
                if args[:2] == ('merge-base', '--is-ancestor'): return b''
                self.assertEqual(args[0], 'show')
                return (p.ROOT/args[1].split(':',1)[1]).read_bytes()
            with patch.object(g, 'bound_record', side_effect=bound), patch.object(p, 'git', side_effect=git):
                return g.checked_profile(p.ROOT, row)
        self.assertEqual(check(value), proposal['nomination'])
        for label, edit in {
            'runtime_permission': lambda v: v.update(new_runtime_iterations_authorized=['P9-8.1']),
            'specialization': lambda v: v.update(admitted_specialization_support_sets=['GRC9V4']),
            'G3': lambda v: v.update(G3_accepted=True),
            'all_pairs': lambda v: v.update(all_ordered_pairs_verified=True),
            'aggregate': lambda v: v.update(aggregate_closed=True),
            'unaccepted': lambda v: v.update(status='proposed'),
            'different_predecessor': lambda v: v.update(predecessor_support=[]),
            'different_release': lambda v: v.update(releases={}),
            'review_hash': lambda v: v['review'].update(sha256='0'*64),
            'review_text_hash': lambda v: v['review_text'].update(sha256='0'*64),
        }.items():
            with self.subTest(label=label):
                bad=deepcopy(value); edit(bad)
                with self.assertRaises((ValueError, KeyError)): check(bad)

    def test_discovery_checks_every_declaration_not_only_latest(self):
        from pygrc.models.grc_v4_profile import get_supported_profile, list_supported_profiles
        ids = sorted(list_supported_profiles())
        profiles = {key:get_supported_profile(key).to_payload() for key in ids}
        g.check_discovery(profiles, ids, get_supported_profile)
        for supported in (ids[:-1], ids+['unaccepted']):
            with self.assertRaises(ValueError): g.check_discovery(profiles, supported, get_supported_profile)
        for target in ids:
            def wrong(key):
                return get_supported_profile(next(k for k in ids if k != key)) if key == target else get_supported_profile(key)
            with self.assertRaises(ValueError): g.check_discovery(profiles, ids, wrong)

    def test_shared_projection_and_browser_metrics_without_status_rerun(self):
        """Synthetic common-view fixture, not a second full status execution."""
        rows = g.registry(p.ROOT)['records']
        support = sorted(r['complete_profile_id'] for r in rows if r['state']=='accepted')
        value = dict(profile_g2=[g.view(r) for r in rows], g2_acceptance={})
        for row in rows[1:]:
            raw = g.bound_record(p.ROOT, row['review'])
            reviewed = dict(row['review_metrics'], record_path=row['review']['path'],
                record_digest=row['review']['record_digest'], gate=row['gate'],
                status='pass_proposal_pending_G2_acceptance', proposed_additional_support=raw['proposed_additional_support'],
                accepted_support_unchanged=raw['accepted_support_unchanged'], obligations=raw['obligations'],
                G2_accepted=False, user_accepted=False, G3_accepted=False, aggregate_closed=False,
                all_ordered_pairs_verified=False, new_G2_support=[])
            value[row['view_key']] = g.project_review(p.ROOT,row,reviewed,support)
            value[row['bounded_view_key']] = dict(user_accepted=True)
            bad=deepcopy(reviewed);bad['catalog_cells']+=1
            with self.assertRaises(ValueError): g.project_review(p.ROOT,row,bad,support)
            bad=deepcopy(row);bad['review_metrics']['catalog_cells']+=1
            with self.assertRaises(ValueError): g.checked_profile(p.ROOT,bad)
        tool=p.ROOT/p.SIDE/'tool';sys.path.insert(0,str(tool/'src'))
        from grcv4_explorer.tooling import managed_node,tool_environment
        code="""
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {checkedG2} from './verification.js';
const v=JSON.parse(readFileSync(0,'utf8'));
checkedG2(v,true);
checkedG2({},false);
assert.throws(()=>checkedG2(v,false));
for(const key of ['a_os_g2_review','a_ci_g2_review','c_ci_g2_review']) {
  for(const metric of ['catalog_cells','supplemental_interface_methods','numerical_tests_rerun']) {
    const bad=structuredClone(v); bad[key][metric]++;
    assert.throws(()=>checkedG2(bad,true));
  }
}
console.log('SHARED_G2_BROWSER_PASS');
"""
        result=subprocess.run([str(managed_node()),'--input-type=module','-e',code],
            cwd=tool/'phase9-web',input=json.dumps(value),text=True,capture_output=True,
            env=tool_environment(),timeout=30)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('SHARED_G2_BROWSER_PASS',result.stdout)

    def test_accepted_evidence_and_runtime_permissions_are_unchanged(self):
        paths = [p.G2_ACCEPTANCE] + [p.PHASE+'tranche-7/P9-7.7-'+name for name in (
            'A_OS-G2Acceptance.json', 'A_OS-G2Review.json', 'A_OS-G2Interface.json',
            'A_OS-G2SourceReuse.json', 'A_CI-LocalProduct.json', 'A_CI-Crossings.json')]
        for name in paths:
            with self.subTest(path=name):
                self.assertEqual((p.ROOT/name).read_bytes(), p.git(p.ROOT,'show','e883ede:'+name))
        name=p.HERE+'phase9_implementation_policy.py'
        def leaf(source):
            return ast.dump(next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=='leaf_permissions'))
        self.assertEqual(leaf((p.ROOT/name).read_text()),leaf(p.git(p.ROOT,'show','e883ede:'+name)))


if __name__ == '__main__':
    unittest.main()

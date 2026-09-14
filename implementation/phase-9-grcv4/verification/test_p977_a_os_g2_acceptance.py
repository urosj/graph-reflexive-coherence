"""Acceptance/discovery pressure without rerunning numerical evidence."""

from copy import deepcopy
import json
import subprocess
import sys
import unittest
from unittest.mock import patch

import phase9_implementation_policy as p
import a_os_g2_source_reuse as reuse
from pygrc.models.grc_v4_profile import get_supported_profile, list_supported_profiles


class AcceptanceTests(unittest.TestCase):
    def test_browser_requires_acceptance_view(self):
        tool = p.ROOT / p.SIDE / 'tool'
        sys.path.insert(0, str(tool / 'src'))
        from grcv4_explorer.tooling import managed_node, tool_environment
        from profile_g2_registry import registry, view
        fixture = dict(profile_g2=[view(r) for r in registry(p.ROOT)['records']], g2_acceptance={})
        code = """
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {checkedG2} from './verification.js';
const fixture=JSON.parse(readFileSync(0,'utf8'));
for (const view of [undefined, null]) {
  assert.throws(() => checkedG2({...fixture, a_os_g2_review:view}, true), /Missing registered G2 view/);
}
"""
        result = subprocess.run([str(managed_node()), '--input-type=module', '-e', code],
            cwd=tool / 'phase9-web', input=json.dumps(fixture), capture_output=True, text=True,
            env=tool_environment(), timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_exact_discovery_and_detached_declaration(self):
        accepted = p.accepted_a_os_g2(p.ROOT)
        self.assertEqual(set(p.accepted_generic_support(p.ROOT)), set(list_supported_profiles()))
        self.assertLessEqual(set(accepted['accepted_generic_runtime_support']), set(list_supported_profiles()))
        key = accepted['accepted_additional_support'][0]
        profile = get_supported_profile(key)
        self.assertEqual(profile.to_payload(), accepted['accepted_profile'])
        detached = profile.to_payload()
        detached.clear()
        self.assertEqual(get_supported_profile(key).to_payload(), accepted['accepted_profile'])
        self.assertFalse(accepted['G3_accepted'])
        self.assertFalse(accepted['aggregate_closed'])
        self.assertFalse(accepted['all_ordered_pairs_verified'])

    def test_original_review_and_execution_records_preserved(self):
        for suffix in ('G2Review', 'G2Interface', 'LocalProduct', 'Crossings'):
            name = p.PHASE + 'tranche-7/P9-7.7-A_OS-' + suffix + '.json'
            self.assertEqual((p.ROOT / name).read_bytes(), p.git(p.ROOT, 'show', reuse.BASE + ':' + name))

    def test_exact_reuse_and_unrelated_source_reject(self):
        value = p.read(p.ROOT / reuse.RECORD)
        current = {n: row['after_sha256'] for n, row in value['changes'].items()}
        old = {n: row['before_sha256'] for n, row in value['changes'].items()}
        self.assertEqual(reuse.retained_bindings(current), old)
        bad = dict(current)
        bad[next(iter(bad))] = '0' * 64
        with self.assertRaises(ValueError):
            reuse.retained_bindings(bad)
        forged = deepcopy(value)
        forged['changes'][next(iter(bad))]['after_sha256'] = '0' * 64
        forged['record_digest'] = p.digest_record(forged)
        with patch.object(p, 'read', return_value=forged), self.assertRaises(ValueError):
            reuse.retained_bindings(current)

    def test_rehashed_acceptance_expansion_rejects(self):
        value = p.accepted_a_os_g2(p.ROOT)
        original = p.read
        for field, replacement in (('G3_accepted', True), ('aggregate_closed', True),
                                   ('all_ordered_pairs_verified', True),
                                   ('accepted_additional_support', ['A_OS'])):
            bad = deepcopy(value)
            bad[field] = replacement
            bad['record_digest'] = p.digest_record(bad)
            def read(path):
                return bad if str(path).endswith('P9-7.7-A_OS-G2Acceptance.json') else original(path)
            with self.subTest(field=field), patch.object(p, 'read', side_effect=read), self.assertRaises(ValueError):
                p.accepted_a_os_g2(p.ROOT)


if __name__ == '__main__':
    unittest.main()

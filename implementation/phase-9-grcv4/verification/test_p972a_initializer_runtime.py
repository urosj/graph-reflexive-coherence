"""Read-only retained-record pressure; no numerical replay."""
from copy import deepcopy
from io import BytesIO
import importlib.util
import json
from pathlib import Path
import sys
import subprocess
import unittest
from unittest.mock import patch

import verify_p972a_initializer_runtime as runtime


class CodecReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = runtime.p.ROOT
        current = runtime.p.read(root / runtime.RECORD)
        old = runtime.p.read(root / runtime.p.PHASE / 'tranche-7/P9-7.2a-Migrations.json')
        cls.receipts = (old['cases']['A_CIPC_PC']['receipts'][0],
                        current['cases']['A_OS']['receipts'][0])

    def test_plain_and_fragment_references_accept_both_receipt_versions(self):
        from pygrc.models.grc_v4_codec import (
            canonical_json_bytes, decode_canonical_json, validate_payload,
        )
        for receipt in self.receipts:
            for name, value in (('successful_receipt_identity_payload', receipt['identity_payload']),
                                ('successful_receipt_envelope', receipt)):
                for ref in (name, '#/$defs/' + name):
                    with self.subTest(version=receipt['identity_payload']['schema_version'], ref=ref):
                        self.assertEqual(validate_payload(ref, value), value)
                        self.assertEqual(validate_payload(
                            ref, decode_canonical_json(canonical_json_bytes(value))), value)

    def test_fragment_dispatch_keeps_closed_shapes_and_version_boundaries(self):
        from pygrc.models.grc_v4_codec import V4SchemaError, validate_payload
        receipt = self.receipts[1]
        for name, value in (('successful_receipt_identity_payload', receipt['identity_payload']),
                            ('successful_receipt_envelope', receipt)):
            for alteration in ('missing_pair', 'extra', 'unknown_version'):
                bad = deepcopy(value)
                payload = bad.get('identity_payload', bad)
                if alteration == 'missing_pair':
                    del payload['initializer_pair_id']
                elif alteration == 'extra':
                    payload['unexpected'] = True
                else:
                    payload['schema_version'] = 'grcv4-profile-migration-receipt-v999'
                for ref in (name, '#/$defs/' + name):
                    with self.subTest(ref=ref, alteration=alteration), self.assertRaises(V4SchemaError):
                        validate_payload(ref, bad)
        for name in ('migration_receipt_payload', 'unknown_receipt'):
            for ref in (name, '#/$defs/' + name):
                with self.subTest(ref=ref), self.assertRaises(V4SchemaError):
                    validate_payload(ref, receipt['identity_payload'])
        for ref in ('#/$defs/#/$defs/successful_receipt_envelope',
                    'https://invalid.example/schema#/$defs/successful_receipt_envelope'):
            with self.subTest(ref=ref), self.assertRaises(V4SchemaError):
                validate_payload(ref, receipt)


class RuntimeEvidenceTests(unittest.TestCase):
    def test_reference_fix_does_not_waive_other_source_changes(self):
        sources = runtime.bindings()
        value = runtime.p.read(runtime.p.ROOT / runtime.RECORD)
        self.assertEqual(runtime.execution_sources(value, sources), value['source_bindings'])
        for name in (runtime.CODEC, runtime.STATUS_API, runtime.EVENT_PACKAGE_CODEC, 'src/pygrc/models/grc_v4_initializer.py'):
            bad = {**sources, name: '0' * 64}
            with self.subTest(path=name), self.assertRaises(ValueError):
                runtime.execution_sources(value, bad)
        with self.assertRaises(ValueError):
            runtime.execution_sources(value, {k: v for k, v in sources.items() if k != runtime.EVENT_PACKAGE_CODEC})
        rewritten = deepcopy(value)
        rewritten['created_utc'] = '2000-01-01T00:00:00+00:00'
        rewritten['record_digest'] = runtime.p.digest_record(rewritten)
        with self.assertRaises(ValueError):
            runtime.execution_sources(rewritten, sources)

    def test_retained_record_and_packaged_contract(self):
        current = runtime.check()
        self.assertTrue(current['positive_migration_verified'])
        self.assertTrue(current['aggregate_closed'])
        self.assertTrue(current['user_accepted'])
        self.assertEqual(current['status'], 'accepted')
        self.assertEqual(current['accepted_migration_classes'], runtime.MIGRATION_CLASSES)
        self.assertEqual(current['acceptance_path'], runtime.ACCEPTANCE_REVIEW)
        recorded = runtime.p.read(runtime.p.ROOT / runtime.RECORD)
        self.assertFalse(recorded['aggregate_closed'])
        self.assertFalse(recorded['user_accepted'])
        self.assertEqual(recorded['record_digest'], runtime.ACCEPTED_RECORD_DIGEST)

    def test_missing_or_changed_acceptance_cannot_close_the_aggregate(self):
        with patch.object(runtime.p, 'sha', return_value='0' * 64), self.assertRaises(ValueError):
            runtime.acceptance()
        with patch.object(Path, 'read_bytes', side_effect=FileNotFoundError), self.assertRaises(FileNotFoundError):
            runtime.acceptance()

    def test_new_execution_is_not_implicitly_accepted(self):
        replacement = runtime.p.read(runtime.p.ROOT / runtime.RECORD)
        replacement['created_utc'] = '2000-01-01T00:00:00+00:00'
        replacement['record_digest'] = runtime.p.digest_record(replacement)
        with patch.object(runtime.p, 'read', return_value=replacement), self.assertRaises(ValueError):
            runtime.check()

    def test_rehashed_overclaim_and_unbound_source_reject(self):
        sources = runtime.bindings()
        value = runtime.p.read(runtime.p.ROOT / runtime.RECORD)
        for field, replacement in (('aggregate_closed', True), ('source_bindings', {}), ('test_ids', [])):
            bad = deepcopy(value)
            bad[field] = replacement
            bad['record_digest'] = runtime.p.digest_record(bad)
            with self.subTest(field=field), self.assertRaises(ValueError):
                runtime.validate(bad, sources)

    def test_rehashed_receipt_link_does_not_authenticate_pair(self):
        bad = deepcopy(runtime.p.read(runtime.p.ROOT / runtime.RECORD))
        bad['cases']['A_OS']['receipts'][0]['identity_payload']['initializer_pair_id'] = 'grcv4-a-reference-pass-pair-sha256:' + '0'*64
        bad['record_digest'] = runtime.p.digest_record(bad)
        with self.assertRaises(ValueError):
            runtime.validate(bad, runtime.bindings())

    def test_actual_status_notebook_and_http_expose_runtime_separately(self):
        root = runtime.p.ROOT
        tool = root / runtime.p.SIDE / 'tool'
        sys.path.insert(0, str(tool / 'src'))
        from grcv4_explorer.phase9_verification import verification_status
        status = verification_status(root)
        self.assertEqual(status['current_boundary'], 'passed', status.get('error'))
        self.assertEqual(status['initializer_runtime'], runtime.check())
        from verify_p972b_acceptance import check as event_check
        self.assertEqual(status['event_runtime'], event_check())
        self.assertEqual(status['event_runtime']['test_count'], 18)
        self.assertTrue(status['event_runtime']['aggregate_closed'])
        self.assertTrue(status['event_runtime']['user_accepted'])
        from verify_p973_acceptance import check as history_check
        self.assertEqual(status['history_policy_verification'], history_check())
        self.assertEqual(status['history_policy_verification']['test_count'], 9)
        self.assertTrue(status['history_policy_verification']['user_accepted'])
        from verify_p974_acceptance import check as target_check
        self.assertEqual(status['target_reference_verification'], target_check())
        self.assertTrue(status['target_reference_verification']['user_accepted'])
        self.assertTrue(status['target_reference_verification']['aggregate_closed'])
        from verify_p975_acceptance import check as failure_check
        self.assertEqual(status['failure_sequence_verification'], failure_check())
        self.assertTrue(status['failure_sequence_verification']['user_accepted'])
        self.assertTrue(status['failure_sequence_verification']['aggregate_closed'])
        from verify_p976_acceptance import check as lineage_check
        self.assertEqual(status['lineage_ownership_verification'], lineage_check())
        self.assertEqual(status['lineage_ownership_verification']['coherent_parent_rejections'], 10)
        self.assertTrue(status['lineage_ownership_verification']['user_accepted'])
        self.assertTrue(status['lineage_ownership_verification']['aggregate_closed'])
        from verify_p977_profile_review import check as profile_review_check
        self.assertEqual(status['profile_conformance_review'], profile_review_check(prior=status['lineage_ownership_verification']))
        self.assertEqual(status['profile_conformance_review']['required_cells'], 305)
        self.assertEqual(len(status['profile_conformance_review']['held_profiles']), 9)
        self.assertFalse(status['profile_conformance_review']['user_accepted'])
        from verify_p977_a_os_local import check as local_check
        self.assertEqual(status['a_os_local_product'],local_check(initial_review=status['profile_conformance_review']))
        self.assertEqual(status['a_os_local_product']['verified_local_cells'],21)
        self.assertFalse(status['a_os_local_product']['G2_accepted'])
        from verify_p977_a_os_acceptance import check as crossing_check
        self.assertEqual(status['a_os_crossings'],crossing_check(local_product=status['a_os_local_product']))
        self.assertEqual(status['a_os_crossings']['reconciled_crossing_cells'],7)
        self.assertFalse(status['a_os_crossings']['all_ordered_pairs_verified'])
        self.assertTrue(status['a_os_crossings']['user_accepted'])
        self.assertEqual(status['event_runtime']['original_record_digest'],
                         'c3fb9823ae040408fd86963754ce6b3f7acbc897c7a5a88504582193d0cc4391')
        self.assertIn('P9-7.2a is user-accepted and closed', status['next_gate'])
        book = json.loads((tool / 'notebooks/phase9_verification.ipynb').read_text())
        cell = next(c for c in book['cells'] if c['id'] == 'query-status')
        namespace = dict(Path=Path, repo_root=root, PHASE9_REPO_ROOT=root,
                         PHASE9_STATUS_ONLY=True, verification_status=verification_status)
        exec(compile(''.join(cell['source']), 'phase9_verification.ipynb:query-status', 'exec'), namespace)
        self.assertEqual(namespace['phase9_status']['initializer_runtime'], status['initializer_runtime'])
        self.assertEqual(namespace['phase9_status']['event_runtime'], status['event_runtime'])
        self.assertEqual(namespace['phase9_status']['history_policy_verification'], status['history_policy_verification'])
        self.assertEqual(namespace['phase9_status']['target_reference_verification'], status['target_reference_verification'])
        self.assertEqual(namespace['phase9_status']['failure_sequence_verification'], status['failure_sequence_verification'])
        self.assertEqual(namespace['phase9_status']['lineage_ownership_verification'], status['lineage_ownership_verification'])
        self.assertEqual(namespace['phase9_status']['profile_conformance_review'], status['profile_conformance_review'])
        self.assertEqual(namespace['phase9_status']['a_os_local_product'],status['a_os_local_product'])
        self.assertEqual(namespace['phase9_status']['a_os_crossings'],status['a_os_crossings'])
        spec = importlib.util.spec_from_file_location('p972a_runtime_http', tool / 'scripts/serve_phase9.py')
        server = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(server)
        handler = server.Handler.__new__(server.Handler)
        handler.path = '/api/status'
        statuses = []
        handler.send_response = statuses.append
        handler.send_header = lambda *args: None
        handler.end_headers = lambda: None
        handler.wfile = BytesIO()
        handler.do_GET()
        self.assertEqual(statuses, [200])
        self.assertEqual(json.loads(handler.wfile.getvalue())['initializer_runtime'], status['initializer_runtime'])
        self.assertEqual(json.loads(handler.wfile.getvalue())['event_runtime'], status['event_runtime'])
        self.assertEqual(json.loads(handler.wfile.getvalue())['history_policy_verification'], status['history_policy_verification'])
        self.assertEqual(json.loads(handler.wfile.getvalue())['target_reference_verification'], status['target_reference_verification'])
        self.assertEqual(json.loads(handler.wfile.getvalue())['failure_sequence_verification'], status['failure_sequence_verification'])
        self.assertEqual(json.loads(handler.wfile.getvalue())['lineage_ownership_verification'], status['lineage_ownership_verification'])
        self.assertEqual(json.loads(handler.wfile.getvalue())['profile_conformance_review'], status['profile_conformance_review'])
        self.assertEqual(json.loads(handler.wfile.getvalue())['a_os_local_product'],status['a_os_local_product'])
        self.assertEqual(json.loads(handler.wfile.getvalue())['a_os_crossings'],status['a_os_crossings'])
        from grcv4_explorer.tooling import managed_node, tool_environment
        code = """
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {verifiedStatus, canonical} from './verification.js';
const value = JSON.parse(readFileSync(0, 'utf8'));
assert.deepEqual(await verifiedStatus(value), value);
for (const edit of [v=>v.initializer_runtime.aggregate_closed=false,
 v=>v.initializer_runtime.acceptance_sha256='0'.repeat(64),
 v=>v.initializer_runtime.accepted_migration_classes.pop(),
 v=>v.initializer_runtime.new_G2_support=['A_OS'],
 v=>v.initializer_runtime.positive_target_families.pop(),
 v=>v.permitted_runtime_paths.push('src/unrelated.py'),
 v=>v.event_runtime.aggregate_closed=false,
 v=>v.event_runtime.acceptance_sha256='0'.repeat(64),
 v=>v.event_runtime.new_G2_support=['A_OS'],
 v=>v.event_runtime.case_count=0,
 v=>v.history_policy_verification.user_accepted=false,
 v=>v.history_policy_verification.new_G2_support=['A_PC'],
 v=>v.history_policy_verification.regression_record_digest='0'.repeat(64),
 v=>v.target_reference_verification.user_accepted=false,
 v=>v.target_reference_verification.acceptance_sha256='0'.repeat(64),
 v=>v.target_reference_verification.new_G2_support=['C_PC'],
 v=>v.target_reference_verification.c_target_families.pop(),
 v=>v.target_reference_verification.record_digest='0'.repeat(64),
 v=>v.target_reference_verification.reference_rejections=0,
 v=>v.failure_sequence_verification.user_accepted=false,
 v=>v.failure_sequence_verification.acceptance_sha256='0'.repeat(64),
 v=>v.failure_sequence_verification.new_G2_support=['C_PC'],
 v=>v.failure_sequence_verification.rejection_cases=0,
 v=>v.failure_sequence_verification.reset_contexts.pop(),
 v=>v.failure_sequence_verification.record_digest='0'.repeat(64),
 v=>v.lineage_ownership_verification.user_accepted=false,
 v=>v.lineage_ownership_verification.acceptance_sha256='0'.repeat(64),
 v=>v.lineage_ownership_verification.new_G2_support=['A_PC'],
 v=>v.lineage_ownership_verification.coherent_parent_rejections=0,
 v=>v.lineage_ownership_verification.symbolic_rejections=0,
 v=>v.lineage_ownership_verification.record_digest='0'.repeat(64),
 v=>v.profile_conformance_review.user_accepted=true,
 v=>v.profile_conformance_review.new_G2_support=['A_OS'],
 v=>v.profile_conformance_review.G3_accepted=true,
 v=>v.profile_conformance_review.required_cells=0,
 v=>v.profile_conformance_review.held_profiles.pop(),
 v=>v.profile_conformance_review.accepted_aliases.push('A_PC'),
 v=>v.profile_conformance_review.new_execution_credit=305,
 v=>v.profile_conformance_review.record_digest='0'.repeat(64),
 v=>v.a_os_local_product.G2_accepted=true,
 v=>v.a_os_local_product.verified_local_cells=28,
 v=>v.a_os_local_product.remaining_catalog_cases.pop(),
 v=>v.a_os_local_product.complete_profile_id='A_OS',
 v=>v.a_os_local_product.user_accepted=true,
 v=>v.a_os_local_product.record_digest='0'.repeat(64),
 v=>v.a_os_crossings.all_ordered_pairs_verified=true,
 v=>v.a_os_crossings.G2_accepted=true,
 v=>v.a_os_crossings.reconciled_crossing_cells=28,
 v=>v.a_os_crossings.complete_profile_id='A_OS',
 v=>v.a_os_crossings.matrix_scope='all_pairs',
 v=>v.a_os_crossings.record_digest='0'.repeat(64)]) {
 const bad=structuredClone(value); edit(bad); delete bad.status_digest;
 bad.status_digest=createHash('sha256').update(canonical(bad)).digest('hex');
 await assert.rejects(verifiedStatus(bad));
}
const held={...value, current_boundary:'failed_closed', runtime_authorized:false};
await assert.rejects(verifiedStatus(held));
console.log('INITIALIZER_EVENT_RUNTIME_BROWSER_PASS controls=52');
"""
        browser = subprocess.run([str(managed_node()), '--input-type=module', '-e', code],
                                 cwd=tool / 'phase9-web', input=json.dumps(status), capture_output=True,
                                 text=True, env=tool_environment(), timeout=60)
        self.assertEqual(browser.returncode, 0, browser.stderr)
        self.assertIn('INITIALIZER_EVENT_RUNTIME_BROWSER_PASS controls=52', browser.stdout)


if __name__ == '__main__':
    unittest.main()

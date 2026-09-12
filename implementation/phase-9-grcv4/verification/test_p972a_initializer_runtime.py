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
        self.assertIn('P9-7.2a is user-accepted and closed', status['next_gate'])
        book = json.loads((tool / 'notebooks/phase9_verification.ipynb').read_text())
        cell = next(c for c in book['cells'] if c['id'] == 'query-status')
        namespace = dict(Path=Path, repo_root=root, PHASE9_REPO_ROOT=root,
                         PHASE9_STATUS_ONLY=True, verification_status=verification_status)
        exec(compile(''.join(cell['source']), 'phase9_verification.ipynb:query-status', 'exec'), namespace)
        self.assertEqual(namespace['phase9_status']['initializer_runtime'], status['initializer_runtime'])
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
 v=>v.permitted_runtime_paths.push('src/unrelated.py')]) {
 const bad=structuredClone(value); edit(bad); delete bad.status_digest;
 bad.status_digest=createHash('sha256').update(canonical(bad)).digest('hex');
 await assert.rejects(verifiedStatus(bad));
}
const held={...value, current_boundary:'failed_closed', runtime_authorized:false};
await assert.rejects(verifiedStatus(held));
console.log('INITIALIZER_RUNTIME_BROWSER_PASS controls=7');
"""
        browser = subprocess.run([str(managed_node()), '--input-type=module', '-e', code],
                                 cwd=tool / 'phase9-web', input=json.dumps(status), capture_output=True,
                                 text=True, env=tool_environment(), timeout=60)
        self.assertEqual(browser.returncode, 0, browser.stderr)
        self.assertIn('INITIALIZER_RUNTIME_BROWSER_PASS controls=7', browser.stdout)


if __name__ == '__main__':
    unittest.main()

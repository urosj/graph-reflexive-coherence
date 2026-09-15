"""Accepted-record reconciliation and bounded UX pressure; no numerical campaign."""

import ast
from copy import deepcopy
from io import BytesIO
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import phase9_implementation_policy as p
import profile_g2_registry as g
import verify_p977_aggregate as a


class AggregateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.expected = a.build()

    def test_exact_305_cells_and_immutable_original(self):
        value = p.read(p.ROOT/a.RECORD)
        a.validate(value, self.expected)
        self.assertEqual(value['summary']['reconciled_cells'], 305)
        self.assertEqual(value['summary']['unresolved_cells'], 0)
        self.assertEqual(len(value['accepted_generic_runtime_support']), 10)
        self.assertEqual(sum(len(r['cells']) for r in value['profiles'] if r['profile_family']=='C_OS'), 33)
        for row in value['profiles']:
            self.assertEqual(len(row['cells']), 28 if row['profile_family'].startswith('A_') else 33)
            if row['profile_family'] != 'C_OS':
                self.assertEqual(len(row['ordered_scope']['matrix']), 7)
                self.assertFalse(row['ordered_scope']['all_ordered_pairs_verified'])
        initial = p.read(p.ROOT/a.original.RECORD)
        self.assertEqual(initial['summary']['unresolved_new_profile_cells'], 272)
        self.assertFalse(value['user_accepted'])
        self.assertFalse(value['aggregate_closed'])

    def test_rehashed_missing_borrowed_or_overclaimed_aggregate_rejected(self):
        edits = {
            'missing_profile': lambda v: v['profiles'].pop(),
            'duplicate_profile': lambda v: v['profiles'].append(deepcopy(v['profiles'][0])),
            'missing_cell': lambda v: v['profiles'][0]['cells'].pop(),
            'duplicate_cell': lambda v: v['profiles'][0]['cells'].append(deepcopy(v['profiles'][0]['cells'][0])),
            'wrong_nomination': lambda v: v['profiles'][0].update(complete_profile_id=v['profiles'][1]['complete_profile_id']),
            'wrong_acceptance': lambda v: v['profiles'][0].update(acceptance=v['profiles'][1]['acceptance']),
            'borrowed_cell': lambda v: v['profiles'][0]['cells'].__setitem__(0, deepcopy(v['profiles'][1]['cells'][0])),
            'lost_endpoint_scope': lambda v: v['profiles'][0]['ordered_scope'].clear(),
            'lost_debt': lambda v: v['profiles'][0]['authority_and_debt'].clear(),
            'invented_closure': lambda v: v.update(aggregate_closed=True),
            'invented_acceptance': lambda v: v.update(user_accepted=True),
            'all_pairs': lambda v: v.update(all_ordered_pairs_verified=True),
            'G3': lambda v: v.update(G3_accepted=True),
            'runtime': lambda v: v.update(new_runtime_iterations_authorized=['P9-8.1a']),
            'new_support': lambda v: v.update(new_G2_support=['A_CI']),
            'new_credit': lambda v: v['summary'].update(new_execution_credit=305),
            'rerun': lambda v: v['summary'].update(numerical_tests_rerun=305),
            'unbound_input': lambda v: v['input_bindings'].pop(next(iter(v['input_bindings']))),
        }
        for name, edit in edits.items():
            bad = deepcopy(self.expected); edit(bad); bad['record_digest'] = p.digest_record(bad)
            with self.subTest(name=name), self.assertRaises(ValueError): a.validate(bad, self.expected)

    def test_changed_accepted_input_fails_checkpoint_binding(self):
        git = p.git
        def changed(root, *args):
            if args == ('show', a.BASE + ':' + a.original.RECORD): return b'{}'
            return git(root, *args)
        with patch.object(p, 'git', side_effect=changed), self.assertRaisesRegex(ValueError, 'aggregate input changed'):
            a.build()

    def test_actual_http_asset_notebook_and_browser_projection(self):
        tool = p.ROOT/p.SIDE/'tool'
        sys.path.insert(0, str(tool/'src'))
        from grcv4_explorer.tooling import managed_node, tool_environment
        # Real accepted-record projection; bounded transport payload, not a
        # substitute for running the full status/predecessor materializer chain.
        status = dict(current_boundary='passed', profile_aggregate_reconciliation=a.view(self.expected))
        spec = importlib.util.spec_from_file_location('p977_aggregate_http', tool/'scripts/serve_phase9.py')
        server = importlib.util.module_from_spec(spec); spec.loader.exec_module(server)
        handler = object.__new__(server.Handler)
        handler.send_response = lambda code: self.assertEqual(code, 200)
        headers = []
        handler.send_header = lambda *args: headers.append(args)
        handler.end_headers = lambda: None
        handler.path = '/api/status'; handler.wfile = BytesIO()
        with patch.object(server, 'verification_status', return_value=deepcopy(status)):
            handler.do_GET()
        self.assertEqual(json.loads(handler.wfile.getvalue()), status)
        handler.path = '/aggregate-review.js'; handler.wfile = BytesIO()
        handler.do_GET()
        self.assertEqual(handler.wfile.getvalue(), (p.ROOT/a.BROWSER).read_bytes())
        self.assertIn(('Content-Type', 'text/javascript'), headers)
        book = p.read(tool/'notebooks/phase9_verification.ipynb')
        cell = next(c for c in book['cells'] if c['id']=='query-status')
        namespace = dict(Path=Path, repo_root=p.ROOT, PHASE9_REPO_ROOT=p.ROOT,
            PHASE9_STATUS_ONLY=True, verification_status=lambda root: deepcopy(status))
        exec(compile(''.join(cell['source']), 'phase9_verification.ipynb:query-status', 'exec'), namespace)
        self.assertEqual(namespace['phase9_status'], status)
        code = """
import {readFileSync} from 'node:fs';
import {checkedAggregate} from './verification.js';
const value=JSON.parse(readFileSync(0,'utf8'));
checkedAggregate(value,true);
console.log('Python/browser aggregate projection agrees');
"""
        completed = subprocess.run([str(managed_node()), '--input-type=module', '-e', code],
            cwd=tool/'phase9-web', env=tool_environment(), input=json.dumps(status),
            text=True, capture_output=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn('projection agrees', completed.stdout)

    def test_materialized_status_alignment_and_next_gate(self):
        roster = g.registry(p.ROOT)
        views = {'profile_g2': [g.view(r) for r in roster['records']]}
        for row in roster['records']:
            if row['adapter'] != 'historical_c_os':
                views[row['view_key']] = dict(status='accepted', G2_accepted=True,
                    record_digest=row['review']['record_digest'], acceptance_digest=row['acceptance']['record_digest'])
        # Only transport wiring is synthetic; the expected reconciliation above
        # is built from real accepted records. Do not rerun every child checker.
        with patch.object(a, 'build', return_value=self.expected):
            actual = g._checker(p.ROOT, 'verify_p977_aggregate')(profile_views=views)
            bad = deepcopy(views); bad['c_rg2b_g2_review']['G2_accepted'] = False
            with self.assertRaises(ValueError): a.check(profile_views=bad)
            bad = deepcopy(views); bad['profile_g2'].pop()
            with self.assertRaises(ValueError): a.check(profile_views=bad)
        source = (p.ROOT/p.SIDE/'tool/src/grcv4_explorer/phase9_verification.py').read_text()
        tree = ast.parse(source)
        node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name=='_profile_next_gate')
        namespace = {}
        exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])), 'next-gate', 'exec'), namespace)
        views['profile_aggregate_reconciliation'] = actual
        message = namespace['_profile_next_gate'](views)
        self.assertIn('305/305', message)
        self.assertIn('aggregate review and acceptance remain pending', message)
        self.assertIn('P9-7.8', message)
        self.assertIn("profile_views['profile_aggregate_reconciliation'] = _checker(root, 'verify_p977_aggregate')", source)
        self.assertLess(source.index("profile_views['profile_aggregate_reconciliation'] ="), source.index('profile_view_keys = set(profile_views)'))


if __name__ == '__main__':
    unittest.main()

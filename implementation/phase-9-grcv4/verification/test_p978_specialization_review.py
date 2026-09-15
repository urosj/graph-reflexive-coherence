"""Bounded admission-review pressure; does not execute specialization science."""
from copy import deepcopy
import importlib.util
from io import BytesIO
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import phase9_implementation_policy as p
import profile_g2_registry as g
import verify_p978_specialization_review as r
import phase9_specialization_acceptance as admission


class SpecializationReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.expected = r.build()

    def test_exact_predecessors_authority_vectors_and_pending_cells(self):
        v = p.read(p.ROOT / r.RECORD)
        r.validate(v, self.expected)
        self.assertEqual(len(v['profiles']), 10)
        self.assertEqual(len(v['authority']), 73)
        self.assertEqual(len(v['disabled_matrix']), 40)
        self.assertEqual(len({c['contract_id'] for c in v['disabled_matrix']}), 40)
        self.assertTrue(all(c['runtime_result'] is None for c in v['disabled_matrix']))
        self.assertEqual(sum('/grc9_expansion_vectors/' in c['json_pointer'] for c in v['vectors']), 17)
        self.assertEqual(sum('/grc9_metamorphic_vectors/' in c['json_pointer'] for c in v['vectors']), 3)
        for c in v['authority']:
            self.assertTrue(c['edge_refs'] and c['source_ref'])
            if c['contract_id'].startswith('D10.2-'):
                self.assertEqual(c['support_disposition'], 'indeterminate_requires_review')
            else:
                special = {
                    'D11-G9-EC-DIHEDRAL-COVARIANCE': 'accepted_design_level_combinatorial_covariance_with_runtime_verification_pending',
                    'D11-G9-EC-LIFECYCLE-READMISSION': 'accepted_bounded_design_level_lifecycle_contract_with_runtime_conformance_pending',
                    'D11-G9-EC-LEGACY-DEFINED-DOMAIN': 'accepted_bounded_GRC9V4_compatibility_boundary_not_a_GRC9_or_GRC9V3_rewrite',
                }
                self.assertEqual(c['support_disposition'], [special.get(c['contract_id'], 'accepted_bounded_GRC9V4_successor')])
        rows = {c['iteration_id']: c for c in v['test_matrix']}
        self.assertEqual(rows['P9-8.3A']['state'], 'pending_child_acceptances')
        self.assertEqual(rows['P9-8.3A.1']['state'], 'pending_oracle_construction_and_review')
        self.assertEqual(rows['P9-8.3A.2']['state'], 'held_pending_accepted_oracle_and_runtime_dependencies')
        work = v['a_expansion_work']
        self.assertEqual(work['oracle_owner'], 'P9-8.3A.1')
        self.assertEqual(work['runtime_owner'], 'P9-8.3A.2')
        self.assertFalse(work['oracle_requires_production_runtime'])
        self.assertIn('accepted_P9-8.3A.1_same_exact_scope', work['runtime_entry'])
        self.assertIn('Tranche 7 correction', work['generic_authority_gap_route'])
        self.assertFalse(work['independent_C_work_blocked'])

    def test_rehashed_scope_evidence_and_gate_mutations_rejected(self):
        edits = (
            lambda v: v['profiles'].pop(),
            lambda v: v['profiles'].append(deepcopy(v['profiles'][0])),
            lambda v: v['profiles'][0]['nomination'].update(complete_profile_id='family:A_CI'),
            lambda v: v['proposed_consumed_support'].pop(),
            lambda v: v['profiles'][0].update(acceptance=v['profiles'][1]['acceptance']),
            lambda v: v['authority'][0].update(support_disposition='normative'),
            lambda v: v['authority'][0].update(trace_digest='0'*64),
            lambda v: v['source_bindings'].clear(),
            lambda v: v['disabled_matrix'].pop(),
            lambda v: v['disabled_matrix'][0].update(runtime_result='passed'),
            lambda v: v['test_matrix'][7].update(state='passed'),
            lambda v: v['vectors'].pop(),
            lambda v: v['legacy_bindings'].clear(),
            lambda v: v.update(G3_accepted=True),
            lambda v: v.update(user_accepted=True, tranche_7_closed=True),
            lambda v: v.update(new_runtime_iterations_authorized=['P9-8.1a']),
            lambda v: v.update(admitted_specialization_support_sets=[v['proposed_consumed_support']]),
            lambda v: v.update(specialization_runtime_conformance=True),
            lambda v: v.update(optional_capabilities_selected=['completed_spark']),
            lambda v: v.update(inherited_debt='none'),
            lambda v: v['a_expansion_work'].update(oracle_owner=None),
            lambda v: v['a_expansion_work']['runtime_entry'].remove('accepted_P9-8.3A.1_same_exact_scope'),
            lambda v: v['a_expansion_work'].update(generic_authority_gap_route='specialization_workaround'),
        )
        for i, edit in enumerate(edits):
            with self.subTest(mutation=i):
                v = deepcopy(self.expected); edit(v); v['record_digest'] = p.digest_record(v)
                with self.assertRaises(ValueError): r.validate(v, self.expected)

    def test_source_drift_and_unaccepted_predecessor_fail_closed(self):
        safe = p.safe_path
        class Changed:
            def read_bytes(self): return b'changed'
        def path(root, name): return Changed() if name == r.SPEC else safe(root, name)
        prior = self.expected['predecessor']
        with patch.object(r.aggregate, 'check', return_value=prior), patch.object(p, 'safe_path', side_effect=path):
            with self.assertRaisesRegex(ValueError, 'input drift'): r.build()
        with patch.object(r.aggregate, 'check', return_value=prior | {'user_accepted': False}):
            with self.assertRaisesRegex(ValueError, 'not accepted'): r.build()

    def test_accepted_projection_preserves_review_and_scoped_entry(self):
        with patch.object(r, 'build', return_value=self.expected):
            v = g._checker(p.ROOT, 'verify_p978_specialization_review')()
        for key in ('G3_accepted', 'user_accepted', 'tranche_7_closed'):
            self.assertTrue(v[key])
            self.assertFalse(self.expected[key])
        self.assertFalse(v['specialization_runtime_conformance'])
        self.assertEqual(v['new_runtime_iterations_authorized'], ['P9-8.1a'])
        self.assertEqual(v['admitted_specialization_support_sets'], [v['proposed_consumed_support']])
        for path in (r.RECORD, r.TEXT):
            self.assertEqual((p.ROOT/path).read_bytes(), p.git(p.ROOT, 'show', admission.CHECKPOINT+':'+path))

    def test_acceptance_tampering_and_entry_widening_rejected(self):
        good = admission.accepted(p.ROOT)
        for edit in (lambda v:v.update(G3_accepted=False), lambda v:v.update(tranche_7_closed=False),
                     lambda v:v['admitted_specialization_support_sets'][0].pop(),
                     lambda v:v['runtime_paths'].append('src/pygrc/models/grc_9_v3.py'),
                     lambda v:v['new_runtime_iterations_authorized'].append('P9-8.3A.2')):
            bad=deepcopy(good);edit(bad);bad['record_digest']=p.digest_record(bad)
            with patch.object(p,'read',return_value=bad), self.assertRaisesRegex(ValueError,'G3 acceptance'):
                admission.accepted(p.ROOT)
        with patch.object(p,'read',side_effect=FileNotFoundError), self.assertRaises(FileNotFoundError):
            admission.accepted(p.ROOT)
        for path in admission.PATHS:
            self.assertTrue(admission.permitted(path,'P9-8.1a'))
            for leaf in ('P9-8.1b','P9-8.2','P9-8.3A.1','P9-8.3A.2','P9-9.2'):
                self.assertFalse(admission.permitted(path,leaf))
        for path in ('src/pygrc/models/grc_9_v3.py','src/pygrc/models/grc_9_v4.py',
                     'src/pygrc/models/grc_9_v4_expansion.py'):
            self.assertFalse(admission.permitted(path,'P9-8.1a'))

    def test_api_browser_notebook_transport_and_failure_cleanup(self):
        tool = p.ROOT / p.SIDE / 'tool'
        sys.path.insert(0, str(tool/'src'))
        from grcv4_explorer.phase9_verification import _profile_next_gate
        from grcv4_explorer.tooling import managed_node, tool_environment
        views = {'profile_g2': [dict(state='accepted', profile_family_id=x['profile_family_id'],
                       complete_profile_id=x['nomination']['complete_profile_id']) for x in self.expected['profiles']],
                 'profile_aggregate_reconciliation': self.expected['predecessor'],
                 'specialization_admission_review': r.view(self.expected)}
        self.assertIn('Tranche 7 closed', _profile_next_gate(views))
        source = (tool/'src/grcv4_explorer/phase9_verification.py').read_text()
        self.assertLess(source.index("profile_views['specialization_admission_review'] ="), source.index('profile_view_keys = set(profile_views)'))
        self.assertIn('for key in profile_view_keys:', source)
        notebook = json.loads((tool/'notebooks/phase9_verification.ipynb').read_text())
        query = next(c for c in notebook['cells'] if c['id'] == 'query-status')
        namespace = dict(Path=Path, repo_root=p.ROOT, PHASE9_STATUS_ONLY=True,
                         verification_status=lambda root: dict(current_boundary='passed', **views))
        exec(''.join(query['source']), namespace)
        self.assertEqual(namespace['phase9_status']['specialization_admission_review'], r.view(self.expected))
        namespace['verification_status'] = lambda root: dict(current_boundary='failed_closed')
        exec(''.join(query['source']), namespace)
        self.assertNotIn('specialization_admission_review', namespace['phase9_status'])
        self.assertIsNone(namespace['phase9_pressure'])
        # Same JSON projection carried by API and notebook; browser validates
        # it, independently of the surrounding historical status fixture.
        completed = subprocess.run([str(managed_node()), '--input-type=module', '-e',
            "import {checkedSpecialization} from './verification.js'; let input=''; for await(const c of process.stdin) input+=c; checkedSpecialization(JSON.parse(input),true);"],
            input=json.dumps(views), text=True, capture_output=True, cwd=tool/'phase9-web', env=tool_environment())
        self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_browser_asset_is_served(self):
        script = p.ROOT / p.SIDE / 'tool/scripts/serve_phase9.py'
        spec = importlib.util.spec_from_file_location('p978_server', script)
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        handler = object.__new__(module.Handler)
        handler.path = '/specialization-review.js'; handler.wfile = BytesIO()
        handler.send_response = lambda code: self.assertEqual(code, 200)
        handler.send_header = lambda *args: None
        handler.end_headers = lambda: None
        handler.do_GET()
        self.assertEqual(handler.wfile.getvalue(), (p.ROOT/r.BROWSER).read_bytes())

    def test_fresh_api_policy_import_resolves_acceptance_helper(self):
        code = '''from pathlib import Path
import sys
root=Path.cwd()
sys.path.insert(0,str(root/'implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/src'))
from grcv4_explorer.phase9_verification import _policy
policy=_policy(root)
import phase9_specialization_acceptance as a
assert Path(a.__file__).resolve()==root/'implementation/phase-9-grcv4/verification/phase9_specialization_acceptance.py'
assert a.accepted(root)['tranche_7_closed'] is True
print('fresh API policy pass')
'''
        result=subprocess.run([sys.executable,'-I','-c',code],cwd=p.ROOT,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('fresh API policy pass',result.stdout)


if __name__ == '__main__': unittest.main()

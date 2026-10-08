"""Pressure aggregate accounting without repeating accepted numerical work."""
from copy import deepcopy
import json
import unittest
from unittest.mock import patch

import p984c_closeout as closeout
import tranche8_evidence as index


class CloseoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # The full boundary audit separately rebuilds/authenticates this display.
        cls.value = json.loads((index.ROOT / index.ASSET).read_text().split(' = ', 1)[1].rstrip(';\n'))
        unsigned = {k: v for k, v in cls.value.items() if k != 'view_digest'}
        assert cls.value['view_digest'] == index.digest(unsigned)
        cls.view = cls.value['coverage']['boundary_contract']
        sources = index.Sources(index.ROOT)
        cls.contract = sources.read(cls.view['record']['path'])
        cls.manifests = {r['family']: sources.read(r['inputs']['path']) for r in cls.view['family_results']}
        cls.record = sources.read(closeout.RECORD)

    def check(self, contract=None, view=None, manifests=None):
        return closeout.reconcile(self.contract if contract is None else contract,
                                 self.view if view is None else view,
                                 self.manifests if manifests is None else manifests)

    def test_exact_all_ten_coverage_and_distinct_scope(self):
        self.assertEqual(self.check(), self.record)
        self.assertEqual((self.record['accepted_cells'], self.record['new_history_cells'],
                          self.record['exact_reused_history_cells']), (640, 600, 40))
        children = {r['work_id']: r for r in self.value['coverage']['children']}
        self.assertTrue(children['P9-8.4c']['accepted'])
        self.assertFalse(self.value['coverage']['aggregate_closed'])
        self.assertTrue(all(not children['P9-8.4' + c]['accepted'] for c in 'defghi'))
        self.assertIn('8.4d–i', index.next_work(self.value))
        aos = next(r for r in self.record['families'] if r['family'] == 'A_OS')
        self.assertTrue(all('ORACLE' in r['planned_subject'] and 'RUNTIME' in r['accepted_runtime_subject']
                            for r in aos['reuse_links']))

    def test_missing_or_duplicate_family_cannot_preserve_total(self):
        for duplicate in (False, True):
            v = deepcopy(self.view)
            v['family_results'].pop()
            if duplicate:
                v['family_results'].append(deepcopy(v['family_results'][0]))
            with self.subTest(duplicate=duplicate), self.assertRaises(ValueError):
                self.check(view=v)

    def test_role_substitution_subject_duplication_and_extra_cells_reject(self):
        for mutation in ('role', 'duplicate', 'extra', 'matrix'):
            m = deepcopy(self.manifests); cases = m['A_RG2b']['cases']
            if mutation == 'role':
                cases[0]['coverage_binding']['cell_ids'][1] = cases[0]['coverage_binding']['cell_ids'][0]
            elif mutation == 'duplicate':
                cases[-1] = deepcopy(cases[0])
            elif mutation == 'extra':
                cases[0]['coverage_binding']['cell_ids'].append('foreign::reset')
            else:
                cases[0]['coverage_binding']['record_digest'] = '0' * 64
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self.check(manifests=m)
        c = deepcopy(self.contract); c['cells'][-1] = deepcopy(c['cells'][0])
        with self.assertRaises(ValueError):
            self.check(contract=c)

    def test_execution_is_not_acceptance_or_event_only_success(self):
        for mutation in ('acceptance', 'pending', 'failure', 'missing_case', 'extra_case', 'mechanics'):
            v = deepcopy(self.view); row = v['family_results'][0]
            if mutation == 'acceptance': row['acceptance'] = deepcopy(row['results'])
            elif mutation == 'pending': row['passing_pending_cells'] = 1
            elif mutation == 'failure': row['cases'][0]['case_passed'] = False
            elif mutation == 'missing_case': row['cases'].pop()
            elif mutation == 'extra_case': row['cases'].append(deepcopy(row['cases'][0]))
            else: v['mechanics']['numerical_history_credit'] = 1
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self.check(view=v)

    def test_reuse_and_original_flags_cannot_be_promoted(self):
        for family in ('A_OS', 'C_CI', 'A_RG2b'):
            m = deepcopy(self.manifests)
            m[family]['exact_reuse'][0]['previous_case_id'] += '-adjacent-subject'
            with self.subTest(family=family), self.assertRaises(ValueError):
                self.check(manifests=m)
        for flag in ('user_accepted', 'aggregate_closed'):
            m = deepcopy(self.manifests); m['A_RG2b'][flag] = True
            with self.subTest(flag=flag), self.assertRaises(ValueError):
                self.check(manifests=m)

    def test_api_source_authentication_and_closed_projection(self):
        import sys
        sys.path.insert(0, str(index.ROOT / index.SIDE / 'tool/src'))
        from grcv4_explorer import tranche8 as api
        with patch.object(index, 'checked', return_value=self.value), patch.object(api, '_index', return_value=index):
            self.assertTrue(api.tranche8_status(index.ROOT)['coverage']['boundary_contract']['closeout']['aggregate_closed'])
            for name in (closeout.RECORD, closeout.REVIEW):
                raw, ref = api.tranche8_source(index.ROOT, name)
                self.assertEqual(index.hashlib.sha256(raw).hexdigest(), ref['sha256'])
        original = index.Sources.current_bytes
        with patch.object(index.Sources, 'current_bytes', lambda self, name: b'forged' if name == closeout.RECORD else original(self, name)):
            with self.assertRaises(ValueError):
                index.Sources(index.ROOT).read(closeout.RECORD)


if __name__ == '__main__':
    unittest.main()

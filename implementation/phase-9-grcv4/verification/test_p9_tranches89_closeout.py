"""Retained all-ten closure, optional-scope distinction and mutation pressure."""
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import p9_tranches89_closeout as closure


class ClosureTests(unittest.TestCase):
    def test_complete_population_and_unchanged_execution(self):
        value = closure.checked()
        self.assertEqual(set(value['families']), closure.FAMILIES)
        self.assertTrue(value['tranche8_closed'] and value['tranche9_closed'])
        self.assertEqual(len(value['compatibility_cells']), 40)
        self.assertTrue(all(c['disposition'] == 'bounded_accepted' for c in value['compatibility_cells']))
        self.assertFalse(value['full_GRC9V4_conformance'])
        self.assertEqual(value['optional_completion'], 'unselected_deferred_not_a_closure_blocker')
        raw = json.loads((closure.b.ROOT / (closure.PREFIX + 'tranche-8/arg2b-native/9.3-Matrix.json')).read_bytes())
        self.assertEqual(raw['counts']['passed_pending_acceptance'], 4)

    def test_resealed_scope_or_missing_family_rejected(self):
        path = closure.b.ROOT / closure.PATH
        original = json.loads(path.read_bytes())
        read = Path.read_bytes
        for key, value in (('families', sorted(closure.FIRST)), ('full_GRC9V4_conformance', True),
                           ('optional_completion', 'executed'), ('sources', [])):
            changed = closure.b.seal(dict(original, **{key: value}))
            with self.subTest(key=key), patch.object(Path, 'read_bytes', lambda p:
                    json.dumps(changed).encode() if p == path else read(p)):
                with self.assertRaises(ValueError):
                    closure.checked()

    def test_family_evidence_and_presentation_drift_rejected(self):
        read = Path.read_bytes
        for name in (closure.PREFIX + 'tranche-9/P9-CPC-Acceptance.json',
                     'implementation/Phase-9-GRCV4-ImplementationChecklist.md'):
            with self.subTest(name=name), patch.object(Path, 'read_bytes', lambda p:
                    read(p) + b'\nchanged' if p == closure.b.ROOT / name else read(p)):
                with self.assertRaises(ValueError):
                    closure.checked()

    def test_bound_maintenance_preserves_the_original_closeout_subject(self):
        name = 'implementation/Phase-9-GRCV4-ImplementationPlan.md'
        row = closure.record(closure.b.ROOT)['presentation_sources'][name]
        live = closure.b.sha((closure.b.ROOT / name).read_bytes())
        self.assertNotEqual(live, row['after_sha256'])
        self.assertEqual(closure.peel_sha(closure.b.ROOT, name, live), row['before_sha256'])
        self.assertNotIn('src/pygrc/models/grc_v4_step.py',
                         closure.MAINTAINED_PRESENTATIONS | closure.POST_CLOSEOUT_READERS)

    def test_registered_test_addition_is_checked_at_its_source_epoch(self):
        import p9_crg2b_historical as old
        import p9_arg2b_historical as successor
        name = 'tests/models/test_grc_9_v4_crg2b_integration.py'
        live = old.sha((closure.b.ROOT / name).read_bytes())
        projected = successor.peel_sha(closure.b.ROOT, name, live)
        expected = old.epochs(closure.b.ROOT)['additions'][name]
        self.assertNotEqual(live, expected)
        self.assertEqual(projected, expected)
        self.assertEqual(old.project(closure.b.ROOT, {name: live}), {})


if __name__ == '__main__':
    unittest.main()

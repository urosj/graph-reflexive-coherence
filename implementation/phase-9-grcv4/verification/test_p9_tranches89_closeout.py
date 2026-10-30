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


if __name__ == '__main__':
    unittest.main()

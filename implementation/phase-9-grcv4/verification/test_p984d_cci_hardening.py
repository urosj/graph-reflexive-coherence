"""Bounded hardening checks; do not repeat native or interval campaigns."""

from copy import deepcopy
from fractions import Fraction as Q
import unittest
from unittest.mock import patch

import p984d_cci_hardening as h


class HardeningTests(unittest.TestCase):
    def test_predeclared_finite_neighborhood(self):
        declared = h.declaration()
        manifest = h.b.read(h.d.INPUTS)
        self.assertEqual(len(declared['probes']), 9)
        base = h.target_for(manifest, declared, declared['probes'][0])
        for probe in declared['probes']:
            target = h.target_for(manifest, declared, probe)
            self.assertEqual(target.geometry.reference.profile, base.geometry.reference.profile)
            self.assertEqual(target.dt, 1/4096)
            for role in h.r.ROLES:
                self.assertGreaterEqual(min(getattr(target, role).C), 0)
                self.assertIsNone(getattr(target, role).W_A)
                self.assertIsNone(getattr(target, role).Z_4)
        for probe in declared['probes'][-2:]:
            target = h.target_for(manifest, declared, probe)
            for role in h.r.ROLES:
                self.assertEqual(sum(map(Q, getattr(target, role).C)), sum(map(Q, getattr(base, role).C)))

    def test_retained_check_has_no_native_producers(self):
        declared, result = h.b.read(h.INPUTS), h.b.read(h.RESULTS)
        with (patch.object(h.r, 'ProvisionalCandidateCIStep', side_effect=AssertionError('native rerun')),
             patch.object(h.r, 'CandidateCIRoot', side_effect=AssertionError('native rerun')),
             patch.object(h.r.native, 'GRC9V4CCIOperation', side_effect=AssertionError('native rerun'))):
            self.assertEqual(h.check(declared, result)['native_steps'], 36)

    def test_resealed_scope_margin_and_rollback_mutations(self):
        declared, result = h.b.read(h.INPUTS), h.b.read(h.RESULTS)
        for kind in ('roster', 'schedule', 'margin', 'current', 'geometry', 'resource_error',
                     'negative', 'rollback', 'late', 'acceptance'):
            bad = deepcopy(result)
            entry = bad['neighborhood'][0]['roles']['current'][0]
            if kind == 'roster': bad['neighborhood'].pop()
            elif kind == 'schedule': bad['neighborhood'][0]['roles']['reset'].pop()
            elif kind == 'margin': entry['margins']['positivity_lower'] = '1'
            elif kind == 'current': entry['step']['selection_current'][0] += 1
            elif kind == 'geometry': entry['step']['root']['H'][0][0] += 1
            elif kind == 'resource_error': entry['step']['resource_error'] = '1'
            elif kind == 'negative': bad['failures']['excluded']['exact_real_negative_coordinate_upper'] = '0'
            elif kind == 'rollback': bad['failures']['excluded']['whole_event_publication_preserved'] = False
            elif kind == 'late': bad['failures']['late_event']['event_committed'] = True
            else: bad['user_accepted'] = True
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                h.check(declared, h.b.seal(bad))


if __name__ == '__main__':
    unittest.main()

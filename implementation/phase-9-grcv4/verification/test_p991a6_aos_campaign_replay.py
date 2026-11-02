"""Bounded real-journal checks for paired cold restore and foreign accounting."""

import unittest
from copy import deepcopy

from p991a6_aos_campaign import PairedCold, delivery, setup
from p991a6_aos_campaign_verify import Capture

from pygrc.models import grc_9_v4_spark_owner as owner


class AOSPairedColdTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cap = Capture()
        with cap.installed():
            models, _, _ = setup(cap)
            for role, model in models.items():
                for beat in (1, 2):
                    result = model.step_v4_input(delivery("paired-test-" + role, beat))
                    assert result.committed and result.local_gain == 0
        cls.checkpoints = {r: m.snapshot() for r, m in models.items()}

    def test_both_actual_journals_replay_in_one_isolated_authority(self):
        registry = owner._SCOPES
        pair = PairedCold()
        for role in ("current", "reset"):
            report = pair(self.checkpoints[role])
            self.assertEqual(report["replayed_steps"], 3)
            self.assertTrue(report["whole_publication_equal"])
            self.assertTrue(report["shared_accounting_reconciled"])
            self.assertIs(owner._SCOPES, registry)
        self.assertIs(
            pair.models[0]._operation._spark_scope,
            pair.models[1]._operation._spark_scope,
        )
        self.assertEqual(len(pair.registry), 1)

    def test_unreconciled_foreign_accounting_cannot_enter_paired_scope(self):
        pair = PairedCold()
        pair(self.checkpoints["current"])
        before = pair.models[0].snapshot()
        bad = deepcopy(self.checkpoints["reset"])
        bad["owner"]["accounting"]["children"].append({"foreign": "unearned"})
        with self.assertRaisesRegex(ValueError, "unreconciled accounting"):
            pair(bad)
        self.assertEqual(pair.models[0].snapshot(), before)

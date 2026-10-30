"""Chained historical projections authenticate live bytes and older subjects."""
from pathlib import Path
from unittest.mock import patch
import unittest
import p9_acipc_historical as h
import p9_ccipc_historical as older
import p9_acipc_review as review

ROOT=review.b.ROOT
NAME=h.BASE+'verification/phase9_implementation_policy.py'


class HistoricalProjectionTests(unittest.TestCase):
    def test_repeated_projection_preserves_an_authenticated_older_subject(self):
        live=h.sha((ROOT/NAME).read_bytes())
        expected=older.epochs(ROOT)['sources'][NAME]['before_sha256']
        self.assertEqual(older.project_sha(ROOT,NAME,live),expected)
        self.assertEqual(older.project_sha(ROOT,NAME,expected),expected)

    def test_unknown_incoming_hash_is_rejected_by_owning_validator(self):
        with self.assertRaises(ValueError):older.project_sha(ROOT,NAME,'0'*64)
        with self.assertRaises(ValueError):h.project_sha(ROOT,NAME,'0'*64)

    def test_older_subject_cannot_hide_changed_live_successor(self):
        expected=older.epochs(ROOT)['sources'][NAME]['before_sha256']
        target=ROOT/NAME;read=Path.read_bytes
        with patch.object(Path,'read_bytes',lambda path:read(path)+b'# drift\n' if path==target else read(path)):
            with self.assertRaises(ValueError):older.project_sha(ROOT,NAME,expected)

    def test_original_four_lifecycle_records_keep_their_exact_owner_test(self):
        from p994a_owner_successor import check, FAMILIES
        for family in FAMILIES:
            with self.subTest(family=family):check(ROOT,family)

    def test_owner_test_successor_cannot_hide_live_mutation(self):
        from p994a_owner_successor import check
        target=ROOT/'tests/models/test_grc_9_v4_owner.py';read=Path.read_bytes
        with patch.object(Path,'read_bytes',lambda path:read(path)+b'# drift\n' if path==target else read(path)):
            with self.assertRaises(ValueError):check(ROOT,'C_OS')

    def test_original_tranche9_and10_views_keep_their_accepted_subjects(self):
        import sys
        sys.path.insert(0,str(ROOT/h.SIDE/'src'))
        from grcv4_explorer import tranche9
        for name in ('tranche9_status','tranche9_compatibility_status',
                     'tranche9_crossing_status','tranche9_public_status',
                     'tranche9_conflict_status','tranche9_support_status'):
            with self.subTest(view=name):getattr(tranche9,name)(ROOT)
        from grcv4_explorer.tranche10_support import tranche10_support_status
        tranche10_support_status(ROOT)


if __name__=='__main__':unittest.main()

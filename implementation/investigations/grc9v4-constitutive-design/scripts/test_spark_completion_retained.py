"""Rehashed retained-record mutations; no long trajectory rerun.

Compute the trap and source preparation once, then reuse those fresh numerical
results while exercising both complete check() paths for each altered record.
"""
import copy
from contextlib import ExitStack
from fractions import Fraction as F
import json
import lzma
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_spark_completion_positive as positive
import check_spark_completion_source_beat as source


class RetainedRecordPressure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = {
            'positive': json.loads(lzma.decompress((positive.ROOT / positive.OUTPUT).read_bytes())),
            'source': json.loads(lzma.decompress((source.ROOT / source.OUTPUT).read_bytes())),
        }
        _, _, targets = positive.fixture()
        fresh_trap = positive.trap(targets['1'])
        fresh_source = source.prepare()
        stack = ExitStack()
        cls.addClassCleanup(stack.close)
        stack.enter_context(patch.object(positive, 'trap', return_value=fresh_trap))
        stack.enter_context(patch.object(source, 'trap', return_value=fresh_trap))
        stack.enter_context(patch.object(source, 'prepare', side_effect=lambda: copy.deepcopy(fresh_source)))

    def subjects(self):
        for name, module in (('positive', positive), ('source', source)):
            roles = ('current', 'reset') if name == 'positive' else ('current',)
            for role in roles:
                value = copy.deepcopy(self.records[name])
                history = (value['checks']['roles'][role] if name == 'positive'
                           else value['checks']['actual_current_target'])
                yield name, role, module, value, history

    def reject(self, mutation, message):
        for name, role, module, value, history in self.subjects():
            with self.subTest(record=name, role=role):
                mutation(history)
                value['record_digest'] = module.digest(value)
                with self.assertRaisesRegex((AssertionError, ValueError), message):
                    module.check(value)

    def test_unmodified_records_pass(self):
        positive.check(self.records['positive'])
        source.check(self.records['source'])

    def test_charge_preserving_checkpoint_shift(self):
        def mutate(history):
            checkpoint = history['checkpoints'][str(history['certified_trap_entry_step'])]
            before = sum(F(pair[0]) for pair in checkpoint.values())
            for node, delta in (('n1', F(1, 64)), ('n2', -F(1, 64))):
                checkpoint[node] = [str(F(x) + delta) for x in checkpoint[node]]
            self.assertEqual(before, sum(F(pair[0]) for pair in checkpoint.values()))
            self.assertGreater(min(F(pair[0]) for pair in checkpoint.values()), 0)
        self.reject(mutate, 'checkpoint metric distance outside trap')

    def test_empty_charts_before_gain(self):
        self.reject(lambda h: h['observations'][0].update(qualified_basins={}),
                    'both observation charts required')

    def test_missing_negative_chart(self):
        self.reject(lambda h: h['observations'][-1]['qualified_basins'].pop('-1'),
                    'both observation charts required')

    def test_extra_chart(self):
        self.reject(lambda h: h['observations'][0]['qualified_basins'].update({'0': {}}),
                    'both observation charts required')

    def test_wrong_complete_membership_same_anchors(self):
        def mutate(history):
            for roster in history['observations'][-1]['qualified_basins'].values():
                roster['p'] = ['n1', 'p', 'private']
        self.reject(mutate, 'checkpoint complete basin dictionary differs')

    def test_missing_entry_checkpoint(self):
        self.reject(lambda h: h['checkpoints'].pop(str(h['certified_trap_entry_step'])),
                    'entry checkpoint missing')

    def test_nonfinite_checkpoint(self):
        def mutate(history):
            history['checkpoints'][str(history['certified_trap_entry_step'])]['n1'] = ['nan', 'nan']
        self.reject(mutate, 'Invalid literal')

    def test_scalar_bound_must_bound_saved_coordinates(self):
        def mutate(history):
            history['trap_distance_upper'] = ['0', '0']
            history['observations'][-1]['trap_distance_upper'] = '0'
        self.reject(mutate, 'saved distance does not bound checkpoint')


if __name__ == '__main__':
    unittest.main()

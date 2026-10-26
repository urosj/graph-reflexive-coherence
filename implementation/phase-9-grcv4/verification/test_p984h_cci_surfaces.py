"""Selected C_CI status authenticates retained inputs, never runs numerics."""
import json
import unittest
from unittest.mock import patch
import tranche8_evidence as index
import p984h_cci as run
import p984h_cci_continuation as cont
import p984h_cci_covariance as cov


class Surfaces(unittest.TestCase):
    def test_selected_status_no_reconstruction(self):
        with patch.object(run,'check',side_effect=AssertionError('full check')), \
             patch.object(run,'seed',side_effect=AssertionError('reconstruction')), \
             patch.object(run,'execute_source',side_effect=AssertionError('native rerun')), \
             patch.object(cont,'initial',side_effect=AssertionError('target reconstruction')), \
             patch.object(cont,'CandidateCIRoot',side_effect=AssertionError('native rerun')), \
             patch.object(cont,'ProvisionalCandidateCIStep',side_effect=AssertionError('native rerun')), \
             patch.object(cov,'subject',side_effect=AssertionError('counterpart reconstruction')):
            value=index.family_status(index.ROOT,'C_CI','8.4h')
        row=value['runtime']
        self.assertTrue(row['source_full_joint_parity']);self.assertTrue(row['fresh_trigger']['eligible'])
        self.assertTrue(row['user_accepted']);self.assertFalse(row['aggregate_closed'])
        self.assertTrue(row['original_execution_flags_unchanged'])
        self.assertEqual(row['accepted_on'],'2026-10-21')
        self.assertFalse(row['native_numerics_rerun']);self.assertFalse(value['other_families_checked'])
        self.assertEqual(row['native_steps'],1);self.assertEqual(row['target_steps'],20)
        self.assertEqual(row['final_reads'],2)
        self.assertTrue(row['continuation']['baseline_complete'])
        self.assertFalse(row['continuation']['uniform_trajectory_enclosure'])
        for role in row['continuation']['roles'].values():
            self.assertEqual(role['native_steps'],10);self.assertEqual(role['final_reads'],1)
            self.assertTrue(all(r['exact_root_lower_approx']>0 for r in role['steps']))
        self.assertEqual(row['native_events'],1)
        self.assertEqual(row['status'],'baseline_and_covariance_accepted')
        self.assertEqual(row['total_native_events'],9);self.assertEqual(row['total_target_steps'],36)
        self.assertTrue(row['covariance']['covariance_complete'])
        self.assertEqual(row['covariance']['native_events'],8);self.assertEqual(row['covariance']['target_steps'],16)
        saved=json.loads((index.ROOT/index.ASSET).read_text().split(' = ',1)[1].rstrip(';\n'))
        self.assertEqual(next(r for r in saved['coverage']['larger_runtime'] if r['family']=='C_CI'),row)
        for name in index.LARGER_RUNTIME_CCI_SOURCES:
            with patch.object(index.Sources,'current_bytes',return_value=b'forged'),self.assertRaisesRegex(ValueError,'source drift'):
                index.Sources(index.ROOT).raw(name)

    def test_missing_counterpart_does_not_close_coverage(self):
        pins=dict(index.LARGER_RUNTIME_CCI_SOURCES)
        pins.pop(cov.path('reflect','reset'))
        with patch.object(index,'LARGER_RUNTIME_CCI_SOURCES',pins), \
             patch.object(cov,'subject',side_effect=AssertionError('reconstruction')):
            row=index.family_status(index.ROOT,'C_CI','8.4h')['runtime']
        self.assertFalse(row['covariance']['covariance_complete'])
        self.assertEqual(row['covariance']['target_steps'],15)
        self.assertEqual(row['status'],'baseline_complete_covariance_pending')
        self.assertFalse(row['user_accepted'])


if __name__=='__main__':unittest.main()

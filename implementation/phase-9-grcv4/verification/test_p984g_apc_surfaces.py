"""Selected A_PC research surfaces authenticate evidence without numerics."""
import json
import sys
import unittest
from unittest.mock import patch
import tranche8_evidence as t
import p984g_apc_investigation as p
import p984g_apc_feasibility as f
import p984g_apc_staged as s
import p984g_apc_hardening as h
import p984g_apc_native as n
import p984g_apc_native_targets as nt
sys.path.insert(0,str(t.ROOT/t.SIDE/'tool/src'))
from grcv4_explorer.tranche8 import tranche8_status


class APCSurfaces(unittest.TestCase):
    def test_api_browser_no_sibling_or_numerical_work(self):
        with patch.object(p,'calculate',side_effect=AssertionError('no research rerun')),patch.object(f,'calculate',side_effect=AssertionError('no feasibility rerun')),patch.object(s,'calculate',side_effect=AssertionError('no oracle rerun')),patch.object(h,'calculate',side_effect=AssertionError('no hardening rerun')),patch.object(h,'compare_final',side_effect=AssertionError('no full-read replay')),patch.object(n,'execute',side_effect=AssertionError('no native replay')),patch.object(n,'summary',side_effect=AssertionError('no full checker replay')),patch.object(nt,'summary',side_effect=AssertionError('no successor checker replay')),patch.object(t,'larger_aci_investigation',side_effect=AssertionError('no sibling')):
            value=tranche8_status(t.ROOT,family='A_PC',checkpoint='8.4g')
        self.assertFalse(value['other_families_checked'])
        row=value['investigation']
        self.assertEqual([c['resource_sign'] for c in row['cases']],['nonnegative']*3+['excluded'])
        self.assertTrue(row['ready_for_8_4h']);self.assertTrue(row['user_accepted'])
        self.assertFalse(row['scalar_certificates_recomputed']);self.assertEqual(row['native_steps'],row['pc_native']['native_steps'])
        native=row['pc_native'];self.assertEqual(native['native_steps'],4);self.assertEqual(native['native_reads'],12)
        self.assertTrue(native['native_prerequisites_complete']);self.assertTrue(native['user_accepted'])
        self.assertTrue(native['ready_for_8_4h']);self.assertTrue(native['original_execution_flags_unchanged'])
        self.assertFalse(native['native_trajectories_rerun']);self.assertEqual(native['committed_steps'],0)
        self.assertEqual(len(native['historical_target_attempts']),2)
        companion=row['feasibility']
        self.assertEqual(companion['shares'],['1/4','3/8','3/8'])
        self.assertFalse(companion['event_pair']['reset_evolves'])
        self.assertFalse(companion['interval_research_recomputed'])
        self.assertFalse(companion['ready_for_8_4h']);self.assertFalse(companion['poststate_read_executed'])
        self.assertTrue(all(c['postbeat_transfer_target_minimum_lower_display']>0 for c in companion['cases']))
        oracle=row['pc_staged']
        self.assertFalse(oracle['ready_for_8_4h']);self.assertEqual(oracle['native_steps'],0)
        self.assertTrue(all(c['final_read_executed'] for c in oracle['cases']))
        target=[c for c in oracle['cases'] if c['graph']=='target']
        self.assertEqual([c['effects']['final']['carrier']['separated_coordinates'] for c in target],[0,0])
        self.assertTrue(all(c['nonzero_offdiagonal_carrier_entries']>0 for c in target))
        hard=row['pc_hardening'];self.assertEqual(hard['scale'],'7/8')
        self.assertFalse(hard['numerical_recomputed']);self.assertFalse(hard['ready_for_8_4h'])
        self.assertEqual(hard['native_steps'],0)
        self.assertTrue(all(c['separated_coordinates']>0 and c['effect_lower_display']>c['combined_error_upper_display'] for c in hard['cases']))
        saved=json.loads((t.ROOT/t.ASSET).read_text().split(' = ',1)[1].rstrip(';\n'))
        self.assertEqual(row,next(r for r in saved['coverage']['larger_prerequisites']['investigations'] if r['family']=='A_PC'))
        for name in {**t.LARGER_APC_RESEARCH_SOURCES,**t.LARGER_APC_FEASIBILITY_SOURCES,**t.LARGER_APC_STAGED_SOURCES,**t.LARGER_APC_HARDENING_SOURCES,**t.LARGER_APC_NATIVE_SOURCES}:
            with patch.object(t.Sources,'current_bytes',return_value=b'forged'),self.assertRaises(ValueError):t.Sources(t.ROOT).raw(name)


if __name__=='__main__':unittest.main()

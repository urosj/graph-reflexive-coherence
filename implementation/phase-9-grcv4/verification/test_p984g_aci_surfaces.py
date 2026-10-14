"""A_CI investigation is reachable without sibling work or native permission."""
import json
import sys
import unittest
from unittest.mock import patch
import tranche8_evidence as t
import p984g_aci_investigation as p
import p984g_aci_feasibility as feasible
import p984g_aci_staged as staged
import p984g_aci_native_check as native
import p984g_aci_native_successor_check as successor

sys.path.insert(0,str(t.ROOT/t.SIDE/'tool/src'))
from grcv4_explorer.tranche8 import tranche8_status


class ACIResearchSurfaces(unittest.TestCase):
    def test_selected_api_browser_and_scope(self):
        with patch.object(t,'larger_view',side_effect=AssertionError('unrelated work')),patch.object(t,'larger_cci_investigation',side_effect=AssertionError('sibling work')),patch.object(feasible,'calculate',side_effect=AssertionError('interval research rerun')),patch.object(staged,'analyze',side_effect=AssertionError('staged interval rerun')),patch.object(native,'check',side_effect=AssertionError('full retained checker rerun')),patch.object(successor,'check',side_effect=AssertionError('successor checker replay')):
            result=tranche8_status(t.ROOT,family='A_CI',checkpoint='8.4g')
        self.assertFalse(result['other_families_checked'])
        row=result['investigation']
        self.assertEqual(row['native_roots'],0)
        self.assertFalse(row['ready_for_8_4h'])
        self.assertFalse(row['user_accepted'])
        self.assertFalse(row['native_attempt']['native_prerequisites_complete'])
        self.assertEqual([c['outcome'] for c in row['native_attempt']['cases']],['incomplete','not_run','not_run','not_run'])
        self.assertEqual(row['native_attempt']['native_steps'],0)
        self.assertEqual(len(row['native_attempt']['known_implementation_holds']),2)
        self.assertEqual(row['native_successor']['native_steps'],4)
        self.assertEqual(row['native_successor']['native_roots'],12)
        self.assertFalse(row['native_successor']['user_accepted'])
        self.assertFalse(row['native_successor']['ready_for_8_4h'])
        self.assertFalse(row['native_successor']['full_retained_checker_rerun'])
        self.assertFalse(row['staged_oracle']['interval_research_recomputed'])
        self.assertFalse(row['staged_oracle']['ready_for_8_4h'])
        self.assertEqual(row['staged_oracle']['native_roots'],0)
        self.assertTrue(all(c['two_consecutive_independent_residual_passes'] and not c['native_stopping_outcome_verified'] for c in row['staged_oracle']['cases']))
        self.assertFalse(row['feasibility']['interval_research_recomputed'])
        self.assertFalse(row['feasibility']['ready_for_8_4h'])
        self.assertFalse(row['feasibility']['event_pair']['reset_evolves'])
        self.assertTrue(all(c['fresh_transfer_target_minimum_lower_display']>0 for c in row['feasibility']['cases']))
        self.assertEqual([c['exact_real_first_step_resources_nonnegative'] for c in row['cases']],[True,True,True,False])
        saved=json.loads((t.ROOT/t.ASSET).read_text().split(' = ',1)[1].rstrip(';\n'))
        self.assertEqual(row,next(c for c in saved['coverage']['larger_prerequisites']['investigations'] if c['family']=='A_CI'))
        for name in (*t.LARGER_ACI_RESEARCH_SOURCES,*t.LARGER_ACI_FEASIBILITY_SOURCES,*t.LARGER_ACI_STAGED_SOURCES,*t.LARGER_ACI_NATIVE_SOURCES,*t.LARGER_ACI_SUCCESSOR_SOURCES):
            with patch.object(t.Sources,'current_bytes',return_value=b'forged'),self.assertRaises(ValueError):
                t.Sources(t.ROOT).raw(name)

    def test_read_only_cli_rejects_execution_flags(self):
        for flag in ('--recheck-numerics','--oracle','--preparation'):
            with patch.object(sys,'argv',['query','verify-retained','--family','A_CI','--checkpoint','8.4g',flag]),self.assertRaises(ValueError):t.main()


if __name__=='__main__':unittest.main()

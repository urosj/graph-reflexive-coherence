"""Selected C_CI research surfaces must not invoke native execution."""
import json
import sys
import unittest
from unittest.mock import patch
import tranche8_evidence as t
import p984g_cci_investigation as p
import p984g_cci_staged as staged
import p984g_cci_feasibility as feasible
import p984g_cci_closure as native

sys.path.insert(0,str(t.ROOT/t.SIDE/'tool/src'))
from grcv4_explorer.tranche8 import tranche8_status


class CIResearchSurfaces(unittest.TestCase):
    def test_selected_api_and_browser(self):
        with patch.object(t,'larger_view',side_effect=AssertionError('unrelated C_OS work')), patch.object(staged,'analyze',side_effect=AssertionError('interval rerun')), patch.object(feasible,'calculate',side_effect=AssertionError('feasibility rerun')), patch.object(native,'execute',side_effect=AssertionError('native rerun')):
            result=tranche8_status(t.ROOT,family='C_CI',checkpoint='8.4g')
        self.assertFalse(result['other_families_checked'])
        row=result['investigation']
        self.assertEqual(row['native_roots'],0)
        self.assertFalse(row['ready_for_8_4h'])
        self.assertEqual(len(row['staged_bridge']['cases']),4)
        self.assertFalse(row['staged_bridge']['native_stopping_outcome_verified'])
        self.assertFalse(row['staged_bridge']['interval_solves_rerun'])
        self.assertEqual(row['staged_bridge']['continuation']['excluded_target_roles'],2)
        self.assertEqual(row['feasibility']['shares'],['5/16','5/16','3/8'])
        self.assertEqual(row['feasibility']['allocation_only_staged_trigger_failed_roles'],['current','reset'])
        self.assertFalse(row['feasibility']['event_pair']['reset_evolves'])
        self.assertFalse(row['feasibility']['ready_for_8_4h'])
        self.assertEqual(row['native_prerequisites']['native_steps'],4)
        self.assertEqual(row['native_prerequisites']['native_roots'],12)
        self.assertEqual(row['native_prerequisites']['native_events'],0)
        self.assertTrue(row['native_prerequisites']['user_accepted'])
        self.assertTrue(row['native_prerequisites']['ready_for_8_4h'])
        self.assertFalse(row['native_prerequisites']['numerical_trajectories_rerun'])
        saved=json.loads((t.ROOT/t.ASSET).read_text().split(' = ',1)[1].rstrip(';\n'))
        self.assertEqual(row,saved['coverage']['larger_prerequisites']['investigations'][0])
        for name in (*t.LARGER_CCI_RESEARCH_SOURCES,*t.LARGER_CCI_STAGED_SOURCES,*t.LARGER_CCI_FEASIBILITY_SOURCES,*t.LARGER_CCI_NATIVE_SOURCES):
            with patch.object(t.Sources,'current_bytes',return_value=b'forged'),self.assertRaises(ValueError):
                t.Sources(t.ROOT).raw(name)

    def test_cli_never_permits_a_native_or_unrelated_recheck(self):
        for flags in (['--recheck-numerics'],['--oracle'],['--preparation']):
            with patch.object(sys,'argv',['query','verify-retained','--family','C_CI','--checkpoint','8.4g',*flags]),self.assertRaises(ValueError):
                t.main()


if __name__=='__main__':unittest.main()

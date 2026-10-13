"""Failed deep preflight must not be presented as native coverage."""

import json
import sys
import unittest
from unittest.mock import patch

import tranche8_evidence as index
import p984d_apc_runtime as runtime
import p984d_apc_feasibility as feasibility

sys.path.insert(0, str(index.ROOT / index.SIDE / "tool/src"))
from grcv4_explorer import tranche8 as api


class DeepAPCSurfaceTests(unittest.TestCase):
    def test_selected_api_browser_scope_and_pins(self):
        with patch.object(index, "checked", side_effect=AssertionError("unrelated full index")), \
                patch.object(api, "_index", return_value=index), \
                patch.object(runtime, "preflight_pressure", side_effect=AssertionError("numerical rerun")), \
                patch.object(feasibility, "inspect_box", side_effect=AssertionError("interval rerun")):
            value = api.tranche8_status(index.ROOT, family="A_PC", checkpoint="8.4d")
        row = value["native"]
        self.assertEqual((row["attempted_cases"], row["unattempted_cases"]), (20,0))
        self.assertEqual((row["native_cases"],row["passed_cases"],row["accepted_cells"]), (20,20,40))
        self.assertEqual(row["committed_events"],20)
        self.assertEqual(row["source_companions_tested"],3)
        self.assertEqual(row['target_steps'],400)
        self.assertEqual(row['passing_pending_cells'],0)
        self.assertEqual(row['successful_history_cells'],40)
        self.assertEqual(row['full_campaign']['newly_executed_cases'],19)
        self.assertEqual(row['full_campaign']['reused_cases'],1)
        self.assertEqual(row['full_campaign']['reused_target_steps'],20)
        self.assertEqual(row['full_campaign']['new_source_steps'],0)
        self.assertEqual(row['full_campaign']['final_reads'],40)
        self.assertFalse(row['full_campaign']['uniform_native_domain'])
        self.assertEqual(row['joint_witness']['target_steps'],1)
        self.assertEqual(row['joint_witness']['passed_cases'],0)
        self.assertEqual(row['joint_successor']['final_reads'],2)
        self.assertFalse(row['joint_successor']['uniform_native_domain'])
        history=row["history_companion"]
        self.assertTrue(history["source_eligible"])
        self.assertEqual((history["native_cases"],history["target_steps"],history["passed_cases"]),(0,0,0))
        self.assertEqual(history["pressure"]["first_negative_step"],1)
        self.assertEqual(history["pressure"]["neighbor_probes"],0)
        self.assertEqual(row["frozen_source_preflight"]["native_cases"],0)
        self.assertTrue(row["allocation_feasibility"]["user_accepted"])
        self.assertEqual(row["source_companion"]["native"]["status"],"incomplete_companion")
        self.assertEqual(row["source_companion"]["independent"]["failures"],[])
        self.assertEqual(row["preflight_pressure"]["certified_exclusions"], 2)
        self.assertEqual(row["allocation_feasibility"]["D94_cases"], 6)
        self.assertEqual(row["allocation_feasibility"]["status"], "frozen_source_allocation_excluded")
        saved = json.loads((index.ROOT / index.ASSET).read_text().split(" = ",1)[1].rstrip(";\n"))
        deep = saved["coverage"]["deep_expansion"]
        self.assertNotIn("A_PC", deep["families_not_executed"])
        self.assertEqual(next(r for r in deep["family_results"] if r["family"] == "A_PC"), row)
        self.assertEqual(sum(r["accepted_cells"] for r in deep["family_results"]), 160)
        self.assertTrue(deep["first_group_closed"])
        self.assertEqual(deep["first_group_accepted_cells"],160)
        self.assertFalse(deep["aggregate_closed"])
        self.assertEqual(row["acceptance"]["anchor"],"scoped-user-acceptance")
        for path in {**index.DEEP_APC_SOURCES,**index.DEEP_APC_FEASIBILITY_SOURCES,**index.DEEP_APC_COMPANION_SOURCES,**index.DEEP_APC_HISTORY_SOURCES,**index.DEEP_APC_JOINT_SOURCES,**index.DEEP_APC_FULL_SOURCES}:
            with patch.object(index.Sources, "current_bytes", return_value=b"forged"), self.assertRaisesRegex(ValueError, "source drift"):
                index.Sources(index.ROOT).raw(path)

    def test_explicit_retained_dispatch(self):
        argv = ["query", "verify-retained", "--family", "A_PC", "--checkpoint", "8.4d", "--recheck-numerics"]
        with patch.object(sys,"argv",argv), patch.object(index.subprocess,"run") as execute:
            index.main()
            calls=[c.args[0] for c in execute.call_args_list]
            self.assertTrue(calls[0][-3].endswith("p984d_apc_runtime.py"))
            self.assertEqual(calls[0][-2:], ["--check-retained", "--recheck-numerics"])
            self.assertTrue(calls[1][-3].endswith("p984d_apc_feasibility.py"))
            self.assertEqual(calls[1][-2:], ["--check", "--recheck-numerics"])
            self.assertTrue(calls[2][-3].endswith("p984d_apc_companion.py"))
            self.assertTrue(calls[3][-3].endswith("p984d_apc_companion_runtime.py"))
            self.assertEqual(len(calls),10)
            self.assertTrue(calls[4][-3].endswith("p984d_apc_history.py"))
            self.assertEqual(calls[4][-2],"--check")
            self.assertEqual(calls[5][-2],"--check-pressure")
            self.assertEqual(calls[6][-2],'check-derivation')
            self.assertEqual(calls[7][-2],'check')
            self.assertTrue(calls[8][-3].endswith('p984d_apc_joint_successor.py'))
            self.assertTrue(calls[9][-3].endswith('p984d_apc_full.py'))
            self.assertEqual(calls[9][-2],'check')
        with patch.object(sys,"argv",argv+["--oracle"]), self.assertRaises(ValueError):
            index.main()


if __name__ == "__main__":
    unittest.main()

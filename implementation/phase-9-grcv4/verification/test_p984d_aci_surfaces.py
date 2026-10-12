"""Selected deep oracle projection/dispatch; no unrelated index or numerics."""

import json
import sys
import unittest
from unittest.mock import patch

import tranche8_evidence as index
import p984d_aci_oracle as oracle

sys.path.insert(0, str(index.ROOT / index.SIDE / "tool/src"))
from grcv4_explorer import tranche8 as api


class DeepACIOracleSurfaceTests(unittest.TestCase):
    def test_selected_api_browser_scope_and_pins(self):
        with patch.object(index, "checked", side_effect=AssertionError("unrelated full index")), \
                patch.object(api, "_index", return_value=index), \
                patch.object(oracle.previous.oracle, "check_step", side_effect=AssertionError("numerical rerun")):
            value = api.tranche8_status(index.ROOT, family="A_CI", checkpoint="8.4d")
        self.assertEqual(value["native"]["accepted_cells"], 40)
        self.assertEqual(value["native"]["passing_pending_cells"], 0)
        self.assertEqual(value["oracle"]["runtime_cells_closed"], 0)
        self.assertTrue(value["oracle"]["oracle_scope_accepted"])
        saved = json.loads((index.ROOT / index.ASSET).read_text().split(" = ", 1)[1].rstrip(";\n"))
        deep = saved["coverage"]["deep_expansion"]
        self.assertEqual(deep["oracle_preparations"], [value["oracle"]])
        self.assertNotIn("A_CI", deep["families_not_executed"])
        self.assertEqual(next(r for r in deep["family_results"] if r['family']=='A_CI'), value['native'])
        self.assertEqual(sum(r["accepted_cells"] for r in deep["family_results"]), 120)
        for path in {**index.DEEP_ACI_ORACLE_SOURCES, **index.DEEP_ACI_SOURCES}:
            with patch.object(index.Sources, "current_bytes", return_value=b"forged"), self.assertRaisesRegex(ValueError, "source drift"):
                index.Sources(index.ROOT).raw(path)

    def test_explicit_oracle_and_native_dispatch(self):
        argv = ["query", "verify-retained", "--family", "A_CI", "--checkpoint", "8.4d"]
        with patch.object(sys, "argv", argv), patch.object(index.subprocess, "run") as execute:
            index.main()
            self.assertTrue(execute.call_args.args[0][-2].endswith("p984d_aci_runtime.py"))
        with patch.object(sys, "argv", argv + ["--oracle", "--recheck-numerics"]), \
                patch.object(index.subprocess, "run") as execute:
            index.main()
            self.assertEqual(execute.call_args.args[0][-2:], ["--check-retained", "--recheck-numerics"])
            self.assertTrue(execute.call_args.args[0][-3].endswith("p984d_aci_oracle.py"))


if __name__ == "__main__":
    unittest.main()

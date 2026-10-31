"""C_PC retained evidence: real API/browser/notebook, no native rerun."""
from copy import deepcopy
from io import BytesIO
import importlib.util
import json
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

from test_p910_family_surfaces import ROOT, TOOL, api, campaign, managed_node, tool_environment


class CPCSurfaces(unittest.TestCase):
    FAMILY = "C_PC"
    ACCEPTED = True
    REMAINING = ["C_CI_PC", "A_CI_PC", "C_RG2b", "A_RG2b"]
    HISTORICAL_FAMILY = "A_OS"
    CELL = "p910-cpc-basin"
    VARIABLE = "phase9_cpc_basin"
    @classmethod
    def setUpClass(cls):
        with campaign.v.no_native_runs():
            cls.evidence = campaign.check(cls.FAMILY)
            cls.view = api.family_basin_status(ROOT, cls.FAMILY)

    def test_execution_never_inherits_historical_source_labels(self):
        live = campaign.references(family=self.HISTORICAL_FAMILY)
        historical = campaign.references(family=self.HISTORICAL_FAMILY, historical=True)
        self.assertNotEqual(live, historical)
        self.assertEqual(campaign.check(self.HISTORICAL_FAMILY)["source_refs"], historical)
        paths = {ROOT/campaign.stem(self.HISTORICAL_FAMILY, "Native"), ROOT/(campaign.stem(self.HISTORICAL_FAMILY, "Native")+".xz")}
        exists = Path.exists
        with patch.object(Path, "exists", lambda p: False if p in paths else exists(p)), \
             patch.object(unittest.TextTestRunner, "run", side_effect=AssertionError("native rerun")):
            with self.assertRaisesRegex(ValueError, "separately declared source epoch"):
                campaign.run_part(self.HISTORICAL_FAMILY, "Native")

    def test_native_evidence_roles_and_carrier_loss(self):
        cases = self.evidence["direct_target"]["observations"]
        initial, returned = [c["saved_native_state"]["inputs"] for c in cases]
        self.assertNotEqual(returned["current"]["C"], returned["reset"]["C"])
        for role in ("current", "reset"):
            self.assertTrue(any(initial[role]["Z_4"]))
            self.assertEqual(set(returned[role]["Z_4"]), {0.0})
            if self.FAMILY.startswith("A_"):
                index = ("current", "reset").index(role)
                self.assertEqual(returned[role]["W_A"], self.evidence["target_compatibility"]["v2"]["return_initializers"][index])
            else:
                self.assertIsNone(returned[role]["W_A"])
        self.assertEqual(self.view["remaining_families"], self.REMAINING)
        self.assertEqual(self.view["user_accepted"], self.ACCEPTED)
        self.assertFalse(self.evidence["user_accepted"])
        self.assertEqual(self.view["P9_10_1_closed"], self.ACCEPTED)
        self.assertEqual(self.view["P9_10_2_closed"], self.ACCEPTED)
        if self.FAMILY.startswith("A_"):
            self.assertNotEqual(returned["current"]["W_A"], returned["reset"]["W_A"])
            policy = f"explicit_A_archive_loss_and_{self.FAMILY}_carrier_zero_initialization"
        else:
            policy = f"explicit_{self.FAMILY}_carrier_loss_and_zero_initialization"
        for version in ("v1", "v2"):
            self.assertEqual(self.evidence["target_compatibility"][version]["history_policy"], policy)

    def test_real_http_notebook_and_historical_source(self):
        spec = importlib.util.spec_from_file_location("cpc_basin_server", TOOL / "scripts/serve_phase9.py")
        server = importlib.util.module_from_spec(spec); spec.loader.exec_module(server)
        def get(path):
            h = server.Handler.__new__(server.Handler)
            h.path, h.wfile = path, BytesIO(); codes = []
            h.send_response = codes.append; h.send_header = lambda *a: None; h.end_headers = lambda: None
            h.do_GET(); return codes[-1], h.wfile.getvalue()
        with patch.object(campaign, "check", return_value=self.evidence):
            code, raw = get("/api/tranche10/families?family="+self.FAMILY)
            self.assertEqual((code, json.loads(raw)), (200, self.view))
            for ref in self.view["evidence"]:
                code, raw = get("/api/tranche10/families/source?family="+self.FAMILY+"&path=" + ref["path"])
                self.assertEqual(code, 200); self.assertEqual(raw, (ROOT/ref["path"]).read_bytes())
            book = json.loads((TOOL/"notebooks/phase9_verification.ipynb").read_bytes())
            cell = next(c for c in book["cells"] if c.get("id") == self.CELL)
            ns = dict(repo_root=ROOT); exec("".join(cell["source"]), ns)
            self.assertEqual(ns[self.VARIABLE], self.view)
            with patch.object(api, "family_basin_status", side_effect=ValueError("drift")):
                with self.assertRaises(ValueError): exec("".join(cell["source"]), ns)
                self.assertIsNone(ns[self.VARIABLE])
        with patch.object(server, "family_basin_status", side_effect=ValueError("drift")):
            self.assertEqual(get("/api/tranche10/families?family="+self.FAMILY)[0], 503)
        raw, ref = api.family_basin_source(ROOT, "src/pygrc/models/grc_9_v4_basin.py", "A_OS")
        self.assertEqual(raw, campaign.successor.original(ROOT, ref["path"]))
        self.assertEqual(ref["revision"], campaign.successor.BASELINE)
        with self.assertRaises(KeyError): api.family_basin_source(ROOT, "../private", self.FAMILY)

    def test_browser_accepted_scope_binding_and_failure_clearing(self):
        js = """
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {canonical} from './verification.js';
import {checkedFamilyBasin,familyBasinLoader} from './tranche10-families.js';
const v=JSON.parse(readFileSync(0,'utf8'));await checkedFamilyBasin(v);
for(const change of [x=>x.family='C_RG2b',x=>x.user_accepted=!v.user_accepted,x=>x.G4_accepted=true,
 x=>x.boundaries[0].role_equations.current.geometry_residual_upper='1']){
 const bad=structuredClone(v);change(bad);const {record_digest,...body}=bad;
 bad.record_digest=createHash('sha256').update(canonical(body)).digest('hex');
 await assert.rejects(()=>checkedFamilyBasin(bad));
}
const output={children:[],replaceChildren(){this.children=[]},append(e){this.children.push(e)}};
const status={textContent:''};let ok=true;
const load=familyBasinLoader(output,status,async()=>({ok,json:async()=>v}),tag=>({tag,textContent:''}));
await load(v.family);assert.equal(output.children.filter(x=>x.tag==='h4').length,2);
assert.match(status.textContent,v.user_accepted?/Accepted within bounded/:/acceptance pending/);
ok=false;await load(v.family);assert.equal(output.children.length,0);assert.match(status.textContent,/unavailable/);
"""
        result = subprocess.run([str(managed_node()), "--input-type=module", "-e", js],
            input=json.dumps(self.view), text=True, capture_output=True,
            cwd=TOOL/"phase9-web", timeout=30, env=tool_environment())
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()

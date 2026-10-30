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
    @classmethod
    def setUpClass(cls):
        with campaign.v.no_native_runs():
            cls.evidence = campaign.check("C_PC")
            cls.view = api.family_basin_status(ROOT, "C_PC")

    def test_execution_never_inherits_historical_source_labels(self):
        live = campaign.references(family="A_OS")
        historical = campaign.references(family="A_OS", historical=True)
        self.assertNotEqual(live, historical)
        self.assertEqual(campaign.check("A_OS")["source_refs"], historical)
        paths = {ROOT/campaign.stem("A_OS", "Native"), ROOT/(campaign.stem("A_OS", "Native")+".xz")}
        exists = Path.exists
        with patch.object(Path, "exists", lambda p: False if p in paths else exists(p)), \
             patch.object(unittest.TextTestRunner, "run", side_effect=AssertionError("native rerun")):
            with self.assertRaisesRegex(ValueError, "separately declared source epoch"):
                campaign.run_part("A_OS", "Native")

    def test_native_evidence_roles_and_carrier_loss(self):
        cases = self.evidence["direct_target"]["observations"]
        initial, returned = [c["saved_native_state"]["inputs"] for c in cases]
        self.assertNotEqual(returned["current"]["C"], returned["reset"]["C"])
        for role in ("current", "reset"):
            self.assertTrue(any(initial[role]["Z_4"]))
            self.assertEqual(set(returned[role]["Z_4"]), {0.0})
            self.assertIsNone(returned[role]["W_A"])
        self.assertEqual(self.view["remaining_families"], ["C_CI_PC", "A_CI_PC", "C_RG2b", "A_RG2b"])
        self.assertTrue(self.view["user_accepted"])
        self.assertFalse(self.evidence["user_accepted"])
        self.assertTrue(self.view["P9_10_1_closed"])
        self.assertTrue(self.view["P9_10_2_closed"])
        for version in ("v1", "v2"):
            self.assertEqual(self.evidence["target_compatibility"][version]["history_policy"],
                             "explicit_C_PC_carrier_loss_and_zero_initialization")

    def test_real_http_notebook_and_historical_source(self):
        spec = importlib.util.spec_from_file_location("cpc_basin_server", TOOL / "scripts/serve_phase9.py")
        server = importlib.util.module_from_spec(spec); spec.loader.exec_module(server)
        def get(path):
            h = server.Handler.__new__(server.Handler)
            h.path, h.wfile = path, BytesIO(); codes = []
            h.send_response = codes.append; h.send_header = lambda *a: None; h.end_headers = lambda: None
            h.do_GET(); return codes[-1], h.wfile.getvalue()
        with patch.object(campaign, "check", return_value=self.evidence):
            code, raw = get("/api/tranche10/families?family=C_PC")
            self.assertEqual((code, json.loads(raw)), (200, self.view))
            for ref in self.view["evidence"]:
                code, raw = get("/api/tranche10/families/source?family=C_PC&path=" + ref["path"])
                self.assertEqual(code, 200); self.assertEqual(raw, (ROOT/ref["path"]).read_bytes())
            book = json.loads((TOOL/"notebooks/phase9_verification.ipynb").read_bytes())
            cell = next(c for c in book["cells"] if c.get("id") == "p910-cpc-basin")
            ns = dict(repo_root=ROOT); exec("".join(cell["source"]), ns)
            self.assertEqual(ns["phase9_cpc_basin"], self.view)
            with patch.object(api, "family_basin_status", side_effect=ValueError("drift")):
                with self.assertRaises(ValueError): exec("".join(cell["source"]), ns)
                self.assertIsNone(ns["phase9_cpc_basin"])
        with patch.object(server, "family_basin_status", side_effect=ValueError("drift")):
            self.assertEqual(get("/api/tranche10/families?family=C_PC")[0], 503)
        raw, ref = api.family_basin_source(ROOT, "src/pygrc/models/grc_9_v4_basin.py", "A_OS")
        self.assertEqual(raw, campaign.successor.original(ROOT, ref["path"]))
        self.assertEqual(ref["revision"], campaign.successor.BASELINE)
        with self.assertRaises(KeyError): api.family_basin_source(ROOT, "../private", "C_PC")

    def test_browser_accepted_scope_binding_and_failure_clearing(self):
        js = """
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {canonical} from './verification.js';
import {checkedFamilyBasin,familyBasinLoader} from './tranche10-families.js';
const v=JSON.parse(readFileSync(0,'utf8'));await checkedFamilyBasin(v);
for(const change of [x=>x.family='C_CI_PC',x=>x.user_accepted=false,x=>x.G4_accepted=true,
 x=>x.boundaries[0].role_equations.current.geometry_residual_upper='1']){
 const bad=structuredClone(v);change(bad);const {record_digest,...body}=bad;
 bad.record_digest=createHash('sha256').update(canonical(body)).digest('hex');
 await assert.rejects(()=>checkedFamilyBasin(bad));
}
const output={children:[],replaceChildren(){this.children=[]},append(e){this.children.push(e)}};
const status={textContent:''};let ok=true;
const load=familyBasinLoader(output,status,async()=>({ok,json:async()=>v}),tag=>({tag,textContent:''}));
await load('C_PC');assert.equal(output.children.filter(x=>x.tag==='h4').length,2);
assert.match(status.textContent,/Accepted within bounded C_PC scope/);
ok=false;await load('C_PC');assert.equal(output.children.length,0);assert.match(status.textContent,/unavailable/);
"""
        result = subprocess.run([str(managed_node()), "--input-type=module", "-e", js],
            input=json.dumps(self.view), text=True, capture_output=True,
            cwd=TOOL/"phase9-web", timeout=30, env=tool_environment())
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()

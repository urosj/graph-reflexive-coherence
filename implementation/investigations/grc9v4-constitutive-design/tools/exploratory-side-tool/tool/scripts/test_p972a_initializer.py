"""Focused initializer authority/API/notebook/browser checks, not migration tests."""

from copy import deepcopy
from io import BytesIO
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

TOOL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL / "src"))
from grcv4_explorer import a_initializer as api  # noqa: E402
from grcv4_explorer import abundance, receipt_parents  # noqa: E402
from grcv4_explorer.canonical import record_digest  # noqa: E402
from grcv4_explorer.errors import SourceAdmissionError  # noqa: E402
from grcv4_explorer.forensic import contract_provenance, reconstruction_path  # noqa: E402
from grcv4_explorer.paths import repository_root  # noqa: E402
from grcv4_explorer.tooling import managed_node, tool_environment  # noqa: E402


class InitializerAuthorityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = repository_root()
        cls.old = abundance.load_abundance_forensic_context(cls.root, TOOL.parent)
        cls.current = api.load_current_forensic_context(cls.root, TOOL.parent)
        cls.payload = api.initializer_authority(cls.root, TOOL.parent)

    def test_append_only_optional_authority_and_forward_debt(self):
        self.assertEqual(len(self.current.nodes) - len(self.old.nodes), 6)
        for key, row in self.old.nodes.items():
            self.assertEqual(self.current.nodes[key], row)
        edges = {e["edge_id"]: e for e in self.current.propagation_edges}
        for row in self.old.propagation_edges:
            self.assertEqual(edges[row["edge_id"]], row)
        for loader in (abundance.load_current_forensic_context, receipt_parents.load_current_forensic_context):
            self.assertEqual(loader(self.root, TOOL.parent).graph_digest, self.current.graph_digest)
        self.assertEqual(self.current.nodes["current_claim:" + api.CLAIM_ID]["attributes"]["claim_class"], "optional")
        with self.assertRaises(KeyError):
            contract_provenance(self.old, api.CONTRACT_ID)
        trace = self.payload["contracts"][0]
        self.assertEqual(trace["rows"][0]["payload"]["support_disposition"], ["required"])
        self.assertEqual(trace["rows"][0]["source_ref"]["source_json_pointer"], "/contracts/0")
        self.assertTrue(trace["rows"][0]["edge_refs"])
        debt = self.payload["debt"]["rows"]
        self.assertEqual(debt[0]["payload"]["status"], "resolved_bounded_design")
        self.assertEqual(debt[1]["classification"], "forward_verification_routing")
        self.assertEqual(debt[1]["payload"]["status"], "pending_forward")
        rebuilt = reconstruction_path(self.current, api.CLAIM_ID)
        self.assertTrue(rebuilt["rows"][0]["payload"]["verification_obligations_excluded"])
        for trace in (self.payload["claim"], self.payload["debt"], self.payload["object"], *self.payload["contracts"]):
            self.assertEqual(trace["trace_digest"], record_digest(trace, "trace_digest"))

    def test_pinned_source_and_admission_reject_coherent_rewrites(self):
        original = api.load_json_object
        for defect in ("rule", "classification", "status", "G2", "resolved_all", "binding", "missing"):
            def altered(path):
                value = deepcopy(original(path))
                if path.name == Path(api.SOURCE).name:
                    if defect == "rule": value["contracts"][0]["staging"]["passes"] = 2
                    if defect == "classification": value["claim"]["claim_class"] = "normative"
                    if defect == "status": value["status"] = "proposed"
                    if defect == "G2": value["G2_accepted"] = True
                    if defect == "resolved_all": value["debt"]["remaining_work"] = []
                    value["record_digest"] = record_digest(value, "record_digest")
                if path.name == api.ADMISSION:
                    if defect == "missing": raise FileNotFoundError(api.ADMISSION)
                    if defect == "binding": value["graph_digest"] = "0" * 64
                    value["record_digest"] = record_digest(value, "record_digest")
                return value
            with self.subTest(defect=defect), patch.object(api, "load_json_object", side_effect=altered):
                with self.assertRaises((SourceAdmissionError, FileNotFoundError)):
                    api.load_current_forensic_context(self.root, TOOL.parent)

    def test_changed_design_and_unknown_source_hold_all_current_loaders(self):
        sha = api.file_sha256
        def changed(path):
            return "0" * 64 if path.name.endswith("Proposal.md") else sha(path)
        with patch.object(api, "file_sha256", side_effect=changed):
            with self.assertRaises(SourceAdmissionError):
                api.load_current_forensic_context(self.root, TOOL.parent)
        for state in ("new_unprocessed_source_available", "admitted_source_changed", "missing_source"):
            with patch.object(api, "discover_sources", return_value={"state": state}):
                for loader in (api.load_current_forensic_context, abundance.load_current_forensic_context,
                               receipt_parents.load_current_forensic_context):
                    with self.subTest(state=state, loader=loader), self.assertRaises(SourceAdmissionError):
                        loader(self.root, TOOL.parent)
        # An explicit historical query is available, never used as a current fallback.
        self.assertEqual(abundance.load_abundance_forensic_context(self.root, TOOL.parent).graph_digest,
                         self.old.graph_digest)

    def test_current_checker_rejects_rehashed_historical_relabels(self):
        verification = self.root / "implementation/phase-9-grcv4/verification"
        sys.path.insert(0, str(verification))
        import verify_p972a_initializer_authority as checker
        read_bytes = Path.read_bytes
        for index, defect in ((0, "missing_pair"), (0, "positive_C_to_A"), (1, "G2")):
            target = self.root / checker.RECORDS[index]
            value = json.loads(read_bytes(target))
            if defect == "missing_pair":
                value["cases"].pop("A_C_PC")
            elif defect == "positive_C_to_A":
                value["pending_positive_classes"] = []
            else:
                value["new_G2_support"] = ["A_PC"]
            value["record_digest"] = record_digest(value, "record_digest")
            changed = json.dumps(value).encode()
            def altered(path):
                return changed if path == target else read_bytes(path)
            checker.preserved_migrations.cache_clear()
            with self.subTest(defect=defect), patch.object(Path, "read_bytes", altered):
                with self.assertRaisesRegex(ValueError, "accepted migration evidence changed"):
                    checker.preserved_migrations()
        checker.preserved_migrations.cache_clear()

    def test_actual_notebook_cell_and_http_handler_match_and_clear(self):
        book = json.loads((TOOL / "notebooks/phase9_verification.ipynb").read_text())
        cell = next(c for c in book["cells"] if c["id"] == "a-initializer-authority")
        namespace = {"Path": Path, "repo_root": self.root, "PHASE9_REPO_ROOT": self.root}
        code = compile("".join(cell["source"]), "phase9_verification.ipynb:a-initializer-authority", "exec")
        exec(code, namespace)
        self.assertEqual(namespace["phase9_initializer_authority"], self.payload)
        with patch.object(api, "initializer_authority", side_effect=SourceAdmissionError("held")):
            with self.assertRaises(SourceAdmissionError): exec(code, namespace)
        self.assertIsNone(namespace["phase9_initializer_authority"])
        spec = importlib.util.spec_from_file_location("p972a_http", TOOL / "scripts/serve_phase9.py")
        server = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(server)
        handler = server.Handler.__new__(server.Handler)
        handler.path = "/api/a-initializer"
        statuses = []
        handler.send_response = statuses.append
        handler.send_header = lambda *args: None
        handler.end_headers = lambda: None
        handler.wfile = BytesIO()
        handler.do_GET()
        self.assertEqual(statuses, [200])
        self.assertEqual(json.loads(handler.wfile.getvalue()), self.payload)
        handler.wfile = BytesIO()
        with patch.object(server, "initializer_authority", side_effect=SourceAdmissionError("held")):
            handler.do_GET()
        self.assertEqual(statuses, [200, 503])
        self.assertEqual(set(json.loads(handler.wfile.getvalue())), {"error"})

    def test_actual_browser_validator_rejects_rehashed_overclaims(self):
        code = """
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {canonical, verifiedInitializer, verifiedParents, verifiedAbundance} from './verification.js';
const input = JSON.parse(readFileSync(0, 'utf8')), value=input.initializer;
assert.deepEqual(await verifiedInitializer(value), value);
await verifiedParents(input.parents); await verifiedAbundance(input.abundance);
for(const edit of [v=>v.G2_accepted=true, v=>v.positive_migration_verified=true,
 v=>v.aggregate_closed=true, v=>v.payload_specification_complete=true,
 v=>v.contracts=[], v=>v.debt.rows.pop(), v=>v.claim.rows[0].classification='normative',
 v=>v.contracts[0].rows[0].edge_refs=[]]) {
 const bad=structuredClone(value); edit(bad); delete bad.projection_digest;
 bad.projection_digest=createHash('sha256').update(canonical(bad)).digest('hex');
 await assert.rejects(verifiedInitializer(bad));
}
console.log('INITIALIZER_VALIDATOR_PASS rehashed_controls=8');
"""
        self.node(code, dict(initializer=self.payload,
                             parents=receipt_parents.parent_authority(self.root, TOOL.parent),
                             abundance=abundance.abundance_authority(self.root, TOOL.parent)),
                  "INITIALIZER_VALIDATOR_PASS rehashed_controls=8")

    def node(self, code, payload, expected):
        result = subprocess.run([str(managed_node()), "--input-type=module", "-e", code],
                                cwd=TOOL / "phase9-web", input=json.dumps(payload),
                                capture_output=True, text=True, env=tool_environment(), timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), expected)

    def test_actual_browser_buttons_selectors_and_stale_clearing(self):
        # Actual shipped HTML/JS in Chromium. Network routes carry the actual API
        # projection; the real HTTP handler is independently exercised above.
        code = """
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {chromium} from '../web/node_modules/playwright/index.mjs';
const value=JSON.parse(readFileSync(0,'utf8'));
const browser=await chromium.launch();
try {
 for(const width of [1440,390]) {
  const page=await browser.newPage({viewport:{width,height:900}});
  const errors=[]; page.on('pageerror',error=>errors.push(String(error)));
  let mode='ok';
  await page.route('http://localhost:4174/**',async route=>{
   const path=new URL(route.request().url()).pathname;
   if(path==='/api/a-initializer') {
    const selected=mode;
    if(selected==='slow') await new Promise(resolve=>setTimeout(resolve,150));
    return route.fulfill({status:selected==='fail'?503:200,contentType:'application/json',
      body:JSON.stringify(selected==='fail'?{error:'held'}:value)});
   }
   if(path.startsWith('/api/')) return route.fulfill({status:503,body:'{}'});
   const name=path==='/'?'index.html':path.slice(1);
   return route.fulfill({body:readFileSync(name),contentType:name.endsWith('.js')?'text/javascript':name.endsWith('.css')?'text/css':'text/html'});
  });
  await page.goto('http://localhost:4174/');
  const button=page.locator('#initializer-refresh'), output=page.locator('#initializer-output');
  await button.click();
  await page.waitForFunction(()=>document.querySelector('#initializer-status').textContent.startsWith('Producer choice resolved'));
  for(const key of ['claim','debt','object','contract']) {
   await page.locator('#initializer-view').selectOption(key);
   assert.deepEqual(JSON.parse(await output.textContent()),key==='contract'?value.contracts[0]:value[key]);
  }
  mode='fail'; await button.click();
  await page.waitForFunction(()=>document.querySelector('#initializer-status').textContent.startsWith('Held:'));
  assert.equal(await output.textContent(),'');
  mode='ok'; await button.click();
  await page.waitForFunction(()=>document.querySelector('#initializer-status').textContent.startsWith('Producer choice resolved'));
  mode='slow'; const pending=page.waitForResponse('**/api/a-initializer'); await button.click();
  mode='fail'; await button.click(); await pending;
  await page.waitForTimeout(200);
  assert.equal(await output.textContent(),'');
  assert.match(await page.locator('#initializer-status').textContent(),/^Held:/);
  assert.deepEqual(errors,[]); await page.close();
 }
} finally { await browser.close(); }
console.log('INITIALIZER_BROWSER_PASS desktop_mobile=true stale_clearing=true');
"""
        self.node(code, self.payload, "INITIALIZER_BROWSER_PASS desktop_mobile=true stale_clearing=true")


if __name__ == "__main__":
    unittest.main()

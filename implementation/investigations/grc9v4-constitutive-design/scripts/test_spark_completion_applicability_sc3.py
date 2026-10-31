"""Focused authority, propagation and user-surface pressure; no numerical reruns."""
from copy import deepcopy
from dataclasses import replace
from io import BytesIO
import importlib.util
import json
import subprocess
import unittest
from unittest.mock import patch

import check_spark_completion_applicability_sc3 as check
from grcv4_explorer import spark_applicability as sc
from grcv4_explorer import spark_completion as prior
from grcv4_explorer import basin
from grcv4_explorer.canonical import record_digest
from grcv4_explorer.errors import SourceAdmissionError
from grcv4_explorer.forensic import contract_provenance, debt_lifecycle
from grcv4_explorer.tooling import managed_node, tool_environment

ROOT, SIDE = check.ROOT, check.SIDE
TOOL = SIDE / "tool"


class ApplicabilitySC3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.view = sc.spark_applicability_authority(ROOT, SIDE)

    def test_conditional_authority_and_preserved_predecessor(self):
        self.assertEqual(check.check()["scientific_families"], ["C_OS", "C_CI"])
        old = prior.load_spark_completion_forensic_context(ROOT, SIDE)
        new = sc.load_spark_applicability_forensic_context(ROOT, SIDE)
        self.assertTrue(all(new.nodes[k] == row for k, row in old.nodes.items()))
        for key in ["SC-CCI-EC-JOINT-ROOT", "SC-CCI-EC-FULL-STATE-RETURN", "SC-CCI-EC-COMPLETION"]:
            trace = contract_provenance(new, key)
            self.assertEqual(trace["rows"][0]["payload"]["support_disposition"], ["accepted_bounded_conditional_science"])
            with self.assertRaises(KeyError):
                contract_provenance(old, key)
        self.assertEqual(contract_provenance(new, "D10.2-EC-CI-C-ROOT")["rows"][0]["payload"]["support_disposition"],
                         contract_provenance(old, "D10.2-EC-CI-C-ROOT")["rows"][0]["payload"]["support_disposition"])
        forward = [r for r in self.view["debts"][0]["rows"] if r["classification"] == "forward_verification_routing"]
        self.assertEqual(len(forward), 2)
        self.assertTrue(all(r["payload"]["status"] == "pending_forward" for r in forward))
        self.assertEqual(sum(r["status"] == "not_yet_investigated" for r in self.view["family_dispositions"]), 8)
        self.assertFalse(self.view["scope"]["native_completed_spark_support"])

    def test_rehashed_widening_and_source_drift_reject(self):
        original = sc.load_json_object
        for defect in ("native", "all_ten", "claim_class", "os_root", "debt", "review", "manifest", "admission"):
            def altered(path):
                value = deepcopy(original(path))
                if path == ROOT / sc.SOURCE:
                    if defect == "native": value["scope"]["native_completed_spark_support"] = True
                    if defect == "all_ten": value["family_dispositions"][2]["status"] = "accepted_bounded_scientific"
                    if defect == "claim_class": value["claims"][0]["claim_class"] = "normative"
                    if defect == "os_root": value["contracts"][0]["normative_equation_or_contract"] = "Use OS predictor."
                    if defect == "debt": value["debts"][0]["remaining_work"] = []
                if path.name == "CCIScientificAcceptance.json" and defect == "review":
                    value["review_limits"] = []
                if path == ROOT / sc.MANIFEST and defect == "manifest": value["chain"].pop()
                if path.name == sc.ADMISSION and defect == "admission": value["graph_digest"] = "0" * 64
                if "record_digest" in value: value["record_digest"] = record_digest(value, "record_digest")
                return value
            with self.subTest(defect=defect), patch.object(sc, "load_json_object", altered):
                with self.assertRaises(SourceAdmissionError): sc.spark_applicability_authority(ROOT, SIDE)
        sha = basin.file_sha256
        target = ROOT / check.INV / "evidence/spark-completion/applicability/CCI-current.json.xz"
        with patch.object(basin, "file_sha256", lambda p: "0" * 64 if p == target else sha(p)):
            with self.assertRaises(SourceAdmissionError): sc.spark_applicability_authority(ROOT, SIDE)
        with self.assertRaises(KeyError): sc.spark_applicability_source(ROOT, SIDE, "../outside")

    def test_forward_obligation_list_rejects_malformed_and_duplicate_ids(self):
        context = sc.load_spark_applicability_forensic_context(ROOT, SIDE)
        document = context.documents_by_record[sc.RECORD_ID]
        original = document.data["debts"][0]["verification_obligation_ids"]
        for value in ("not-a-list", [None], [original[0], original[0]]):
            data = deepcopy(document.data)
            data["debts"][0]["verification_obligation_ids"] = value
            documents = tuple(replace(d, data=data) if d.record_identifier == sc.RECORD_ID else d
                              for d in context.documents)
            with self.subTest(value=value), self.assertRaises(SourceAdmissionError):
                debt_lifecycle(replace(context, documents=documents), "SC-APP-DEBT-C_CI")

    def test_http_notebook_and_failed_refresh(self):
        book = json.loads((TOOL / "notebooks/phase9_verification.ipynb").read_bytes())
        cell = next(c for c in book["cells"] if c.get("id") == "spark-completion-applicability")
        code = compile("".join(cell["source"]), "applicability-cell", "exec")
        ns = {"repo_root": ROOT}; exec(code, ns)
        self.assertEqual(ns["phase9_spark_applicability"], self.view)
        with patch.object(sc, "spark_applicability_authority", side_effect=SourceAdmissionError("held")):
            with self.assertRaises(SourceAdmissionError): exec(code, ns)
        self.assertIsNone(ns["phase9_spark_applicability"])
        spec = importlib.util.spec_from_file_location("applicability_server", TOOL / "scripts/serve_phase9.py")
        server = importlib.util.module_from_spec(spec); spec.loader.exec_module(server)
        h = server.Handler.__new__(server.Handler); codes = []
        h.send_response = codes.append; h.send_header = lambda *a: None; h.end_headers = lambda: None
        h.path = "/api/spark-completion/applicability"; h.wfile = BytesIO(); h.do_GET()
        self.assertEqual(codes[-1], 200); self.assertEqual(json.loads(h.wfile.getvalue()), self.view)
        with patch.object(server, "spark_applicability_authority", side_effect=SourceAdmissionError("held")):
            h.wfile = BytesIO(); h.do_GET()
        self.assertEqual(codes[-1], 503); self.assertEqual(set(json.loads(h.wfile.getvalue())), {"error"})
        h.path += "?family=C_PC"; h.wfile = BytesIO(); h.do_GET(); self.assertEqual(codes[-1], 404)
        h.path = "/api/spark-completion/applicability/source?path=specs%2Fgrc-9-v4-spark-completion-ci.md"
        h.wfile = BytesIO(); h.do_GET(); self.assertEqual(codes[-1], 200)
        self.assertEqual(h.wfile.getvalue(), (ROOT / "specs/grc-9-v4-spark-completion-ci.md").read_bytes())
        h.path = "/spark-applicability.js"; h.wfile = BytesIO(); h.do_GET()
        self.assertEqual(codes[-1], 200)
        self.assertEqual(h.wfile.getvalue(), (TOOL / "phase9-web/spark-applicability.js").read_bytes())

    def test_browser_scope_and_stale_output(self):
        js = r'''
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {canonicalBasin} from './basin.js';
import {checkedSparkApplicability,sparkApplicabilityLoader} from './spark-applicability.js';
const value=JSON.parse(readFileSync(0,'utf8'));
assert.deepEqual(await checkedSparkApplicability(value),value);
for(const edit of [v=>v.scope.native_completed_spark_support=true,
 v=>v.scope.scientific_families.push('C_PC'),v=>v.review_limits=[],
 v=>v.claims.pop(),v=>v.family_dispositions.pop(),v=>v.scope.G4_accepted=true]) {
 const bad=structuredClone(value);edit(bad);delete bad.projection_digest;
 bad.projection_digest=createHash('sha256').update(canonicalBasin(bad)).digest('hex');
 await assert.rejects(checkedSparkApplicability(bad));
}
const output={children:[],replaceChildren(){this.children=[]},append(e){this.children.push(e)}},status={};
let ok=true;
const load=sparkApplicabilityLoader(output,status,async()=>({ok,json:async()=>value}),tag=>({tag,append(){}}));
await load();assert.ok(output.children.length>20);assert.match(status.textContent,/Native work remains separate/);
assert.ok(output.children.some(e=>e.textContent.includes('C_PC · not_yet_investigated')));
ok=false;await load();assert.equal(output.children.length,0);assert.match(status.textContent,/unavailable/);
assert.match(readFileSync('index.html','utf8'),/id="spark-applicability-refresh"/);
console.log('SPARK_APPLICABILITY_BROWSER_PASS');
'''
        result = subprocess.run([str(managed_node()), "--input-type=module", "-e", js],
            cwd=TOOL / "phase9-web", input=json.dumps(self.view), text=True, capture_output=True,
            timeout=30, env=tool_environment())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "SPARK_APPLICABILITY_BROWSER_PASS")


if __name__ == "__main__":
    unittest.main()

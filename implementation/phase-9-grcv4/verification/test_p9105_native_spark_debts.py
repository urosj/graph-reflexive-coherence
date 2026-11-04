"""Focused reconciliation pressure; accepted numerical campaigns are reused."""

from copy import deepcopy
import io
import json
import subprocess
import sys
import unittest
from unittest.mock import patch

import p9105_native_spark_debts as c

sys.path.insert(0, str(c.ROOT / (c.INV + "tools/exploratory-side-tool/tool/src")))
from grcv4_explorer import spark_native_debts as api


class NativeDebtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Pressure the new mapping against immutable accepted inputs. The
        # unchanged native support checker is exercised separately, not once
        # per mutation/surface; no numerical campaign is repeated here.
        cls.expected = c.build(checked_support=c.frozen(c.ROOT, c.support.RECORD))
        cls.value = c.validate(
            json.loads((c.ROOT / c.LEDGER).read_bytes()), cls.expected
        )
        cls.view = dict(ledger=cls.value)

    def test_exact_coverage_and_native_research_separation(self):
        v = self.value
        self.assertEqual(len(v["families"]), 10)
        self.assertEqual(len(v["verification_obligations"]), 30)
        self.assertEqual(len(v["debts"]), 14)
        self.assertEqual(len(v["inherited_debts"]), 29)
        self.assertEqual(
            len(
                [
                    o
                    for o in v["verification_obligations"]
                    if o["residual_obligation_ids"]
                ]
            ),
            4,
        )
        for r in v["families"]:
            self.assertEqual(r["exact_subject"]["roles"]["current"]["local_gain"], 1)
            self.assertEqual(r["exact_subject"]["roles"]["reset"]["local_gain"], 0)
            self.assertIn(
                r["scientific_acceptance"]["path"],
                {s["path"] for s in v["source_refs"]},
            )
        self.assertEqual(v["scope"]["new_scientific_claims"], [])
        self.assertFalse(v["scope"]["G4_accepted"])
        site = next(
            r for r in v["debts"] if r["debt_id"] == "SC2-DEBT-NONLINEAR-SITE-BINDING"
        )
        self.assertEqual(site["disposition"], "resolved_bounded_scientific_and_native")
        self.assertEqual(site["residual_obligation_ids"], [])
        self.assertEqual(
            sum(r["adopted_endpoint_successor"] is not None for r in v["families"]), 5
        )

    def test_resealed_overclaims_and_missing_lineage_reject(self):
        mutations = [
            lambda v: v["verification_obligations"].pop(),
            lambda v: v["verification_obligations"][0].update(
                disposition="resolved_unconditionally"
            ),
            lambda v: v["verification_obligations"][0].update(family="A_RG2b"),
            lambda v: v["residual_obligations"].clear(),
            lambda v: v["scientific_claims"][0]["scientific_claim"].update(
                claim_class="normative_unconditional"
            ),
            lambda v: v["families"][0]["exact_subject"]["subjects"][1].update(
                graph_digest="foreign"
            ),
            lambda v: v["families"][0]["exact_subject"]["roles"]["reset"].update(
                local_gain=1
            ),
            lambda v: v["families"][0]["native_evidence"]["native_obligations"].pop(),
            lambda v: v["families"][1]["scientific_acceptance"].update(
                path="wrong.json"
            ),
            lambda v: v["inherited_debts"][0].update(disposition="resolved"),
            lambda v: v["scope"].update(hierarchy_support=True),
            lambda v: v["scope"].update(G4_accepted=True),
            lambda v: v.update(reconciliation_user_accepted=True),
        ]
        for mutate in mutations:
            value = deepcopy(self.value)
            mutate(value)
            with (
                self.subTest(mutation=mutations.index(mutate)),
                self.assertRaises(ValueError),
            ):
                c.validate(c.seal(value), self.expected)

    def test_changed_accepted_source_and_nonportable_ref_reject(self):
        path = c.REGRESSION
        expected = (c.ROOT / path).read_bytes()
        with patch.object(c, "baseline_bytes", return_value=expected + b" "):
            with self.assertRaises(ValueError):
                c.frozen(c.ROOT, path)
        for name in ("/absolute/record.json", "../record.json"):
            with self.assertRaises(ValueError):
                c.ref(c.ROOT, name)

    def test_typed_queries_preserve_scientific_payloads_and_residuals(self):
        for row in self.value["scientific_claims"]:
            trace = api.query(self.view, "scientific_claim", row["claim_id"])
            self.assertEqual(trace["row"]["scientific_claim"], row["scientific_claim"])
            self.assertNotIn("new_authority", trace["support_disposition"])
        trace = api.query(
            self.view, "verification_obligation", "SC-VO-NATIVE-LIFECYCLE"
        )
        self.assertEqual(trace["residual_obligations"][0]["obligation_id"], c.HIERARCHY)
        self.assertEqual(trace["row"]["predecessor"]["status"], "pending_forward")
        self.assertTrue(trace["row"]["native_portion_discharged"])
        trace = api.query(self.view, "debt_lifecycle", "SC-DEBT-STABILITY")
        self.assertEqual(len(trace["evidence"]), 10)
        with self.assertRaises(KeyError):
            api.query(self.view, "debt_lifecycle", "UNKNOWN")

    def test_http_handlers_browser_and_notebook(self):
        from grcv4_explorer.tooling import managed_node, tool_environment

        side = c.ROOT / (c.INV + "tools/exploratory-side-tool/tool")
        sys.path.insert(0, str(side / "scripts"))
        import serve_phase9 as server

        with patch.object(c, "checked", return_value=self.value):
            view = api.native_spark_debts(c.ROOT)

        def request(url):
            handler = object.__new__(server.Handler)
            handler.path = url
            handler.wfile = io.BytesIO()
            status = []
            handler.send_response = status.append
            handler.send_header = lambda *args: None
            handler.end_headers = lambda: None
            handler.do_GET()
            return status[0], handler.wfile.getvalue()

        with patch.object(server, "native_spark_debts", return_value=view):
            code, data = request("/api/native-spark/debts")
            self.assertEqual(code, 200)
            self.assertEqual(json.loads(data), view)
            self.assertEqual(request("/api/native-spark/debts?run=1")[0], 503)
            self.assertEqual(
                request("/api/native-spark/debts/source?name=../bad")[0], 503
            )
            with patch.object(
                server, "native_spark_debts", side_effect=ValueError("changed source")
            ):
                self.assertEqual(request("/api/native-spark/debts")[0], 503)
        script = """
import {checkedDebts, debtLoader} from './implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/phase9-web/spark-native-debts.js';
const v=JSON.parse(await new Promise(r=>{let s='';process.stdin.on('data',d=>s+=d);process.stdin.on('end',()=>r(s));}));
await checkedDebts(v);
const bad=structuredClone(v);bad.ledger.scope.G4_accepted=true;
let rejected=false;try{await checkedDebts(bad);}catch{rejected=true;}if(!rejected)throw Error('accepted mutation');
const output={children:[],replaceChildren(){this.children=[]},append(v){this.children.push(v)}};
const status={};let fail=false;
const run=debtLoader(output,status,async()=>({ok:!fail,json:async()=>v}),()=>({}));
await run();if(output.children.length<10)throw Error('no family rows');
fail=true;await run();if(output.children.length)throw Error('stale results survived');
"""
        subprocess.run(
            [str(managed_node()), "--input-type=module", "-e", script],
            input=json.dumps(view).encode(),
            cwd=c.ROOT,
            env=tool_environment(),
            timeout=30,
            check=True,
        )
        notebook = json.loads(
            (side / "notebooks/phase9_verification.ipynb").read_bytes()
        )
        cell = next(x for x in notebook["cells"] if x.get("id") == "native-spark-debts")
        source = "".join(cell["source"])
        self.assertIn("native_debt_view = None", source)
        self.assertIn("native_spark_debts(repo_root)", source)
        self.assertEqual(cell["outputs"], [])


if __name__ == "__main__":
    unittest.main()

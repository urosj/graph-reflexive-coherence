"""Publication, compact-subject and preserved-source checks; no trajectories."""

import importlib.util
import json
import subprocess
import sys
import unittest
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
TOOL = (
    ROOT
    / "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool"
)
sys.path[:0] = [str(TOOL / "src"), str(ROOT / "src")]
from grcv4_explorer import spark_native_rg2b_campaign as surface
from grcv4_explorer.errors import SourceAdmissionError
from p991a6_rg2b_campaign import Adapter


class RG2bCampaignSurfaceTests(unittest.TestCase):
    def test_both_retained_records_and_fixed_scope(self):
        for family in ("C_RG2b", "A_RG2b"):
            value = surface.native_rg2b_campaign(ROOT, family)
            self.assertTrue(value["native_endpoint_verified"])
            self.assertFalse(value["native_completion_support"])
            self.assertFalse(value["user_accepted"])
            self.assertEqual(value["roles"]["current"]["local_gain"], 1)
            self.assertEqual(value["roles"]["reset"]["local_gain"], 0)

    def test_changed_record_source_and_stream_reject(self):
        original = Path.read_bytes
        for family in ("C_RG2b", "A_RG2b"):
            a = Adapter(family)
            for name in (
                a.path("Campaign.json"),
                a.path("current.jsonl.xz"),
                "src/pygrc/models/grc_9_v4_api_lifecycle.py",
            ):

                def bad(path, name=name):
                    return original(path) + (b"changed" if path == ROOT / name else b"")

                with (
                    patch.object(Path, "read_bytes", bad),
                    self.assertRaises((ValueError, SourceAdmissionError)),
                ):
                    surface.native_rg2b_campaign(ROOT, family)

    def test_http_source_static_and_query_rejection(self):
        spec = importlib.util.spec_from_file_location(
            "rg2b_campaign_server", TOOL / "scripts/serve_phase9.py"
        )
        server = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(server)
        handler = server.Handler.__new__(server.Handler)
        codes = []
        handler.command = "GET"
        handler.send_response = lambda code, message=None: codes.append(code)
        handler.send_header = lambda *args: None
        handler.end_headers = lambda: None
        for slug in ("c-rg2b", "a-rg2b"):
            for suffix in ("", "/source", "?widen=true"):
                handler.path = "/api/native-spark/" + slug + "/campaign" + suffix
                handler.wfile = BytesIO()
                handler.do_GET()
                self.assertEqual(codes[-1], 503 if suffix.startswith("?") else 200)
        handler.path = "/spark-native-rg2b-campaign.js"
        handler.wfile = BytesIO()
        handler.do_GET()
        self.assertEqual(codes[-1], 200)

    def test_notebook_clears_old_results(self):
        notebook = json.loads(
            (TOOL / "notebooks/phase9_verification.ipynb").read_bytes()
        )
        cell = next(
            c for c in notebook["cells"] if c.get("id") == "spark-native-rg2b-campaigns"
        )
        source = "".join(cell["source"])
        self.assertLess(
            source.index("native_rg2b_campaign_results = None"),
            source.index("from grcv4_explorer"),
        )
        scope = {"repo_root": ROOT, "native_rg2b_campaign_results": {"stale": True}}
        with (
            patch.object(
                surface, "native_rg2b_campaign", side_effect=ValueError("unavailable")
            ),
            self.assertRaises(ValueError),
        ):
            exec(source, scope)
        self.assertIsNone(scope["native_rg2b_campaign_results"])

    def test_current_and_historical_source_epochs(self):
        from p991a5_native_spark_compact_epoch import validated_history
        import p991a6_rg2b_campaign_epoch as epoch

        self.assertEqual(
            json.loads((ROOT / epoch.PATH).read_bytes()), epoch.manifest(ROOT)
        )
        self.assertTrue(validated_history(ROOT))
        from grcv4_explorer.spark_native_crg2b import native_crg2b
        from grcv4_explorer.spark_native_arg2b import native_arg2b

        for project in (native_crg2b, native_arg2b):
            historical = project(ROOT)
            self.assertFalse(historical["native_endpoint_verified"])
            self.assertEqual(historical["full_trajectory_runs"], 0)

    def test_browser_scope_stale_fetch_and_failure_clearing(self):
        from grcv4_explorer.tooling import managed_node, tool_environment

        code = r"""
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const {checkedRG2bCampaign,rg2bCampaignLoader}=await import('./phase9-web/spark-native-rg2b-campaign.js');
const views=JSON.parse(readFileSync(0,'utf8'));
for(const view of views){
  const family=view.family;
  assert.deepEqual(await checkedRG2bCampaign(view,family),view);
  await assert.rejects(checkedRG2bCampaign({...view,native_completion_support:true},family));
  await assert.rejects(checkedRG2bCampaign(view,family==='C_RG2b'?'A_RG2b':'C_RG2b'));
  function el(){return {textContent:'',children:[],append(x){this.children.push(x)},replaceChildren(){this.children=[]}}}
  const out=el(),status=el(),queue=[];
  const load=rg2bCampaignLoader(family,out,status,()=>new Promise(resolve=>queue.push(resolve)),el);
  const old=load(),fresh=load();
  queue[1]({ok:true,json:async()=>view});await fresh;
  assert.match(status.textContent,/endpoint verified/);
  assert.ok(out.children.some(x=>x.href===view.source_url));
  const count=out.children.length;queue[0]({ok:false});await old;
  assert.equal(out.children.length,count);
  await rg2bCampaignLoader(family,out,status,async()=>({ok:false}),el)();
  assert.equal(out.children.length,0);
}
"""
        result = subprocess.run(
            [str(managed_node()), "--input-type=module", "-e", code],
            input=json.dumps(
                [surface.native_rg2b_campaign(ROOT, f) for f in ("C_RG2b", "A_RG2b")]
            ),
            text=True,
            capture_output=True,
            cwd=TOOL,
            env=tool_environment(),
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()

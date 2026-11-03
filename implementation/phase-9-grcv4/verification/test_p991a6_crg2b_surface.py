"""Preflight evidence, estimate, publication and historical-source controls."""

import importlib.util
import json
import lzma
import subprocess
import sys
import unittest
from copy import deepcopy
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
TOOL = (
    ROOT
    / "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool"
)
sys.path.insert(0, str(TOOL / "src"))

import p991a6_crg2b_epoch as epoch
import p991a6_crg2b_preflight as preflight
from grcv4_explorer import spark_native_crg2b as native
from grcv4_explorer.canonical import record_digest
from grcv4_explorer.errors import SourceAdmissionError
from grcv4_explorer.tooling import managed_node, tool_environment


class NativeCRG2bPreflightTests(unittest.TestCase):
    def test_measurements_cache_gate_and_scope(self):
        value = preflight.check(ROOT)
        self.assertLess(value["elapsed_seconds"], value["sampling_cap_seconds"])
        self.assertEqual(value["certificate_precision_bits"], 256)
        self.assertEqual(value["duration"], "8")
        self.assertEqual(value["tests"]["count"], 23)
        for key in ("graph", "domain", "section"):
            self.assertGreater(
                value["caches"]["warm"][key]["hits"],
                value["caches"]["cold"][key]["hits"],
            )
        for rows in value["samples"].values():
            self.assertEqual(len(rows), 20)
            self.assertTrue(
                all(r["fresh_reads"] == 2 and r["full_state_writes"] == 1 for r in rows)
            )
        self.assertTrue(value["optimization"]["identical_source_and_40_target_outputs"])
        self.assertFalse(value["native_endpoint_verified"])
        self.assertFalse(value["native_completion_support"])

    def test_rehashed_cost_or_scope_forgery_rejects(self):
        original = native.load_json_object
        for key, change in (
            ("native_endpoint_verified", True),
            ("full_trajectory_runs", 1),
            ("estimate", {}),
            ("source_bindings", []),
        ):

            def altered(path, key=key, change=change):
                value = deepcopy(original(path))
                value[key] = change
                value["record_digest"] = record_digest(value, "record_digest")
                return value

            with (
                self.subTest(key=key),
                patch.object(native, "load_json_object", altered),
                self.assertRaises(SourceAdmissionError),
            ):
                native.native_crg2b(ROOT)

    def test_changed_current_source_or_evidence_rejects(self):
        original = Path.open
        for name in ("src/pygrc/models/grc_v4_spark_crg2b.py", preflight.EVIDENCE):
            bad = (ROOT / name).read_bytes() + b"changed"

            def altered(path, *args, name=name, bad=bad, **kwargs):
                return (
                    BytesIO(bad)
                    if path == ROOT / name
                    else original(path, *args, **kwargs)
                )

            with (
                self.subTest(path=name),
                patch.object(Path, "open", altered),
                self.assertRaises(SourceAdmissionError),
            ):
                native.native_crg2b(ROOT)

    def test_historical_execution_and_finite_epoch(self):
        import p991a6_acipc_campaign_epoch as previous
        from grcv4_explorer.basin import _bound_file
        from grcv4_explorer.spark_native_acipc_campaign import native_acipc_campaign

        self.assertEqual(
            epoch.manifest(ROOT), json.loads((ROOT / epoch.PATH).read_bytes())
        )
        self.assertEqual(
            previous.manifest(ROOT), json.loads((ROOT / previous.PATH).read_bytes())
        )
        for name in epoch.CHANGED:
            raw = epoch.original(ROOT, name)
            self.assertEqual(_bound_file(ROOT, name, epoch.sha(raw)).read_bytes(), raw)
        for suffix in (
            "Preflight.json.xz",
            "Pressure.json",
            ".5-Campaign.json.xz",
            ".5-SourceEpoch.json",
        ):
            name = (
                preflight.BASE
                + "P9-9.1a.6-ACIPC"
                + ("" if suffix.startswith(".") else "-")
                + suffix
            )
            self.assertEqual((ROOT / name).read_bytes(), epoch.original(ROOT, name))
        old = native_acipc_campaign(ROOT)
        self.assertTrue(old["native_endpoint_verified"])
        self.assertEqual(old["full_trajectory_runs"], 2)
        name = min(epoch.CHANGED)
        original = Path.read_bytes
        with (
            patch.object(
                Path,
                "read_bytes",
                lambda p: original(p) + b"changed" if p == ROOT / name else original(p),
            ),
            self.assertRaises(ValueError),
        ):
            epoch.previous_bytes(ROOT, name)

    def test_lossless_stream_and_recomputed_boundary_samples(self):
        from dataclasses import replace

        from crg2b_native_spark_oracle import verify_step

        from pygrc.models.grc_v4_state import FrozenJSONMap

        data = json.loads(lzma.decompress((ROOT / preflight.EVIDENCE).read_bytes()))
        for role, rows in data["samples"].items():
            prior = None
            self.assertEqual(len(rows), 20)
            for i, row in enumerate(rows):
                payload = preflight.expand(row["transition"], prior)
                step = preflight.decoded(payload)
                self.assertEqual(preflight.transition(step), payload)
                if i in (0, 19):
                    self.assertEqual(verify_step(step), row["independent"])
                prior = payload
            self.assertEqual(prior["after"], data["final_states"][role])
        bad = step.restart_section.to_dict()
        bad["section_tail"] = ["0", "0"]
        with self.assertRaises(AssertionError):
            verify_step(replace(step, restart_section=FrozenJSONMap(bad)))

    def test_http_download_script_and_fixed_scope(self):
        spec = importlib.util.spec_from_file_location(
            "preflight_server", TOOL / "scripts/serve_phase9.py"
        )
        server = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(server)
        handler = server.Handler.__new__(server.Handler)
        codes = []
        handler.command = "GET"
        handler.send_response = lambda code, message=None: codes.append(code)
        handler.send_header = lambda *args: None
        handler.end_headers = lambda: None
        for route in (
            "/api/native-spark/c-rg2b/preflight",
            "/api/native-spark/c-rg2b/preflight/source",
            "/spark-native-crg2b.js",
        ):
            handler.path = route
            handler.wfile = BytesIO()
            handler.do_GET()
            self.assertEqual(codes[-1], 200)
            if route.endswith("/source"):
                self.assertEqual(
                    handler.wfile.getvalue(),
                    lzma.decompress((ROOT / native.RECORD).read_bytes()),
                )
            elif not route.endswith(".js"):
                self.assertEqual(
                    json.loads(handler.wfile.getvalue()), native.native_crg2b(ROOT)
                )
        handler.path = "/api/native-spark/c-rg2b/preflight?other=true"
        handler.wfile = BytesIO()
        handler.do_GET()
        self.assertEqual(codes[-1], 503)

    def test_notebook_clears_stale_preflight(self):
        book = json.loads((TOOL / "notebooks/phase9_verification.ipynb").read_text())
        cell = next(c for c in book["cells"] if c.get("id") == "spark-native-crg2b")
        code = compile("".join(cell["source"]), "preflight-notebook", "exec")
        ns = {"repo_root": ROOT}
        exec(code, ns)  # noqa: S102 - execute the pinned repository notebook cell
        self.assertEqual(ns["native_crg2b_result"], native.native_crg2b(ROOT))
        with (
            patch.object(
                native, "native_crg2b", side_effect=SourceAdmissionError("stale")
            ),
            self.assertRaises(SourceAdmissionError),
        ):
            exec(code, ns)  # noqa: S102 - execute the pinned repository notebook cell
        self.assertIsNone(ns["native_crg2b_result"])

    def test_browser_cost_endpoint_boundary_and_stale_fetch(self):
        code = r"""
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const {checkedNativeCRG2b,nativeCRG2bLoader}=await import('./phase9-web/spark-native-crg2b.js');
const view=JSON.parse(readFileSync(0,'utf8'));
assert.deepEqual(await checkedNativeCRG2b(view),view);
await assert.rejects(checkedNativeCRG2b({...view,native_endpoint_verified:true}));
function element(){return {textContent:'',children:[],append(e){this.children.push(e)},replaceChildren(){this.children=[]}}}
const output=element(),status=element();let queue=[];
const load=nativeCRG2bLoader(output,status,()=>new Promise(r=>queue.push(r)),element);
const old=load(),fresh=load();queue[1]({ok:true,json:async()=>view});await fresh;
assert.match(status.textContent,/Bounded native preflight verified/);
assert.ok(output.children.some(e=>/bounded preflight contains no endpoint run/.test(e.textContent)));
const count=output.children.length;queue[0]({ok:false});await old;assert.equal(output.children.length,count);
await nativeCRG2bLoader(output,status,async()=>({ok:true,json:async()=>({...view,full_trajectory_runs:1})}),element)();
assert.equal(output.children.length,0);assert.match(status.textContent,/Unbound/);
"""
        result = subprocess.run(
            [str(managed_node()), "--input-type=module", "-e", code],
            input=json.dumps(native.native_crg2b(ROOT)),
            text=True,
            capture_output=True,
            cwd=TOOL,
            env=tool_environment(),
            timeout=20,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()

"""Native evidence access and honest scope; no numerical campaign rerun."""

from copy import deepcopy
from io import BytesIO
import importlib.util
import json
import lzma
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import p9101a_native as native
import p9101a_basin_pressure as pressure
import p9101a_acceptance as acceptance

ROOT = native.ROOT
TOOL = (
    ROOT
    / "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool"
)
sys.path.insert(0, str(TOOL / "src"))
from grcv4_explorer import basin_native as surface  # noqa: E402
from grcv4_explorer.tooling import managed_node, tool_environment  # noqa: E402


class NativeSurfaceTests(unittest.TestCase):
    def test_scope_sources_and_rehashed_widening(self):
        value = surface.basin_native_status(ROOT)
        self.assertEqual(value["tests_run"], 37)
        self.assertEqual(
            (value["original_tests_run"], value["pressure_tests_run"]), (20, 17)
        )
        self.assertTrue(value["user_accepted"])
        self.assertTrue(value["P9_10_1a_closed"])
        self.assertEqual(
            value["verification_obligation_resolution"]["status"],
            "resolved_bounded_native",
        )
        self.assertEqual(value["remaining_work"], ["P9-10.1b", "P9-10.1c"])
        for row in (*value["records"], *value["source_refs"]):
            raw, ref = surface.basin_native_source(ROOT, row["path"])
            self.assertEqual(native.sha(raw), ref["sha256"])
            if row["path"].endswith(".xz"):
                evidence = json.loads(lzma.decompress(raw))
                self.assertEqual(evidence["record_digest"], row["record_digest"])
                self.assertTrue(evidence["evidence"]["observations"])
        with self.assertRaises(KeyError):
            surface.basin_native_source(ROOT, "../outside")
        for key in ("user_accepted", "P9_10_1a_closed", "full_GRC9V4_conformance"):
            bad = deepcopy(pressure.status(ROOT))
            bad[key] = True
            with patch.object(pressure, "status", return_value=native.seal(bad)):
                with self.assertRaises(ValueError):
                    surface.basin_native_status(ROOT)

    def test_rehashed_acceptance_and_obligation_widening_reject(self):
        original = Path.read_bytes
        for field in ("families", "resolution", "full_conformance", "acceptance"):
            bad = deepcopy(acceptance.decision(ROOT))
            if field == "families":
                bad["families"].append("A_OS")
            elif field == "resolution":
                bad["verification_obligation_resolution"]["status"] = "pending_forward"
            elif field == "full_conformance":
                bad["full_GRC9V4_conformance"] = True
            else:
                bad["user_accepted"] = False
            raw = json.dumps(native.seal(bad)).encode()
            with patch.object(
                Path,
                "read_bytes",
                lambda p: raw if p == ROOT / acceptance.PATH else original(p),
            ):
                with self.assertRaisesRegex(ValueError, "acceptance decision or scope"):
                    surface.basin_native_status(ROOT)

    def test_actual_http_and_notebook_fail_closed(self):
        spec = importlib.util.spec_from_file_location(
            "native_basin_server", TOOL / "scripts/serve_phase9.py"
        )
        server = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(server)
        handler = server.Handler.__new__(server.Handler)
        codes = []
        handler.send_response = codes.append
        handler.send_header = lambda *args: None
        handler.end_headers = lambda: None
        handler.path = "/api/basin/native"
        handler.wfile = BytesIO()
        handler.do_GET()
        self.assertEqual(codes, [200])
        self.assertEqual(
            json.loads(handler.wfile.getvalue()), surface.basin_native_status(ROOT)
        )
        compressed = next(
            r
            for r in surface.basin_native_status(ROOT)["records"]
            if r["path"].endswith(".xz")
        )
        handler.path = "/api/basin/native/source?path=" + compressed["path"]
        handler.wfile = BytesIO()
        handler.do_GET()
        self.assertEqual(codes[-1], 200)
        self.assertEqual(native.sha(handler.wfile.getvalue()), compressed["sha256"])
        self.assertEqual(
            json.loads(lzma.decompress(handler.wfile.getvalue()))["record_digest"],
            compressed["record_digest"],
        )
        handler.path = "/api/basin/native"
        with patch.object(
            server, "basin_native_status", side_effect=ValueError("source drift")
        ):
            handler.wfile = BytesIO()
            handler.do_GET()
            self.assertEqual(codes[-1], 503)
            self.assertEqual(set(json.loads(handler.wfile.getvalue())), {"error"})
        book = json.loads((TOOL / "notebooks/phase9_verification.ipynb").read_bytes())
        cell = next(c for c in book["cells"] if c.get("id") == "basin-native")
        code = compile("".join(cell["source"]), "basin-native-cell", "exec")
        ns = {"repo_root": ROOT}
        exec(code, ns)
        self.assertEqual(ns["phase9_basin_native"], surface.basin_native_status(ROOT))
        with patch.object(
            surface, "basin_native_status", side_effect=ValueError("source drift")
        ):
            with self.assertRaises(ValueError):
                exec(code, ns)
        self.assertIsNone(ns["phase9_basin_native"])

    def test_browser_scope_and_stale_output_clearing(self):
        js = """
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {checkedNativeBasin,nativeBasinLoader,canonicalBasin} from './basin.js';
const value=JSON.parse(readFileSync(0,'utf8'));
assert.deepEqual(await checkedNativeBasin(value),value);
for(const edit of [v=>v.user_accepted=false,v=>v.P9_10_1a_closed=false,v=>v.full_GRC9V4_conformance=true,
 v=>v.verification_obligation_resolution.status='pending_forward',v=>v.acceptance.record_digest='0'.repeat(64),
 v=>v.families.push('A_OS'),v=>v.records.pop(),v=>v.records[0].record_digest='0'.repeat(64)]) {
 const bad=structuredClone(value);edit(bad);delete bad.record_digest;
 bad.record_digest=createHash('sha256').update(canonicalBasin(bad)).digest('hex');
 await assert.rejects(checkedNativeBasin(bad));
}
const output={children:[],replaceChildren(){this.children=[]},append(e){this.children.push(e)}},status={};
let ok=true;
const load=nativeBasinLoader(output,status,async()=>({ok,json:async()=>value}),tag=>({tag}));
await load();assert.ok(output.children.length>5);assert.match(status.textContent,/bounded accepted/);
ok=false;await load();assert.equal(output.children.length,0);assert.match(status.textContent,/unavailable/);
assert.match(readFileSync('index.html','utf8'),/id="basin-native-refresh"/);
"""
        run = subprocess.run(
            [str(managed_node()), "--input-type=module", "-e", js],
            cwd=TOOL / "phase9-web",
            input=json.dumps(surface.basin_native_status(ROOT)),
            text=True,
            capture_output=True,
            timeout=30,
            env=tool_environment(),
        )
        self.assertEqual(run.returncode, 0, run.stderr)


if __name__ == "__main__":
    unittest.main()

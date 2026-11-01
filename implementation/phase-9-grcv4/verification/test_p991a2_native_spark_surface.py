"""Read-only native numerical evidence across API, browser and notebook."""
from copy import deepcopy
from io import BytesIO
import importlib.util
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
SIDE = ROOT / "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool"
TOOL = SIDE / "tool"
sys.path.insert(0, str(TOOL / "src"))
from grcv4_explorer import spark_native_cos as native
from grcv4_explorer.canonical import record_digest
from grcv4_explorer.errors import SourceAdmissionError
from grcv4_explorer.tooling import managed_node, tool_environment


class NativeSparkSurfaceTests(unittest.TestCase):
    def test_bound_record_scope_and_rehashed_forgery(self):
        view = native.native_cos_numerics(ROOT)
        self.assertFalse(view["native_completion_support"])
        self.assertFalse(view["native_endpoint_verified"])
        self.assertEqual(view["native_kernel_steps"], 5)
        original = native.load_json_object
        for key, value in (("native_completion_support", True), ("native_endpoint_verified", True),
                           ("native_kernel_steps", 400), ("source_bindings", [])):
            def changed(path):
                result = deepcopy(original(path)); result[key] = value
                result["record_digest"] = record_digest(result, "record_digest")
                return result
            with self.subTest(key=key), patch.object(native, "load_json_object", changed), self.assertRaises(SourceAdmissionError):
                native.native_cos_numerics(ROOT)
        from grcv4_explorer import basin
        original_sha = basin.file_sha256
        runtime = ROOT / "src/pygrc/models/grc_v4_spark_cos.py"
        with patch.object(basin, "file_sha256", lambda p: hashlib.sha256(p.read_bytes()+b"\nchanged\n").hexdigest() if p == runtime else original_sha(p)), self.assertRaises(SourceAdmissionError):
            native.native_cos_numerics(ROOT)

    def test_http_projection_download_script_and_unavailable_state(self):
        spec = importlib.util.spec_from_file_location("native_spark_server", TOOL / "scripts/serve_phase9.py")
        server = importlib.util.module_from_spec(spec); spec.loader.exec_module(server)
        handler = server.Handler.__new__(server.Handler); codes = []; headers = []
        handler.command = "GET"
        handler.send_response = lambda code, message=None: codes.append(code)
        handler.send_header = lambda *args: headers.append(args)
        handler.end_headers = lambda: None
        for route in ("/api/native-spark/c-os/numerical-bridge", "/api/native-spark/c-os/numerical-bridge/source", "/spark-native-cos.js"):
            handler.path = route; handler.wfile = BytesIO(); handler.do_GET()
            self.assertEqual(codes[-1], 200)
            if route.endswith("/source"):
                self.assertEqual(handler.wfile.getvalue(), (ROOT/native.RECORD).read_bytes())
            elif route.endswith(".js"):
                self.assertIn(("Content-Type", "text/javascript"), headers)
            else:
                self.assertEqual(json.loads(handler.wfile.getvalue()), native.native_cos_numerics(ROOT))
        handler.path = "/api/native-spark/c-os/numerical-bridge?path=../private"
        handler.wfile = BytesIO(); handler.do_GET(); self.assertEqual(codes[-1], 503)
        handler.path = "/api/native-spark/c-os/numerical-bridge"
        with patch.object(server, "native_cos_numerics", side_effect=SourceAdmissionError("changed source")):
            handler.wfile = BytesIO(); handler.do_GET()
        self.assertEqual(codes[-1], 503)
        self.assertEqual(json.loads(handler.wfile.getvalue())["evidence_state"], "unavailable_not_admitted")

    def test_notebook_resets_stale_projection(self):
        book = json.loads((TOOL / "notebooks/phase9_verification.ipynb").read_text())
        cell = next(c for c in book["cells"] if c.get("id") == "native-cos-numerics")
        ns = dict(repo_root=ROOT); code = compile("".join(cell["source"]), "native-cos-notebook", "exec")
        exec(code, ns)
        self.assertEqual(ns["phase9_native_cos_numerics"], native.native_cos_numerics(ROOT))
        with patch.object(native, "native_cos_numerics", side_effect=SourceAdmissionError("changed")), self.assertRaises(SourceAdmissionError):
            exec(code, ns)
        self.assertIsNone(ns["phase9_native_cos_numerics"])

    def test_browser_digest_scope_failure_and_stale_fetch(self):
        code = r'''
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const {checkedNativeCOS, nativeCOSLoader} = await import('./phase9-web/spark-native-cos.js');
const view = JSON.parse(readFileSync(0, 'utf8'));
assert.deepEqual(await checkedNativeCOS(view), view);
await assert.rejects(checkedNativeCOS({...view, native_completion_support:true}));
function element() {return {textContent:'', children:[], append(e){this.children.push(e)}, replaceChildren(){this.children=[]}}}
const output=element(), status=element(); let queue=[];
const load=nativeCOSLoader(output,status,()=>new Promise(r=>queue.push(r)),element);
const old=load(), fresh=load();
queue[1]({ok:true,json:async()=>view}); await fresh;
assert.match(status.textContent,/Numerical evidence verified/);
const count=output.children.length;
queue[0]({ok:false}); await old;
assert.equal(output.children.length,count);
await nativeCOSLoader(output,status,async()=>({ok:true,json:async()=>({...view, native_owner_steps:1})}),element)();
assert.equal(output.children.length,0); assert.match(status.textContent,/Unbound/);
'''
        result = subprocess.run([str(managed_node()), "--input-type=module", "-e", code],
            input=json.dumps(native.native_cos_numerics(ROOT)), text=True, capture_output=True,
            cwd=TOOL, env=tool_environment(), timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__": unittest.main()

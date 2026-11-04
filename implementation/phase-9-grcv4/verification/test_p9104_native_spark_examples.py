"""Tutorial wiring and public prefix checks; accepted long trajectories are reused."""

from copy import deepcopy
import importlib.util
from io import BytesIO
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from examples.grc9v4 import native_spark as ex
import p9104_native_spark_examples as publication

TOOL = ex.ROOT / publication.SIDE / "tool"
sys.path.insert(0, str(TOOL / "src"))
from grcv4_explorer import spark_native_workflow as api  # noqa: E402


class NativeSparkExampleTests(unittest.TestCase):
    def test_all_ten_retained_workflows_and_portable_links(self):
        with patch.object(ex, "prepare", side_effect=AssertionError("implicit run")):
            value = publication.checked()
        self.assertEqual([r["family"] for r in value["families"]], list(ex.FAMILIES))
        for row in value["families"]:
            self.assertEqual(row["endpoints"]["current"]["local_gain"], 1)
            self.assertEqual(row["endpoints"]["reset"]["local_gain"], 0)
        for name in (publication.GUIDE, publication.SIDE + "docs/NativeSparkWorkflow.md"):
            path = ex.ROOT / name
            for link in re.findall(r"\]\(([^)]+)\)", path.read_text()):
                if not link.startswith(("https:", "http:", "#")):
                    self.assertTrue((path.parent / link.split("#")[0]).exists(), link)
        self.assertNotIn("/home/", (ex.ROOT / publication.GUIDE).read_text())

    def test_public_source_expansion_certificate_and_short_cold_replay(self):
        model, pair, subject = ex.prepare()
        initial = ex.observation(model, 0)
        self.assertEqual((initial["decision"], initial["window_observations"], initial["local_gain"]), ("pending", 0, 0))
        self.assertFalse(initial["membership"]["current"]["inside"])
        before = model.snapshot()
        self.assertFalse(model.install_completion_certificates(*reversed(pair)).committed)
        self.assertEqual(model.snapshot(), before)
        result = ex.committed(model.step(), "one target beat")
        self.assertEqual(result.local_gain, 0)
        self.assertEqual(ex.observation(model, 1)["decision"], "pending")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "checkpoint.json.xz"
            ex.write_compressed(path, model.snapshot())
            with self.assertRaises(FileExistsError):
                ex.write_compressed(path, model.snapshot())
            result = subprocess.run(
                [sys.executable, "-m", "examples.grc9v4.native_spark", "replay", "--checkpoint", str(path)],
                cwd=ex.ROOT, capture_output=True, text=True, timeout=60,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(json.loads(result.stdout)["exact_checkpoint_equal"])
        self.assertEqual(len(subject["certificate_ids"]), 2)

    def test_execution_loop_requires_actual_completion_and_stops_on_failure(self):
        # A controller test, not new scientific trajectory evidence.
        ok = SimpleNamespace(committed=True, reason=None, local_gain=0)
        bad = SimpleNamespace(committed=False, reason="domain failure", local_gain=0)
        gain = SimpleNamespace(committed=True, reason=None, local_gain=1)
        model = SimpleNamespace(step=lambda: ok)
        pending = dict(decision="pending", window_observations=1, local_gain=0)
        with patch.object(ex, "observation", return_value=pending), self.assertRaisesRegex(RuntimeError, "without a completed"):
            ex.continue_to_completion(model, max_steps=2)
        model.step = lambda: bad
        with self.assertRaisesRegex(ValueError, "domain failure"):
            ex.continue_to_completion(model, max_steps=1)
        model.step = lambda: ok
        with patch.object(ex, "observation", return_value=dict(pending, decision="completed")), self.assertRaisesRegex(ValueError, "increment"):
            ex.continue_to_completion(model, max_steps=1)
        outcomes = iter((ok, ok, gain))
        model.step = lambda: next(outcomes)
        with patch.object(ex, "observation", side_effect=[pending, dict(pending, window_observations=2), dict(pending, decision="completed", window_observations=3, local_gain=1)]):
            self.assertEqual(len(ex.continue_to_completion(model, max_steps=4)), 3)

    def test_input_and_publication_drift_reject(self):
        value = ex.support()
        altered = deepcopy(value)
        altered["families"][0]["roles"]["reset"]["local_gain"] = 1
        altered["record_digest"] = ex.digest({k: v for k, v in altered.items() if k != "record_digest"})
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / ex.SUPPORT
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps(altered))
            with self.assertRaisesRegex(ValueError, "support identity"):
                ex.support(root)
            path = root / "input.json"
            path.write_text("altered")
            with self.assertRaisesRegex(ValueError, "input changed"):
                ex.checked_bytes(dict(path="input.json", sha256="0" * 64), root)
        with self.assertRaises(ValueError):
            ex.checked_bytes(dict(path="../input.json", sha256="0" * 64))

    def test_api_browser_and_notebook_are_read_only(self):
        from grcv4_explorer.tooling import managed_node, tool_environment
        view = api.native_spark_workflow(ex.ROOT)
        spec = importlib.util.spec_from_file_location("native_workflow_server", TOOL / "scripts/serve_phase9.py")
        server = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(server)
        with patch.object(ex, "prepare", side_effect=AssertionError("implicit execution")):
            for path, code in (
                ("/api/native-spark/workflow", 200),
                ("/api/native-spark/workflow/source?name=guide", 200),
                ("/api/native-spark/workflow/source?name=code", 200),
                ("/api/native-spark/workflow?run=true", 503),
                ("/api/native-spark/workflow/source?name=../../src", 503),
                ("/spark-native-workflow.js", 200),
            ):
                handler = server.Handler.__new__(server.Handler)
                handler.path, handler.wfile = path, BytesIO()
                codes = []
                handler.send_response = lambda n, *args: codes.append(n)
                handler.send_header = lambda *args: None
                handler.end_headers = lambda: None
                handler.do_GET()
                self.assertEqual(codes[-1], code, path)
                if path.endswith("name=guide"):
                    self.assertEqual(handler.wfile.getvalue(), (ex.ROOT / publication.GUIDE).read_bytes())
        code = r"""
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {checkedWorkflow,workflowLoader} from './phase9-web/spark-native-workflow.js';
const view=JSON.parse(readFileSync(0,'utf8'));
await checkedWorkflow(view);
await assert.rejects(checkedWorkflow({...view,projection_digest:'0'.repeat(64)}));
function el(){return {textContent:'',children:[],append(v){this.children.push(v)},replaceChildren(){this.children=[]}}}
const output=el(),status=el(),queue=[];
const load=workflowLoader(output,status,()=>new Promise(resolve=>queue.push(resolve)),el);
const old=load(),fresh=load();queue[1]({ok:true,json:async()=>view});await fresh;
assert.match(status.textContent,/no trajectory executed/);
assert.equal(output.children.filter(e=>e.textContent.includes('reset comparison')).length,10);
const size=output.children.length;queue[0]({ok:false});await old;assert.equal(output.children.length,size);
await workflowLoader(output,status,async()=>({ok:false}),el)();assert.equal(output.children.length,0);
"""
        result = subprocess.run([str(managed_node()), "--input-type=module", "-e", code],
                                cwd=TOOL, input=json.dumps(view), text=True, capture_output=True,
                                env=tool_environment(), timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        notebook = json.loads((TOOL / "notebooks/phase9_verification.ipynb").read_bytes())
        cell = next(c for c in notebook["cells"] if c.get("id") == "native-spark-workflow")
        scope = dict(repo_root=ex.ROOT, native_spark_workflow_result={"stale": True})
        with patch.object(api, "native_spark_workflow", side_effect=ValueError("unavailable")), self.assertRaises(ValueError):
            exec("".join(cell["source"]), scope)
        self.assertIsNone(scope["native_spark_workflow_result"])


if __name__ == "__main__":
    unittest.main()

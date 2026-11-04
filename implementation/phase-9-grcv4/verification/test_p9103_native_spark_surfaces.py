"""Retained regression integrity and real publication paths; no trajectory run."""

from copy import deepcopy
import importlib.util
from io import BytesIO
import json
import subprocess
import sys
import unittest
from unittest.mock import patch

import p9103_native_spark as check

TOOL = check.ROOT / (check.support.SIDE + "tool")
sys.path.insert(0, str(TOOL / "src"))
from grcv4_explorer import spark_native_regressions as api  # noqa: E402


class NativeRegressionSurfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch.object(check, "run_group", side_effect=AssertionError("test rerun")):
            cls.value = check.check()
        with patch.object(check, "check", return_value=cls.value):
            cls.view = api.native_spark_regressions(check.ROOT)

    def test_resealed_coverage_source_and_scope_mutations_reject(self):
        self.assertEqual(self.value["tests_run"], 28)
        self.assertEqual(len(self.value["reused_evidence"]["families"]), 10)
        self.assertFalse(self.value["user_accepted"])
        self.assertTrue(self.view["user_accepted"])
        self.assertFalse(self.view["execution_user_accepted"])
        self.assertEqual(self.view["status"], "accepted_bounded_regressions")
        decision = json.loads((check.ROOT / api.ACCEPTANCE_PATH).read_bytes())
        for key, altered in (
            ("execution_record_digest", "0" * 64),
            ("families", []),
            ("user_accepted", False),
            ("G4_accepted", True),
        ):
            with self.subTest(acceptance=key), self.assertRaises(ValueError):
                api.accepted_decision(check.seal(dict(decision, **{key: altered})), self.value)
        from grcv4_explorer.spark_native_support import native_spark_support

        previous = native_spark_support(check.ROOT)
        self.assertTrue(previous["reconciliation_user_accepted"])
        self.assertEqual(
            previous["record_digest"], self.value["reused_evidence"]["record_digest"]
        )
        self.assertEqual(
            (check.ROOT / check.support.RECORD).read_bytes(),
            check.git("show", check.ENTRY + ":" + check.support.RECORD),
        )

        def change(v, kind):
            if kind == "source":
                v["source_refs"][0]["sha256"] = "0" * 64
            elif kind == "family":
                v["reused_evidence"]["families"].pop()
            elif kind == "skip":
                v["regressions"][0]["skips"] = 1
            elif kind == "test":
                v["regressions"][0]["tests"].pop()
            elif kind == "rerun":
                v["source_to_completion_campaigns_rerun"] = 1
            else:
                v[kind] = True

        for kind in (
            "source",
            "family",
            "skip",
            "test",
            "rerun",
            "G4_accepted",
            "user_accepted",
            "hierarchy_tracking",
        ):
            value = deepcopy(self.value)
            change(value, kind)
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                check.check_value(
                    check.seal(value),
                    self.value["source_refs"],
                    self.value["reused_evidence"],
                )

    def test_http_inspection_download_and_fixed_scope(self):
        spec = importlib.util.spec_from_file_location(
            "native_regression_server", TOOL / "scripts/serve_phase9.py"
        )
        server = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(server)
        with (
            patch.object(check, "check", return_value=self.value),
            patch.object(check, "run_group", side_effect=AssertionError("test rerun")),
        ):
            for path, expected in (
                ("/api/native-spark/regressions", 200),
                ("/api/native-spark/regressions/source", 200),
                ("/api/native-spark/regressions?run=true", 503),
                ("/spark-native-regressions.js", 200),
            ):
                handler = server.Handler.__new__(server.Handler)
                handler.path, handler.wfile = path, BytesIO()
                codes = []
                handler.send_response = lambda code, *args: codes.append(code)
                handler.send_header = lambda *args: None
                handler.end_headers = lambda: None
                handler.do_GET()
                self.assertEqual(codes[-1], expected, path)
                if path == "/api/native-spark/regressions":
                    self.assertEqual(json.loads(handler.wfile.getvalue()), self.view)
                if path.endswith("/source"):
                    self.assertEqual(
                        handler.wfile.getvalue(), (check.ROOT / check.PATH).read_bytes()
                    )

    def test_browser_tampering_stale_refresh_and_notebook_clearing(self):
        from grcv4_explorer.tooling import managed_node, tool_environment

        code = r"""
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {checkedNativeRegressions,nativeRegressionsLoader} from './phase9-web/spark-native-regressions.js';
const view=JSON.parse(readFileSync(0,'utf8'));
await checkedNativeRegressions(view);
await assert.rejects(checkedNativeRegressions({...view,G4_accepted:true}));
await assert.rejects(checkedNativeRegressions({...view,source_to_completion_campaigns_rerun:1}));
function el(){return {textContent:'',children:[],append(v){this.children.push(v)},replaceChildren(){this.children=[]}}}
const output=el(),status=el(),queue=[];
const load=nativeRegressionsLoader(output,status,()=>new Promise(resolve=>queue.push(resolve)),el);
const old=load(),fresh=load();queue[1]({ok:true,json:async()=>view});await fresh;
assert.match(status.textContent,/passed/);assert.equal(output.children.filter(e=>e.textContent.includes(' seconds.')).length,4);
const size=output.children.length;queue[0]({ok:false});await old;assert.equal(output.children.length,size);
await nativeRegressionsLoader(output,status,async()=>({ok:false}),el)();assert.equal(output.children.length,0);
"""
        result = subprocess.run(
            [str(managed_node()), "--input-type=module", "-e", code],
            cwd=TOOL,
            input=json.dumps(self.view),
            text=True,
            capture_output=True,
            env=tool_environment(),
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        notebook = json.loads(
            (TOOL / "notebooks/phase9_verification.ipynb").read_bytes()
        )
        ids = [c.get("id") for c in notebook["cells"]]
        self.assertLess(
            ids.index("discover-and-import"), ids.index("native-spark-regressions")
        )
        cell = notebook["cells"][ids.index("native-spark-regressions")]
        scope = {
            "repo_root": check.ROOT,
            "native_spark_regressions_result": {"stale": True},
        }
        with (
            patch.object(
                api, "native_spark_regressions", side_effect=ValueError("unavailable")
            ),
            self.assertRaises(ValueError),
        ):
            exec("".join(cell["source"]), scope)
        self.assertIsNone(scope["native_spark_regressions_result"])


if __name__ == "__main__":
    unittest.main()

"""Support integration and representation pressure; no campaign reexecution."""

import copy
import importlib.util
import json
import subprocess
import sys
import unittest
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

import p991a7_support as reconciliation

ROOT = reconciliation.ROOT
TOOL = ROOT / (reconciliation.SIDE + "tool")
sys.path.insert(0, str(TOOL / "src"))
from grcv4_explorer import spark_native_support as surface  # noqa: E402


class SupportSurfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = reconciliation.checked(ROOT)
        # The projection uses this freshly authenticated input. Do not repeat
        # the identical retained-stream hash sweep just to project its fields.
        with patch.object(reconciliation, "checked", return_value=cls.value):
            cls.view = surface.native_spark_support(ROOT)
        cls.roster = reconciliation.load(ROOT / reconciliation.ASSET)

    def test_exact_population_obligations_and_current_projection(self):
        self.assertEqual(len(self.value["families"]), 10)
        self.assertEqual(sum(len(r["subjects"]) for r in self.value["families"]), 20)
        obligations = [
            o for r in self.value["evidence"] for o in r["native_obligations"]
        ]
        self.assertEqual(len(set(obligations)), 30)
        self.assertFalse(self.value["G4_accepted"])
        self.assertFalse(self.value["hierarchy_tracking"])
        self.assertEqual(self.value["new_numerical_trajectories"], 0)
        self.assertEqual(self.view["record_digest"], self.value["record_digest"])

    def test_rehashed_support_and_evidence_mutations_reject(self):
        # Reuse the freshly checked trusted derivation; mutate the supplied record.
        # This isolates record comparison from repeated historical file reads.
        for key, val in [
            ("hierarchy_tracking", True),
            ("G4_accepted", True),
            ("general_ATC", True),
            ("native_obligation_count", 29),
            ("families", self.value["families"][:-1]),
        ]:
            wrong = copy.deepcopy(self.value)
            wrong[key] = val
            wrong = reconciliation.seal(wrong)
            original = reconciliation.load

            def changed(path):
                return wrong if path == ROOT / reconciliation.RECORD else original(path)

            with (
                patch.object(
                    reconciliation, "build", return_value=(self.roster, self.value)
                ),
                patch.object(reconciliation, "load", changed),
                self.assertRaises(ValueError),
            ):
                reconciliation.checked(ROOT)
        wrong = copy.deepcopy(self.value)
        wrong["evidence"][0]["accepted_commit"] = "HEAD"
        wrong = reconciliation.seal(wrong)
        with (
            patch.object(
                reconciliation, "build", return_value=(self.roster, self.value)
            ),
            patch.object(reconciliation, "load", side_effect=[self.roster, wrong]),
            self.assertRaises(ValueError),
        ):
            reconciliation.checked(ROOT)

    def test_history_snapshot_checks_exit_and_older_scientific_source(self):
        from hashlib import sha256
        from p991a5_native_spark_compact_epoch import history_snapshot, reviewed_bytes
        from grcv4_explorer.spark_arg2b import SOURCE
        from grcv4_explorer import spark_arg2b_sc3_metadata as historical
        from grcv4_explorer.canonical import record_digest
        from grcv4_explorer.basin import _bound_file
        from grcv4_explorer.errors import SourceAdmissionError

        authority = reconciliation.load(ROOT / SOURCE)
        acceptance = reconciliation.load(ROOT / authority["acceptance"]["path"])
        older = next(
            r
            for r in acceptance["subjects"]
            if r["path"].endswith("/spark_arg2b_metadata.py")
        )
        epoch = reconciliation.load(ROOT / historical.SOURCE)
        self.assertEqual(record_digest(epoch, "record_digest"), historical.DIGEST)
        with history_snapshot(ROOT):
            # Exercise the lookup boundary and the scientific helper's own Git
            # preimage/hash check. Its unchanged aggregate metadata validator is
            # outside this regression; validate this subject's postimage here.
            row = next(r for r in epoch["sources"] if r["path"] == older["path"])
            self.assertIsNotNone(reviewed_bytes(ROOT, row["path"], row["after_sha256"]))
            with patch.object(
                historical, "checked_acceptance_epoch", return_value=epoch
            ):
                raw = historical.reviewed_source_bytes(
                    ROOT, older["path"], older["sha256"]
                )
                with self.assertRaises(SourceAdmissionError):
                    historical.reviewed_source_bytes(ROOT, older["path"], "0" * 64)
            self.assertEqual(sha256(raw).hexdigest(), older["sha256"])
            self.assertIsNone(reviewed_bytes(ROOT, older["path"], "0" * 64))
            with self.assertRaises(SourceAdmissionError):
                _bound_file(ROOT, older["path"], "0" * 64)
        scope = history_snapshot(ROOT)
        scope.__enter__()
        original = Path.read_bytes

        def corrupt(path):
            raw = original(path)
            return (
                raw + b"changed"
                if path == ROOT / "src/pygrc/models/grc_9_v4.py"
                else raw
            )

        with patch.object(Path, "read_bytes", corrupt), self.assertRaises(ValueError):
            scope.__exit__(None, None, None)

    def test_http_browser_asset_and_source(self):
        spec = importlib.util.spec_from_file_location(
            "spark_support_server", TOOL / "scripts/serve_phase9.py"
        )
        server = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(server)
        handler = server.Handler.__new__(server.Handler)
        codes = []
        handler.command = "GET"
        handler.send_response = lambda code, message=None: codes.append(code)
        handler.send_header = lambda *args: None
        handler.end_headers = lambda: None
        with (
            patch.object(server, "native_spark_support", return_value=self.view),
            patch.object(
                server,
                "native_spark_support_source",
                return_value=json.dumps(self.value).encode(),
            ),
        ):
            for path, status in [
                ("/api/native-spark/support", 200),
                ("/api/native-spark/support/source", 200),
                ("/api/native-spark/support?widen=true", 503),
                ("/spark-native-support.js", 200),
            ]:
                handler.path = path
                handler.wfile = BytesIO()
                handler.do_GET()
                self.assertEqual(codes[-1], status, path)

    def test_notebook_failure_clears_stale_result(self):
        notebook = json.loads(
            (TOOL / "notebooks/phase9_verification.ipynb").read_bytes()
        )
        cell = next(
            c for c in notebook["cells"] if c.get("id") == "native-spark-support"
        )
        ids = [c.get("id") for c in notebook["cells"]]
        self.assertLess(
            ids.index("discover-and-import"), ids.index("native-spark-support")
        )
        source = "".join(cell["source"])
        scope = {"repo_root": ROOT, "native_spark_support_result": {"stale": True}}
        with (
            patch.object(
                surface, "native_spark_support", side_effect=ValueError("unavailable")
            ),
            self.assertRaises(ValueError),
        ):
            exec(source, scope)
        self.assertIsNone(scope["native_spark_support_result"])

    def test_real_browser_renderer_scope_and_stale_responses(self):
        from grcv4_explorer.tooling import managed_node, tool_environment

        code = r"""
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const {checkedSparkSupport,sparkSupportLoader}=await import('./phase9-web/spark-native-support.js');
const view=JSON.parse(readFileSync(0,'utf8'));
await checkedSparkSupport(view);
await assert.rejects(checkedSparkSupport({...view,G4_accepted:true}));
await assert.rejects(checkedSparkSupport({...view,families:view.families.slice(1)}));
function el(){return {textContent:'',children:[],append(x){this.children.push(x)},replaceChildren(){this.children=[]}}}
const out=el(),status=el(),queue=[];
const load=sparkSupportLoader(out,status,()=>new Promise(resolve=>queue.push(resolve)),el);
const old=load(),fresh=load();queue[1]({ok:true,json:async()=>view});await fresh;
assert.match(status.textContent,/All ten/);assert.equal(out.children.filter(x=>x.textContent.includes('duration')).length,10);
const count=out.children.length;queue[0]({ok:false});await old;assert.equal(out.children.length,count);
await sparkSupportLoader(out,status,async()=>({ok:false}),el)();assert.equal(out.children.length,0);
"""
        r = subprocess.run(
            [str(managed_node()), "--input-type=module", "-e", code],
            input=json.dumps(self.view),
            text=True,
            capture_output=True,
            cwd=TOOL,
            env=tool_environment(),
            timeout=30,
        )
        self.assertEqual(r.returncode, 0, r.stderr)


if __name__ == "__main__":
    unittest.main()

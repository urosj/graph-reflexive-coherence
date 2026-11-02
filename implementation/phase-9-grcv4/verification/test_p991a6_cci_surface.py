"""Preflight evidence, estimate, publication and historical-source controls."""

import importlib.util
import json
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

import p991a6_cci_epoch as epoch
import p991a6_cci_preflight as preflight
from grcv4_explorer import spark_native_cci as native
from grcv4_explorer.canonical import record_digest
from grcv4_explorer.errors import SourceAdmissionError
from grcv4_explorer.tooling import managed_node, tool_environment


class NativeCCIPreflightTests(unittest.TestCase):
    def test_retained_measurements_recompute_estimate_and_bind_real_operands(self):
        value = preflight.check(ROOT)
        self.assertTrue(value["estimate"]["within_budget"])
        self.assertLess(value["elapsed_seconds"], value["sampling_cap_seconds"])
        self.assertEqual(value["certificate_precision_bits"], 256)
        self.assertTrue(value["precision_comparison"]["identical_represented_states"])
        self.assertEqual(value["tests"]["count"], 19)
        self.assertGreater(
            value["caches"]["root_warm"]["hits"], value["caches"]["root_cold"]["hits"]
        )
        for rows in value["samples"].values():
            self.assertEqual(len(rows), 40)
            self.assertTrue(all(row["root_calls"] == 2 for row in rows))

    def test_rehashed_cost_or_scope_forgery_is_not_admitted_by_surface(self):
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
                native.native_cci(ROOT)

    def test_changed_runtime_or_compressed_evidence_rejects_projection(self):
        original = Path.open
        for name in ("src/pygrc/models/grc_v4_spark_cos.py", preflight.EVIDENCE):
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
                native.native_cci(ROOT)

    def test_finite_metadata_epoch_keeps_committed_lifecycle_record(self):
        import p991a3_native_spark_epoch as previous
        from grcv4_explorer.basin import _bound_file
        from grcv4_explorer.spark_native_lifecycle import native_lifecycle

        self.assertEqual(
            epoch.manifest(ROOT), json.loads((ROOT / epoch.PATH).read_bytes())
        )
        self.assertEqual(
            previous.manifest(ROOT), json.loads((ROOT / previous.PATH).read_bytes())
        )
        for name in epoch.CHANGED:
            raw = epoch.original(ROOT, name)
            self.assertEqual(_bound_file(ROOT, name, epoch.sha(raw)).read_bytes(), raw)
        record = "implementation/phase-9-grcv4/tranche-9/P9-9.1a.3-Verification.json"
        self.assertEqual((ROOT / record).read_bytes(), epoch.original(ROOT, record))
        self.assertEqual(native_lifecycle(ROOT)["tests_passed"], 30)
        name = next(iter(epoch.CHANGED))
        original = Path.read_bytes
        with (
            patch.object(
                Path,
                "read_bytes",
                lambda path: (
                    original(path) + b"unreviewed"
                    if path == ROOT / name
                    else original(path)
                ),
            ),
            self.assertRaises(ValueError),
        ):
            epoch.previous_bytes(ROOT, name)

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
            "/api/native-spark/c-ci/preflight",
            "/api/native-spark/c-ci/preflight/source",
            "/spark-native-cci.js",
        ):
            handler.path = route
            handler.wfile = BytesIO()
            handler.do_GET()
            self.assertEqual(codes[-1], 200)
            if route.endswith("/source"):
                self.assertEqual(
                    handler.wfile.getvalue(), (ROOT / native.RECORD).read_bytes()
                )
            elif not route.endswith(".js"):
                self.assertEqual(
                    json.loads(handler.wfile.getvalue()), native.native_cci(ROOT)
                )
        handler.path = "/api/native-spark/c-ci/preflight?other=true"
        handler.wfile = BytesIO()
        handler.do_GET()
        self.assertEqual(codes[-1], 503)

    def test_notebook_clears_stale_preflight(self):
        book = json.loads((TOOL / "notebooks/phase9_verification.ipynb").read_text())
        cell = next(c for c in book["cells"] if c.get("id") == "spark-native-cci")
        code = compile("".join(cell["source"]), "preflight-notebook", "exec")
        ns = {"repo_root": ROOT}
        exec(code, ns)  # noqa: S102 - execute the pinned repository notebook cell
        self.assertEqual(ns["native_cci_result"], native.native_cci(ROOT))
        with (
            patch.object(
                native, "native_cci", side_effect=SourceAdmissionError("stale")
            ),
            self.assertRaises(SourceAdmissionError),
        ):
            exec(code, ns)  # noqa: S102 - execute the pinned repository notebook cell
        self.assertIsNone(ns["native_cci_result"])

    def test_browser_cost_endpoint_boundary_and_stale_fetch(self):
        code = r"""
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const {checkedNativeCCI,nativeCCILoader}=await import('./phase9-web/spark-native-cci.js');
const view=JSON.parse(readFileSync(0,'utf8'));
assert.deepEqual(await checkedNativeCCI(view),view);
await assert.rejects(checkedNativeCCI({...view,native_endpoint_verified:true}));
function element(){return {textContent:'',children:[],append(e){this.children.push(e)},replaceChildren(){this.children=[]}}}
const output=element(),status=element();let queue=[];
const load=nativeCCILoader(output,status,()=>new Promise(r=>queue.push(r)),element);
const old=load(),fresh=load();queue[1]({ok:true,json:async()=>view});await fresh;
assert.match(status.textContent,/Measured native preflight verified/);
assert.ok(output.children.some(e=>/Full campaign has not started/.test(e.textContent)));
const count=output.children.length;queue[0]({ok:false});await old;assert.equal(output.children.length,count);
await nativeCCILoader(output,status,async()=>({ok:true,json:async()=>({...view,full_trajectory_runs:1})}),element)();
assert.equal(output.children.length,0);assert.match(status.textContent,/Unbound/);
"""
        result = subprocess.run(
            [str(managed_node()), "--input-type=module", "-e", code],
            input=json.dumps(native.native_cci(ROOT)),
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

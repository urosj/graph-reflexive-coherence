"""Pinned CI+PC pressure publication, independent retained checks and fixed scope."""

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
import p991a6_ccipc_pressure as checker
from grcv4_explorer import spark_native_ccipc_pressure as surface
from grcv4_explorer.canonical import record_digest
from grcv4_explorer.errors import SourceAdmissionError
from grcv4_explorer.spark_native_ccipc import native_ccipc
from grcv4_explorer.tooling import managed_node, tool_environment


class CCIPCPressureSurfaceTests(unittest.TestCase):
    def test_retained_five_steps_and_both_events_recompute_full_audits(self):
        value = checker.check(ROOT, numerical=True)
        self.assertEqual(value["tests_passed"], 27)
        self.assertGreaterEqual(len(value["measurements"]["mutations"]), 30)
        self.assertTrue(value["prior_60_direction_certificate_checks_retained"])
        self.assertEqual(value["measurements"]["actual_target_steps"], 4)
        self.assertFalse(value["native_endpoint_verified"])
        self.assertFalse(value["runtime_changed"])

    def test_discovery_collects_only_the_mandatory_CI_PC_roster(self):
        import test_ccipc_native_spark_pressure as cases

        suite = unittest.defaultTestLoader.loadTestsFromModule(cases)

        def names(s):
            for x in s:
                if isinstance(x, unittest.TestSuite):
                    yield from names(x)
                else:
                    yield x._testMethodName

        self.assertEqual(tuple(names(suite)), checker.ROSTER)

    def test_rehashed_scope_or_history_report_forgery_rejects(self):
        original = surface.load_json_object
        for key, value in [
            ("native_endpoint_verified", True),
            ("tests_passed", 0),
            ("measurements", {}),
            ("source_bindings", []),
        ]:

            def altered(path, key=key, value=value):
                data = deepcopy(original(path))
                data[key] = value
                data["record_digest"] = record_digest(data, "record_digest")
                return data

            with (
                patch.object(surface, "load_json_object", altered),
                self.assertRaises(SourceAdmissionError),
            ):
                surface.native_ccipc_pressure(ROOT)
        original_open = Path.open
        bad = (
            ROOT
            / "implementation/phase-9-grcv4/verification/ccipc_native_spark_audit.py"
        )

        def changed(path, *args, **kwargs):
            return (
                BytesIO(b"changed equations")
                if path == bad
                else original_open(path, *args, **kwargs)
            )

        with (
            patch.object(Path, "open", changed),
            self.assertRaises(SourceAdmissionError),
        ):
            native_ccipc(ROOT)

    def test_http_pressure_download_and_query_rejection(self):
        spec = importlib.util.spec_from_file_location(
            "ccipc_pressure_server", TOOL / "scripts/serve_phase9.py"
        )
        server = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(server)
        handler = server.Handler.__new__(server.Handler)
        codes = []
        handler.command = "GET"
        handler.send_response = lambda code, message=None: codes.append(code)
        handler.send_header = lambda *args: None
        handler.end_headers = lambda: None
        for route in [
            "/api/native-spark/c-ci-pc/pressure",
            "/api/native-spark/c-ci-pc/pressure/source",
            "/api/native-spark/c-ci-pc/pressure?campaign=true",
        ]:
            handler.path = route
            handler.wfile = BytesIO()
            handler.do_GET()
            self.assertEqual(codes[-1], 503 if "?" in route else 200)
            if route.endswith("/source"):
                self.assertEqual(
                    handler.wfile.getvalue(), (ROOT / surface.RECORD).read_bytes()
                )

    def test_browser_exposes_pressure_and_rejects_mutated_child_projection(self):
        code = r"""
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const {checkedNativeCCIPC,nativeCCIPCLoader}=await import('./phase9-web/spark-native-ccipc.js');
const view=JSON.parse(readFileSync(0,'utf8'));
assert.equal((await checkedNativeCCIPC(view)).pressure.tests_passed,27);
await assert.rejects(checkedNativeCCIPC({...view,pressure:{...view.pressure,native_endpoint_verified:true}}));
function element(){return {textContent:'',children:[],append(e){this.children.push(e)},replaceChildren(){this.children=[]}}}
const output=element(),status=element();
await nativeCCIPCLoader(output,status,async()=>({ok:true,json:async()=>view}),element)();
assert.ok(output.children.some(e=>/27 bounded composite pressure tests/.test(e.textContent)));
assert.ok(output.children.some(e=>e.href==='/api/native-spark/c-ci-pc/pressure/source'));
"""
        result = subprocess.run(
            [str(managed_node()), "--input-type=module", "-e", code],
            input=json.dumps(native_ccipc(ROOT)),
            text=True,
            capture_output=True,
            cwd=TOOL,
            env=tool_environment(),
            timeout=20,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_notebook_clears_result_when_pressure_sources_fail(self):
        book = json.loads((TOOL / "notebooks/phase9_verification.ipynb").read_text())
        cell = next(c for c in book["cells"] if c.get("id") == "spark-native-ccipc")
        code = compile("".join(cell["source"]), "ccipc-pressure-notebook", "exec")
        ns = {"repo_root": ROOT}
        exec(code, ns)  # noqa: S102 - execute the pinned repository notebook cell
        self.assertEqual(ns["native_ccipc_result"]["pressure"]["tests_passed"], 27)
        with (
            patch.object(
                surface,
                "checked_record",
                side_effect=SourceAdmissionError("pressure unavailable"),
            ),
            self.assertRaises(SourceAdmissionError),
        ):
            exec(code, ns)  # noqa: S102 - execute the pinned repository notebook cell
        self.assertIsNone(ns["native_ccipc_result"])


if __name__ == "__main__":
    unittest.main()

"""Pinned A_CI pressure publication, independent retained checks and fixed scope."""

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
import p991a6_aci_pressure as checker
from grcv4_explorer import spark_native_aci_pressure as surface
from grcv4_explorer.canonical import record_digest
from grcv4_explorer.errors import SourceAdmissionError
from grcv4_explorer.spark_native_aci import native_aci
from grcv4_explorer.tooling import managed_node, tool_environment


class ACIPressureSurfaceTests(unittest.TestCase):
    def test_retained_five_steps_and_both_events_recompute_full_audits(self):
        value = checker.check(ROOT, numerical=True)
        self.assertEqual(value["tests_passed"], 32)
        self.assertEqual(len(value["measurements"]["mutations"]), 45)
        self.assertTrue(value["prior_30_direction_certificate_checks_retained"])
        self.assertEqual(value["measurements"]["CI_staging"]["actual_target_steps"], 4)
        self.assertFalse(value["native_endpoint_verified"])
        self.assertFalse(value["runtime_changed"])

    def test_retained_operand_trace_rejects_wrong_read_and_writer_roles(self):
        import lzma

        from aci_native_spark_audit import audit_trace

        evidence = json.loads(lzma.decompress((ROOT / checker.EVIDENCE).read_bytes()))
        step = checker.decoded(evidence["actual_steps"][0]["step"])
        for mode in ("read_current", "writer_history", "extra_writer"):
            trace = deepcopy(evidence["operand_trace"])
            if mode == "read_current":
                row = next(
                    r for r in trace if r["stage"] == "drive" and r["phase"] == "root"
                )
                row["J"][0][0] = ["0", "0"]
            elif mode == "writer_history":
                row = next(
                    r for r in trace if r["stage"] == "drive" and r["phase"] == "writer"
                )
                from flint import fmpq as Q

                row["W"][0][0] = [str(Q(x) + Q(1, 4096)) for x in row["W"][0][0]]
            else:
                trace.append(next(r for r in trace if r["stage"] == "writer"))
            with self.subTest(mode=mode), self.assertRaises(AssertionError):
                audit_trace(step, trace)

    def test_discovery_collects_only_the_mandatory_A_CI_roster(self):
        import test_aci_native_spark_pressure as cases

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
                surface.native_aci_pressure(ROOT)
        original_open = Path.open
        bad = (
            ROOT / "implementation/phase-9-grcv4/verification/aci_native_spark_audit.py"
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
            native_aci(ROOT)

    def test_http_pressure_download_and_query_rejection(self):
        spec = importlib.util.spec_from_file_location(
            "aci_pressure_server", TOOL / "scripts/serve_phase9.py"
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
            "/api/native-spark/a-ci/pressure",
            "/api/native-spark/a-ci/pressure/source",
            "/api/native-spark/a-ci/pressure?campaign=true",
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
const {checkedNativeACI,nativeACILoader}=await import('./phase9-web/spark-native-aci.js');
const view=JSON.parse(readFileSync(0,'utf8'));
assert.equal((await checkedNativeACI(view)).pressure.tests_passed,32);
await assert.rejects(checkedNativeACI({...view,pressure:{...view.pressure,native_endpoint_verified:true}}));
function element(){return {textContent:'',children:[],append(e){this.children.push(e)},replaceChildren(){this.children=[]}}}
const output=element(),status=element();
await nativeACILoader(output,status,async()=>({ok:true,json:async()=>view}),element)();
assert.ok(output.children.some(e=>/32 bounded A_CI pressure tests/.test(e.textContent)));
assert.ok(output.children.some(e=>e.href==='/api/native-spark/a-ci/pressure/source'));
"""
        result = subprocess.run(
            [str(managed_node()), "--input-type=module", "-e", code],
            input=json.dumps(native_aci(ROOT)),
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
        cell = next(c for c in book["cells"] if c.get("id") == "spark-native-aci")
        code = compile("".join(cell["source"]), "aci-pressure-notebook", "exec")
        ns = {"repo_root": ROOT}
        exec(code, ns)  # noqa: S102 - execute the pinned repository notebook cell
        self.assertEqual(ns["native_aci_result"]["pressure"]["tests_passed"], 32)
        with (
            patch.object(
                surface,
                "checked_record",
                side_effect=SourceAdmissionError("pressure unavailable"),
            ),
            self.assertRaises(SourceAdmissionError),
        ):
            exec(code, ns)  # noqa: S102 - execute the pinned repository notebook cell
        self.assertIsNone(ns["native_aci_result"])


if __name__ == "__main__":
    unittest.main()

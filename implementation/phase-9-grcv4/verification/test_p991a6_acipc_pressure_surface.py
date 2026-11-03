"""Pinned A_CI_PC pressure publication, independent retained checks and fixed scope."""

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
import p991a6_acipc_pressure as checker
from grcv4_explorer import spark_native_acipc_pressure as surface
from grcv4_explorer.canonical import record_digest
from grcv4_explorer.errors import SourceAdmissionError
from grcv4_explorer.spark_native_acipc import native_acipc
from grcv4_explorer.tooling import managed_node, tool_environment


class ACIPCPressureSurfaceTests(unittest.TestCase):
    def test_retained_five_steps_and_both_events_recompute_full_audits(self):
        value = checker.check(ROOT, numerical=True)
        self.assertEqual(value["tests_passed"], 26)
        self.assertGreaterEqual(len(value["measurements"]["mutations"]), 50)
        self.assertTrue(value["prior_76_direction_certificate_checks_retained"])
        self.assertEqual(
            value["measurements"]["two_writer_staging"]["actual_target_steps"], 4
        )
        self.assertFalse(value["native_endpoint_verified"])
        self.assertFalse(value["runtime_changed"])
        self.assertIn(
            "implementation/phase-9-grcv4/verification/aci_native_spark_oracle.py",
            {row["path"] for row in value["source_bindings"]},
        )

    def test_retained_operand_trace_rejects_wrong_read_and_writer_roles(self):
        import lzma

        from acipc_native_spark_audit import audit_trace

        evidence = json.loads(lzma.decompress((ROOT / checker.EVIDENCE).read_bytes()))
        step = checker.decoded(evidence["actual_steps"][0]["step"])
        for mode in ("writer_final_C", "held_source", "old_Z", "extra_writer"):
            trace = deepcopy(evidence["operand_trace"])
            if mode == "writer_final_C":
                trace[1]["final_C"][0] = "0"
            elif mode == "held_source":
                trace[1]["held_source_after"][0][0] = ["1", "1"]
            elif mode == "old_Z":
                trace[2]["state"]["Z_4"][0][0] = "1/65536"
            else:
                trace.append(trace[2])
            wrapped = {"trace": trace}
            wrapped["record_digest"] = record_digest(wrapped, "record_digest")
            with self.subTest(mode=mode), self.assertRaises(AssertionError):
                audit_trace(step, wrapped["trace"])

    def test_rehashed_manufactured_inputs_must_satisfy_independent_algebra(self):
        import lzma

        from acipc_native_spark_pressure_oracle import audit_twins
        from flint import ctx

        evidence = json.loads(lzma.decompress((ROOT / checker.EVIDENCE).read_bytes()))
        with ctx.workprec(768):
            self.assertEqual(
                audit_twins(evidence["manufactured"]), evidence["manufactured_audit"]
            )
            altered = deepcopy(evidence["manufactured"])
            altered["equal_current_twin"]["source0"][0][0] = ["1", "1"]
            wrapped = {"probe": altered}
            wrapped["record_digest"] = record_digest(wrapped, "record_digest")
            with self.assertRaisesRegex(
                AssertionError, "manufactured source definition"
            ):
                audit_twins(wrapped["probe"])

    def test_rehashed_trial_reference_and_counterfeit_reject_numerically(self):
        import lzma

        from acipc_native_spark_audit import audit_trials
        from acipc_native_spark_pressure_oracle import audit_counterfeit
        from flint import ctx

        evidence = json.loads(lzma.decompress((ROOT / checker.EVIDENCE).read_bytes()))
        row = evidence["root_trials"]
        bad = deepcopy(row["roots"])
        bad[0]["trials"][1]["read"]["drive"][0][0] = ["0", "0"]
        wrapped = {"roots": bad}
        wrapped["record_digest"] = record_digest(wrapped, "record_digest")
        with self.assertRaisesRegex(AssertionError, "trial fresh drive"):
            audit_trials(checker.decoded(row["step"]), wrapped["roots"])
        with ctx.workprec(768):
            self.assertEqual(
                audit_counterfeit(evidence["counterfeit"]),
                evidence["counterfeit_audit"],
            )

    def test_discovery_collects_only_the_mandatory_A_CI_PC_roster(self):
        import test_acipc_native_spark_pressure as cases

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
                surface.native_acipc_pressure(ROOT)
        original_open = Path.open
        bad = (
            ROOT
            / "implementation/phase-9-grcv4/verification/acipc_native_spark_audit.py"
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
            native_acipc(ROOT)

    def test_http_pressure_download_and_query_rejection(self):
        spec = importlib.util.spec_from_file_location(
            "acipc_pressure_server", TOOL / "scripts/serve_phase9.py"
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
            "/api/native-spark/a-ci-pc/pressure",
            "/api/native-spark/a-ci-pc/pressure/source",
            "/api/native-spark/a-ci-pc/pressure?campaign=true",
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
const {checkedNativeACIPC,nativeACIPCLoader}=await import('./phase9-web/spark-native-acipc.js');
const view=JSON.parse(readFileSync(0,'utf8'));
assert.equal((await checkedNativeACIPC(view)).pressure.tests_passed,26);
await assert.rejects(checkedNativeACIPC({...view,pressure:{...view.pressure,native_endpoint_verified:true}}));
function element(){return {textContent:'',children:[],append(e){this.children.push(e)},replaceChildren(){this.children=[]}}}
const output=element(),status=element();
await nativeACIPCLoader(output,status,async()=>({ok:true,json:async()=>view}),element)();
assert.ok(output.children.some(e=>/26 bounded A_CI_PC pressure tests/.test(e.textContent)));
assert.ok(output.children.some(e=>e.href==='/api/native-spark/a-ci-pc/pressure/source'));
"""
        result = subprocess.run(
            [str(managed_node()), "--input-type=module", "-e", code],
            input=json.dumps(native_acipc(ROOT)),
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
        cell = next(c for c in book["cells"] if c.get("id") == "spark-native-acipc")
        code = compile("".join(cell["source"]), "acipc-pressure-notebook", "exec")
        ns = {"repo_root": ROOT}
        exec(code, ns)  # noqa: S102 - execute the pinned repository notebook cell
        self.assertEqual(ns["native_acipc_result"]["pressure"]["tests_passed"], 26)
        with (
            patch.object(
                surface,
                "checked_record",
                side_effect=SourceAdmissionError("pressure unavailable"),
            ),
            self.assertRaises(SourceAdmissionError),
        ):
            exec(code, ns)  # noqa: S102 - execute the pinned repository notebook cell
        self.assertIsNone(ns["native_acipc_result"])


if __name__ == "__main__":
    unittest.main()

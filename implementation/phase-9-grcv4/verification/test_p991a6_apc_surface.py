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

import p991a6_apc_epoch as epoch
import p991a6_apc_preflight as preflight
from grcv4_explorer import spark_native_apc as native
from grcv4_explorer.canonical import record_digest
from grcv4_explorer.errors import SourceAdmissionError
from grcv4_explorer.tooling import managed_node, tool_environment


class NativeAPCPreflightTests(unittest.TestCase):
    def test_retained_measurements_recompute_estimate_and_bind_real_operands(self):
        value = preflight.check(ROOT)
        self.assertEqual(value["estimate"]["profiling_target_seconds"], 1800)
        self.assertLess(value["elapsed_seconds"], value["sampling_cap_seconds"])
        self.assertEqual(value["certificate_precision_bits"], 256)
        self.assertTrue(value["precision_comparison"]["identical_represented_states"])
        self.assertEqual(value["tests"]["count"], 29)
        self.assertGreater(
            value["caches"]["domain_warm"]["hits"],
            value["caches"]["domain_cold"]["hits"],
        )
        for rows in value["samples"].values():
            self.assertEqual(len(rows), 40)
            self.assertTrue(
                all(
                    row["fresh_reads"] == 2
                    and row["writer_calls"]
                    == row["carrier_writer_calls"]
                    == row["full_state_writes"]
                    == 1
                    for row in rows
                )
            )

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
                native.native_apc(ROOT)

    def test_changed_runtime_or_compressed_evidence_rejects_projection(self):
        original = Path.open
        for name in ("src/pygrc/models/grc_v4_spark_apc.py", preflight.EVIDENCE):
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
                native.native_apc(ROOT)

    def test_finite_epoch_preserves_predecessor_records_and_rejects_drift(self):
        import p991a6_aci_campaign_epoch as previous
        from grcv4_explorer.basin import _bound_file
        from grcv4_explorer.spark_native_aos import native_aos

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
        for name in (
            "P9-9.1a.6-ACI-Preflight.json.xz",
            "P9-9.1a.6-ACI-Pressure.json",
            "P9-9.1a.6-ACI.5-Campaign.json.xz",
            "P9-9.1a.6-AOS-Preflight.json.xz",
            "P9-9.1a.6-AOS-Pressure.json",
            "P9-9.1a.6-AOS.5-Campaign.json.xz",
        ):
            path = "implementation/phase-9-grcv4/tranche-9/" + name
            self.assertEqual((ROOT / path).read_bytes(), epoch.original(ROOT, path))
        self.assertEqual(native_aos(ROOT)["tests"]["count"], 25)
        from grcv4_explorer.spark_native_aci import native_aci

        self.assertEqual(native_aci(ROOT)["tests"]["count"], 28)
        from grcv4_explorer.spark_native_aci_campaign import native_aci_campaign
        from grcv4_explorer.spark_native_aos_campaign import native_aos_campaign

        for campaign in (native_aci_campaign(ROOT), native_aos_campaign(ROOT)):
            self.assertTrue(campaign["native_endpoint_verified"])
            self.assertEqual(campaign["full_trajectory_runs"], 2)
            self.assertFalse(campaign["native_completion_support"])
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

    def test_compact_and_full_samples_recompute_and_detect_changed_witnesses(self):
        import lzma
        from dataclasses import replace

        from apc_native_spark_oracle import verify_step

        from pygrc.models.grc_9_v4_completion_certificate import CompletionCertificate
        from pygrc.models.grc_v4_state import FrozenJSONMap

        value = preflight.check(ROOT)
        certs = dict(
            zip(
                ("current", "reset"),
                map(CompletionCertificate.from_payload, value["certificates"]),
                strict=True,
            )
        )
        evidence = json.loads(lzma.decompress((ROOT / preflight.EVIDENCE).read_bytes()))
        self.assertEqual(len(evidence["samples"]), 80)
        self.assertEqual(len(evidence["full_samples"]), 6)
        previous = {}
        samples = {}
        for row in evidence["samples"]:
            step = preflight.decoded(row["transition"])
            role = row["role"]
            if role in previous:
                self.assertEqual(previous[role], step.before)
            previous[role] = step.after
            samples[role, row["index"]] = row
            actual = verify_step(step, certs[role], role, compact=True)
            expected = dict(row["independent"], full_diagnostics_checked=False)
            self.assertEqual(actual, expected)
        for row in evidence["full_samples"]:
            step = preflight.decoded(row["transition"])
            compact = samples[row["role"], row["index"]]
            self.assertEqual(preflight.compact_transition(step), compact["transition"])
            self.assertEqual(
                verify_step(step, certs[row["role"]], row["role"]),
                compact["independent"],
            )
        source = preflight.decoded(evidence["source_transition"])
        self.assertEqual(verify_step(source), evidence["source_independent"])
        step = preflight.decoded(evidence["samples"][0]["transition"])
        for field, key, bad in (
            ("writer", "consumed_state_digest", "0" * 64),
            ("writer", "midpoint", ["0"] * 16),
            ("carrier_writer", "consumed_state_digest", "0" * 64),
            ("carrier_writer", "midpoint", [["0"] * 16 for _ in range(16)]),
            ("consumed_read", "current_midpoint", ["0"] * 16),
            ("restart_read", "current_midpoint", ["0"] * 16),
        ):
            altered = getattr(step, field).to_dict()
            self.assertIn(key, altered)
            altered[key] = bad
            with self.subTest(field=field, key=key), self.assertRaises(AssertionError):
                verify_step(
                    replace(step, **{field: FrozenJSONMap(altered)}), compact=True
                )

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
            "/api/native-spark/a-pc/preflight",
            "/api/native-spark/a-pc/preflight/source",
            "/spark-native-apc.js",
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
                    json.loads(handler.wfile.getvalue()), native.native_apc(ROOT)
                )
        handler.path = "/api/native-spark/a-pc/preflight?other=true"
        handler.wfile = BytesIO()
        handler.do_GET()
        self.assertEqual(codes[-1], 503)

    def test_notebook_clears_stale_preflight(self):
        book = json.loads((TOOL / "notebooks/phase9_verification.ipynb").read_text())
        cell = next(c for c in book["cells"] if c.get("id") == "spark-native-apc")
        code = compile("".join(cell["source"]), "preflight-notebook", "exec")
        ns = {"repo_root": ROOT}
        exec(code, ns)  # noqa: S102 - execute the pinned repository notebook cell
        self.assertEqual(ns["native_apc_result"], native.native_apc(ROOT))
        with (
            patch.object(
                native, "native_apc", side_effect=SourceAdmissionError("stale")
            ),
            self.assertRaises(SourceAdmissionError),
        ):
            exec(code, ns)  # noqa: S102 - execute the pinned repository notebook cell
        self.assertIsNone(ns["native_apc_result"])

    def test_browser_cost_endpoint_boundary_and_stale_fetch(self):
        code = r"""
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const {checkedNativeAPC,nativeAPCLoader}=await import('./phase9-web/spark-native-apc.js');
const view=JSON.parse(readFileSync(0,'utf8'));
assert.deepEqual(await checkedNativeAPC(view),view);
await assert.rejects(checkedNativeAPC({...view,native_endpoint_verified:true}));
function element(){return {textContent:'',children:[],append(e){this.children.push(e)},replaceChildren(){this.children=[]}}}
const output=element(),status=element();let queue=[];
const load=nativeAPCLoader(output,status,()=>new Promise(r=>queue.push(r)),element);
const old=load(),fresh=load();queue[1]({ok:true,json:async()=>view});await fresh;
assert.match(status.textContent,/Bounded native preflight verified/);
assert.ok(output.children.some(e=>/bounded preflight contains no endpoint run/.test(e.textContent)));
const count=output.children.length;queue[0]({ok:false});await old;assert.equal(output.children.length,count);
await nativeAPCLoader(output,status,async()=>({ok:true,json:async()=>({...view,full_trajectory_runs:1})}),element)();
assert.equal(output.children.length,0);assert.match(status.textContent,/Unbound/);
"""
        result = subprocess.run(
            [str(managed_node()), "--input-type=module", "-e", code],
            input=json.dumps(native.native_apc(ROOT)),
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

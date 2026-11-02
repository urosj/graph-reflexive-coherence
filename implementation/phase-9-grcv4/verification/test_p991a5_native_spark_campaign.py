"""Campaign continuity, hostile stage mutations and publication controls."""

import importlib.util
import json
import subprocess
import sys
import tempfile
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

import lzma

import p991a5_native_spark_campaign as campaign
import p991a5_native_spark_epoch as epoch
from cos_native_spark_oracle import classify, infinity, matrix, vector
from grcv4_explorer import spark_native_campaign as native
from grcv4_explorer.canonical import record_digest
from grcv4_explorer.errors import SourceAdmissionError
from grcv4_explorer.tooling import managed_node, tool_environment
from p991a5_native_spark_verify import verify_step


class NativeSparkCampaignTests(unittest.TestCase):
    def test_retained_trajectory_chain_and_actual_endpoints(self):
        value = campaign.check(ROOT)
        self.assertTrue(value["native_endpoint_verified"])
        self.assertFalse(value["native_completion_support"])
        self.assertFalse(value["user_accepted"])
        self.assertLess(value["elapsed_seconds"], value["cap_seconds"])
        self.assertEqual(value["physical_supporting_tail_steps"], 0)
        for role, endpoints in campaign.EXPECTED.items():
            row = value["roles"][role]
            self.assertEqual((row["entry"], row["completion"]), endpoints)
            self.assertEqual(row["window"], list(range(endpoints[0], endpoints[1] + 1)))
            self.assertEqual(row["local_gain"], int(role == "current"))
        pressure = {r["fault"]: r for r in value["pressure"]}
        for phase in ("after_numerics", "after_window", "before_publication"):
            self.assertTrue(pressure[phase]["whole_root_unchanged"])
        self.assertEqual(
            pressure["failed_fork_retry_after_primary_claim"]["additional_gain"], 0
        )
        self.assertEqual(len(value["completion"]["children"]), 1)

    def test_archived_membership_classification_and_once_only_window(self):
        with lzma.open(ROOT / campaign.FILES["inputs"], "rt") as stream:
            inputs = json.loads(next(stream))
        config = inputs["target_configuration"]
        value = native.checked_record(ROOT)
        for index, role in enumerate(("current", "reset")):
            cert = inputs["certificates"][index]
            U, center = (
                matrix(cert["operands"]["U"]),
                vector(cert["operands"]["center"]),
            )
            inside, gains, last = [], [], None
            with lzma.open(ROOT / campaign.FILES[role], "rt") as stream:
                for line in stream:
                    row = json.loads(line)
                    C = row["stage"]["after"]
                    norm = infinity(U * (vector(C) - center))
                    self.assertEqual(row["membership"]["norm"], str(norm))
                    self.assertEqual(row["membership"]["inside"], norm <= 1)
                    basins, terminals, rows = classify(
                        config["reference"]["graph"],
                        C,
                        config["specialization"]["resolved"]["completion_policy"],
                    )
                    actual = row["membership"]["classification"]
                    self.assertEqual(
                        tuple(
                            (
                                r["anchor"]["value"],
                                tuple(n["value"] for n in r["members"]),
                            )
                            for r in actual["basins"]
                        ),
                        basins,
                    )
                    self.assertEqual(
                        tuple(
                            (
                                r["node"]["value"],
                                tuple(n["value"] for n in r["terminals"]),
                            )
                            for r in actual["terminals"]
                        ),
                        terminals,
                    )
                    self.assertEqual(actual["rows"], rows)
                    if norm <= 1:
                        inside.append(row["beat"])
                    if row["local_gain"]:
                        gains.append((row["beat"], row["local_gain"]))
                    last = row
            self.assertEqual(inside, value["roles"][role]["window"])
            self.assertEqual(gains, [(376, 1)] if role == "current" else [])
            self.assertEqual(
                last["membership"], value["roles"][role]["final_membership"]
            )

    def test_independent_stage_oracle_rejects_same_state_wrong_diagnostics(self):
        with lzma.open(ROOT / campaign.FILES["inputs"], "rt") as stream:
            inputs = json.loads(next(stream))
        with lzma.open(ROOT / campaign.FILES["current"], "rt") as stream:
            row = json.loads(next(stream))
        cert = inputs["certificates"][0]
        graph = inputs["target_configuration"]["reference"]["graph"]
        U, bound = matrix(cert["operands"]["U"]), cert["proof"]["full_step_error"]
        self.assertEqual(
            verify_step(graph, row["stage"], U, bound), row["independent_error_upper"]
        )
        for stage in range(4):
            for key in ("J", "f"):
                changed = deepcopy(row["stage"])
                changed["reads"][stage][key][0] = "123456"
                with self.subTest(stage=stage, key=key), self.assertRaises(ValueError):
                    verify_step(graph, changed, U, bound)

    def test_lossless_storage_keeps_original_execution_and_trace(self):
        from p991a5_native_spark_storage import EXECUTION, check

        value = check(ROOT)
        original = json.loads((ROOT / EXECUTION).read_bytes())
        self.assertEqual(value["storage_repack"]["numerical_steps_executed"], 0)
        self.assertEqual(value["elapsed_seconds"], original["elapsed_seconds"])
        self.assertEqual(value["roles"], original["roles"])
        self.assertEqual(value["pressure"], original["pressure"])
        self.assertTrue(
            all(r["compressed_bytes"] < 100 * 2**20 for r in value["streams"])
        )

    def test_fresh_checkout_restores_exact_summary_records(self):
        names = [
            campaign.RECORD,
            "implementation/phase-9-grcv4/tranche-9/P9-9.1a.5-Execution.json",
        ]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in [
                "scripts/evidence_storage.py",
                "artifact-storage.json",
                *(n + ".xz" for n in names),
            ]:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / name).read_bytes())
            native.restore_evidence(root)
            for name in names:
                self.assertEqual((root / name).read_bytes(), (ROOT / name).read_bytes())
            (root / names[0]).write_bytes(b"changed local record")
            with self.assertRaises(ValueError):
                native.restore_evidence(root)

    def test_rehashed_endpoint_or_scope_forgery_is_not_admitted_by_surface(self):
        original = native.load_json_object
        for key, change in (
            ("native_endpoint_verified", False),
            ("full_trajectory_runs", 1),
            ("roles", {}),
            ("user_accepted", True),
            ("physical_supporting_tail_steps", 1600),
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
                native.native_campaign(ROOT)

    def test_changed_runtime_or_compressed_evidence_rejects_projection(self):
        original = Path.open
        for name in (
            "src/pygrc/models/grc_v4_spark_cos.py",
            campaign.FILES["checkpoints"],
        ):
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
                native.native_campaign(ROOT)

    def test_finite_metadata_epoch_keeps_committed_lifecycle_record(self):
        import p991a4_native_spark_epoch as previous
        from grcv4_explorer.basin import _bound_file
        from grcv4_explorer.spark_native_preflight import native_preflight

        self.assertEqual(
            epoch.manifest(ROOT), json.loads((ROOT / epoch.PATH).read_bytes())
        )
        self.assertEqual(
            previous.manifest(ROOT), json.loads((ROOT / previous.PATH).read_bytes())
        )
        for name in epoch.CHANGED:
            raw = epoch.original(ROOT, name)
            self.assertEqual(_bound_file(ROOT, name, epoch.sha(raw)).read_bytes(), raw)
        record = "implementation/phase-9-grcv4/tranche-9/P9-9.1a.4-Preflight.json"
        self.assertEqual((ROOT / record).read_bytes(), epoch.original(ROOT, record))
        self.assertFalse(native_preflight(ROOT)["native_endpoint_verified"])
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
            "campaign_server", TOOL / "scripts/serve_phase9.py"
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
            "/api/native-spark/c-os/campaign",
            "/api/native-spark/c-os/campaign/source",
            "/spark-native-campaign.js",
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
                    json.loads(handler.wfile.getvalue()), native.native_campaign(ROOT)
                )
        handler.path = "/api/native-spark/c-os/campaign?other=true"
        handler.wfile = BytesIO()
        handler.do_GET()
        self.assertEqual(codes[-1], 503)

    def test_notebook_clears_stale_preflight(self):
        book = json.loads((TOOL / "notebooks/phase9_verification.ipynb").read_text())
        cell = next(c for c in book["cells"] if c.get("id") == "native-cos-campaign")
        code = compile("".join(cell["source"]), "campaign-notebook", "exec")
        ns = {"repo_root": ROOT}
        exec(code, ns)  # noqa: S102 - execute the pinned repository notebook cell
        self.assertEqual(ns["phase9_native_cos_campaign"], native.native_campaign(ROOT))
        with (
            patch.object(
                native, "native_campaign", side_effect=SourceAdmissionError("stale")
            ),
            self.assertRaises(SourceAdmissionError),
        ):
            exec(code, ns)  # noqa: S102 - execute the pinned repository notebook cell
        self.assertIsNone(ns["phase9_native_cos_campaign"])

    def test_browser_cost_endpoint_boundary_and_stale_fetch(self):
        code = r"""
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const {checkedNativeCampaign,nativeCampaignLoader}=await import('./phase9-web/spark-native-campaign.js');
const view=JSON.parse(readFileSync(0,'utf8'));
assert.deepEqual(await checkedNativeCampaign(view),view);
await assert.rejects(checkedNativeCampaign({...view,native_endpoint_verified:false}));
function element(){return {textContent:'',children:[],append(e){this.children.push(e)},replaceChildren(){this.children=[]}}}
const output=element(),status=element();let queue=[];
const load=nativeCampaignLoader(output,status,()=>new Promise(r=>queue.push(r)),element);
const old=load(),fresh=load();queue[1]({ok:true,json:async()=>view});await fresh;
assert.match(status.textContent,/Native C_OS campaign verified/);
assert.ok(output.children.some(e=>/No supporting trajectory tail/.test(e.textContent)));
const count=output.children.length;queue[0]({ok:false});await old;assert.equal(output.children.length,count);
await nativeCampaignLoader(output,status,async()=>({ok:true,json:async()=>({...view,full_trajectory_runs:1})}),element)();
assert.equal(output.children.length,0);assert.match(status.textContent,/Unbound/);
"""
        result = subprocess.run(
            [str(managed_node()), "--input-type=module", "-e", code],
            input=json.dumps(native.native_campaign(ROOT)),
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

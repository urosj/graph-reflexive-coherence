"""Retained native CI endpoint, stream, source and side-tool admission checks."""

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
import p991a6_cpc_campaign as campaign
from cos_native_spark_oracle import classify
from grcv4_explorer import spark_native_cpc_campaign as surface
from grcv4_explorer.canonical import record_digest
from grcv4_explorer.errors import SourceAdmissionError
from grcv4_explorer.tooling import managed_node, tool_environment
from p991a6_cpc_campaign_verify import verify

from pygrc.models.grc_9_v4_completion_certificate import CompletionCertificate
from pygrc.models.grc_9_v4_spark_contracts import GRC9V4SparkConfiguration


def read_stream(name):
    with lzma.open(ROOT / campaign.FILES[name], "rt") as stream:
        for line in stream:
            yield json.loads(line)


class CPCCampaignSurfaceTests(unittest.TestCase):
    def test_full_trace_chain_membership_and_once_only_endpoint(self):
        value = campaign.check(ROOT)
        self.assertEqual(value["full_trajectory_runs"], 2)
        self.assertEqual(value["physical_supporting_tail_steps"], 0)
        self.assertEqual(value["time_limit_policy"], "profiling_only_user_authorized")
        self.assertEqual(
            value["profiling_target_exceeded"], value["elapsed_seconds"] > 1800
        )
        self.assertEqual(len(value["completion"]["children"]), 1)
        self.assertEqual(len(value["completion"]["consumed_occurrences"]), 1)
        self.assertEqual(len(value["pressure"]), 11)
        self.assertFalse(value["native_completion_support"])
        self.assertFalse(value["user_accepted"])
        phases = {r["fault"]: r for r in value["pressure"]}
        for name in (
            "incoming_read",
            "poststate_read",
            "carrier_writer",
            "after_numerics",
            "after_window",
            "before_publication",
        ):
            self.assertTrue(phases[name]["whole_root_unchanged"])
        self.assertEqual(
            phases["failed_fork_retry_after_primary_claim"]["committed"], 6
        )
        checkpoints = [
            r for r in read_stream("checkpoints") if r["label"] != "periodic"
        ]
        self.assertEqual(
            [(r["role"], r["beat"], r["label"]) for r in checkpoints],
            [
                (role, entry + offset, label)
                for role, entry in [("current", 374), ("reset", 375)]
                for offset, label in [
                    (-1, "before_entry"),
                    (0, "entry"),
                    (1, "first_window"),
                    (2, "complete"),
                ]
            ],
        )

    def test_recovery_preserves_primary_and_matches_original_prefix(self):
        from hashlib import sha256

        from p991a6_cpc_resume_cost import rows, stopped

        from pygrc.models.grc_v4_codec import canonical_json_bytes

        stop = stopped()
        value = surface.checked_record(ROOT)
        recovered = value["recovery"]
        self.assertEqual(recovered["cold_ordinary_journal_steps"], 527)
        self.assertEqual(recovered["checkpoint_replay_target_steps"], 42)
        self.assertEqual(recovered["first_new_reset_beat"], 192)
        self.assertEqual(value["failed_recovery_seconds"], 1011)
        self.assertGreater(
            value["elapsed_seconds"], value["resume_elapsed_seconds"] + 1748
        )
        original = {
            role: rows(stop["streams"][role]["path"]) for role in ("current", "reset")
        }
        self.assertEqual(list(read_stream("reset"))[:191], original["reset"])
        for row in recovered["exact_prefix_replays"]:
            expected = original[row["role"]][row["beat"] - 1]["stage"]
            self.assertEqual(
                row["stage_digest"], sha256(canonical_json_bytes(expected)).hexdigest()
            )
            self.assertTrue(row["matches_original"])

    def test_full_source_prefix_and_both_event_archives(self):
        from dataclasses import replace

        from cpc_native_spark_pressure_oracle import audit_event
        from p991a6_cpc_campaign_verify import decoded

        inputs = next(read_stream("inputs"))
        source = GRC9V4SparkConfiguration.from_payload(inputs["source_configuration"])
        target = GRC9V4SparkConfiguration.from_payload(inputs["target_configuration"])
        report = verify(source, inputs["source_stage"])
        retained = inputs["source_error_in_target_chart"]
        self.assertEqual(
            report,
            {
                k: v
                for k, v in retained.items()
                if k
                not in {
                    "transported_resource_chart_error_upper",
                    "transported_carrier_error",
                }
            },
        )
        before = replace(source, current=decoded(inputs["source_stage"]).after)
        self.assertEqual(
            audit_event(before, target, inputs["event"]), inputs["event_audit"]
        )
        self.assertEqual(retained["transported_carrier_error"], "0")
        for role in ("current", "reset"):
            state = inputs["initial_roles"][role]
            self.assertTrue(all(x == "0" for row in state["Z_4"] for x in row))

    def test_complete_independent_geometric_classifications(self):
        inputs = next(read_stream("inputs"))
        config = inputs["target_configuration"]
        for role in ("current", "reset"):
            gain = []
            inside = []
            for row in read_stream(role):
                b, t, r = classify(
                    config["reference"]["graph"],
                    row["stage"]["after"]["C"],
                    config["specialization"]["resolved"]["completion_policy"],
                )
                actual = row["membership"]["classification"]
                self.assertEqual(
                    tuple(
                        (x["anchor"]["value"], tuple(n["value"] for n in x["members"]))
                        for x in actual["basins"]
                    ),
                    b,
                )
                self.assertEqual(
                    tuple(
                        (x["node"]["value"], tuple(n["value"] for n in x["terminals"]))
                        for x in actual["terminals"]
                    ),
                    t,
                )
                self.assertEqual(actual["rows"], r)
                if row["membership"]["inside"]:
                    inside.append(row["beat"])
                if row["local_gain"]:
                    gain.append((row["beat"], row["local_gain"]))
            self.assertEqual(gain, [(376, 1)] if role == "current" else [])
            self.assertEqual(
                inside, [374, 375, 376] if role == "current" else [375, 376, 377]
            )

    def test_independent_actual_boundary_history_and_wrong_diagnostic_rejection(self):
        inputs = next(read_stream("inputs"))
        config = GRC9V4SparkConfiguration.from_payload(inputs["target_configuration"])
        for i, role in enumerate(("current", "reset")):
            cert = CompletionCertificate.from_payload(inputs["certificates"][i])
            for row in read_stream(role):
                if row["beat"] in (1, *campaign.EXPECTED[role]):
                    audit = verify(config, row["stage"], cert, role)
                    self.assertEqual(audit, row["independent_history_and_error_audit"])
                    if row["beat"] == campaign.EXPECTED[role][1]:
                        bad = deepcopy(row["stage"])
                        bad["restart_read"]["H"][0][0] = ["0", "0"]
                        with self.assertRaises((ValueError, AssertionError)):
                            verify(config, bad, cert, role)

    def test_rehashed_scope_forgery_and_changed_execution_source_reject(self):
        original = surface.load_record
        for key, value in [
            ("time_limit_policy", "hard_stop"),
            ("native_endpoint_verified", False),
            ("native_completion_support", True),
            ("roles", {}),
            ("physical_supporting_tail_steps", 1600),
            ("source_bindings", []),
        ]:

            def altered(path, key=key, value=value):
                data = deepcopy(original(path))
                data[key] = value
                data["record_digest"] = record_digest(data, "record_digest")
                return data

            with (
                patch.object(surface, "load_record", altered),
                self.assertRaises(SourceAdmissionError),
            ):
                surface.native_cpc_campaign(ROOT)
        original_open = Path.open
        for name in [
            "src/pygrc/models/grc_v4_spark_cpc.py",
            campaign.FILES["checkpoints"],
        ]:

            def changed(path, *args, name=name, **kwargs):
                return (
                    BytesIO(b"changed execution")
                    if path == ROOT / name
                    else original_open(path, *args, **kwargs)
                )

            with (
                patch.object(Path, "open", changed),
                self.assertRaises(SourceAdmissionError),
            ):
                surface.native_cpc_campaign(ROOT)

    def test_http_source_and_fixed_scope(self):
        spec = importlib.util.spec_from_file_location(
            "cpc_campaign_server", TOOL / "scripts/serve_phase9.py"
        )
        server = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(server)
        h = server.Handler.__new__(server.Handler)
        codes = []
        h.command = "GET"
        h.send_response = lambda code, message=None: codes.append(code)
        h.send_header = lambda *args: None
        h.end_headers = lambda: None
        for route in [
            "/api/native-spark/c-pc/campaign",
            "/api/native-spark/c-pc/campaign/source",
            "/spark-native-cpc-campaign.js",
            "/api/native-spark/c-pc/campaign?role=reset",
        ]:
            h.path = route
            h.wfile = BytesIO()
            h.do_GET()
            self.assertEqual(codes[-1], 503 if "?" in route else 200)
            if route.endswith("/source"):
                self.assertEqual(
                    h.wfile.getvalue(),
                    lzma.decompress((ROOT / surface.RECORD).read_bytes()),
                )

    def test_browser_scope_stale_fetch_and_failure_clearing(self):
        code = r"""
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const {checkedNativeCPCCampaign,nativeCPCCampaignLoader}=await import('./phase9-web/spark-native-cpc-campaign.js');
const view=JSON.parse(readFileSync(0,'utf8'));
assert.deepEqual(await checkedNativeCPCCampaign(view),view);
await assert.rejects(checkedNativeCPCCampaign({...view,native_completion_support:true}));
function element(){return {textContent:'',children:[],append(e){this.children.push(e)},replaceChildren(){this.children=[]}}}
const output=element(),status=element();let queue=[];
const load=nativeCPCCampaignLoader(output,status,()=>new Promise(r=>queue.push(r)),element);
const old=load(),fresh=load();queue[1]({ok:true,json:async()=>view});await fresh;
assert.match(status.textContent,/endpoint verified/);
assert.ok(output.children.some(e=>/374 → completion 376/.test(e.textContent)));
assert.ok(output.children.some(e=>e.href==='/api/native-spark/c-pc/campaign/source'));
const count=output.children.length;queue[0]({ok:false});await old;assert.equal(output.children.length,count);
await nativeCPCCampaignLoader(output,status,async()=>({ok:false}),element)();
assert.equal(output.children.length,0);
"""
        result = subprocess.run(
            [str(managed_node()), "--input-type=module", "-e", code],
            input=json.dumps(surface.native_cpc_campaign(ROOT)),
            text=True,
            capture_output=True,
            cwd=TOOL,
            env=tool_environment(),
            timeout=20,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_notebook_clears_stale_campaign(self):
        book = json.loads((TOOL / "notebooks/phase9_verification.ipynb").read_text())
        cell = next(
            c for c in book["cells"] if c.get("id") == "spark-native-cpc-campaign"
        )
        code = compile("".join(cell["source"]), "cpc-campaign-notebook", "exec")
        ns = {"repo_root": ROOT}
        exec(code, ns)  # noqa: S102 - execute the repository notebook cell
        self.assertEqual(
            ns["native_cpc_campaign_result"], surface.native_cpc_campaign(ROOT)
        )
        with (
            patch.object(
                surface,
                "native_cpc_campaign",
                side_effect=SourceAdmissionError("stale"),
            ),
            self.assertRaises(SourceAdmissionError),
        ):
            exec(code, ns)  # noqa: S102 - execute the repository notebook cell
        self.assertIsNone(ns["native_cpc_campaign_result"])

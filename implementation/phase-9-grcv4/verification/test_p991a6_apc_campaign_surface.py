"""Retained native A_PC endpoint, compact evidence and publication checks."""

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
import p991a6_apc_campaign as campaign
import p991a6_apc_campaign as evidence
from grcv4_explorer import spark_native_apc_campaign as surface
from grcv4_explorer.canonical import record_digest
from grcv4_explorer.errors import SourceAdmissionError
from grcv4_explorer.tooling import managed_node, tool_environment
from p991a6_apc_campaign_verify import classify_and_membership, expand, verify

from pygrc.models.grc_9_v4_completion_certificate import CompletionCertificate
from pygrc.models.grc_9_v4_spark_contracts import GRC9V4SparkConfiguration


def read_stream(name):
    with lzma.open(ROOT / campaign.FILES[name], "rt") as stream:
        for line in stream:
            yield json.loads(line)


class APCCampaignSurfaceTests(unittest.TestCase):
    def test_publication_successor_preserves_accepted_records(self):
        import p991a6_apc_campaign_epoch as epoch
        import p991a6_apc_epoch as predecessor

        self.assertEqual(
            epoch.manifest(ROOT), json.loads((ROOT / epoch.PATH).read_bytes())
        )
        self.assertEqual(
            predecessor.manifest(ROOT),
            json.loads((ROOT / predecessor.PATH).read_bytes()),
        )
        for name in (
            "P9-9.1a.6-APC-Preflight.json.xz",
            "P9-9.1a.6-APC-Samples.json.xz",
            "P9-9.1a.6-APC-PressureSamples.json.xz",
            "P9-9.1a.6-APC-Pressure.json",
            "P9-9.1a.6-APC-SourceEpoch.json",
            "P9-9.1a.6-ACI.5-Campaign.json.xz",
            "P9-9.1a.6-ACI.5-SourceEpoch.json",
            "P9-9.1a.6-CPC.5-Campaign.json.xz",
            "P9-9.1a.6-CPC.5-EvidenceEpoch.json",
            "P9-9.1a.6-AOS.5-Campaign.json.xz",
            "P9-9.1a.6-AOS.5-current.jsonl.xz",
            "P9-9.1a.6-AOS.5-reset.jsonl.xz",
            "P9-9.1a.6-AOS.5-inputs.jsonl.xz",
            "P9-9.1a.6-AOS.5-checkpoints.jsonl.xz",
            "P9-9.1a.6-AOS.5-diagnostics.jsonl.xz",
        ):
            path = campaign.BASE + name
            self.assertEqual((ROOT / path).read_bytes(), epoch.original(ROOT, path))
        from grcv4_explorer.spark_native_aci_campaign import native_aci_campaign
        from grcv4_explorer.spark_native_aos_campaign import native_aos_campaign

        self.assertTrue(native_aos_campaign(ROOT)["native_endpoint_verified"])
        self.assertTrue(native_aci_campaign(ROOT)["native_endpoint_verified"])

    def test_full_trace_chain_membership_and_once_only_endpoint(self):
        value = evidence.check(ROOT)
        self.assertEqual(value["full_trajectory_runs"], 2)
        self.assertEqual(sum(r["target_steps"] for r in value["roles"].values()), 751)
        self.assertEqual(value["full_diagnostic_samples"], 10)
        self.assertEqual(
            value["evidence_format"],
            "compact_complete_state_read_and_two_writer_witnesses_v1",
        )
        self.assertEqual(value["physical_supporting_tail_steps"], 0)
        self.assertEqual(
            sum(
                row["stage"]["consumed_read"] == {"previous_restart": True}
                for role in ("current", "reset")
                for row in read_stream(role)
            ),
            749,
        )
        self.assertEqual(value["time_limit_policy"], "profiling_only_user_authorized")
        self.assertEqual(
            value["profiling_target_exceeded"], value["elapsed_seconds"] > 1800
        )
        self.assertEqual(len(value["completion"]["children"]), 1)
        self.assertEqual(len(value["completion"]["consumed_occurrences"]), 1)
        self.assertEqual(len(value["pressure"]), 12)
        self.assertFalse(value["native_completion_support"])
        self.assertFalse(value["user_accepted"])
        phases = {r["fault"]: r for r in value["pressure"]}
        for name in (
            "incoming_read",
            "poststate_read",
            "conductance_writer",
            "carrier_writer",
            "after_numerics",
            "after_window",
            "before_publication",
        ):
            self.assertTrue(phases[name]["whole_root_unchanged"])
        self.assertEqual(
            phases["failed_fork_retry_after_primary_claim"]["committed"], 7
        )
        checkpoints = [
            r for r in read_stream("checkpoints") if r["label"] != "periodic"
        ]
        self.assertEqual(
            [(r["role"], r["beat"], r["label"]) for r in checkpoints],
            [
                (role, entry + offset, label)
                for role, entry in [("current", 375), ("reset", 372)]
                for offset, label in [
                    (-1, "before_entry"),
                    (0, "entry"),
                    (1, "first_window"),
                    (2, "complete"),
                ]
            ],
        )

    def test_both_completed_journals_were_cold_replayed(self):
        value = surface.checked_record(ROOT)
        for role, beats in (("current", 377), ("reset", 374)):
            row = value["cold_checkpoint_validation"][role]
            self.assertEqual(row["ordinary_journal_steps"], beats + 1)
            self.assertEqual(row["replayed_steps"], beats + 1)
            self.assertTrue(row["whole_publication_equal"])
            self.assertGreater(row["seconds"], 0)

    def test_full_source_prefix_and_both_event_archives(self):
        from dataclasses import replace

        from apc_native_spark_audit import audit_event
        from p991a6_apc_campaign_verify import decoded

        inputs = next(read_stream("inputs"))
        source = GRC9V4SparkConfiguration.from_payload(inputs["source_configuration"])
        target = GRC9V4SparkConfiguration.from_payload(inputs["target_configuration"])
        report = verify(source, inputs["source_stage"])
        retained = inputs["source_error_in_target_chart"]
        self.assertTrue(all(v == retained[k] for k, v in report.items()))
        before = replace(source, current=decoded(inputs["source_stage"]).after)
        self.assertEqual(
            audit_event(before, target, inputs["event"]), inputs["event_audit"]
        )
        self.assertTrue(retained["old_edge_logW_error_retained"])
        self.assertEqual(retained["new_edge_conversion_error"], "0")
        self.assertEqual(
            retained["carrier_error_transport"],
            "0; entire target carrier explicitly reset",
        )
        self.assertTrue(
            all(
                x == "0"
                for state in inputs["initial_roles"].values()
                for row in state["Z_4"]
                for x in row
            )
        )
        self.assertNotEqual(
            inputs["initial_roles"]["current"]["W_A"],
            inputs["initial_roles"]["reset"]["W_A"],
        )

    def test_complete_independent_geometric_classifications(self):
        from pygrc.models.grc_v4_spark_carrier import exact_state

        inputs = next(read_stream("inputs"))
        config = GRC9V4SparkConfiguration.from_payload(inputs["target_configuration"])
        for i, role in enumerate(("current", "reset")):
            cert = CompletionCertificate.from_payload(inputs["certificates"][i])
            before = inputs["initial_roles"][role]
            gain, inside = [], []
            previous_restart = None
            for row in read_stream(role):
                data = expand(row["stage"], before, previous_restart)
                previous_restart = data["restart_read"]
                before = data["after"]
                state = exact_state(before)
                actual = classify_and_membership(state, config.policy, cert)
                self.assertEqual(actual, row["membership"])
                if actual["inside"]:
                    inside.append(row["beat"])
                if row["local_gain"]:
                    gain.append((row["beat"], row["local_gain"]))
            self.assertEqual(gain, [(377, 1)] if role == "current" else [])
            self.assertEqual(
                inside, [375, 376, 377] if role == "current" else [372, 373, 374]
            )

    def test_independent_actual_boundary_history_and_wrong_diagnostic_rejection(self):
        inputs = next(read_stream("inputs"))
        config = GRC9V4SparkConfiguration.from_payload(inputs["target_configuration"])
        for i, role in enumerate(("current", "reset")):
            cert = CompletionCertificate.from_payload(inputs["certificates"][i])
            primary = {r["beat"]: r for r in read_stream(role)}
            for row in read_stream("diagnostics"):
                if row["role"] != role:
                    continue
                audit = verify(config, row["stage"], cert, role)
                self.assertEqual(
                    audit, primary[row["beat"]]["independent_history_and_error_audit"]
                )
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
                surface.native_apc_campaign(ROOT)
        original_open = Path.open
        for name in [
            "src/pygrc/models/grc_v4_spark_apc.py",
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
                surface.native_apc_campaign(ROOT)

    def test_http_source_and_fixed_scope(self):
        spec = importlib.util.spec_from_file_location(
            "apc_campaign_server", TOOL / "scripts/serve_phase9.py"
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
            "/api/native-spark/a-pc/campaign",
            "/api/native-spark/a-pc/campaign/source",
            "/spark-native-apc-campaign.js",
            "/api/native-spark/a-pc/campaign?role=reset",
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
const {checkedNativeAPCCampaign,nativeAPCCampaignLoader}=await import('./phase9-web/spark-native-apc-campaign.js');
const view=JSON.parse(readFileSync(0,'utf8'));
assert.deepEqual(await checkedNativeAPCCampaign(view),view);
await assert.rejects(checkedNativeAPCCampaign({...view,native_completion_support:true}));
function element(){return {textContent:'',children:[],append(e){this.children.push(e)},replaceChildren(){this.children=[]}}}
const output=element(),status=element();let queue=[];
const load=nativeAPCCampaignLoader(output,status,()=>new Promise(r=>queue.push(r)),element);
const old=load(),fresh=load();queue[1]({ok:true,json:async()=>view});await fresh;
assert.match(status.textContent,/endpoint verified/);
assert.ok(output.children.some(e=>/375 → completion 377/.test(e.textContent)));
assert.ok(output.children.some(e=>e.href==='/api/native-spark/a-pc/campaign/source'));
const count=output.children.length;queue[0]({ok:false});await old;assert.equal(output.children.length,count);
await nativeAPCCampaignLoader(output,status,async()=>({ok:false}),element)();
assert.equal(output.children.length,0);
"""
        result = subprocess.run(
            [str(managed_node()), "--input-type=module", "-e", code],
            input=json.dumps(surface.native_apc_campaign(ROOT)),
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
            c for c in book["cells"] if c.get("id") == "spark-native-apc-campaign"
        )
        code = compile("".join(cell["source"]), "apc-campaign-notebook", "exec")
        ns = {"repo_root": ROOT}
        exec(code, ns)  # noqa: S102 - execute the repository notebook cell
        self.assertEqual(
            ns["native_apc_campaign_result"], surface.native_apc_campaign(ROOT)
        )
        with (
            patch.object(
                surface,
                "native_apc_campaign",
                side_effect=SourceAdmissionError("stale"),
            ),
            self.assertRaises(SourceAdmissionError),
        ):
            exec(code, ns)  # noqa: S102 - execute the repository notebook cell
        self.assertIsNone(ns["native_apc_campaign_result"])

"""Bounded design/authority/schema pressure; no native basin conformance."""

from copy import deepcopy
from io import BytesIO
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import jsonschema
import verify_p9101a_propagation as propagation

ROOT = propagation.ROOT
SIDE = ROOT / propagation.SIDE
TOOL = SIDE / "tool"
sys.path.insert(0, str(TOOL / "src"))
from grcv4_explorer import basin  # noqa: E402
from grcv4_explorer.canonical import record_digest  # noqa: E402
from grcv4_explorer.errors import SourceAdmissionError  # noqa: E402
from grcv4_explorer.forensic import contract_provenance  # noqa: E402
from grcv4_explorer.tooling import managed_node, tool_environment  # noqa: E402


class BasinAuthorityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old = basin.load_predecessor(ROOT, SIDE)
        cls.current = basin.load_basin_forensic_context(ROOT, SIDE)
        cls.view = basin.basin_authority(ROOT, SIDE)

    def test_scoped_authority_and_forward_debt_preserve_predecessors(self):
        self.assertEqual(len(self.current.nodes) - len(self.old.nodes), 11)
        for key, value in self.old.nodes.items():
            self.assertEqual(self.current.nodes[key], value)
        edges = {e["edge_id"]: e for e in self.current.propagation_edges}
        for e in self.old.propagation_edges:
            self.assertEqual(edges[e["edge_id"]], e)
        with self.assertRaises(KeyError):
            contract_provenance(self.old, basin.CONTRACT_IDS[0])
        for trace in self.view["contracts"]:
            row = trace["rows"][0]
            self.assertEqual(row["payload"]["support_disposition"], ["required"])
            self.assertTrue(row["edge_refs"])
            self.assertEqual(row["source_ref"]["record_id"], basin.RECORD_ID)
        debt = self.view["debt"]["rows"]
        self.assertEqual(debt[0]["payload"]["status"], "resolved_bounded_design")
        self.assertEqual(debt[1]["classification"], "forward_verification_routing")
        self.assertEqual(debt[1]["payload"]["status"], "pending_forward")
        for name in (
            "native_conformance",
            "P9_10_1a_closed",
            "full_GRC9V4_conformance",
        ):
            self.assertIs(self.view[name], False)

    def test_rehashed_authority_and_admission_drift_fail_closed(self):
        original = basin.load_json_object
        for defect in ("law", "native", "debt", "admission", "acceptance"):

            def altered(path):
                v = deepcopy(original(path))
                if path == ROOT / basin.SOURCE:
                    if defect == "law":
                        v["contracts"][1]["normative_equation_or_contract"] = (
                            "choose strongest edge"
                        )
                    if defect == "native":
                        v["runtime_conformance_inferred"] = True
                    if defect == "debt":
                        v["debt"]["remaining_work"] = []
                if path.name == basin.ADMISSION and defect == "admission":
                    v["graph_digest"] = "0" * 64
                if (
                    path.name == "P9-10.1a-DesignAcceptance.json"
                    and defect == "acceptance"
                ):
                    v["status"] = "proposed"
                if "record_digest" in v:
                    v["record_digest"] = record_digest(v, "record_digest")
                return v

            with (
                self.subTest(defect=defect),
                patch.object(basin, "load_json_object", altered),
            ):
                with self.assertRaises(SourceAdmissionError):
                    basin.load_basin_forensic_context(ROOT, SIDE)
        sha = basin.file_sha256
        with patch.object(
            basin,
            "file_sha256",
            side_effect=lambda p: (
                "0" * 64 if p.name.endswith("Proposal.md") else sha(p)
            ),
        ):
            with self.assertRaises(SourceAdmissionError):
                basin.load_basin_forensic_context(ROOT, SIDE)
        with self.assertRaises(KeyError):
            basin.basin_source(ROOT, SIDE, "../outside")

    def test_paper_spec_transfer_and_unrelated_edit_rejection(self):
        self.assertEqual(propagation.check()["status"], "passed_design_propagation")
        from p994b_runtime_successor import SOURCES, historical_source

        # Historical execution retains its exact original document/checker
        # subjects. The compatibility reader is not an arbitrary-edit exemption.
        for name, row in SOURCES.items():
            if set(row["predecessors"].values()) != {"1275bd1f"}:
                continue
            expected = next(iter(row["predecessors"]))
            self.assertEqual(historical_source(ROOT, name, expected), expected)
            raw_reader = Path.read_bytes
            with patch.object(
                Path,
                "read_bytes",
                lambda p: (
                    raw_reader(p) + b"\nunauthorized change\n"
                    if p == ROOT / name
                    else raw_reader(p)
                ),
            ):
                self.assertIsNone(historical_source(ROOT, name, expected))
        original = Path.read_bytes
        target = ROOT / propagation.DOCUMENTS[1]
        for addition in (
            b"\nUnreviewed mathematical assertion.\n",
            b"\n### A.5.1 repeated\n",
        ):
            with patch.object(
                Path,
                "read_bytes",
                lambda p: original(p) + addition if p == target else original(p),
            ):
                with self.assertRaises(ValueError):
                    propagation.predecessor_document_bytes(
                        ROOT, propagation.DOCUMENTS[1]
                    )

    def test_closed_schema_and_explicit_snapshot_modes(self):
        schema = json.loads(
            (ROOT / "specs/grc-9-v4-basin-interface-schema.json").read_bytes()
        )
        validator = jsonschema.Draft202012Validator(schema)
        state_only = dict(
            schema_version="grc9v4-basin-checkpoint-extension-v1",
            policy_id=basin.POLICY_ID,
            replay_mode="state_only",
            current_observation=None,
            reset_observation=None,
        )
        validator.validate(state_only)
        for edit in (
            {"replay_mode": "exact_observation"},
            {"fallback": "state_only"},
            {"policy_id": "other"},
        ):
            self.assertTrue(list(validator.iter_errors({**state_only, **edit})))
        node = jsonschema.Draft202012Validator(
            {"$ref": "#/$defs/node_id", "$defs": schema["$defs"]}
        )
        for value in (
            {"kind": "int", "value": 0},
            {"kind": "str", "value": "0"},
            {"kind": "str", "value": ""},
        ):
            node.validate(value)
        for value in (
            {"kind": "int", "value": True},
            {"kind": "int", "value": 2**53},
            {"kind": "str", "value": 0},
        ):
            self.assertTrue(list(node.iter_errors(value)))
        number = jsonschema.Draft202012Validator(schema["$defs"]["binary64"])
        for x in (0.0, -0.0, 5e-324, -5e-324, 1.0, 1e200):
            number.validate(x.hex())
        for bad in ("nan", "inf", "1.0", 1.0):
            self.assertTrue(list(number.iter_errors(bad)))

    def test_actual_notebook_and_http_projection_and_failure(self):
        book = json.loads((TOOL / "notebooks/phase9_verification.ipynb").read_bytes())
        cell = next(c for c in book["cells"] if c.get("id") == "basin-authority")
        ns = {"repo_root": ROOT}
        code = compile("".join(cell["source"]), "basin-authority-cell", "exec")
        exec(code, ns)
        self.assertEqual(ns["phase9_basin_authority"], self.view)
        with patch.object(
            basin, "basin_authority", side_effect=SourceAdmissionError("held")
        ):
            with self.assertRaises(SourceAdmissionError):
                exec(code, ns)
        self.assertIsNone(ns["phase9_basin_authority"])
        spec = importlib.util.spec_from_file_location(
            "basin_server", TOOL / "scripts/serve_phase9.py"
        )
        server = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(server)
        handler = server.Handler.__new__(server.Handler)
        codes = []
        handler.send_response = codes.append
        handler.send_header = lambda *args: None
        handler.end_headers = lambda: None
        handler.path = "/api/basin"
        handler.wfile = BytesIO()
        handler.do_GET()
        self.assertEqual(codes, [200])
        self.assertEqual(json.loads(handler.wfile.getvalue()), self.view)
        handler.wfile = BytesIO()
        with patch.object(
            server, "basin_authority", side_effect=SourceAdmissionError("held")
        ):
            handler.do_GET()
        self.assertEqual(codes[-1], 503)
        self.assertEqual(set(json.loads(handler.wfile.getvalue())), {"error"})

    def test_browser_scope_and_stale_output_clearing(self):
        js = """
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {checkedBasin,basinLoader,canonicalBasin} from './basin.js';
const value=JSON.parse(readFileSync(0,'utf8'));
assert.deepEqual(await checkedBasin(value),value);
for(const edit of [v=>v.native_conformance=true,v=>v.P9_10_1a_closed=true,
 v=>v.selected_native_scope.push('A_OS'),v=>v.contracts.pop(),v=>v.debt.rows.pop()]) {
 const bad=structuredClone(value);edit(bad);delete bad.projection_digest;
 bad.projection_digest=createHash('sha256').update(canonicalBasin(bad)).digest('hex');
 await assert.rejects(checkedBasin(bad));
}
const forged=structuredClone(value);
forged.contracts[0].rows[0].payload.invented_native_support=true;
delete forged.contracts[0].trace_digest;
forged.contracts[0].trace_digest=createHash('sha256').update(canonicalBasin(forged.contracts[0])).digest('hex');
delete forged.projection_digest;
forged.projection_digest=createHash('sha256').update(canonicalBasin(forged)).digest('hex');
await assert.rejects(checkedBasin(forged));
const output={children:[],replaceChildren(){this.children=[]},append(e){this.children.push(e)}},status={};
let ok=true;
const load=basinLoader(output,status,async()=>({ok,json:async()=>value}),tag=>({tag}));
await load();assert.ok(output.children.length>10);assert.match(status.textContent,/inspect native acceptance/);
ok=false;await load();assert.equal(output.children.length,0);assert.match(status.textContent,/unavailable/);
assert.match(readFileSync('index.html','utf8'),/id="basin-refresh"/);
console.log('BASIN_BROWSER_PASS');
"""
        run = subprocess.run(
            [str(managed_node()), "--input-type=module", "-e", js],
            cwd=TOOL / "phase9-web",
            input=json.dumps(self.view),
            text=True,
            capture_output=True,
            timeout=30,
            env=tool_environment(),
        )
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(run.stdout.strip(), "BASIN_BROWSER_PASS")


if __name__ == "__main__":
    unittest.main()

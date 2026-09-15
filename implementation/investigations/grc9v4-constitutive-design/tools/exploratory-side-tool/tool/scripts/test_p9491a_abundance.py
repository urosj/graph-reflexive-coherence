"""Focused accepted-source/UX controls; no numeric abundance or G2 inference."""

from copy import deepcopy
import importlib.util
from io import BytesIO
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

TOOL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL / "src"))
from grcv4_explorer import abundance as api  # noqa: E402
from grcv4_explorer import a_initializer  # noqa: E402
from grcv4_explorer.canonical import record_digest  # noqa: E402
from grcv4_explorer.errors import SourceAdmissionError  # noqa: E402
from grcv4_explorer.forensic import contract_provenance  # noqa: E402
from grcv4_explorer.paths import repository_root  # noqa: E402
from grcv4_explorer.receipt_parents import load_parent_forensic_context  # noqa: E402
from grcv4_explorer.tooling import managed_node, tool_environment  # noqa: E402


class AbundanceAuthorityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = repository_root()
        cls.old = load_parent_forensic_context(cls.root, TOOL.parent)
        cls.current = api.load_current_forensic_context(cls.root, TOOL.parent)

    def test_append_only_graph_and_typed_source_boundary(self):
        self.assertEqual(len(self.current.nodes) - len(self.old.nodes), 13)
        for name, node in self.old.nodes.items():
            self.assertEqual(self.current.nodes[name], node)
        edges = {e["edge_id"]: e for e in self.current.propagation_edges}
        for edge in self.old.propagation_edges:
            self.assertEqual(edges[edge["edge_id"]], edge)
        for identifier in api.CONTRACT_IDS:
            trace = contract_provenance(self.current, identifier)
            self.assertEqual(trace["trace_digest"], record_digest(trace, "trace_digest"))
            row = trace["rows"][0]
            self.assertEqual(row["payload"]["support_disposition"], ["required"])
            self.assertEqual(row["source_ref"]["record_id"], api.RECORD_ID)
            self.assertTrue(row["edge_refs"])
            with self.assertRaises(KeyError):
                contract_provenance(self.old, identifier)

    def test_source_propagation_and_legacy_immutability(self):
        sections = []
        for name in ("GRCV4-proposal.md", "2026-09-GRC-V4.md"):
            text = (TOOL.parent.parents[1] / "drafts" / name).read_text()
            sections.append(text.split("#### 14.2.1 ", 1)[1].split("### 14.3 ", 1)[0])
        self.assertEqual(*sections)
        for identifier in (*api.CONTRACT_IDS, api.CLAIM_ID, api.POLICY_ID):
            self.assertIn(identifier, sections[0])
        ext = (self.root / "specs/grc-common-interface-v4-ext.md").read_text()
        for identifier in (*api.CONTRACT_IDS, api.POLICY_ID, "observed_state_digest"):
            self.assertIn(identifier, ext)
        for name in ("specs/grc-common-interface.md", "specs/grc-v3-spec.md", "specs/grc-9-v3-spec.md"):
            before = subprocess.check_output(["git", "show", "7905e7e:" + name], cwd=self.root)
            self.assertEqual((self.root / name).read_bytes(), before)
        value = api.load_json_object(self.root / api.SOURCE)
        self.assertEqual(value["contracts"][0]["admitted_numeric_definitions"], [])
        release = api.load_json_object(self.root / "specs/grc-v4-specification-release.json")
        self.assertEqual(release["accepted_abundance_authority"]["record_digest"], api.ACCEPTED_SOURCE_DIGEST)

    def test_mutated_missing_or_unprocessed_authority_fails_closed(self):
        original = api.load_json_object
        for defect in ("rule", "status", "G2", "admission", "missing"):
            def changed(path):
                value = deepcopy(original(path))
                if path.name == Path(api.SOURCE).name:
                    if defect == "rule":
                        value["contracts"][0]["admitted_numeric_definitions"] = ["invented"]
                    if defect == "status":
                        value["status"] = "proposed"
                    if defect == "G2":
                        value["G2_accepted"] = True
                    value["record_digest"] = record_digest(value, "record_digest")
                if path.name == api.ADMISSION:
                    if defect == "missing":
                        raise FileNotFoundError(api.ADMISSION)
                    if defect == "admission":
                        value["graph_digest"] = "0" * 64
                    value["record_digest"] = record_digest(value, "record_digest")
                return value
            with self.subTest(defect=defect), patch.object(api, "load_json_object", side_effect=changed):
                with self.assertRaises((SourceAdmissionError, FileNotFoundError)):
                    api.load_current_forensic_context(self.root, TOOL.parent)
        with patch.object(a_initializer, "discover_sources", return_value={"state": "new_unprocessed_source_available"}):
            with self.assertRaisesRegex(SourceAdmissionError, "not exact"):
                api.load_current_forensic_context(self.root, TOOL.parent)

    def test_actual_notebook_and_http_handler_match_api_and_fail_closed(self):
        notebook = json.loads((TOOL / "notebooks/phase9_verification.ipynb").read_text())
        cell = next(c for c in notebook["cells"] if c["id"] == "abundance-authority")
        namespace = {"Path": Path, "repo_root": self.root, "side_tool_root": TOOL.parent,
                     "PHASE9_REPO_ROOT": self.root}
        code = compile("".join(cell["source"]), "phase9_verification.ipynb:abundance-authority", "exec")
        exec(code, namespace)
        expected = api.abundance_authority(self.root, TOOL.parent)
        self.assertEqual(namespace["phase9_abundance_authority"], expected)
        with patch.object(api, "abundance_authority", side_effect=SourceAdmissionError("held")):
            with self.assertRaises(SourceAdmissionError):
                exec(code, namespace)
        self.assertIsNone(namespace["phase9_abundance_authority"])
        spec = importlib.util.spec_from_file_location("p9491a_http", TOOL / "scripts/serve_phase9.py")
        server = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(server)
        # Execute the real handler without a network server/browser campaign.
        handler = server.Handler.__new__(server.Handler)
        handler.path = "/api/abundance"
        statuses = []
        handler.send_response = statuses.append
        handler.send_header = lambda *args: None
        handler.end_headers = lambda: None
        handler.wfile = BytesIO()
        handler.do_GET()
        self.assertEqual(statuses, [200])
        self.assertEqual(json.loads(handler.wfile.getvalue()), expected)
        handler.wfile = BytesIO()
        with patch.object(server, "abundance_authority", side_effect=SourceAdmissionError("held")):
            handler.do_GET()
        self.assertEqual(statuses, [200, 503])
        self.assertEqual(set(json.loads(handler.wfile.getvalue())), {"error"})

    def test_actual_browser_validator_matches_api_and_rejects_overclaims(self):
        payload = api.abundance_authority(self.root, TOOL.parent)
        code = """
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {canonical, verifiedAbundance} from './verification.js';
const value = JSON.parse(readFileSync(0, 'utf8'));
assert.deepEqual(await verifiedAbundance(value), value);
for (const edit of [{G2_accepted:true}, {numeric_definition_admitted:true},
 {runtime_conformance_inferred:true}, {authority_extension_digest:'0'.repeat(64)}]) {
 const bad = {...value, ...edit}; delete bad.projection_digest;
 bad.projection_digest=createHash('sha256').update(canonical(bad)).digest('hex');
 await assert.rejects(verifiedAbundance(bad));
}
const stale = structuredClone(value); stale.claim.rows[0].classification='invented';
await assert.rejects(verifiedAbundance(stale));
console.log('P9491A_BROWSER_VALIDATOR_PASS');
"""
        result = subprocess.run([str(managed_node()), "--input-type=module", "-e", code],
                                cwd=TOOL / "phase9-web", input=json.dumps(payload),
                                capture_output=True, text=True, env=tool_environment())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "P9491A_BROWSER_VALIDATOR_PASS")


if __name__ == "__main__":
    unittest.main()

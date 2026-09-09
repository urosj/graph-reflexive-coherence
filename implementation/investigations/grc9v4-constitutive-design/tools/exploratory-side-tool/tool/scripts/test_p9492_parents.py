"""Read-only P9 parent graph, forensic API and executable notebook pressure."""

from copy import deepcopy
import ast
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

TOOL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL / "src"))
from grcv4_explorer import receipt_parents as api  # noqa: E402
from grcv4_explorer.canonical import record_digest  # noqa: E402
from grcv4_explorer.errors import SourceAdmissionError  # noqa: E402
from grcv4_explorer.forensic import contract_provenance  # noqa: E402
from grcv4_explorer.paths import repository_root  # noqa: E402
from grcv4_explorer.successor import load_successor_forensic_context  # noqa: E402


class ParentAuthorityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = repository_root()
        cls.side = TOOL.parent
        cls.old = load_successor_forensic_context(cls.root, cls.side)
        cls.current = api.load_current_forensic_context(cls.root, cls.side)

    def test_append_only_graph_and_exact_typed_authority(self):
        for name, node in self.old.nodes.items():
            self.assertEqual(self.current.nodes[name], node)
        current_edges = {e["edge_id"]: e for e in self.current.propagation_edges}
        for edge in self.old.propagation_edges:
            self.assertEqual(current_edges[edge["edge_id"]], edge)
        self.assertEqual(len(self.current.nodes) - len(self.old.nodes), 7)
        for identifier in api.CONTRACT_IDS:
            trace = contract_provenance(self.current, identifier)
            self.assertEqual(
                trace["trace_digest"], record_digest(trace, "trace_digest")
            )
            row = trace["rows"][0]
            self.assertEqual(row["payload"]["support_disposition"], ["required"])
            self.assertEqual(row["source_ref"]["record_id"], api.RECORD_ID)
            self.assertTrue(row["edge_refs"])
            with self.assertRaises(KeyError):
                contract_provenance(self.old, identifier)
        self.assertEqual(
            self.current.nodes["current_claim:" + api.CLAIM_ID]["attributes"][
                "claim_class"
            ],
            "normative",
        )

    def test_proposal_paper_specs_and_runtime_declare_the_same_policy(self):
        drafts = self.side.parents[1] / "drafts"
        start = "#### 12.5.1 Successful-commit receipt parents"
        end = "### 12.6 Graph-generic Candidate A history-free initializer"
        sections = []
        for name in ("GRCV4-proposal.md", "2026-09-GRC-V4.md"):
            text = (drafts / name).read_text()
            self.assertEqual(text.count(start), 1)
            sections.append(text.split(start, 1)[1].split(end, 1)[0])
        self.assertEqual(*sections)
        for identifier in (*api.CONTRACT_IDS, api.CLAIM_ID, api.POLICY_ID):
            self.assertIn(identifier, sections[0])
        spec = (self.root / "specs/grc-common-interface-v4-ext.md").read_text()
        for identifier in (*api.CONTRACT_IDS, api.POLICY_ID, "pygrc-c-os-snapshot-v3"):
            self.assertIn(identifier, spec)
        codec = ast.parse((self.root / "src/pygrc/models/grc_v4_codec.py").read_text())
        constants = {
            target.id: ast.literal_eval(node.value)
            for node in codec.body
            if isinstance(node, ast.Assign)
            for target in node.targets
            if isinstance(target, ast.Name)
            and target.id
            in {"RECEIPT_PARENT_POLICY_ID", "COS_SNAPSHOT_LAYOUT_ID", "RELEASE_ID"}
        }
        self.assertEqual(constants["RECEIPT_PARENT_POLICY_ID"], api.POLICY_ID)
        self.assertEqual(constants["COS_SNAPSHOT_LAYOUT_ID"], "pygrc-c-os-snapshot-v3")
        release = json.loads(
            (self.root / "specs/grc-v4-specification-release.json").read_text()
        )
        self.assertEqual(release["release_id"], constants["RELEASE_ID"])
        self.assertEqual(
            release["accepted_parent_authority"]["record_digest"],
            api.ACCEPTED_SOURCE_DIGEST,
        )

    def test_rehashed_source_or_admission_cannot_self_authorize(self):
        original = api.load_json_object
        for defect in ("status", "rule", "G2", "admission", "missing"):

            def altered(path):
                value = deepcopy(original(path))
                if path.name == Path(api.SOURCE).name:
                    if defect == "status":
                        value["status"] = "proposed"
                    elif defect == "rule":
                        value["contracts"][0]["normative_equation_or_contract"] = (
                            "all parents allowed"
                        )
                    elif defect == "G2":
                        value["G2_accepted"] = True
                    value["record_digest"] = record_digest(value, "record_digest")
                elif path.name == api.ADMISSION:
                    if defect == "admission":
                        value["graph_digest"] = "0" * 64
                    elif defect == "missing":
                        raise FileNotFoundError(api.ADMISSION)
                    value["record_digest"] = record_digest(value, "record_digest")
                return value

            with (
                self.subTest(defect=defect),
                patch.object(api, "load_json_object", side_effect=altered),
            ):
                with self.assertRaises((SourceAdmissionError, FileNotFoundError)):
                    api.load_current_forensic_context(self.root, self.side)

    def test_unknown_source_holds_current_but_does_not_become_accepted(self):
        with patch.object(
            api,
            "discover_sources",
            return_value={"state": "new_unprocessed_source_available"},
        ):
            with self.assertRaisesRegex(SourceAdmissionError, "not exact"):
                api.load_current_forensic_context(self.root, self.side)

    def test_actual_notebook_cell_matches_api_and_clears_stale_result(self):
        notebook = json.loads(
            (TOOL / "notebooks/phase9_verification.ipynb").read_text()
        )
        cell = next(
            c for c in notebook["cells"] if c["id"] == "receipt-parent-authority"
        )
        namespace = {"Path": Path, "repo_root": self.root}
        code = compile(
            "".join(cell["source"]),
            "phase9_verification.ipynb:receipt-parent-authority",
            "exec",
        )
        exec(code, namespace)
        self.assertEqual(
            namespace["phase9_parent_authority"],
            api.parent_authority(self.root, self.side),
        )
        with patch.object(
            api, "parent_authority", side_effect=SourceAdmissionError("held")
        ):
            with self.assertRaises(SourceAdmissionError):
                exec(code, namespace)
        self.assertIsNone(namespace["phase9_parent_authority"])


if __name__ == "__main__":
    unittest.main()

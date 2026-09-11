"""Focused proposal/paper/release separation; no model or numerical campaign."""

from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import verify_p972a_proposal as v

sys.path.insert(0, str(v.p.ROOT / v.p.SIDE / "tool/src"))


class ProposalReviewTests(unittest.TestCase):
    def override(self, name, content):
        original = Path.read_bytes
        target = v.p.ROOT / name
        return patch.object(Path, "read_bytes",
                            lambda path: content if path == target else original(path))

    def test_accepted_documents_are_not_a_new_release_or_spec_acceptance(self):
        stage = v.proposal_status()
        release = v.verify_release()
        self.assertNotEqual(stage["proposal_sha256"], release["released_proposal_sha256"])
        self.assertEqual(stage["proposal_status"], "accepted")
        self.assertTrue(stage["proposal_revision_accepted"])
        self.assertTrue(stage["paper_propagated"])
        self.assertEqual(stage["paper_status"], "accepted")
        self.assertTrue(stage["paper_revision_accepted"])
        self.assertEqual(stage["exact_transferred_sections"], 6)
        self.assertNotEqual(stage["paper_sha256"], release["released_paper_sha256"])
        self.assertTrue(stage["specification_propagated"])
        self.assertEqual(stage["specification_status"], "accepted")
        self.assertTrue(stage["specification_revision_accepted"])
        self.assertFalse(stage["executable_successor_released"])
        self.assertFalse(release["release_regenerated"])
        self.assertFalse(release["runtime_support_changed"])
        self.assertEqual(release["release_id"], v.p.ABUNDANCE_RELEASE_ID)

    def test_proposal_drift_and_coherently_rehashed_authority_reject(self):
        with self.override(v.PROPOSAL, (v.p.ROOT / v.PROPOSAL).read_bytes() + b"\nC-to-A complete.\n"):
            with self.assertRaisesRegex(ValueError, "proposal candidate drift"):
                v.proposal_status()
        from grcv4_explorer.a_initializer import initializer_authority
        from grcv4_explorer.canonical import record_digest
        value = deepcopy(initializer_authority(v.p.ROOT, v.p.ROOT / v.p.SIDE))
        value["positive_migration_verified"] = True
        value["projection_digest"] = record_digest(value, "projection_digest")
        with patch("grcv4_explorer.a_initializer.initializer_authority", return_value=value):
            with self.assertRaisesRegex(ValueError, "authority drift"):
                v.proposal_status()

    def test_specs_source_and_old_generator_are_not_draft_exemptions(self):
        for name in ("specs/grc-9-v4-spec.md", "specs/grc-v4-contract-schema.json", v.SOURCE_MANIFEST,
                     v.p.ABUNDANCE_AUTHORITY, v.p.ABUNDANCE_RELEASE_BUILDER):
            with self.subTest(path=name), self.override(name, (v.p.ROOT / name).read_bytes() + b"\n"):
                with self.assertRaisesRegex(ValueError, "released source/member changed"):
                    v.verify_release()

    def test_release_rehash_package_and_codec_changes_reject(self):
        value = json.loads((v.p.ROOT / v.RELEASE).read_bytes())
        value["release_identity_payload"]["initializer_implemented"] = True
        value["release_id"] = "grcv4-spec-release-sha256:" + v.p.sha(v.canonical(value["release_identity_payload"]))
        with self.override(v.RELEASE, json.dumps(value).encode()):
            with self.assertRaisesRegex(ValueError, "executable release changed"):
                v.verify_release()
        for name in (v.CHECKSUM, v.ASSETS + "asset-index.json",
                     v.ASSETS + "grc-v4-specification-release.json",
                     v.ASSETS + "grc-v4-contract-schema.json"):
            with self.subTest(path=name), self.override(name, b"{}\n"):
                with self.assertRaises(ValueError):
                    v.verify_release()
        original = Path.read_text
        target = v.p.ROOT / v.CODEC
        def altered(path, *args, **kwargs):
            result = original(path, *args, **kwargs)
            return result.replace(v.p.ABUNDANCE_RELEASE_ID.split(":")[1], "wrong-release") if path == target else result
        with patch.object(Path, "read_text", altered):
            with self.assertRaisesRegex(ValueError, "codec release pins changed"):
                v.verify_release()

    def test_missing_or_changed_historical_documents_cannot_use_new_bytes(self):
        original = v.historical_blobs
        for target in (v.PROPOSAL, v.PAPER, *sorted(v.SPECIFICATION_REVIEW_PATHS)):
            def altered(names, commit):
                result = original(names, commit)
                if target in result:
                    result[target] = (v.p.ROOT / target).read_bytes()
                return result
            with self.subTest(target=target), patch.object(v, "historical_blobs", side_effect=altered):
                with self.assertRaisesRegex(ValueError, "released source/member changed"):
                    v.verify_release()
        with patch.object(v, "historical_blobs", side_effect=ValueError("missing historical source")):
            with self.assertRaisesRegex(ValueError, "missing historical source"):
                v.verify_release()

    def test_paper_drift_and_wrong_proposal_acceptance_subject_reject(self):
        with self.override(v.PAPER, (v.p.ROOT / v.PAPER).read_bytes() + b"\nC-to-A complete.\n"):
            with self.assertRaisesRegex(ValueError, "paper candidate drift"):
                v.proposal_status()
        original = v.historical_blobs
        def changed(names, commit):
            result = original(names, commit)
            if commit == v.PROPOSAL_COMMIT:
                result[v.PROPOSAL] += b"\n"
            return result
        with patch.object(v, "historical_blobs", side_effect=changed):
            with self.assertRaisesRegex(ValueError, "accepted proposal subject changed"):
                v.proposal_status()

    def test_spec_candidates_have_no_free_current_tree_exemption(self):
        for name in v.SPECIFICATION_BINDINGS:
            with self.subTest(name=name), self.override(name, (v.p.ROOT / name).read_bytes() + b"\n"):
                with self.assertRaisesRegex(ValueError, "specification candidate drift"):
                    v.verify_release()
        original = v.historical_blobs
        def changed(names, commit):
            result = original(names, commit)
            if commit == v.PAPER_COMMIT:
                result[v.PAPER] += b"\n"
            return result
        with patch.object(v, "historical_blobs", side_effect=changed):
            with self.assertRaisesRegex(ValueError, "accepted paper subject changed"):
                v.proposal_status()

    def test_copied_equation_staging_and_claim_ceiling_are_not_hash_only(self):
        proposal = (v.p.ROOT / v.PROPOSAL).read_text()
        paper = (v.p.ROOT / v.PAPER).read_text()
        for before, after in (
            ("Exactly one pass is selected", "Two passes are selected"),
            ("\\gamma}{2}J_{\\mathrm{ref},e}^{2}", "\\gamma}{3}J_{\\mathrm{ref},e}^{2}"),
            ("Specification binding, implementation and positive C→A through all five A",
             "Verified implementation and positive C→A through all five A"),
            ("Keep target PC/CI/RG2b charts fixed", "Adjust target PC/CI/RG2b charts to the output"),
        ):
            self.assertTrue(before in paper, "missing mutation target: " + before)
            with self.subTest(before=before), self.assertRaisesRegex(ValueError, "transfer drift"):
                v.check_transferred_sections(proposal, paper.replace(before, after))


if __name__ == "__main__":
    unittest.main()

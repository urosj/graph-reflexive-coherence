"""Small retrieval/identity checks; no scientific or runtime reruns."""

from copy import deepcopy
import io
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import zipfile

import handoff_evidence as evidence


class HandoffEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = json.loads(evidence.MANIFEST.read_bytes())
        cls.archive = (
            evidence.MANIFEST.parent / cls.original["archive"]["file"]
        ).read_bytes()

    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory(prefix="p9-handoff-test-")
        self.addCleanup(self.scratch.cleanup)
        self.root = Path(self.scratch.name)
        self.manifest = self.root / "manifest.json"
        self.value = deepcopy(self.original)
        self.archive_path = self.root / self.value["archive"]["file"]
        self.archive_path.write_bytes(self.archive)
        self.save()

    def save(self):
        self.manifest.write_text(json.dumps(self.value))

    def test_fresh_clone_without_generated_outputs(self):
        clone = self.root / "repository"
        subprocess.run(
            [
                "git",
                "clone",
                "--quiet",
                "--no-checkout",
                "--no-local",
                str(evidence.HERE.parents[2]),
                str(clone),
            ],
            check=True,
        )
        handoff = clone / "handoff"
        handoff.mkdir()
        for path in [self.manifest, self.archive_path]:
            shutil.copyfile(path, handoff / path.name)
        before = (self.manifest.read_bytes(), self.archive_path.read_bytes())
        result = evidence.verify(handoff / self.manifest.name, clone)
        self.assertEqual(result["subjects"], 3)
        self.assertFalse(result["new_acceptance"])
        self.assertFalse(result["original_bytes_verified"])
        self.assertFalse((clone / ".git/objects/info/alternates").exists())
        self.assertFalse((clone / "implementation").exists())
        self.assertEqual(
            before, (self.manifest.read_bytes(), self.archive_path.read_bytes())
        )

    def test_missing_bundle(self):
        self.archive_path.unlink()
        with self.assertRaises(FileNotFoundError):
            evidence.verify(self.manifest)

    def test_corrupt_bundle(self):
        self.archive_path.write_bytes(self.archive[:-1] + b"!")
        with self.assertRaisesRegex(ValueError, "archive binding mismatch"):
            evidence.verify(self.manifest)

    def test_wrong_member_digest(self):
        self.value["artifacts"][0]["sha256"] = "0" * 64
        self.save()
        with self.assertRaisesRegex(ValueError, "evidence hash mismatch"):
            evidence.verify(self.manifest)

    def test_undeclared_archive_member(self):
        self.value["artifacts"].pop()
        self.save()
        with self.assertRaisesRegex(ValueError, "member roster drift"):
            evidence.verify(self.manifest)

    def test_rerun_cannot_replace_original_identity(self):
        # A later replay has the same code/tree, but different original bytes.
        original, _, replay = self.value["subjects"]
        self.assertEqual(original["tree"], replay["tree"])
        original["receipt"] = replay["receipt"]
        self.save()
        with self.assertRaisesRegex(ValueError, "historical receipt identity mismatch"):
            evidence.verify(self.manifest)

    def test_wrong_historical_input(self):
        self.value["input_bindings"][0]["sha256"] = "0" * 64
        self.save()
        with self.assertRaisesRegex(ValueError, "historical input tree mismatch"):
            evidence.verify(self.manifest)

    def test_rehashed_manifest_cannot_replace_the_published_identity(self):
        self.value["acceptance_digest"] = "0" * 64
        self.save()
        with self.assertRaisesRegex(ValueError, "manifest identity mismatch"):
            evidence.verify(self.manifest)

    def test_availability_and_integrity_are_distinct(self):
        self.archive_path.unlink()
        self.assertEqual(evidence.status(None, self.manifest)["status"], "unavailable")
        self.archive_path.write_bytes(b"invalid archive")
        self.assertEqual(evidence.status(None, self.manifest)["status"], "invalid")
        self.archive_path.write_bytes(self.archive)
        self.assertEqual(evidence.status(None, self.manifest)["status"], "verified")

    def test_only_selected_supporting_runs_are_published(self):
        with zipfile.ZipFile(io.BytesIO(self.archive)) as bundle:
            self.assertFalse(any(n.startswith("runs/") for n in bundle.namelist()))
            for subject in self.original["subjects"]:
                report = json.loads(bundle.read(subject["pressure_report"]))
                self.assertEqual(report.get("failed", 0), 0)
        self.assertTrue(
            any("overwritten" in limit for limit in self.original["limits"])
        )

    def test_original_hashes_remain_citable_not_normalized_checksums(self):
        self.assertEqual(
            self.original["archive"]["original_sha256"],
            "089185f8251dbf888d23fcaf67df712f17755ab69ed2ea1ecb3f0749df04b8af",
        )
        self.assertNotEqual(
            self.original["archive"]["sha256"],
            self.original["archive"]["original_sha256"],
        )
        with zipfile.ZipFile(io.BytesIO(self.archive)) as bundle:
            for subject in self.original["subjects"]:
                receipt = json.loads(bundle.read(subject["receipt"]))
                self.assertEqual(receipt["receipt_digest"], subject["receipt_digest"])
                self.assertEqual(
                    evidence.digest(receipt, "receipt_digest"),
                    subject["normalized_receipt_digest"],
                )
                self.assertNotEqual(
                    subject["receipt_digest"], subject["normalized_receipt_digest"]
                )

    def test_no_machine_local_paths_in_published_text(self):
        with zipfile.ZipFile(io.BytesIO(self.archive)) as bundle:
            for name in bundle.namelist():
                content = bundle.read(name)
                self.assertEqual(evidence.normalize_member(content), content, name)

    def test_normalization_preserves_values_and_distinct_fixture_roots(self):
        original = {
            "command": "/home/example/a checkout/graph-reflexive-coherence/.venv/bin/python",
            "fixtures": ["/tmp/probe-one/repository", "/tmp/probe-two/repository"],
            "run_id": "original-run-123",
            "value": 1.2345,
            "passed": 106,
            "failed": 0,
            "receipt_digest": "a" * 64,
        }
        normalized = json.loads(
            evidence.normalize_member(json.dumps(original).encode())
        )
        self.assertEqual(normalized.pop("command"), "<checkout>/.venv/bin/python")
        self.assertEqual(
            normalized.pop("fixtures"),
            ["<temporary>/probe-one/repository", "<temporary>/probe-two/repository"],
        )
        self.assertEqual(
            normalized,
            {k: v for k, v in original.items() if k not in {"command", "fixtures"}},
        )

    def test_wrong_normalized_digest(self):
        self.value["subjects"][0]["normalized_receipt_digest"] = "0" * 64
        self.save()
        with self.assertRaisesRegex(ValueError, "normalized execution digest mismatch"):
            evidence.verify(self.manifest)

    def test_input_locations_do_not_depend_on_parent_directory_names(self):
        for parent in ["incoming", "review files/nested", "elsewhere"]:
            for filename, target in [
                ("pasted-text.txt", evidence.REVIEW_INPUT),
                (Path(evidence.AUDIT_INPUT).name, evidence.AUDIT_INPUT),
            ]:
                self.assertEqual(
                    evidence.normalize_text(f"/home/example/{parent}/{filename}"),
                    target,
                )
        self.assertEqual(
            evidence.normalize_text("/home/example/incoming/unrelated.md"),
            "<user-home>/incoming/unrelated.md",
        )

    def test_descriptive_location_cleanup_preserves_the_claim(self):
        original = (
            "dependency on a particular user's local-inputs directory; the input remains\n"
            "external engineering evidence, not newly accepted scientific authority.\n"
        )
        self.assertEqual(
            evidence.normalize_text(original),
            "dependency on machine-local input locations; the input remains\n"
            "external engineering evidence, not newly accepted scientific authority.\n",
        )

    def test_original_archive_is_not_claimed_without_original_bytes(self):
        with self.assertRaisesRegex(ValueError, "original archive binding mismatch"):
            evidence.verify(self.manifest, original_archive=self.archive_path)

    def test_snapshot_keeps_original_and_normalized_hashes_separate(self):
        raw = json.dumps(
            {
                "snapshot_digest": "b" * 64,
                "files": [
                    {
                        "path": "plan.md",
                        "utf8": "/tmp/probe/plan.md",
                        "sha256": "c" * 64,
                    }
                ],
            }
        ).encode()
        result = evidence.normalized_snapshot(raw)
        self.assertEqual(result["snapshot_digest"], "b" * 64)
        self.assertEqual(result["normalization"]["original_sha256"], evidence.sha(raw))
        self.assertEqual(result["files"][0]["sha256"], "c" * 64)
        self.assertEqual(
            result["files"][0]["normalized_sha256"],
            evidence.sha(b"<temporary>/probe/plan.md"),
        )


if __name__ == "__main__":
    unittest.main()

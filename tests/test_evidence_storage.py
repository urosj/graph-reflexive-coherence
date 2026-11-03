"""Pressure lossless storage, failure-closed restoration and the Git size gate."""

import importlib.util
import bz2
import gzip
import io
import json
import lzma
import os
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location(
    "evidence_storage", Path(__file__).resolve().parents[1] / "scripts/evidence_storage.py"
)
storage = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(storage)


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.limit = patch.object(storage, "LIMIT", 256)
        self.limit.start()
        self.addCleanup(self.limit.stop)
        self.raw = b'{"values":[' + b"0," * 512 + b"0]}\n"
        self.packed = lzma.compress(self.raw)
        self.row = {
            "path": "data/result.json", "size": len(self.raw),
            "sha256": storage.sha(self.raw), "storage_path": "data/result.json.xz",
            "storage_size": len(self.packed), "storage_sha256": storage.sha(self.packed),
        }
        (self.root / "data").mkdir()
        (self.root / self.row["storage_path"]).write_bytes(self.packed)
        self.manifest = {"schema": "exact-evidence-storage-v2",
                         "compression_threshold_bytes": 256, "files": [self.row]}
        self.save()

    def save(self):
        (self.root / storage.MANIFEST).write_text(json.dumps(self.manifest))

    def test_exact_restore_and_idempotence(self):
        self.assertTrue(storage.verify(self.root)["byte_exact"])
        self.assertEqual(storage.restore(self.root)["restored"], 1)
        self.assertEqual((self.root / self.row["path"]).read_bytes(), self.raw)
        self.assertEqual(storage.restore(self.root)["restored"], 0)
        self.assertEqual(len(list((self.root / "data").iterdir())), 2)

    def test_bad_archive_rejects_even_with_a_good_expanded_copy(self):
        storage.restore(self.root)
        (self.root / self.row["storage_path"]).write_bytes(b"bad")
        with self.assertRaisesRegex(ValueError, "compressed evidence drift"):
            storage.restore(self.root)

    def test_changed_expanded_file_is_preserved_and_rejected(self):
        path = self.root / self.row["path"]
        path.write_bytes(b"my changed result")
        with self.assertRaisesRegex(ValueError, "refusing overwrite"):
            storage.restore(self.root)
        self.assertEqual(path.read_bytes(), b"my changed result")

    def test_changed_original_identity_cannot_be_reconstructed(self):
        self.row["sha256"] = "0" * 64
        self.save()
        with self.assertRaisesRegex(ValueError, "expanded evidence drift"):
            storage.restore(self.root)
        self.assertFalse((self.root / self.row["path"]).exists())

    def test_truncation_trailing_bytes_and_wrong_size_fail(self):
        for data in (self.packed[:-1], self.packed + b"extra", self.packed * 2):
            with self.subTest(data=len(data)), self.assertRaises(ValueError):
                storage.unpack(data, self.row)
        with self.assertRaises(ValueError):
            storage.unpack(self.packed, {**self.row, "size": len(self.raw) - 1})

    def test_unsafe_names_and_duplicate_entries_fail(self):
        for name in ("../outside.json", "/outside.json", "data/../outside.json", "data\\bad.json"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                storage.safe_path(self.root, name)
        self.manifest["files"].append(self.row.copy())
        self.save()
        with self.assertRaisesRegex(ValueError, "duplicate"):
            storage.entries(self.root)

    def test_symlink_file_and_parent_are_rejected(self):
        path = self.root / self.row["path"]
        path.symlink_to(self.root / self.row["storage_path"])
        with self.assertRaisesRegex(ValueError, "symlink"):
            storage.restore(self.root)
        path.unlink()
        (self.root / "alias").symlink_to(self.root / "data", target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            storage.safe_path(self.root, "alias/result.json")

    def test_manifest_types_and_positive_sizes_are_strict(self):
        for key, value in (("size", True), ("storage_size", -1), ("storage_size", True)):
            old = self.row[key]
            self.row[key] = value
            self.save()
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                storage.entries(self.root)
            self.row[key] = old

    def test_concurrent_valid_restore_is_safe(self):
        real_link = os.link

        def concurrent(source, target):
            real_link(source, target)
            raise FileExistsError()

        with patch.object(storage.os, "link", side_effect=concurrent):
            self.assertEqual(storage.restore(self.root)["restored"], 0)
        self.assertEqual((self.root / self.row["path"]).read_bytes(), self.raw)
        self.assertEqual(len(list((self.root / "data").iterdir())), 2)

    def test_size_gate_checks_index_not_smaller_work_file(self):
        def git(*args):
            subprocess.run(["git", *args], cwd=self.root, check=True, capture_output=True)

        git("init", "--quiet")
        path = self.root / "large.json"
        path.write_bytes(self.raw)
        git("add", "large.json")
        path.write_bytes(b"{}")
        with self.assertRaisesRegex(ValueError, "Git files exceed storage policy"):
            storage.git_size_check(self.root)
        git("add", "large.json")
        (self.root / "ignored-local.json").write_bytes(self.raw)
        self.assertEqual(storage.git_size_check(self.root)["changed_git_files"], 1)

    def test_pack_new_subject_and_resume_exact_archive(self):
        name = "data/new.json"
        (self.root / name).write_bytes(self.raw)
        (self.root / (name + ".xz")).write_bytes(lzma.compress(self.raw, preset=6))
        storage.pack(self.root, [name])
        self.assertEqual(storage.verify(self.root)["files"], 2)
        self.assertIn("/data/new.json", (self.root / ".gitignore").read_text())
        self.assertEqual(storage.pack(self.root, [name])["files"], 2)
        (self.root / name).write_bytes(b"modified scientific subject")
        with self.assertRaisesRegex(ValueError, "refusing overwrite"):
            storage.pack(self.root, [name])

    def test_pack_allows_large_archive_and_non_json_payload(self):
        name = "data/entropy.bin"
        (self.root / name).write_bytes(os.urandom(1024))
        storage.pack(self.root, [name])
        row = next(r for r in storage.entries(self.root) if r['path'] == name)
        self.assertGreater(row['storage_size'], storage.LIMIT)
        self.assertEqual(storage.unpack(storage.packed_bytes(self.root, row), row), (self.root/name).read_bytes())
        with self.assertRaisesRegex(ValueError, 'already compressed'):
            storage.pack(self.root, [name+'.xz'])

    def test_threshold_is_strictly_greater_and_legacy_manifest_reads(self):
        name = 'data/boundary.txt'
        (self.root/name).write_bytes(b'a'*storage.LIMIT)
        with self.assertRaisesRegex(ValueError, 'does not exceed'):
            storage.pack(self.root, [name])
        (self.root/name).write_bytes(b'a'*(storage.LIMIT+1))
        storage.pack(self.root,[name])
        self.assertEqual(len(storage.entries(self.root)),2)
        self.manifest = {'schema':'exact-evidence-storage-v1','max_git_file_bytes':10_000_000,'files':[self.row]}
        self.save()
        self.assertEqual(storage.entries(self.root), [self.row])

    def test_git_gate_is_forward_only_and_checks_compressed_bytes(self):
        def git(*args):
            subprocess.run(['git',*args],cwd=self.root,check=True,capture_output=True)
        git('init','--quiet')
        historical=self.root/'historical.json'
        historical.write_bytes(self.raw)
        git('add','historical.json')
        git('-c','user.name=Storage Test','-c','user.email=storage@example.invalid',
            'commit','--quiet','-m','fixture')
        self.assertEqual(storage.git_size_check(self.root)['changed_git_files'],0)
        archive=self.root/'new.xz'
        archive.write_bytes(lzma.compress(os.urandom(1024)))
        git('add','new.xz')
        self.assertEqual(storage.git_size_check(self.root)['large_blob_review_threshold_bytes'], 10_000_000)
        with patch.object(storage, 'LARGE_BLOB_REVIEW_BYTES', 1000):
            with self.assertRaisesRegex(ValueError, 'review trigger'):
                storage.git_size_check(self.root)
        archive.write_bytes(os.urandom(1024))
        git('add','new.xz')
        archive.write_bytes(lzma.compress(self.raw))
        with self.assertRaisesRegex(ValueError,'new.xz'):
            storage.git_size_check(self.root)
        git('add','new.xz')
        historical.write_bytes(self.raw+b' ')
        git('add','historical.json')
        with self.assertRaisesRegex(ValueError,'historical.json'):
            storage.git_size_check(self.root)

    def review_fixture(self):
        compression = patch.object(storage, "LIMIT", 1600)
        compression.start()
        self.addCleanup(compression.stop)
        def git(*args):
            subprocess.run(["git", *args], cwd=self.root, check=True, capture_output=True)
        git("init", "--quiet")
        name = "large.xz"
        data = lzma.compress(os.urandom(2048))
        (self.root / name).write_bytes(data)
        git("add", name)
        return git, name, data

    def review_row(self, name, data):
        return {
            "path": name, "size": len(data), "sha256": storage.sha(data),
            "required_for": "Independent replay of every retained certificate witness.",
            "why_not_smaller": "Compared selected samples and shared operands; both omit the per-step witness needed by this review.",
            "retention_reason": "Keep the complete bounded witness for this verification, with its exact identity recorded.",
        }

    def write_reviews(self, rows):
        (self.root / storage.SIZE_REVIEWS).write_text(json.dumps({
            "schema": "evidence-size-reviews-v1", "reviews": rows,
        }))

    def test_large_review_trigger_is_strictly_over_threshold(self):
        git, name, data = self.review_fixture()
        with patch.object(storage, "LARGE_BLOB_REVIEW_BYTES", len(data)):
            self.assertEqual(storage.git_size_check(self.root)["reviewed_large_files"], [])
        with patch.object(storage, "LARGE_BLOB_REVIEW_BYTES", len(data) - 1):
            with self.assertRaisesRegex(ValueError, "review trigger"):
                storage.git_size_check(self.root)
            self.write_reviews([self.review_row(name, data)])
            git("add", storage.SIZE_REVIEWS)
            self.assertEqual(storage.git_size_check(self.root)["reviewed_large_files"], [name])

    def test_large_review_requires_staged_decision_for_exact_staged_bytes(self):
        git, name, data = self.review_fixture()
        with patch.object(storage, "LARGE_BLOB_REVIEW_BYTES", 1800):
            self.write_reviews([self.review_row(name, data)])
            with self.assertRaisesRegex(ValueError, "review trigger"):
                storage.git_size_check(self.root)  # Unstaged reason is not a decision.
            git("add", storage.SIZE_REVIEWS)
            self.assertEqual(storage.git_size_check(self.root)["reviewed_large_files"], [name])
            changed = lzma.compress(os.urandom(2048))
            (self.root / name).write_bytes(changed)
            git("add", name)
            (self.root / name).write_bytes(b"small unstaged copy")
            with self.assertRaisesRegex(ValueError, "does not match the staged blob"):
                storage.git_size_check(self.root)
            self.write_reviews([self.review_row(name, changed)])
            with self.assertRaisesRegex(ValueError, "does not match the staged blob"):
                storage.git_size_check(self.root)
            git("add", storage.SIZE_REVIEWS)
            self.assertEqual(storage.git_size_check(self.root)["reviewed_large_files"], [name])

    def test_large_reviews_require_complete_unique_specific_reasons(self):
        git, name, data = self.review_fixture()
        valid = self.review_row(name, data)
        invalid = []
        for key in ("required_for", "why_not_smaller", "retention_reason"):
            invalid.append([{**valid, key: "   "}])
        invalid.extend([
            [{k: v for k, v in valid.items() if k != "why_not_smaller"}],
            [{**valid, "size": True}], [{**valid, "sha256": "bad"}],
            [valid, valid],
        ])
        with patch.object(storage, "LARGE_BLOB_REVIEW_BYTES", 1800):
            for rows in invalid:
                self.write_reviews(rows)
                git("add", storage.SIZE_REVIEWS)
                with self.subTest(rows=rows), self.assertRaises(ValueError):
                    storage.git_size_check(self.root)

    def test_review_cannot_cover_another_path_or_bypass_compression(self):
        git, name, data = self.review_fixture()
        other = "other.xz"
        (self.root / other).write_bytes(data)
        git("add", other)
        with patch.object(storage, "LARGE_BLOB_REVIEW_BYTES", 1800):
            reviews = [self.review_row(name, data)]
            self.write_reviews(reviews)
            git("add", storage.SIZE_REVIEWS)
            with self.assertRaisesRegex(ValueError, "other.xz"):
                storage.git_size_check(self.root)
            reviews.append(self.review_row(other, data))
            raw = b"uncompressed" * 180
            (self.root / "raw.bin").write_bytes(raw)
            git("add", "raw.bin")
            reviews.append(self.review_row("raw.bin", raw))
            self.write_reviews(reviews)
            git("add", storage.SIZE_REVIEWS)
            with self.assertRaisesRegex(ValueError, "compress raw evidence first"):
                storage.git_size_check(self.root)

    def test_recognized_archives_are_validated_not_just_named(self):
        buffer=io.BytesIO()
        with zipfile.ZipFile(buffer,'w',compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr('payload',self.raw)
        for name,data in [('a.xz',self.packed),('a.gz',gzip.compress(self.raw)),
                          ('a.bz2',bz2.compress(self.raw)),('a.zip',buffer.getvalue())]:
            with self.subTest(name=name):
                self.assertTrue(storage.valid_compressed(name,data))
                self.assertFalse(storage.valid_compressed(name,self.raw))
                self.assertFalse(storage.valid_compressed(name,data[:-8]))
        self.assertFalse(storage.valid_compressed('a.xz',self.packed+b'raw trailing bytes'))

    def test_scoped_restore_does_not_require_unrelated_local_outputs(self):
        path = self.root / self.row["path"]
        path.write_bytes(b"unrelated edited local output")
        result = storage.restore(self.root, prefix="another-phase/")
        self.assertEqual(result, {"files": 0, "restored": 0})
        self.assertEqual(path.read_bytes(), b"unrelated edited local output")


if __name__ == "__main__":
    unittest.main()

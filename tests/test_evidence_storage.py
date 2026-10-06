"""Pressure lossless storage, failure-closed restoration and the Git size gate."""

import importlib.util
import json
import lzma
import os
import subprocess
import tempfile
import unittest
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
        self.manifest = {"schema": "exact-evidence-storage-v1",
                         "max_git_file_bytes": 256, "files": [self.row]}
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

    def test_manifest_types_and_archive_budget_are_strict(self):
        for key, value in (("size", True), ("storage_size", -1), ("storage_size", 257)):
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
        with self.assertRaisesRegex(ValueError, "Git files exceed 10 MB"):
            storage.git_size_check(self.root)
        git("add", "large.json")
        (self.root / "ignored-local.json").write_bytes(self.raw)
        self.assertEqual(storage.git_size_check(self.root)["git_files"], 1)

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

    def test_pack_rejects_archive_over_budget_without_registering_it(self):
        name = "data/entropy.json"
        (self.root / name).write_bytes(os.urandom(1024))
        with self.assertRaisesRegex(ValueError, "archive still exceeds"):
            storage.pack(self.root, [name])
        self.assertFalse((self.root / (name + ".xz")).exists())
        self.assertEqual(len(storage.entries(self.root)), 1)

    def test_scoped_restore_does_not_require_unrelated_local_outputs(self):
        path = self.root / self.row["path"]
        path.write_bytes(b"unrelated edited local output")
        result = storage.restore(self.root, prefix="another-phase/")
        self.assertEqual(result, {"files": 0, "restored": 0})
        self.assertEqual(path.read_bytes(), b"unrelated edited local output")


if __name__ == "__main__":
    unittest.main()

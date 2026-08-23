from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from artifact_io import artifact_envelope, assert_payload_digest, canonical_json_bytes, find_machine_local_path, require_repo_relative  # noqa: E402


class CanonicalJsonTest(unittest.TestCase):
    def test_canonical_order_and_digest(self) -> None:
        self.assertEqual(b'{"a":1,"b":2}', canonical_json_bytes({"b": 2, "a": 1}))
        envelope = artifact_envelope({"b": 2, "a": 1}, schema_version="test", generating_command="test")
        assert_payload_digest(envelope)

    def test_nan_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            canonical_json_bytes({"bad": float("nan")})

    def test_paths_are_repository_relative(self) -> None:
        self.assertEqual("outputs/example.json", require_repo_relative("outputs/example.json"))
        for invalid in ("/tmp/example", "../example", "C:/example", "https://example.test/a"):
            with self.assertRaises(ValueError):
                require_repo_relative(invalid)

    def test_machine_local_path_scan_is_structural(self) -> None:
        self.assertEqual(["$.path"], find_machine_local_path({"path": "/tmp/example"}))
        self.assertEqual([], find_machine_local_path({"statement": "not/a/path"}))


if __name__ == "__main__":
    unittest.main()

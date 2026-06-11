"""Tests for GRC9 to GRCL-9 suitability handoff generation."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from pygrc.discovery import run_grc9_grcl9_handoff as exported_runner
from pygrc.discovery.grc9_grcl9_handoff import run_grc9_grcl9_handoff


class GRC9GRCL9HandoffTest(unittest.TestCase):
    def test_handoff_uses_accepted_motifs_only_and_preserves_non_claims(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            catalog_path = root / "reviewed_motif_catalog.json"
            catalog_path.write_text(
                json.dumps(
                    {
                        "accepted_motifs": [
                            {
                                "motif_id": "grc9-motif-accepted",
                                "phenomenon": "spark",
                                "lane": "spark_column_proxy_eps_pass",
                                "profile": "grc9_discovery_lifecycle_emitter_repair_v1",
                                "seed_name": "spark_column_proxy_eps_pass",
                                "observed_evidence_fields": [
                                    "event_counts_by_kind.spark",
                                ],
                                "predicted_evidence_fields": [
                                    "event_counts_by_kind.spark",
                                ],
                                "review_status": "accepted",
                                "confidence_score": 5,
                                "non_claims": [
                                    "grcl9_lowering",
                                    "grcv3_semantics",
                                ],
                                "notes": {
                                    "artifact_root": "outputs/example",
                                    "seed_family": "spark_column_proxy_emitter",
                                    "seed_parameters_path": "outputs/example/telemetry/run_summary.json#raw_params",
                                },
                            }
                        ],
                        "review_status_counts": {
                            "accepted": 1,
                            "strong_candidate": 3,
                            "rejected": 2,
                        },
                    }
                ),
                encoding="utf-8",
            )
            session = run_grc9_grcl9_handoff(
                session_id="S0991",
                reviewed_session_id="S0990",
                session_root=root / "S0991",
                reviewed_catalog_path=catalog_path,
            )
            payload = json.loads(Path(session.json_path).read_text(encoding="utf-8"))
            markdown = Path(session.markdown_path).read_text(encoding="utf-8")

        self.assertEqual(1, session.accepted_count)
        self.assertEqual(1, len(payload["entries"]))
        self.assertIn("grc9_graph_preconditions", payload["entries"][0])
        self.assertIn("no_grcl9_lowering_implemented", payload["non_claims"])
        self.assertIn("grc9-motif-accepted", markdown)
        self.assertIn("does not implement GRCL-9 lowering", markdown)
        self.assertNotIn("strong_candidate", markdown)

    def test_s0025_handoff_smoke(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            session = run_grc9_grcl9_handoff(
                session_id="S0992",
                reviewed_session_id="S0025",
                session_root=Path(tmpdir) / "S0992",
            )
            payload = json.loads(Path(session.json_path).read_text(encoding="utf-8"))

        self.assertEqual(10, session.accepted_count)
        self.assertEqual(10, len(payload["entries"]))
        self.assertTrue(
            all(entry["review_status"] == "accepted" for entry in payload["entries"])
        )
        self.assertTrue(
            all(entry["observed_validation_fields"] for entry in payload["entries"])
        )
        self.assertTrue(
            all(entry["grc9_graph_preconditions"] for entry in payload["entries"])
        )

    def test_handoff_is_exported_from_discovery_package(self) -> None:
        self.assertIs(exported_runner, run_grc9_grcl9_handoff)


if __name__ == "__main__":
    unittest.main()

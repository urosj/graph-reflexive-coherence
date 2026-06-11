"""Tests for GRC9V3 source-language handoff generation."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from pygrc.discovery import run_grc9v3_source_handoff as exported_runner
from pygrc.discovery.grc9v3_source_handoff import run_grc9v3_source_handoff


class GRC9V3SourceHandoffTest(unittest.TestCase):
    def test_handoff_classifies_source_vocab_and_runtime_only_records(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            catalog_path = root / "expanded_motif_catalog.json"
            catalog_path.write_text(
                json.dumps(
                    {
                        "records": [
                            _record(
                                motif_id="motif-source",
                                phenomenon="hybrid_spark_gate",
                                lane_name="hybrid_spark_gate_positive_control",
                                review_status="accepted",
                                catalog_category="simple_lifecycle_motif",
                                control_role="positive_control",
                            ),
                            _record(
                                motif_id="motif-negative",
                                phenomenon="growth_pressure",
                                lane_name="growth_pressure_negative_control",
                                review_status="strong_candidate",
                                catalog_category="negative_control",
                                control_role="negative_control",
                            ),
                            _record(
                                motif_id="motif-runtime",
                                phenomenon="hessian_backend_comparison",
                                lane_name="hessian_backend_comparison_positive_control",
                                review_status="diagnostic_comparator",
                                catalog_category="diagnostic_comparator",
                                control_role="positive_control",
                            ),
                        ]
                    }
                ),
                encoding="utf-8",
            )
            session = run_grc9v3_source_handoff(
                session_id="S0991",
                source_catalog_session_id="S0990",
                session_root=root / "S0991",
                source_catalog_path=catalog_path,
            )
            payload = json.loads(Path(session.handoff_json_path).read_text(encoding="utf-8"))
            markdown = Path(session.handoff_markdown_path).read_text(encoding="utf-8")

        self.assertEqual(3, session.to_mapping()["motif_count"])
        self.assertEqual(1, session.to_mapping()["source_expression_candidate_count"])
        self.assertEqual(1, session.to_mapping()["requires_new_source_vocabulary_count"])
        self.assertEqual(1, session.to_mapping()["runtime_only_count"])
        self.assertEqual("motif-source", payload["source_expression_candidates"][0]["motif_id"])
        self.assertEqual("motif-negative", payload["requires_new_source_vocabulary"][0]["motif_id"])
        self.assertEqual("motif-runtime", payload["runtime_only"][0]["motif_id"])
        self.assertIn("does not implement GRCL/source lowering", markdown)
        self.assertIn("runtime_evidence_only", payload["entries"][0]["source_claim_status"])

    def test_s0013_handoff_smoke(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            session = run_grc9v3_source_handoff(
                session_id="S0992",
                source_catalog_session_id="S0013",
                session_root=Path(tmpdir) / "S0992",
            )
            payload = json.loads(Path(session.handoff_json_path).read_text(encoding="utf-8"))

        summary = session.to_mapping()
        self.assertEqual(26, summary["motif_count"])
        self.assertEqual(8, summary["source_expression_candidate_count"])
        self.assertEqual(12, summary["requires_new_source_vocabulary_count"])
        self.assertEqual(6, summary["runtime_only_count"])
        self.assertTrue(payload["source_expression_candidates"])
        self.assertTrue(payload["requires_new_source_vocabulary"])
        self.assertTrue(payload["runtime_only"])
        self.assertTrue(
            all(
                entry["source_claim_status"] == "runtime_evidence_only"
                for entry in payload["entries"]
            )
        )

    def test_handoff_is_exported_from_discovery_package(self) -> None:
        self.assertIs(exported_runner, run_grc9v3_source_handoff)


def _record(
    *,
    motif_id: str,
    phenomenon: str,
    lane_name: str,
    review_status: str,
    catalog_category: str,
    control_role: str,
) -> dict[str, object]:
    return {
        "motif_id": motif_id,
        "phenomenon": phenomenon,
        "lane_name": lane_name,
        "profile": f"{phenomenon}_profile",
        "review_status": review_status,
        "catalog_category": catalog_category,
        "control_role": control_role,
        "telemetry_artifact_root": "outputs/example",
        "checkpoint_links": [{"checkpoint_id": "step-00000000"}],
        "observed_evidence_fields": ["family_extensions.grc9v3.contract_version"],
        "predicted_evidence_fields": ["family_extensions.grc9v3.contract_version"],
        "event_counts_by_kind": {},
        "non_claims": ["no_grcl9_source_lowering_claim"],
    }


if __name__ == "__main__":
    unittest.main()

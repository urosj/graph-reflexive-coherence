"""Tests for GRC9 reviewed motif catalog generation."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from pygrc.discovery import run_grc9_reviewed_motif_catalog as exported_runner
from pygrc.discovery.grc9_manifest import (
    GRC9DiscoveryManifest,
    GRC9ManifestRunScope,
    GRC9MotifRecord,
)
from pygrc.discovery.grc9_reviewed_motif_catalog import (
    run_grc9_reviewed_motif_catalog,
)


class GRC9ReviewedMotifCatalogTest(unittest.TestCase):
    def test_synthetic_review_policy_promotes_reruns_and_rejections(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifest_path = root / "selector_manifest.json"
            report_path = root / "selector_report.json"
            source_manifest = GRC9DiscoveryManifest(
                source_artifacts=(),
                run_scope=GRC9ManifestRunScope(
                    profiles=("grc9_discovery_spark_precursor_v1",),
                    lanes=(
                        "spark_column_proxy_eps_pass",
                        "spark_column_proxy_eps_fail",
                        "spark_instability_tau_pass",
                    ),
                ),
                motifs=(
                    self._motif(
                        motif_id="grc9-motif-synthetic-accepted",
                        lane="spark_column_proxy_eps_pass",
                        confidence_score=5,
                        confidence_label="strong_candidate",
                    ),
                    self._motif(
                        motif_id="grc9-motif-synthetic-strong",
                        lane="spark_column_proxy_eps_fail",
                        confidence_score=4,
                        confidence_label="candidate",
                    ),
                    self._motif(
                        motif_id="grc9-motif-synthetic-rerun",
                        lane="spark_instability_tau_pass",
                        confidence_score=4,
                        confidence_label="candidate",
                    ),
                ),
            )
            manifest_path.write_text(
                json.dumps(source_manifest.to_mapping(), indent=2),
                encoding="utf-8",
            )
            report_path.write_text(
                json.dumps(
                    {
                        "validations": [
                            self._validation("spark_column_proxy_eps_pass", 5),
                            self._validation("spark_column_proxy_eps_fail", 4),
                            self._validation(
                                "spark_instability_tau_pass",
                                4,
                                observed_value="missing_surface",
                            ),
                            self._validation(
                                "growth_pressure_positive_control",
                                1,
                                confidence_label="rejected",
                                missing_selector_ids=("growth_event_present",),
                            ),
                        ]
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
            session = run_grc9_reviewed_motif_catalog(
                session_id="S0992",
                selector_session_id="S0991",
                session_root=root / "S0992",
                selector_manifest_path=manifest_path,
                selector_report_path=report_path,
                reviewer="unit_test_reviewer",
                review_timestamp_utc="2026-04-25T12:00:00Z",
            )

        statuses = {motif.lane: motif.review_status for motif in session.manifest.motifs}
        self.assertEqual("accepted", statuses["spark_column_proxy_eps_pass"])
        self.assertEqual("strong_candidate", statuses["spark_column_proxy_eps_fail"])
        self.assertEqual("needs-rerun", statuses["spark_instability_tau_pass"])
        self.assertEqual("rejected", statuses["growth_pressure_positive_control"])
        self.assertEqual(1, session.accepted_count)
        self.assertEqual(1, session.strong_candidate_count)
        self.assertEqual(1, session.needs_rerun_count)
        self.assertEqual(1, session.rejected_count)
        self.assertTrue(
            all(entry.reviewer == "unit_test_reviewer" for entry in session.manifest.review_history)
        )
        self.assertTrue(
            all(
                entry.timestamp_utc == "2026-04-25T12:00:00Z"
                for entry in session.manifest.review_history
            )
        )

    def test_s0022_replay_smoke_preserves_review_invariants(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            session = run_grc9_reviewed_motif_catalog(
                session_id="S0991",
                selector_session_id="S0022",
                session_root=Path(tmpdir) / "S0991",
            )

        payload = session.to_mapping()
        self.assertGreater(payload["motif_count"], 0)
        self.assertGreater(payload["accepted_count"], 0)
        self.assertGreater(payload["strong_candidate_count"], 0)
        self.assertGreater(payload["rejected_count"], 0)
        self.assertEqual(0, payload["duplicate_count"])
        self.assertEqual(0, payload["needs_rerun_count"])
        self.assertEqual(payload["motif_count"], payload["review_history_count"])

        accepted = [
            motif for motif in session.manifest.motifs if motif.review_status == "accepted"
        ]
        self.assertTrue(all(motif.confidence_score == 5 for motif in accepted))
        self.assertTrue(
            all(motif.confidence_label == "accepted_after_review" for motif in accepted)
        )
        self.assertTrue(all("seed_family" in dict(motif.notes or {}) for motif in accepted))
        self.assertTrue(
            all("seed_parameters_path" in dict(motif.notes or {}) for motif in accepted)
        )
        rejected = [
            motif for motif in session.manifest.motifs if motif.review_status == "rejected"
        ]
        self.assertTrue(all(motif.rejection_reason for motif in rejected))

    def test_reviewed_manifest_round_trips(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "S0990"
            session = run_grc9_reviewed_motif_catalog(
                session_id="S0990",
                selector_session_id="S0022",
                session_root=root,
            )
            restored = GRC9DiscoveryManifest.from_mapping(
                __import__("json").loads(Path(session.reviewed_manifest_path).read_text())
            )

        self.assertEqual(session.manifest.to_mapping(), restored.to_mapping())

    def test_reviewed_catalog_is_exported_from_discovery_package(self) -> None:
        self.assertIs(exported_runner, run_grc9_reviewed_motif_catalog)

    def _motif(
        self,
        *,
        motif_id: str,
        lane: str,
        confidence_score: int,
        confidence_label: str,
    ) -> GRC9MotifRecord:
        return GRC9MotifRecord(
            motif_id=motif_id,
            hypothesis_id=f"grc9_selector_{lane}",
            phenomenon="spark",
            profile="grc9_discovery_spark_precursor_v1",
            lane=lane,
            run_id=f"run-{lane}",
            seed_name=lane,
            session_ids=("S0001",),
            step_window=(0, 1),
            predicted_evidence_fields=("event_counts_by_kind.spark",),
            observed_evidence_fields=("event_counts_by_kind.spark",),
            confidence_score=confidence_score,
            confidence_label=confidence_label,
            review_status=confidence_label if confidence_label != "accepted_after_review" else "accepted",
            non_claims=("grcl9_lowering", "grcv3_semantics", "lorentzian_causal_layer"),
        )

    def _validation(
        self,
        lane_name: str,
        confidence_score: int,
        *,
        confidence_label: str | None = None,
        observed_value: int | str = 1,
        missing_selector_ids: tuple[str, ...] = (),
    ) -> dict[str, object]:
        return {
            "confidence_label": confidence_label or (
                "strong_candidate" if confidence_score >= 5 else "candidate"
            ),
            "confidence_score": confidence_score,
            "expected_selector_ids": ("spark_event_present",),
            "lane_name": lane_name,
            "missing_selector_ids": missing_selector_ids,
            "notes": {},
            "profile": "grc9_discovery_spark_precursor_v1",
            "requested_steps": 1,
            "run_id": f"run-{lane_name}",
            "seed_name": lane_name,
            "selector_results": (
                {
                    "field_path": "event_counts_by_kind.spark",
                    "observed_value": observed_value,
                    "passed": not missing_selector_ids and observed_value != "missing_surface",
                    "selector_id": "spark_event_present",
                },
            ),
            "session_id": "S0001",
        }


if __name__ == "__main__":
    unittest.main()

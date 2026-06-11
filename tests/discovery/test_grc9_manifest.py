"""Tests for the GRC9 phenomenology discovery manifest contract."""

from __future__ import annotations

import json
import unittest

from pygrc.discovery import (
    GRC9_PHENOMENOLOGY_DISCOVERY_MANIFEST_VERSION,
    GRC9DiscoveryManifest,
    GRC9EvidenceFields,
    GRC9ManifestRunScope,
    GRC9MotifRecord,
    GRC9PredictedSignature,
    GRC9ReviewHistoryEntry,
    GRC9SelectorSpec,
    GRC9SourceArtifact,
    GRC9SourceReference,
    GRC9StructureHypothesis,
    generated_lane_name,
    is_discovery_profile_name,
    is_generated_lane_name,
    is_session_id,
    perturbation_lane_name,
    profile_name,
)


class GRC9DiscoveryManifestTest(unittest.TestCase):
    def _manifest(self) -> GRC9DiscoveryManifest:
        profile = profile_name("spark_precursor", 1)
        lane = generated_lane_name("spark_precursor", "positive_control")
        hypothesis = GRC9StructureHypothesis(
            hypothesis_id="grc9_hypothesis_0001",
            target_phenomenon="spark_precursor",
            runtime_status="testable",
            paper_sources=(
                GRC9SourceReference(
                    source="papers/2026-04-GRC-9.md",
                    section="Appendix D",
                    equation="D.1",
                ),
            ),
            graph_preconditions={
                "requires_saturation": True,
                "target_effective_degree": 14,
            },
            seed_family="spark_precursor",
            seed_parameters={"control_role": "positive_control"},
            generator="generate_grc9_seed",
            predicted_signatures=(
                GRC9PredictedSignature(
                    field_path=(
                        "family_extensions.grc9.column_diagnostic."
                        "column_proxy_candidate_count"
                    ),
                    predicate="> 0",
                    expected_type="int",
                ),
            ),
        )
        motif = GRC9MotifRecord(
            motif_id="grc9-motif-0001",
            hypothesis_id="grc9_hypothesis_0001",
            phenomenon="spark_precursor",
            profile=profile,
            lane=lane,
            run_id="run-1",
            seed_name="generated_spark_precursor_0001",
            session_ids=("S0001",),
            step_window=(3, 5),
            event_ids=("event-1",),
            checkpoint_ids=("checkpoint-3",),
            predicted_evidence_fields=(
                "family_extensions.grc9.column_diagnostic.column_proxy_candidate_count",
            ),
            observed_evidence_fields=(
                "family_extensions.grc9.spark_evidence.column_proxy_gate_pass",
            ),
            evidence_fields=GRC9EvidenceFields(
                predicted=(
                    "family_extensions.grc9.column_diagnostic.column_proxy_candidate_count",
                ),
                observed=(
                    "family_extensions.grc9.spark_evidence.column_proxy_gate_pass",
                ),
                missing=("family_extensions.grc9.spark_evidence.sign_crossing_gate_pass",),
            ),
            confidence_score=3,
            confidence_label="candidate",
            review_status="candidate",
            notes={"field_interpretation": "column proxy matched"},
        )
        return GRC9DiscoveryManifest(
            source_artifacts=(
                GRC9SourceArtifact(
                    artifact_role="smoke_reference",
                    path="outputs/representative/grc9/phase_t_grc9_iter6_representative/",
                    used_for_discovery=False,
                ),
            ),
            run_scope=GRC9ManifestRunScope(
                profiles=(profile,),
                lanes=(lane,),
            ),
            structure_hypotheses=(hypothesis,),
            selectors=(
                GRC9SelectorSpec(
                    selector_id="spark_confirmed_events",
                    surface="events.jsonl",
                    query="family_extensions.grc9.event_domain == 'spark'",
                    expected_type="event_row",
                ),
            ),
            motifs=(motif,),
            review_history=(
                GRC9ReviewHistoryEntry(
                    motif_id="grc9-motif-0001",
                    from_status="unreviewed",
                    to_status="candidate",
                    reviewer="",
                    reason="initial selector pass",
                    timestamp_utc="",
                ),
            ),
        )

    def test_manifest_round_trips_through_json(self) -> None:
        manifest = self._manifest()
        payload = manifest.to_mapping()

        self.assertEqual(
            GRC9_PHENOMENOLOGY_DISCOVERY_MANIFEST_VERSION,
            payload["manifest_version"],
        )
        encoded = json.dumps(payload, sort_keys=True)
        restored = GRC9DiscoveryManifest.from_mapping(json.loads(encoded))

        self.assertEqual(payload, restored.to_mapping())
        self.assertEqual(("S0001",), restored.motifs[0].session_ids)

    def test_missing_optional_fields_are_deterministic(self) -> None:
        profile = profile_name("quiescent_basin", 1)
        lane = generated_lane_name("quiescent_basin", "negative_control")
        manifest = GRC9DiscoveryManifest.from_mapping(
            {
                "source_artifacts": [],
                "run_scope": {"family": "grc9", "profiles": [profile], "lanes": [lane]},
                "motifs": [
                    {
                        "motif_id": "grc9-motif-0002",
                        "hypothesis_id": "grc9_hypothesis_0002",
                        "phenomenon": "quiescent_basin",
                        "profile": profile,
                        "lane": lane,
                        "run_id": "",
                        "seed_name": "generated_quiescent_basin_0001",
                        "step_window": [0, 0],
                    }
                ],
            }
        )

        payload = manifest.to_mapping()
        motif = payload["motifs"][0]
        self.assertEqual([], motif["event_ids"])
        self.assertEqual([], motif["predicted_evidence_fields"])
        self.assertEqual({"predicted": [], "observed": [], "missing": []}, motif["evidence_fields"])
        self.assertEqual(False, motif["rerun_requested"])
        self.assertEqual("outputs/grc9/phenomenology_discovery/sessions", payload["output_roots"]["sessions"])

    def test_review_transitions_preserve_rejected_motif(self) -> None:
        profile = profile_name("growth_pressure", 1)
        lane = generated_lane_name("growth_pressure", "positive_control")
        motif = GRC9MotifRecord(
            motif_id="grc9-motif-0003",
            hypothesis_id="grc9_hypothesis_0003",
            phenomenon="growth_pressure",
            profile=profile,
            lane=lane,
            run_id="run-3",
            seed_name="generated_growth_pressure_0001",
            step_window=(10, 12),
            confidence_score=1,
            confidence_label="rejected",
            review_status="rejected",
            rejection_reason="primary predicted fields were contradicted",
        )
        entry = GRC9ReviewHistoryEntry(
            motif_id="grc9-motif-0003",
            from_status="candidate",
            to_status="rejected",
            reviewer="reviewer",
            reason="contradiction",
            timestamp_utc="2026-04-25T00:00:00Z",
        )

        payload = GRC9DiscoveryManifest(
            source_artifacts=(),
            run_scope=GRC9ManifestRunScope(profiles=(profile,), lanes=(lane,)),
            motifs=(motif,),
            review_history=(entry,),
        ).to_mapping()

        self.assertEqual("rejected", payload["motifs"][0]["review_status"])
        self.assertEqual(
            "primary predicted fields were contradicted",
            payload["motifs"][0]["rejection_reason"],
        )
        self.assertEqual("rejected", payload["review_history"][0]["to_status"])

    def test_manifest_update_helpers_return_new_instances(self) -> None:
        manifest = self._manifest()
        motif = manifest.motifs[0]
        updated = manifest.update_motif(
            motif.motif_id,
            review_status="accepted",
            confidence_label="accepted_after_review",
            confidence_score=5,
        )
        entry = GRC9ReviewHistoryEntry(
            motif_id=motif.motif_id,
            from_status="candidate",
            to_status="accepted",
            reviewer="reviewer",
            reason="manual acceptance",
            timestamp_utc="2026-04-25T00:00:00Z",
        )
        with_history = updated.add_review_history(entry)

        self.assertEqual("candidate", manifest.motifs[0].review_status)
        self.assertEqual("accepted", updated.motifs[0].review_status)
        self.assertEqual(2, len(with_history.review_history))

    def test_manifest_add_motif_rejects_duplicate_ids(self) -> None:
        manifest = self._manifest()
        with self.assertRaisesRegex(ValueError, "duplicate motif_id"):
            manifest.add_motif(manifest.motifs[0])

    def test_naming_helpers_distinguish_discovery_from_smoke_lanes(self) -> None:
        profile = profile_name("spark_precursor", 2)
        lane = generated_lane_name("spark_precursor", "positive_control")
        perturbation = perturbation_lane_name(
            "spark_precursor",
            "positive_control",
            "conductance",
            "+10%",
        )

        self.assertTrue(is_discovery_profile_name(profile))
        self.assertTrue(is_generated_lane_name(lane))
        self.assertTrue(is_generated_lane_name(perturbation))
        self.assertTrue(is_generated_lane_name("spark_column_proxy_emitter"))
        self.assertTrue(is_generated_lane_name("spark_growth_combo"))
        self.assertTrue(is_generated_lane_name("spark_column_proxy_eps_fail"))
        self.assertFalse(is_discovery_profile_name("phase_t_grc9_iter7_seed"))
        self.assertFalse(is_generated_lane_name("phase_t_grc9_iter7_seed"))
        self.assertFalse(is_session_id("S1"))
        self.assertTrue(is_session_id("S0001"))

    def test_invalid_names_raise_before_manifest_use(self) -> None:
        with self.assertRaises(ValueError):
            profile_name("Spark Precursor", 1)
        with self.assertRaises(ValueError):
            GRC9ManifestRunScope(profiles=("phase_t_grc9_iter7_seed",), lanes=())
        with self.assertRaises(ValueError):
            GRC9MotifRecord(
                motif_id="grc9-motif-0004",
                hypothesis_id="grc9_hypothesis_0004",
                phenomenon="spark_precursor",
                profile=profile_name("spark_precursor", 1),
                lane=generated_lane_name("spark_precursor", "positive_control"),
                run_id="",
                seed_name="seed",
                session_ids=("S1",),
                step_window=(0, 0),
            )


if __name__ == "__main__":
    unittest.main()

"""Tests for the GRCL-9 lowering manifest contract."""

from __future__ import annotations

import json
import unittest

from pygrc.landscapes.extensions.grcl9 import (
    GRCL9_ACCEPTED_SOURCE_CONSTRUCT_KINDS,
    GRCL9_LOWERING_MANIFEST_VERSION,
    GRCL9LoweringManifest,
    GRCL9LoweringManifestEntry,
    GRCL9LoweringPassFailControl,
    GRCL9TelemetryExpectation,
    default_grcl9_lowering_manifest,
)


EXPECTED_S0026_MOTIF_IDS = {
    "grc9-motif-s0006-spark-column-proxy-eps-pass",
    "grc9-motif-s0006-spark-column-proxy-eps-fail",
    "grc9-motif-s0006-spark-instability-tau-pass",
    "grc9-motif-s0006-spark-instability-tau-fail",
    "grc9-motif-s0006-spark-to-expansion-d-eff-low",
    "grc9-motif-s0006-spark-to-expansion-d-eff-high",
    "grc9-motif-s0006-growth-pressure-lambda-high",
    "grc9-motif-s0006-growth-pressure-lambda-low",
    "grc9-motif-s0006-post-expansion-fission-min-mass-pass",
    "grc9-motif-s0006-post-expansion-fission-min-mass-fail",
}


class GRCL9LoweringManifestTest(unittest.TestCase):
    def test_default_manifest_round_trips_through_json(self) -> None:
        manifest = default_grcl9_lowering_manifest()
        payload = manifest.to_mapping()

        self.assertEqual(GRCL9_LOWERING_MANIFEST_VERSION, payload["manifest_version"])
        encoded = json.dumps(payload, sort_keys=True)
        restored = GRCL9LoweringManifest.from_mapping(json.loads(encoded))

        self.assertEqual(payload, restored.to_mapping())
        self.assertEqual(
            EXPECTED_S0026_MOTIF_IDS,
            set(restored.accepted_motif_ids()),
        )

    def test_default_manifest_covers_revision_one_constructs(self) -> None:
        manifest = default_grcl9_lowering_manifest()
        construct_kinds = {
            construct_kind
            for entry in manifest.entries
            for construct_kind in entry.source_construct_kinds
        }

        self.assertEqual(GRCL9_ACCEPTED_SOURCE_CONSTRUCT_KINDS, construct_kinds)
        self.assertEqual(
            {
                "spark_column_proxy_emitter",
                "spark_instability_emitter",
                "spark_to_expansion_emitter",
                "growth_pressure_emitter",
                "post_expansion_fission_emitter",
            },
            set(manifest.by_seed_family()),
        )

    def test_expected_telemetry_paths_are_contract_aligned(self) -> None:
        manifest = default_grcl9_lowering_manifest()
        all_expectations = [
            expectation
            for entry in manifest.entries
            for expectation in entry.expected_telemetry
        ]

        self.assertTrue(all_expectations)
        self.assertTrue(
            all(
                expectation.field_path.startswith("family_extensions.grc9.")
                for expectation in all_expectations
            )
        )
        self.assertFalse(
            any("event_counts_by_kind" in expectation.field_path for expectation in all_expectations)
        )
        self.assertTrue(any(not expectation.required for expectation in all_expectations))

    def test_rejects_stale_event_counts_path(self) -> None:
        with self.assertRaisesRegex(ValueError, "event_counts_by_kind"):
            GRCL9TelemetryExpectation(
                field_path="event_counts_by_kind.spark",
                surface="run_summary.json",
                predicate="> 0",
                expected_type="int",
            )

    def test_rejects_duplicate_motif_ids(self) -> None:
        control = GRCL9LoweringPassFailControl(
            control_role="pass_control",
            source_fixture_name="spark_column_proxy_eps_pass",
            source_construct_id="spark_column_proxy_eps_pass",
            accepted_motif_id="grc9-motif-s0006-spark-column-proxy-eps-pass",
            s0026_lane="spark_column_proxy_eps_pass",
            expected_outcome="spark evidence is observed",
        )
        entry_a = self._entry("grcl9_lowering_duplicate_a", control)
        entry_b = self._entry("grcl9_lowering_duplicate_b", control)

        with self.assertRaisesRegex(ValueError, "accepted_motif_id values must be unique"):
            GRCL9LoweringManifest(entries=(entry_a, entry_b))

    def test_rejects_unsupported_construct_kind(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported source construct kind"):
            GRCL9LoweringManifestEntry(
                entry_id="grcl9_lowering_bad_construct",
                phenomenon="spark",
                seed_family="bad_construct",
                source_construct_kinds=("spark_happened",),
                graph_preconditions={"saturated_candidate_node": True},
                required_source_knobs=("candidate_id",),
                lowering_carriers=("cached_quantities.grcl9_provenance",),
                expected_telemetry=(
                    GRCL9TelemetryExpectation(
                        field_path="family_extensions.grc9.lifecycle_event_counts.spark_confirmed_count",
                        surface="run_summary.json",
                        predicate="> 0",
                        expected_type="int",
                    ),
                ),
                controls=(
                    GRCL9LoweringPassFailControl(
                        control_role="pass_control",
                        source_fixture_name="bad_construct_pass",
                        source_construct_id="bad_construct_pass",
                        accepted_motif_id="grc9-motif-bad",
                        s0026_lane="bad_construct_pass",
                        expected_outcome="bad construct rejected",
                    ),
                ),
            )

    def test_fission_entry_records_min_mass_controls_and_non_claim(self) -> None:
        manifest = default_grcl9_lowering_manifest()
        entry = manifest.by_seed_family()["post_expansion_fission_emitter"]
        controls = {control.source_fixture_name for control in entry.controls}

        self.assertEqual(
            {
                "post_expansion_fission_min_mass_pass",
                "post_expansion_fission_min_mass_fail",
            },
            controls,
        )
        self.assertIn("no_source_level_fission_confirmation", entry.non_claims)
        self.assertIn("runtime-computed basins", entry.notes)

    def _entry(
        self,
        entry_id: str,
        control: GRCL9LoweringPassFailControl,
    ) -> GRCL9LoweringManifestEntry:
        return GRCL9LoweringManifestEntry(
            entry_id=entry_id,
            phenomenon="spark",
            seed_family=entry_id,
            source_construct_kinds=("spark_candidate_region",),
            graph_preconditions={"saturated_candidate_node": True},
            required_source_knobs=("candidate_id",),
            lowering_carriers=("cached_quantities.grcl9_provenance",),
            expected_telemetry=(
                GRCL9TelemetryExpectation(
                    field_path="family_extensions.grc9.lifecycle_event_counts.spark_confirmed_count",
                    surface="run_summary.json",
                    predicate="> 0",
                    expected_type="int",
                ),
            ),
            controls=(control,),
        )


if __name__ == "__main__":
    unittest.main()

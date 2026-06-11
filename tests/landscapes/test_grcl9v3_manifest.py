"""Tests for the GRCL-9V3 lowering manifest contract."""

from __future__ import annotations

import json
import unittest

from pygrc.landscapes.extensions import (
    default_grcl9v3_lowering_manifest as exported_default_manifest,
)
from pygrc.landscapes.extensions.grcl9v3 import (
    GRCL9V3_ACCEPTED_SOURCE_CONSTRUCT_KINDS,
    GRCL9V3_LOWERING_MANIFEST_VERSION,
    GRCL9V3_OWNERSHIP_TAGS,
    GRCL9V3_TELEMETRY_FIELD_PREFIX,
    GRCL9V3LoweringControl,
    GRCL9V3LoweringManifest,
    GRCL9V3LoweringManifestEntry,
    GRCL9V3RuntimeOnlyExclusion,
    GRCL9V3TelemetryExpectation,
    default_grcl9v3_lowering_manifest,
    validate_grcl9v3_manifest_against_handoff,
)


EXPECTED_SOURCE_CANDIDATE_IDS = {
    "grc9v3-motif-s0006-hybrid-spark-gate-positive-control",
    "grc9v3-motif-s0006-spark-to-expansion-positive-control",
    "grc9v3-motif-s0006-appendix-e-cell-division-positive-control",
    "grc9v3-motif-s0006-choice-collapse-positive-control",
    "grc9v3-motif-s0006-growth-pressure-positive-control",
    "grc9v3-motif-s0008-complex-spark-expansion-hierarchy-complex-control",
    "grc9v3-motif-s0008-complex-spark-expansion-choice-collapse-complex-control",
    "grc9v3-motif-s0008-complex-expansion-growth-budget-coarse-complex-control",
}
EXPECTED_FUTURE_VOCABULARY_COUNT = 12
EXPECTED_RUNTIME_ONLY_COUNT = 6


class GRCL9V3LoweringManifestTest(unittest.TestCase):
    def test_default_manifest_round_trips_through_json(self) -> None:
        manifest = default_grcl9v3_lowering_manifest()
        payload = manifest.to_mapping()

        self.assertEqual(GRCL9V3_LOWERING_MANIFEST_VERSION, payload["manifest_version"])
        encoded = json.dumps(payload, sort_keys=True)
        restored = GRCL9V3LoweringManifest.from_mapping(json.loads(encoded))

        self.assertEqual(payload, restored.to_mapping())
        self.assertEqual(
            EXPECTED_SOURCE_CANDIDATE_IDS,
            set(restored.source_candidate_motif_ids()),
        )
        self.assertEqual(
            EXPECTED_FUTURE_VOCABULARY_COUNT,
            len(restored.future_vocabulary_records),
        )
        self.assertEqual(
            EXPECTED_RUNTIME_ONLY_COUNT,
            len(restored.runtime_only_exclusions),
        )

    def test_default_manifest_covers_revision_one_constructs_and_ownership(self) -> None:
        manifest = default_grcl9v3_lowering_manifest()
        construct_kinds = {
            construct_kind
            for entry in manifest.entries
            for construct_kind in entry.source_construct_kinds
        }
        ownership_tags = {
            ownership for entry in manifest.entries for ownership in entry.ownership_tags
        }

        self.assertTrue(construct_kinds <= GRCL9V3_ACCEPTED_SOURCE_CONSTRUCT_KINDS)
        self.assertIn("hybrid_spark_region", construct_kinds)
        self.assertIn("choice_collapse_region", construct_kinds)
        self.assertIn("growth_locus", construct_kinds)
        self.assertIn("appendix_e_division_region", construct_kinds)
        self.assertNotIn("transport_rerouting_region", construct_kinds)
        self.assertNotIn("quiescent_hybrid_region", construct_kinds)
        self.assertTrue(ownership_tags <= GRCL9V3_OWNERSHIP_TAGS)
        self.assertEqual(GRCL9V3_OWNERSHIP_TAGS, ownership_tags)

    def test_expected_telemetry_paths_are_contract_aligned(self) -> None:
        manifest = default_grcl9v3_lowering_manifest()
        all_expectations = [
            expectation
            for entry in manifest.entries
            for expectation in entry.expected_telemetry
        ]

        self.assertTrue(all_expectations)
        self.assertTrue(
            all(
                expectation.field_path.startswith("family_extensions.grc9v3.")
                for expectation in all_expectations
            )
        )
        self.assertFalse(
            any("event_counts_by_kind" in expectation.field_path for expectation in all_expectations)
        )
        self.assertTrue(any(not expectation.required for expectation in all_expectations))

    def test_runtime_only_records_are_exclusions_not_source_entries(self) -> None:
        manifest = default_grcl9v3_lowering_manifest()
        entry_motif_ids = set(manifest.source_candidate_motif_ids())
        runtime_only_ids = set(manifest.runtime_only_motif_ids())

        self.assertEqual(EXPECTED_RUNTIME_ONLY_COUNT, len(runtime_only_ids))
        self.assertFalse(entry_motif_ids & runtime_only_ids)
        self.assertTrue(
            any(
                item.phenomenon == "hessian_backend_comparison"
                for item in manifest.runtime_only_exclusions
            )
        )
        self.assertTrue(
            any(
                item.phenomenon == "coarse_cache_invalidation"
                for item in manifest.runtime_only_exclusions
            )
        )

    def test_future_vocabulary_records_are_preserved(self) -> None:
        manifest = default_grcl9v3_lowering_manifest()
        future_ids = set(manifest.future_vocabulary_motif_ids())

        self.assertEqual(EXPECTED_FUTURE_VOCABULARY_COUNT, len(future_ids))
        self.assertIn(
            "grc9v3-motif-s0006-transport-basin-rerouting-positive-control",
            future_ids,
        )
        self.assertIn(
            "grc9v3-motif-s0006-quiescent-hybrid-control-no-event-control",
            future_ids,
        )
        self.assertTrue(
            all(record.required_vocabulary for record in manifest.future_vocabulary_records)
        )

    def test_rejects_stale_event_counts_path(self) -> None:
        with self.assertRaisesRegex(ValueError, "event_counts_by_kind"):
            GRCL9V3TelemetryExpectation(
                field_path="event_counts_by_kind.hybrid_spark_candidate",
                surface="run_summary.json",
                predicate="> 0",
                expected_type="int",
            )

    def test_rejects_non_grc9v3_telemetry_path(self) -> None:
        with self.assertRaisesRegex(ValueError, "family_extensions.grc9v3"):
            GRCL9V3TelemetryExpectation(
                field_path="family_extensions.grc9.lifecycle_event_counts.spark_count",
                surface="run_summary.json",
                predicate="> 0",
                expected_type="int",
            )

    def test_rejects_duplicate_reviewed_motif_ids(self) -> None:
        control = _control()
        entry_a = _entry("grcl9v3_duplicate_a", control)
        entry_b = _entry("grcl9v3_duplicate_b", control)

        with self.assertRaisesRegex(ValueError, "reviewed_motif_id values must be unique"):
            GRCL9V3LoweringManifest(
                entries=(entry_a, entry_b),
                future_vocabulary_records=(),
                runtime_only_exclusions=(
                    GRCL9V3RuntimeOnlyExclusion(
                        motif_id="grc9v3-motif-s0006-budget-preservation-positive-control",
                        phenomenon="budget_preservation",
                        lane_name="budget_preservation_positive_control",
                        reason="runtime diagnostic",
                    ),
                ),
            )

    def test_reviewed_motif_ids_use_explicit_hyphenated_format(self) -> None:
        with self.assertRaisesRegex(ValueError, "reviewed GRC9V3 motif-id format"):
            GRCL9V3LoweringControl(
                control_role="positive_control",
                source_fixture_name="hybrid_spark_gate_positive_control",
                source_construct_id="hybrid_spark_gate_positive_control",
                reviewed_motif_id="hybrid_spark_gate_positive_control",
                s0014_lane="hybrid_spark_gate_positive_control",
                expected_outcome="hybrid spark evidence is observed",
            )
        with self.assertRaisesRegex(ValueError, "reviewed GRC9V3 motif-id format"):
            GRCL9V3RuntimeOnlyExclusion(
                motif_id="runtime_only",
                phenomenon="budget_preservation",
                lane_name="budget_preservation_positive_control",
                reason="runtime diagnostic",
            )

    def test_rejects_unsupported_construct_kind_and_ownership(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported source construct kind"):
            _entry("grcl9v3_bad_construct", _control(), construct_kinds=("spark_happened",))
        with self.assertRaisesRegex(ValueError, "unsupported ownership tag"):
            _entry("grcl9v3_bad_ownership", _control(), ownership=("grc9",))

    def test_rejects_runtime_result_smuggling_in_graph_preconditions(self) -> None:
        with self.assertRaisesRegex(ValueError, "runtime-result key"):
            _entry(
                "grcl9v3_bad_runtime_key",
                _control(),
                graph_preconditions={"event_counts_by_kind": {"growth": 1}},
            )

    def test_rejects_unregistered_lowering_carrier_namespace(self) -> None:
        with self.assertRaisesRegex(ValueError, "GRCL-9V3 carrier namespaces"):
            _entry(
                "grcl9v3_bad_carrier",
                _control(),
                lowering_carriers=("cached_quantities.grcl9_provenance",),
            )

    def test_validates_default_manifest_against_s0014_handoff(self) -> None:
        summary = validate_grcl9v3_manifest_against_handoff(
            default_grcl9v3_lowering_manifest()
        )

        self.assertEqual(8, summary["source_expression_candidate_count"])
        self.assertEqual(12, summary["future_vocabulary_count"])
        self.assertEqual(6, summary["runtime_only_count"])

    def test_telemetry_prefix_is_centralized_constant(self) -> None:
        expectation = GRCL9V3TelemetryExpectation(
            field_path=f"{GRCL9V3_TELEMETRY_FIELD_PREFIX}contract_version",
            surface="steps.jsonl",
            predicate="matches contract version",
            expected_type="string",
        )

        self.assertEqual(
            "family_extensions.grc9v3.contract_version",
            expectation.field_path,
        )

    def test_manifest_is_exported_from_landscape_extensions(self) -> None:
        self.assertIs(exported_default_manifest, default_grcl9v3_lowering_manifest)


def _control() -> GRCL9V3LoweringControl:
    return GRCL9V3LoweringControl(
        control_role="positive_control",
        source_fixture_name="hybrid_spark_gate_positive_control",
        source_construct_id="hybrid_spark_gate_positive_control",
        reviewed_motif_id="grc9v3-motif-s0006-hybrid-spark-gate-positive-control",
        s0014_lane="hybrid_spark_gate_positive_control",
        expected_outcome="hybrid spark evidence is observed",
    )


def _entry(
    entry_id: str,
    control: GRCL9V3LoweringControl,
    *,
    construct_kinds: tuple[str, ...] = ("hybrid_spark_region",),
    ownership: tuple[str, ...] = ("grc9v3_hybrid",),
    graph_preconditions: dict[str, object] | None = None,
    lowering_carriers: tuple[str, ...] = ("cached_quantities.grcl9v3_provenance",),
) -> GRCL9V3LoweringManifestEntry:
    return GRCL9V3LoweringManifestEntry(
        entry_id=entry_id,
        phenomenon="hybrid_spark_gate",
        source_construct_kinds=construct_kinds,
        ownership_tags=ownership,
        graph_preconditions=graph_preconditions or {"saturated_identity_region": True},
        required_source_knobs=("candidate_region_id",),
        lowering_carriers=lowering_carriers,
        expected_telemetry=(
            GRCL9V3TelemetryExpectation(
                field_path="family_extensions.grc9v3.lifecycle_event_counts.hybrid_spark_candidate_count",
                surface="run_summary.json",
                predicate="> 0",
                expected_type="int",
            ),
        ),
        controls=(control,),
    )


if __name__ == "__main__":
    unittest.main()

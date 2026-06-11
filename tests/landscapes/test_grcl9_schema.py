"""Tests for the GRCL-9 source schema contract."""

from __future__ import annotations

import json
import unittest

from pygrc.landscapes.extensions.grcl9 import (
    GRCL9BridgePolicy,
    GRCL9BudgetPolicy,
    GRCL9ColumnProxyProfile,
    GRCL9ExpansionRefinementRegion,
    GRCL9GrowthLocus,
    GRCL9InstabilityProfile,
    GRCL9PostExpansionFissionGeometry,
    GRCL9SourceDocument,
    GRCL9SparkCandidateRegion,
    GRCL9TelemetryExpectation,
    grcl9_source_construct_from_mapping,
    validate_grcl9_paper_facing_growth_semantics,
)


class GRCL9SourceSchemaTest(unittest.TestCase):
    def _source_document(self) -> GRCL9SourceDocument:
        return GRCL9SourceDocument(
            fixture_name="spark_column_proxy_eps_pass",
            manifest_entry_id="grcl9_lowering_spark_column_proxy_v1",
            expected_selector_ids=("spark_column_proxy_count",),
            constructs=(
                GRCL9SparkCandidateRegion(
                    construct_id="spark_region",
                    motif_id="spark_column_proxy",
                    candidate_id="candidate",
                    coherence_allocation={"candidate": 1.0, "neighbors": 0.5},
                    neighbor_coherence_profile={"column_2": "balanced"},
                    spark_gate_intent="saturation_column_proxy",
                ),
                GRCL9ColumnProxyProfile(
                    construct_id="column_profile",
                    motif_id="spark_column_proxy",
                    candidate_id="candidate",
                    target_column=2,
                    cancellation_mode="cancellation",
                    conductance_profile={"column_2": "balanced"},
                    coherence_profile={"column_2": "near_epsilon"},
                ),
            ),
            expected_telemetry=(
                GRCL9TelemetryExpectation(
                    field_path=(
                        "family_extensions.grc9.lifecycle_event_counts."
                        "spark_column_proxy_count"
                    ),
                    surface="run_summary.json",
                    predicate="> 0",
                    expected_type="int",
                ),
                GRCL9TelemetryExpectation(
                    field_path=(
                        "family_extensions.grc9.growth_summary."
                        "birth_probability_max"
                    ),
                    surface="run_summary.json",
                    predicate="finite when emitted",
                    expected_type="float",
                    required=False,
                ),
            ),
        )

    def test_source_document_round_trips_through_json(self) -> None:
        document = self._source_document()
        payload = document.to_mapping()
        encoded = json.dumps(payload, sort_keys=True)
        restored = GRCL9SourceDocument.from_mapping(json.loads(encoded))

        self.assertEqual(payload, restored.to_mapping())
        self.assertEqual("grcl9.source.v1", restored.source_schema_version)
        self.assertFalse(restored.expected_telemetry[1].required)

    def test_construct_dispatch_parses_specific_constructs(self) -> None:
        mapping = GRCL9GrowthLocus(
            construct_id="growth_locus",
            motif_id="growth_pressure",
            parent_id="parent",
            inactive_parent_port=5,
            pressure_profile={"front": "high"},
            lambda_birth=1.5,
        ).to_mapping()

        parsed = grcl9_source_construct_from_mapping(mapping)

        self.assertIsInstance(parsed, GRCL9GrowthLocus)
        self.assertEqual(mapping, parsed.to_mapping())
        self.assertEqual("legacy_growth_locus", parsed.growth_semantics)
        self.assertEqual("legacy_source_growth_locus", parsed.front_capacity_source)

    def test_front_capacity_growth_round_trips(self) -> None:
        mapping = GRCL9GrowthLocus(
            construct_id="front_growth",
            motif_id="growth_pressure",
            parent_id="candidate",
            inactive_parent_port=5,
            pressure_profile={"front": "high"},
            lambda_birth=1.5,
            growth_semantics="front_capacity",
            front_capacity_source="spark_expansion_front",
            front_source_construct_id="spark_region",
        ).to_mapping()

        parsed = grcl9_source_construct_from_mapping(mapping)

        self.assertIsInstance(parsed, GRCL9GrowthLocus)
        self.assertEqual("front_capacity", parsed.growth_semantics)
        self.assertEqual("spark_expansion_front", parsed.front_capacity_source)
        self.assertEqual("spark_region", parsed.front_source_construct_id)

    def test_pressure_boundary_front_capacity_growth_round_trips(self) -> None:
        mapping = GRCL9GrowthLocus(
            construct_id="pressure_boundary_growth",
            motif_id="growth_pressure",
            parent_id="candidate",
            inactive_parent_port=5,
            pressure_profile={"front": "pressure_boundary", "pressure": "high"},
            lambda_birth=1.5,
            growth_semantics="front_capacity",
            front_capacity_source="pressure_boundary",
        ).to_mapping()

        parsed = grcl9_source_construct_from_mapping(mapping)

        self.assertIsInstance(parsed, GRCL9GrowthLocus)
        self.assertEqual("front_capacity", parsed.growth_semantics)
        self.assertEqual("pressure_boundary", parsed.front_capacity_source)
        self.assertIsNone(parsed.front_source_construct_id)

    def test_paper_facing_growth_semantics_rejects_legacy_growth_locus(self) -> None:
        document = GRCL9SourceDocument(
            fixture_name="legacy_growth",
            manifest_entry_id="grcl9_lowering_growth_pressure_v1",
            expected_selector_ids=("growth_events",),
            constructs=(
                GRCL9GrowthLocus(
                    construct_id="growth_locus",
                    motif_id="growth_pressure",
                    parent_id="parent",
                    inactive_parent_port=5,
                    pressure_profile={"pressure": "high"},
                    lambda_birth=1.5,
                ),
            ),
        )

        with self.assertRaisesRegex(ValueError, "standalone executable growth_locus"):
            validate_grcl9_paper_facing_growth_semantics(document)

    def test_paper_facing_growth_semantics_accepts_front_capacity_growth(self) -> None:
        document = GRCL9SourceDocument(
            fixture_name="front_growth",
            manifest_entry_id="grcl9_lowering_growth_pressure_v1",
            expected_selector_ids=("front_growth_provenance",),
            constructs=(
                GRCL9SparkCandidateRegion(
                    construct_id="spark_region",
                    motif_id="growth_pressure",
                    candidate_id="candidate",
                    coherence_allocation={"candidate": 1.0},
                    neighbor_coherence_profile={"active_degree": 9},
                    spark_gate_intent="saturation_column_proxy",
                ),
                GRCL9GrowthLocus(
                    construct_id="front_growth",
                    motif_id="growth_pressure",
                    parent_id="candidate",
                    inactive_parent_port=5,
                    pressure_profile={"pressure": "front"},
                    lambda_birth=1.5,
                    growth_semantics="front_capacity",
                    front_capacity_source="spark_expansion_front",
                    front_source_construct_id="spark_region",
                ),
            ),
        )

        result = validate_grcl9_paper_facing_growth_semantics(document)

        self.assertEqual("front_capacity", result["growth_semantics"])
        self.assertEqual("front_growth", result["growth_records"][0]["construct_id"])

    def test_invalid_spark_gate_intent_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "spark_gate_intent"):
            GRCL9SparkCandidateRegion(
                construct_id="spark_region",
                motif_id="spark",
                candidate_id="candidate",
                coherence_allocation={},
                neighbor_coherence_profile={},
                spark_gate_intent="combined",
            )

    def test_reserved_spark_gate_intent_requires_non_executable(self) -> None:
        with self.assertRaisesRegex(ValueError, "reserved spark gate"):
            GRCL9SparkCandidateRegion(
                construct_id="spark_region",
                motif_id="spark",
                candidate_id="candidate",
                coherence_allocation={},
                neighbor_coherence_profile={},
                spark_gate_intent="saturation_sign_crossing",
            )

        deferred = GRCL9SparkCandidateRegion(
            construct_id="spark_region",
            motif_id="spark",
            executable=False,
            candidate_id="candidate",
            coherence_allocation={},
            neighbor_coherence_profile={},
            spark_gate_intent="saturation_sign_crossing",
        )
        self.assertFalse(deferred.executable)

    def test_missing_required_source_fields_fail(self) -> None:
        with self.assertRaisesRegex(ValueError, "candidate_id"):
            GRCL9SourceDocument.from_mapping(
                {
                    "fixture_name": "bad_fixture",
                    "manifest_entry_id": "grcl9_lowering_spark_column_proxy_v1",
                    "constructs": [
                        {
                            "construct_kind": "spark_candidate_region",
                            "construct_id": "spark_region",
                            "motif_id": "spark",
                            "coherence_allocation": {},
                            "neighbor_coherence_profile": {},
                            "spark_gate_intent": "saturation_column_proxy",
                        }
                    ],
                }
            )

    def test_bridge_policy_requires_bridge_edge_kind(self) -> None:
        with self.assertRaisesRegex(ValueError, 'grcl9_edge_kind = "bridge"'):
            GRCL9BridgePolicy(edge_kind="transport")

    def test_budget_policy_rejects_unknown_policy(self) -> None:
        with self.assertRaisesRegex(ValueError, "budget_preservation_policy"):
            GRCL9BudgetPolicy(budget_preservation_policy="copy_mass")

    def test_runtime_result_smuggling_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "encodes runtime results"):
            GRCL9ColumnProxyProfile(
                construct_id="column_profile",
                motif_id="spark",
                candidate_id="candidate",
                target_column=2,
                cancellation_mode="cancellation",
                conductance_profile={"event_counts_by_kind": {"spark": 1}},
                coherence_profile={},
            )

    def test_all_revision_one_constructs_round_trip(self) -> None:
        constructs = (
            GRCL9InstabilityProfile(
                construct_id="instability",
                motif_id="spark_instability",
                candidate_id="candidate",
                row_anisotropy_profile={"row_1": "high"},
                support_cut_profile={"cut": "high"},
                tau_instability=0.25,
            ),
            GRCL9ExpansionRefinementRegion(
                construct_id="expansion",
                motif_id="expansion_refinement",
                candidate_id="candidate",
                target_effective_degree=30,
                bond_weight_mode="fixed",
                coherence_transfer_mode="equal",
            ),
            GRCL9PostExpansionFissionGeometry(
                construct_id="fission",
                motif_id="post_expansion_fission",
                module_region_id="module",
                sink_region_a="sink_a",
                sink_region_b="sink_b",
                identity_fission_min_basin_mass=0.1,
                identity_fission_persistence_delta=3,
            ),
        )

        for construct in constructs:
            restored = grcl9_source_construct_from_mapping(construct.to_mapping())
            self.assertEqual(construct.to_mapping(), restored.to_mapping())

    def test_fission_construct_does_not_accept_same_sink_twice(self) -> None:
        with self.assertRaisesRegex(ValueError, "sink regions must be distinct"):
            GRCL9PostExpansionFissionGeometry(
                construct_id="fission",
                motif_id="post_expansion_fission",
                module_region_id="module",
                sink_region_a="sink",
                sink_region_b="sink",
                identity_fission_min_basin_mass=0.1,
                identity_fission_persistence_delta=3,
            )


if __name__ == "__main__":
    unittest.main()

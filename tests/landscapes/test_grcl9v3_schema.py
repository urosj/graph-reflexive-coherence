"""Tests for the GRCL-9V3 source schema contract."""

from __future__ import annotations

import json
import unittest

from pygrc.landscapes.extensions import (
    GRCL9V3HybridSparkRegion as ExportedHybridSparkRegion,
)
from pygrc.landscapes.extensions.grcl9v3 import (
    GRCL9V3AppendixEDivisionRegion,
    GRCL9V3BridgePolicy,
    GRCL9V3BudgetPolicy,
    GRCL9V3ChoiceCollapseRegion,
    GRCL9V3ColumnProxyFallbackProfile,
    GRCL9V3ExpansionRefinementRegion,
    GRCL9V3GrowthLocus,
    GRCL9V3HybridSparkRegion,
    GRCL9V3HybridTensorProfile,
    GRCL9V3ProvenancePolicy,
    GRCL9V3QuiescentHybridRegion,
    GRCL9V3RowBasisHessianProfile,
    GRCL9V3SourceDocument,
    GRCL9V3TelemetryExpectation,
    GRCL9V3TransportReroutingRegion,
    grcl9v3_source_construct_from_mapping,
    validate_grcl9v3_paper_facing_growth_semantics,
    validate_grcl9v3_source_document_against_manifest,
)


MOTIF_ID = "grc9v3-motif-s0006-hybrid-spark-gate-positive-control"


class GRCL9V3SourceSchemaTest(unittest.TestCase):
    def _source_document(self) -> GRCL9V3SourceDocument:
        return GRCL9V3SourceDocument(
            fixture_name="hybrid_spark_gate_positive_control",
            manifest_entry_id="grcl9v3_lowering_hybrid_spark_gate_v1",
            expected_selector_ids=("hybrid_spark_events",),
            constructs=(
                GRCL9V3HybridSparkRegion(
                    construct_id="spark_region",
                    motif_id=MOTIF_ID,
                    source_role="positive_control",
                    ownership="grc9v3_hybrid",
                    expected_selector_ids=("hybrid_spark_events",),
                    candidate_region_id="candidate",
                    saturation_profile={"active_degree": 9},
                    spark_threshold=0.05,
                ),
                GRCL9V3HybridTensorProfile(
                    construct_id="tensor_profile",
                    motif_id=MOTIF_ID,
                    source_role="positive_control",
                    ownership="grc9v3_hybrid",
                    region_id="candidate",
                    anisotropy_axis="row_2",
                    tensor_profile={"row_mismatch": "high"},
                ),
            ),
            expected_telemetry=(
                GRCL9V3TelemetryExpectation(
                    field_path=(
                        "family_extensions.grc9v3.lifecycle_event_counts."
                        "hybrid_spark_candidate_count"
                    ),
                    surface="run_summary.json",
                    predicate="> 0",
                    expected_type="int",
                ),
            ),
            notes={"source_boundary": "runtime_evidence_only"},
        )

    def test_source_document_round_trips_through_json(self) -> None:
        document = self._source_document()
        payload = document.to_mapping()
        encoded = json.dumps(payload, sort_keys=True)
        restored = GRCL9V3SourceDocument.from_mapping(json.loads(encoded))

        self.assertEqual(payload, restored.to_mapping())
        self.assertEqual("grcl9v3.source.v1", restored.source_schema_version)
        self.assertEqual("extensions.grcl9v3", restored.provenance_policy.source_member_path)

    def test_construct_dispatch_parses_specific_construct(self) -> None:
        mapping = GRCL9V3GrowthLocus(
            construct_id="growth_locus",
            motif_id="grc9v3-motif-s0006-growth-pressure-positive-control",
            source_role="positive_control",
            ownership="grc9_mechanical",
            parent_region_id="parent",
            inactive_parent_port=5,
            outward_pressure_profile={"front": "high"},
            lambda_birth=1.5,
        ).to_mapping()

        parsed = grcl9v3_source_construct_from_mapping(mapping)

        self.assertIsInstance(parsed, GRCL9V3GrowthLocus)
        self.assertEqual(mapping, parsed.to_mapping())
        self.assertEqual("legacy_growth_locus", parsed.growth_semantics)
        self.assertEqual("legacy_source_growth_locus", parsed.front_capacity_source)

    def test_front_capacity_growth_round_trips(self) -> None:
        mapping = GRCL9V3GrowthLocus(
            construct_id="front_growth",
            motif_id=MOTIF_ID,
            source_role="positive_control",
            ownership="grc9_mechanical",
            parent_region_id="candidate",
            inactive_parent_port=5,
            outward_pressure_profile={"pressure": "front"},
            lambda_birth=0.5,
            growth_semantics="front_capacity",
            front_capacity_source="spark_expansion_front",
            front_source_construct_id="spark_region",
        ).to_mapping()

        parsed = grcl9v3_source_construct_from_mapping(mapping)

        self.assertIsInstance(parsed, GRCL9V3GrowthLocus)
        self.assertEqual("front_capacity", parsed.growth_semantics)
        self.assertEqual("spark_expansion_front", parsed.front_capacity_source)
        self.assertEqual("spark_region", parsed.front_source_construct_id)

    def test_pressure_boundary_front_capacity_growth_round_trips(self) -> None:
        mapping = GRCL9V3GrowthLocus(
            construct_id="pressure_boundary_growth",
            motif_id=MOTIF_ID,
            source_role="positive_control",
            ownership="grc9_mechanical",
            parent_region_id="boundary_parent",
            inactive_parent_port=6,
            outward_pressure_profile={"pressure": "boundary_front"},
            lambda_birth=0.75,
            growth_semantics="front_capacity",
            front_capacity_source="pressure_boundary",
        ).to_mapping()

        parsed = grcl9v3_source_construct_from_mapping(mapping)

        self.assertIsInstance(parsed, GRCL9V3GrowthLocus)
        self.assertEqual("front_capacity", parsed.growth_semantics)
        self.assertEqual("pressure_boundary", parsed.front_capacity_source)
        self.assertIsNone(parsed.front_source_construct_id)

    def test_paper_facing_growth_semantics_rejects_legacy_growth_locus(self) -> None:
        document = GRCL9V3SourceDocument(
            fixture_name="legacy_growth",
            manifest_entry_id="future_vocabulary_growth_pressure_v1",
            expected_selector_ids=("growth_events",),
            constructs=(
                GRCL9V3GrowthLocus(
                    construct_id="growth_locus",
                    motif_id="grc9v3-motif-s0006-growth-pressure-positive-control",
                    source_role="positive_control",
                    ownership="grc9_mechanical",
                    parent_region_id="parent",
                    inactive_parent_port=5,
                    outward_pressure_profile={"pressure": "high"},
                    lambda_birth=1.5,
                ),
            ),
        )

        with self.assertRaisesRegex(ValueError, "standalone executable growth_locus"):
            validate_grcl9v3_paper_facing_growth_semantics(document)

    def test_paper_facing_growth_semantics_accepts_front_capacity_growth(self) -> None:
        document = GRCL9V3SourceDocument(
            fixture_name="front_growth",
            manifest_entry_id="composed_grcl9v3_hybrid_composition_v1",
            expected_selector_ids=("front_growth_provenance",),
            constructs=(
                GRCL9V3HybridSparkRegion(
                    construct_id="spark_region",
                    motif_id=MOTIF_ID,
                    source_role="positive_control",
                    ownership="grc9v3_hybrid",
                    candidate_region_id="candidate",
                    saturation_profile={"active_degree": 9},
                    spark_threshold=0.05,
                ),
                GRCL9V3GrowthLocus(
                    construct_id="front_growth",
                    motif_id=MOTIF_ID,
                    source_role="positive_control",
                    ownership="grc9_mechanical",
                    parent_region_id="candidate",
                    inactive_parent_port=5,
                    outward_pressure_profile={"pressure": "front"},
                    lambda_birth=0.5,
                    growth_semantics="front_capacity",
                    front_capacity_source="spark_expansion_front",
                    front_source_construct_id="spark_region",
                ),
            ),
            compiled_source_provenance={"composed_source_ancestry": ("spark", "growth")},
        )

        result = validate_grcl9v3_paper_facing_growth_semantics(document)

        self.assertEqual("front_capacity", result["growth_semantics"])
        self.assertEqual("front_growth", result["growth_records"][0]["construct_id"])

    def test_all_revision_one_constructs_round_trip(self) -> None:
        constructs = (
            GRCL9V3RowBasisHessianProfile(
                construct_id="hessian",
                motif_id=MOTIF_ID,
                source_role="positive_control",
                ownership="grcv3_semantic",
                candidate_region_id="candidate",
                row_basis_profile={"row_1": "weak"},
            ),
            GRCL9V3ColumnProxyFallbackProfile(
                construct_id="column_proxy",
                motif_id=MOTIF_ID,
                source_role="positive_control",
                ownership="grc9_mechanical",
                candidate_region_id="candidate",
                target_column=2,
                column_profile={"column_2": "near_cancellation"},
            ),
            GRCL9V3ExpansionRefinementRegion(
                construct_id="expansion",
                motif_id="grc9v3-motif-s0006-spark-to-expansion-positive-control",
                source_role="positive_control",
                ownership="grc9_mechanical",
                candidate_region_id="candidate",
                target_effective_degree=30,
            ),
            GRCL9V3ChoiceCollapseRegion(
                construct_id="choice",
                motif_id="grc9v3-motif-s0006-choice-collapse-positive-control",
                source_role="positive_control",
                ownership="grcv3_semantic",
                choice_region_id="choice_region",
                basin_region_a="basin_a",
                basin_region_b="basin_b",
                collapse_target_region="basin_a",
                compatibility_profile={"contrast": "high"},
            ),
            GRCL9V3TransportReroutingRegion(
                construct_id="transport",
                motif_id="grc9v3-motif-s0006-transport-basin-rerouting-positive-control",
                source_role="positive_control",
                ownership="shared_runtime",
                route_region_id="route",
                source_region_id="source",
                sink_region_id="sink",
                route_preference_profile={"corridor": "preferred"},
            ),
            GRCL9V3AppendixEDivisionRegion(
                construct_id="division",
                motif_id="grc9v3-motif-s0006-appendix-e-cell-division-positive-control",
                source_role="positive_control",
                ownership="grc9v3_hybrid",
                parent_region_id="parent",
                daughter_region_a="daughter_a",
                daughter_region_b="daughter_b",
                module_basin_support={"mass": "balanced"},
            ),
            GRCL9V3QuiescentHybridRegion(
                construct_id="quiescent",
                motif_id="grc9v3-motif-s0006-quiescent-hybrid-control-no-event-control",
                source_role="no_event_control",
                ownership="grc9v3_hybrid",
                region_id="quiet",
                stability_margin_profile={"active_degree": 5},
            ),
        )

        for construct in constructs:
            restored = grcl9v3_source_construct_from_mapping(construct.to_mapping())
            self.assertEqual(construct.to_mapping(), restored.to_mapping())

    def test_missing_required_source_fields_fail(self) -> None:
        with self.assertRaisesRegex(ValueError, "candidate_region_id"):
            GRCL9V3SourceDocument.from_mapping(
                {
                    "fixture_name": "bad_fixture",
                    "manifest_entry_id": "grcl9v3_lowering_hybrid_spark_gate_v1",
                    "expected_selector_ids": ["hybrid_spark_events"],
                    "constructs": [
                        {
                            "construct_kind": "hybrid_spark_region",
                            "construct_id": "spark_region",
                            "motif_id": MOTIF_ID,
                            "source_role": "positive_control",
                            "ownership": "grc9v3_hybrid",
                            "saturation_profile": {},
                        }
                    ],
                }
            )

    def test_invalid_ownership_and_motif_id_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "ownership"):
            GRCL9V3HybridSparkRegion(
                construct_id="spark_region",
                motif_id=MOTIF_ID,
                source_role="positive_control",
                ownership="grc9",
                candidate_region_id="candidate",
                saturation_profile={},
            )
        with self.assertRaisesRegex(ValueError, "reviewed GRC9V3 motif-id"):
            GRCL9V3HybridSparkRegion(
                construct_id="spark_region",
                motif_id="hybrid_spark_gate",
                source_role="positive_control",
                ownership="grc9v3_hybrid",
                candidate_region_id="candidate",
                saturation_profile={},
            )

    def test_runtime_result_smuggling_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "encodes runtime results"):
            GRCL9V3HybridTensorProfile(
                construct_id="tensor_profile",
                motif_id=MOTIF_ID,
                source_role="positive_control",
                ownership="grc9v3_hybrid",
                region_id="candidate",
                tensor_profile={"event_counts_by_kind": {"hybrid_spark_candidate": 1}},
            )
        with self.assertRaisesRegex(ValueError, "encodes runtime results"):
            GRCL9V3SourceDocument(
                fixture_name="bad_notes",
                manifest_entry_id="grcl9v3_lowering_hybrid_spark_gate_v1",
                expected_selector_ids=("hybrid_spark_events",),
                constructs=(
                    GRCL9V3HybridSparkRegion(
                        construct_id="spark_region",
                        motif_id=MOTIF_ID,
                        source_role="positive_control",
                        ownership="grc9v3_hybrid",
                        candidate_region_id="candidate",
                        saturation_profile={},
                    ),
                ),
                notes={"spark_happened": True},
            )

    def test_policy_validation(self) -> None:
        with self.assertRaisesRegex(ValueError, 'grcl9v3_edge_kind = "bridge"'):
            GRCL9V3BridgePolicy(edge_kind="transport")
        with self.assertRaisesRegex(ValueError, "budget_preservation_policy"):
            GRCL9V3BudgetPolicy(budget_preservation_policy="copy_mass")
        with self.assertRaisesRegex(ValueError, "source_member_path"):
            GRCL9V3ProvenancePolicy(source_member_path="extensions.grcl9")

    def test_source_document_requires_shared_motif_id(self) -> None:
        with self.assertRaisesRegex(ValueError, "share one motif_id"):
            GRCL9V3SourceDocument(
                fixture_name="mixed_fixture",
                manifest_entry_id="grcl9v3_lowering_hybrid_spark_gate_v1",
                expected_selector_ids=("hybrid_spark_events",),
                constructs=(
                    GRCL9V3HybridSparkRegion(
                        construct_id="spark_region",
                        motif_id=MOTIF_ID,
                        source_role="positive_control",
                        ownership="grc9v3_hybrid",
                        candidate_region_id="candidate",
                        saturation_profile={},
                    ),
                    GRCL9V3GrowthLocus(
                        construct_id="growth",
                        motif_id="grc9v3-motif-s0006-growth-pressure-positive-control",
                        source_role="positive_control",
                        ownership="grc9_mechanical",
                        parent_region_id="parent",
                        inactive_parent_port=4,
                        outward_pressure_profile={},
                        lambda_birth=1.0,
                    ),
                ),
            )

    def test_construct_specific_validation(self) -> None:
        with self.assertRaisesRegex(ValueError, "coherence_transfer_ratios"):
            GRCL9V3ExpansionRefinementRegion(
                construct_id="expansion",
                motif_id="grc9v3-motif-s0006-spark-to-expansion-positive-control",
                source_role="positive_control",
                ownership="grc9_mechanical",
                candidate_region_id="candidate",
                coherence_transfer_ratios=(0.5, 0.5, 0.5),
            )
        with self.assertRaisesRegex(ValueError, "basin regions must be distinct"):
            GRCL9V3ChoiceCollapseRegion(
                construct_id="choice",
                motif_id="grc9v3-motif-s0006-choice-collapse-positive-control",
                source_role="positive_control",
                ownership="grcv3_semantic",
                choice_region_id="choice_region",
                basin_region_a="basin",
                basin_region_b="basin",
                collapse_target_region="basin",
                compatibility_profile={},
            )
        with self.assertRaisesRegex(ValueError, "daughter regions must be distinct"):
            GRCL9V3AppendixEDivisionRegion(
                construct_id="division",
                motif_id="grc9v3-motif-s0006-appendix-e-cell-division-positive-control",
                source_role="positive_control",
                ownership="grc9v3_hybrid",
                parent_region_id="parent",
                daughter_region_a="daughter",
                daughter_region_b="daughter",
                module_basin_support={},
            )

    def test_non_executable_construct_requires_non_claim(self) -> None:
        with self.assertRaisesRegex(ValueError, "non_executable_source_construct"):
            GRCL9V3HybridSparkRegion(
                construct_id="spark_region",
                motif_id=MOTIF_ID,
                source_role="positive_control",
                ownership="grc9v3_hybrid",
                executable=False,
                candidate_region_id="candidate",
                saturation_profile={},
            )

        construct = GRCL9V3HybridSparkRegion(
            construct_id="spark_region",
            motif_id=MOTIF_ID,
            source_role="positive_control",
            ownership="grc9v3_hybrid",
            executable=False,
            non_claims=(
                "no_grcl9v3_lowering_result_claim",
                "no_runtime_event_claim",
                "no_lorentzian_causal_layer_claim",
                "no_visual_only_promotion",
                "runtime_evidence_required",
                "non_executable_source_construct",
            ),
            candidate_region_id="candidate",
            saturation_profile={},
        )
        self.assertFalse(construct.executable)

    def test_column_proxy_directly_enforces_three_column_range(self) -> None:
        with self.assertRaisesRegex(ValueError, "three GRC9 columns"):
            GRCL9V3ColumnProxyFallbackProfile(
                construct_id="column_proxy",
                motif_id=MOTIF_ID,
                source_role="positive_control",
                ownership="grc9_mechanical",
                candidate_region_id="candidate",
                target_column=4,
                column_profile={},
            )

    def test_source_document_validates_against_manifest(self) -> None:
        document = self._source_document()
        summary = validate_grcl9v3_source_document_against_manifest(document)

        self.assertEqual(
            "grcl9v3_lowering_hybrid_spark_gate_v1",
            summary["manifest_entry_id"],
        )
        self.assertEqual([MOTIF_ID], summary["motif_ids"])

    def test_manifest_linkage_rejects_unknown_entry_and_wrong_construct(self) -> None:
        document = self._source_document()
        bad_entry_document = GRCL9V3SourceDocument(
            fixture_name=document.fixture_name,
            manifest_entry_id="unknown_entry",
            expected_selector_ids=document.expected_selector_ids,
            constructs=document.constructs,
        )
        with self.assertRaisesRegex(ValueError, "manifest_entry_id"):
            validate_grcl9v3_source_document_against_manifest(bad_entry_document)

        wrong_construct_document = GRCL9V3SourceDocument(
            fixture_name="bad_construct_link",
            manifest_entry_id="grcl9v3_lowering_growth_pressure_v1",
            expected_selector_ids=("growth_events",),
            constructs=document.constructs,
        )
        with self.assertRaisesRegex(ValueError, "motif_id"):
            validate_grcl9v3_source_document_against_manifest(wrong_construct_document)

    def test_schema_is_exported_from_landscape_extensions(self) -> None:
        self.assertIs(ExportedHybridSparkRegion, GRCL9V3HybridSparkRegion)


if __name__ == "__main__":
    unittest.main()

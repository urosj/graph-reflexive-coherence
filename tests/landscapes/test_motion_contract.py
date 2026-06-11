from __future__ import annotations

import unittest

from pygrc.core import InvalidLandscapeSeedError, canonical_json_dumps
from pygrc.landscapes import (
    LANDSCAPE_INFERENCE_EXTENSION_NAMESPACE,
    MOTION_INFERENCE_AUTHORITY,
    MOTION_INFERENCE_CONFIDENCE_THRESHOLDS,
    MOTION_INFERENCE_CONTRACT_VERSION,
    MOTION_INFERENCE_EVIDENCE_QUALITY,
    MOTION_INFERENCE_EXTENSION_NAMESPACE,
    MOTION_INFERENCE_KINDS,
    MOTION_INFERENCE_RELATIONSHIPS,
    BasinSeedPrimitive,
    LandscapeSeed,
    MotionCarrierSet,
    MotionCheckpointSpacing,
    MotionCompetingClaim,
    MotionEvidence,
    MotionPrimitiveExtension,
    MotionRecord,
    MotionReport,
    MotionWindow,
    SeedConstitutiveProfile,
    SeedDocumentMeta,
    SeedPotential,
    landscape_seed_from_data,
    landscape_seed_to_data,
    motion_primitive_extension_mapping,
    motion_record_mapping,
    motion_report_mapping,
    validate_motion_seed_extensions,
)


def _profile() -> SeedConstitutiveProfile:
    return SeedConstitutiveProfile(
        lambda_c=1.0,
        xi_c=1.0,
        zeta_c=0.1,
        kappa_c=0.5,
        dt=0.1,
        potential=SeedPotential(type="quadratic"),
    )


def _motion_record() -> MotionRecord:
    return MotionRecord(
        motion_id="motion_identity_walked_001",
        classifier_id="identity_motion_matcher",
        classifier_version="motion_iter1_test_v1",
        motion_kind="identity",
        relationship="walked",
        confidence=0.86,
        evidence_quality="strong",
        source_runtime_family="grc9v3",
        step_window=(4, 9),
        step_ids=(4, 5, 6, 7, 8, 9),
        old_carriers=MotionCarrierSet(node_ids=(4,), basin_ids=("basin_a",)),
        new_carriers=MotionCarrierSet(node_ids=(7,), basin_ids=("basin_a",)),
        transferred_mass=0.75,
        evidence=MotionEvidence(
            telemetry_fields=("family_extensions.grc9v3.transport.flux_abs_sum",),
            checkpoint_ids=("checkpoint_0004", "checkpoint_0009"),
            step_ids=(4, 9),
            node_ids=(4, 7),
            edge_ids=(12,),
            event_ids=("event_choice_4",),
            budget_accountability="redistributes",
        ),
        competing_claims=(
            MotionCompetingClaim(
                relationship="dissolved",
                confidence=0.12,
                reason="old basin mass mostly transfers to the new carrier",
                classifier_id="identity_motion_matcher",
            ),
        ),
        non_claims=("no_source_authored_motion_outcome",),
    )


def _motion_report() -> MotionReport:
    return MotionReport(
        source_session_id="S0001",
        source_runtime_family="grc9v3",
        source_artifact_paths=("outputs/motion/sessions/S0001",),
        motion_window=MotionWindow(
            start_step=4,
            end_step=9,
            checkpoint_ids=("checkpoint_0004", "checkpoint_0009"),
            policy="explicit",
            checkpoint_spacing=MotionCheckpointSpacing(
                spacing_mode="regular",
                step_deltas=(5,),
                time_deltas=(0.5,),
            ),
        ),
        records=(_motion_record(),),
    )


class MotionInferenceContractTest(unittest.TestCase):
    def test_contract_constants_match_iteration_1_boundary(self) -> None:
        self.assertEqual("motion_inference_iter1_v1", MOTION_INFERENCE_CONTRACT_VERSION)
        self.assertEqual("motion_inference", MOTION_INFERENCE_EXTENSION_NAMESPACE)
        self.assertEqual("observed", MOTION_INFERENCE_AUTHORITY)
        self.assertEqual(
            ("coherence", "representative", "identity", "boundary", "topological"),
            MOTION_INFERENCE_KINDS,
        )
        self.assertEqual(
            (
                "stationary",
                "drifted",
                "walked",
                "split",
                "merged",
                "collapsed",
                "dissolved",
                "emerged",
                "ambiguous",
            ),
            MOTION_INFERENCE_RELATIONSHIPS,
        )
        self.assertNotIn("walked_candidate", MOTION_INFERENCE_RELATIONSHIPS)
        self.assertEqual(
            ("strong", "partial", "degraded", "missing_surface", "diagnostic_only"),
            MOTION_INFERENCE_EVIDENCE_QUALITY,
        )
        self.assertEqual(
            {
                "strong": 0.80,
                "partial": 0.50,
                "degraded": 0.40,
                "diagnostic_only": 0.25,
            },
            dict(MOTION_INFERENCE_CONFIDENCE_THRESHOLDS),
        )

    def test_motion_report_round_trips_deterministically(self) -> None:
        report = _motion_report()
        payload = motion_report_mapping(report)
        restored = MotionReport.from_mapping(payload)

        self.assertEqual(
            canonical_json_dumps(payload),
            canonical_json_dumps(motion_report_mapping(restored)),
        )
        record = restored.records[0]
        self.assertEqual("observed", record.authority)
        self.assertEqual("identity_motion_matcher", record.classifier_id)
        self.assertEqual("motion_iter1_test_v1", record.classifier_version)
        self.assertEqual("strong", record.evidence_quality)
        self.assertEqual((4, 9), record.step_window)
        self.assertEqual("dissolved", record.competing_claims[0].relationship)

    def test_motion_record_mapping_is_json_safe(self) -> None:
        payload = motion_record_mapping(_motion_record())

        self.assertEqual("motion_inference_iter1_v1", payload["contract_version"])
        self.assertEqual("observed", payload["authority"])
        self.assertEqual([4, 9], payload["step_window"])
        self.assertEqual([4, 5, 6, 7, 8, 9], payload["step_ids"])
        self.assertEqual([4], payload["old_carriers"]["node_ids"])
        self.assertEqual([7], payload["new_carriers"]["node_ids"])

    def test_motion_extensions_can_coexist_with_landscape_inference_extensions(self) -> None:
        primitive = BasinSeedPrimitive(
            id="observed_basin",
            role="identity_basin",
            extensions={
                LANDSCAPE_INFERENCE_EXTENSION_NAMESPACE: {
                    "contract_version": "landscape_inference_iter1_v1",
                    "authority": "observed",
                    "classifier_id": "basin_classifier",
                    "classifier_version": "test",
                    "confidence": 0.8,
                    "source_runtime_family": "grc9v3",
                    "observed_from": {
                        "session_id": "S0001",
                        "run_id": "run_001",
                        "artifact_root": "outputs/motion/sessions/S0001",
                        "step_window": [4, 9],
                    },
                    "evidence": {
                        "telemetry_fields": ["family_extensions.grc9v3.identity_basin.sink_count"],
                        "checkpoint_ids": ["checkpoint_0004"],
                        "node_ids": [4],
                        "edge_ids": [],
                        "path_node_ids": [],
                    },
                    "matched_authored_primitive_id": None,
                    "relationship_to_authored": "preserved",
                },
                MOTION_INFERENCE_EXTENSION_NAMESPACE: motion_primitive_extension_mapping(
                    MotionPrimitiveExtension(
                        motion_id="motion_identity_walked_001",
                        motion_kind="identity",
                        relationship="walked",
                        source_window=(4, 9),
                        confidence=0.86,
                    )
                ),
            },
        )
        seed = LandscapeSeed(
            seed_schema="pygrc.landscape_seed",
            seed_version="0.1",
            meta=SeedDocumentMeta(
                name="observed landscape with motion",
                source_kind="inferred_observed_landscape",
            ),
            constitutive_profile=_profile(),
            primitives=[primitive],
            extensions={
                MOTION_INFERENCE_EXTENSION_NAMESPACE: {
                    "contract_version": MOTION_INFERENCE_CONTRACT_VERSION,
                    "motion_record_ids": ["motion_identity_walked_001"],
                }
            },
        )

        validate_motion_seed_extensions(seed)
        payload = landscape_seed_to_data(seed)
        restored = landscape_seed_from_data(payload)
        validate_motion_seed_extensions(restored)

        self.assertEqual(
            canonical_json_dumps(payload),
            canonical_json_dumps(landscape_seed_to_data(restored)),
        )

    def test_invalid_labels_confidence_and_empty_carriers_raise(self) -> None:
        valid = motion_record_mapping(_motion_record())

        invalid_relationship = dict(valid)
        invalid_relationship["relationship"] = "walked_candidate"
        with self.assertRaises(InvalidLandscapeSeedError):
            MotionRecord.from_mapping(invalid_relationship)

        invalid_confidence = dict(valid)
        invalid_confidence["confidence"] = 1.5
        with self.assertRaises(InvalidLandscapeSeedError):
            MotionRecord.from_mapping(invalid_confidence)

        with self.assertRaises(InvalidLandscapeSeedError):
            MotionCarrierSet()

    def test_non_stationary_identity_records_require_competing_claims(self) -> None:
        valid = motion_record_mapping(_motion_record())
        valid["competing_claims"] = []

        with self.assertRaises(InvalidLandscapeSeedError):
            MotionRecord.from_mapping(valid)

    def test_runtime_state_smuggling_is_rejected(self) -> None:
        report = motion_report_mapping(_motion_report())
        report["records"][0]["evidence"] = dict(report["records"][0]["evidence"])
        report["records"][0]["evidence"]["node_records"] = [{"node_id": 4}]

        with self.assertRaises(InvalidLandscapeSeedError):
            MotionReport.from_mapping(report)

        primitive_extension = motion_primitive_extension_mapping(
            MotionPrimitiveExtension(
                motion_id="motion_identity_walked_001",
                motion_kind="identity",
                relationship="walked",
                source_window=(4, 9),
                confidence=0.86,
            )
        )
        primitive_extension["topology"] = {}
        with self.assertRaises(InvalidLandscapeSeedError):
            MotionPrimitiveExtension.from_mapping(primitive_extension)


if __name__ == "__main__":
    unittest.main()

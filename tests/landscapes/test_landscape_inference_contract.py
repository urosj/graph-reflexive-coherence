from __future__ import annotations

import unittest

from pygrc.core import InvalidLandscapeSeedError, canonical_json_dumps
from pygrc.landscapes import (
    LANDSCAPE_INFERENCE_AUTHORITIES,
    LANDSCAPE_INFERENCE_CONTRACT_VERSION,
    LANDSCAPE_INFERENCE_RELATIONSHIPS,
    BasinSeedPrimitive,
    LandscapeInferenceEvidence,
    LandscapeInferenceObservedFrom,
    LandscapeInferencePrimitiveExtension,
    LandscapeInferenceTopLevelExtension,
    LandscapeInferenceWindow,
    LandscapeSeed,
    SeedConstitutiveProfile,
    SeedDocumentMeta,
    SeedPotential,
    landscape_inference_primitive_mapping,
    landscape_inference_top_level_mapping,
    landscape_seed_from_data,
    landscape_seed_to_data,
    validate_landscape_inference_seed_extensions,
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


def _top_level_extension() -> LandscapeInferenceTopLevelExtension:
    return LandscapeInferenceTopLevelExtension(
        source_session_id="S0001",
        source_artifact_paths=("outputs/landscape_inference/sessions/S0001",),
        source_runtime_family="grc9v3",
        inference_window=LandscapeInferenceWindow(
            start_step=3,
            end_step=8,
            policy="event_centered",
        ),
    )


def _primitive_extension() -> LandscapeInferencePrimitiveExtension:
    return LandscapeInferencePrimitiveExtension(
        authority="observed",
        classifier_id="basin_classifier_v1",
        classifier_version="iter1_test_v1",
        confidence=0.75,
        source_runtime_family="grc9v3",
        observed_from=LandscapeInferenceObservedFrom(
            session_id="S0001",
            run_id="run_001",
            artifact_root="outputs/landscape_inference/sessions/S0001",
            step_window=(3, 8),
        ),
        evidence=LandscapeInferenceEvidence(
            telemetry_fields=("family_extensions.grc9v3.identity_basin.sink_count",),
            checkpoint_ids=("checkpoint_0003", "checkpoint_0008"),
            node_ids=(1, 2),
        ),
        matched_authored_primitive_id="source_basin",
        relationship_to_authored="preserved",
    )


class LandscapeInferenceContractTest(unittest.TestCase):
    def test_contract_constants_match_iteration_1_boundary(self) -> None:
        self.assertEqual(
            "landscape_inference_iter1_v1",
            LANDSCAPE_INFERENCE_CONTRACT_VERSION,
        )
        self.assertEqual(("authored", "lowered", "observed"), LANDSCAPE_INFERENCE_AUTHORITIES)
        self.assertEqual(
            (
                "preserved",
                "transformed",
                "split",
                "collapsed",
                "emerged",
                "dissolved",
                "unknown",
            ),
            LANDSCAPE_INFERENCE_RELATIONSHIPS,
        )

    def test_inferred_seed_uses_normal_landscape_seed_extensions(self) -> None:
        primitive = BasinSeedPrimitive(
            id="observed_identity_basin",
            role="identity_basin",
            extensions={
                "landscape_inference": landscape_inference_primitive_mapping(
                    _primitive_extension()
                )
            },
        )
        seed = LandscapeSeed(
            seed_schema="pygrc.landscape_seed",
            seed_version="0.1",
            meta=SeedDocumentMeta(
                name="observed landscape",
                source_kind="inferred_observed_landscape",
            ),
            constitutive_profile=_profile(),
            primitives=[primitive],
            extensions={
                "landscape_inference": landscape_inference_top_level_mapping(
                    _top_level_extension()
                )
            },
        )

        validate_landscape_inference_seed_extensions(seed)
        payload = landscape_seed_to_data(seed)
        restored = landscape_seed_from_data(payload)
        validate_landscape_inference_seed_extensions(restored)

        self.assertEqual("basin", restored.primitives[0].type)
        self.assertEqual("identity_basin", restored.primitives[0].role)
        self.assertIn("landscape_inference", restored.extensions)
        self.assertEqual(
            canonical_json_dumps(payload),
            canonical_json_dumps(landscape_seed_to_data(restored)),
        )

    def test_primitive_extension_rejects_invalid_authority_and_relationship(self) -> None:
        valid = landscape_inference_primitive_mapping(_primitive_extension())
        invalid_authority = dict(valid)
        invalid_authority["authority"] = "knowledge_graph_node"
        with self.assertRaises(InvalidLandscapeSeedError):
            LandscapeInferencePrimitiveExtension.from_mapping(invalid_authority)

        invalid_relationship = dict(valid)
        invalid_relationship["relationship_to_authored"] = "same_as"
        with self.assertRaises(InvalidLandscapeSeedError):
            LandscapeInferencePrimitiveExtension.from_mapping(invalid_relationship)

    def test_primitive_extension_requires_real_evidence_reference(self) -> None:
        with self.assertRaises(InvalidLandscapeSeedError):
            LandscapeInferenceEvidence()

    def test_extensions_reject_runtime_state_smuggling(self) -> None:
        top_level = landscape_inference_top_level_mapping(_top_level_extension())
        top_level["node_records"] = [{"node_id": 1}]
        with self.assertRaises(InvalidLandscapeSeedError):
            LandscapeInferenceTopLevelExtension.from_mapping(top_level)

        primitive = landscape_inference_primitive_mapping(_primitive_extension())
        primitive["evidence"] = dict(primitive["evidence"])
        primitive["evidence"]["edge_records"] = [{"edge_id": 1}]
        with self.assertRaises(InvalidLandscapeSeedError):
            LandscapeInferencePrimitiveExtension.from_mapping(primitive)


if __name__ == "__main__":
    unittest.main()

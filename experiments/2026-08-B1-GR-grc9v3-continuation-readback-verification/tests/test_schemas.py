from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SchemaCoverageTest(unittest.TestCase):
    def test_all_normative_schemas_are_valid_json(self) -> None:
        expected = {
            "common_artifact.schema.json", "gate_result_receipt.schema.json",
            "gate_acceptance.schema.json", "baseline_manifest.schema.json",
            "state_codec.schema.json", "fixed_branch_registry.schema.json",
            "complete_step_jacobians.schema.json", "intervention_registry.schema.json",
            "causal_role_matrix.schema.json", "return_orbit_registry.schema.json",
            "grv6_36_point_review_audit.schema.json",
            "spatial_temporal_threshold_matrix.schema.json",
            "grv8_classification.schema.json",
            "evidence_bundle_manifest.schema.json", "assumption_status_matrix.schema.json",
            "lgrc_handoff.schema.json",
        }
        actual = {path.name for path in (ROOT / "schemas").glob("*.schema.json")}
        self.assertEqual(expected, actual)
        for name in expected:
            payload = json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))
            self.assertEqual("https://json-schema.org/draft/2020-12/schema", payload["$schema"])
            self.assertIn("$id", payload)

    def test_common_definitions_cover_required_final_records(self) -> None:
        common = json.loads((ROOT / "schemas/common_artifact.schema.json").read_text(encoding="utf-8"))
        required = {"protectedPathManifest", "experimentPathManifest", "theorySourceManifest", "numericalEnvironment", "contradictionRegister", "theoryReopeningDecision", "extensionDecision", "artifactEnvelope"}
        self.assertTrue(required.issubset(common["$defs"]))

    def test_baseline_schema_requires_exact_specification_identity(self) -> None:
        baseline = json.loads((ROOT / "schemas/baseline_manifest.schema.json").read_text(encoding="utf-8"))
        payload = baseline["properties"]["payload"]
        self.assertIn("specification_id", payload["required"])
        self.assertEqual(
            "b1_grc9v3_continuation_readback_verification_v3_4_1",
            payload["properties"]["specification_id"]["const"],
        )


if __name__ == "__main__":
    unittest.main()

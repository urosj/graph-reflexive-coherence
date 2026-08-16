"""Validate I116 consumer dry runs and the low-context replay freeze."""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from typing import Any

from pygrc.causal_pathways import canonical_digest

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "implementation/evidence/causal-pathway-binding/i116"
SPECIFICATION = (
    ROOT / "implementation/evidence/causal-pathway-binding/"
    "i116-low-context-consumer-specification.json"
)


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"{path} must contain an object")
    return value


def _strings(value: object) -> set[str]:
    if isinstance(value, str):
        return {value}
    if isinstance(value, dict):
        return {item for child in value.values() for item in _strings(child)}
    if isinstance(value, list):
        return {item for child in value for item in _strings(child)}
    return set()


class CausalPathwayBindingI116Test(unittest.TestCase):
    """Keep dry-run and post-freeze replay evidence reproducible."""

    def test_all_ten_consumer_dry_runs_passed(self) -> None:
        summary = _load(EVIDENCE / "consumer-dry-run-summary.json")

        self.assertEqual("passed", summary["status"])
        self.assertEqual(10, summary["case_count"])
        self.assertEqual(10, summary["passed_case_count"])
        self.assertEqual(
            summary["summary_digest"],
            canonical_digest(summary, excluding="summary_digest"),
        )
        conformance = summary["binding_conformance"]
        assert isinstance(conformance, list)
        self.assertEqual(8, len(conformance))
        self.assertTrue(all(row["status"] == "passed" for row in conformance))

    def test_low_context_input_contains_no_canonical_identity(self) -> None:
        specification = _load(SPECIFICATION)
        registry = _load(ROOT / "specs/grc-lgrc-causal-pathway-contracts.json")
        matrix = _load(ROOT / "specs/grc-lgrc-causal-pathway-composition-matrix.json")
        pathway_ids = {item["pathway_id"] for item in registry["pathways"]}
        composition_ids = {item["composition_id"] for item in matrix["compositions"]}

        self.assertFalse(_strings(specification) & pathway_ids)
        self.assertFalse(_strings(specification) & composition_ids)
        self.assertFalse(specification["expected_pathway_ids_supplied"])
        self.assertFalse(specification["expected_composition_ids_supplied"])
        self.assertFalse(specification["expected_stage_ids_supplied"])
        self.assertFalse(specification["expected_symbol_ids_supplied"])

    def test_post_freeze_oracle_matches_replay_and_was_not_consumed(self) -> None:
        oracle = _load(EVIDENCE / "low-context-replay.oracle.json")
        result = _load(EVIDENCE / "low-context-replay.result.json")
        receipt = _load(EVIDENCE / "low-context-replay.receipt.json")

        self.assertTrue(oracle["oracle_created_after_consumer_replay"])
        self.assertFalse(oracle["oracle_consumed_by_consumer"])
        self.assertTrue(oracle["identity_match"])
        self.assertEqual(
            oracle["oracle_digest"],
            canonical_digest(oracle, excluding="oracle_digest"),
        )
        self.assertFalse(result["expected_identity_oracle_consumed"])
        self.assertEqual(
            result["selected_pathway_id"],
            receipt["actual_bound_pathways_used"][0]["pathway_id"],
        )
        self.assertEqual(
            result["selected_stage_ids"],
            receipt["actual_bound_pathways_used"][0]["actual_stage_ids"],
        )


if __name__ == "__main__":
    unittest.main()

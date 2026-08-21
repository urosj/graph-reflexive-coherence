"""Enforce the I118 pre-refactor compatibility and golden-byte freeze."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
BUILDER_PATH = ROOT / "scripts/build_phase8_causal_pathway_binding_i118.py"
EVIDENCE_DIR = ROOT / "implementation/evidence/causal-pathway-binding/i118"
FREEZE_PATHS = (
    EVIDENCE_DIR / "I118PublicAPICompatibilityFreeze.json",
    EVIDENCE_DIR / "I118ArtifactRuntimeFreeze.json",
    EVIDENCE_DIR / "I118CheckerIndependenceFreeze.json",
)
EXECUTION_PATH = EVIDENCE_DIR / "I118BaselineExecution.json"
REQUIRED_SEMANTIC_FAMILIES = {
    "native_pathway",
    "producer_composition",
    "adapter_composition",
    "diagnostic_composition",
    "dynamic_choice",
    "candidate_pathway",
    "candidate_composition",
    "reviewed_invalid_pair_candidate",
    "unused_declaration",
    "non_qualifying_returned_effect",
    "raised_effect",
    "multi_edge_graph",
}


def _load_module(name: str, path: Path) -> Any:
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return value


def _record_digest(record: dict[str, Any], *, excluding: str) -> str:
    payload = {key: value for key, value in record.items() if key != excluding}
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


BUILDER = _load_module("causal_pathway_binding_i118_builder", BUILDER_PATH)


class CausalPathwayBindingI118Test(unittest.TestCase):
    """Keep the modular refactor pinned to the accepted pre-refactor behavior."""

    def test_all_freeze_records_are_self_consistent(self) -> None:
        for path in FREEZE_PATHS:
            with self.subTest(path=path.name):
                record = _load_json(path)
                self.assertEqual(118, record["iteration"])
                self.assertEqual("frozen", record["status"])
                self.assertFalse(record["runtime_behavior_changed"])
                self.assertEqual(
                    record["freeze_digest"],
                    _record_digest(record, excluding="freeze_digest"),
                )
        execution = _load_json(EXECUTION_PATH)
        self.assertEqual("passed", execution["status"])
        self.assertEqual(
            execution["execution_digest"],
            _record_digest(execution, excluding="execution_digest"),
        )

    def test_public_api_matches_behavioral_freeze(self) -> None:
        BUILDER.verify_public_api_freeze()

    def test_checker_remains_independent_and_unchanged(self) -> None:
        BUILDER.verify_checker_independence_freeze()

    def test_corpus_covers_every_required_semantic_family(self) -> None:
        freeze = _load_json(EVIDENCE_DIR / "I118ArtifactRuntimeFreeze.json")
        cases = freeze["regenerated_corpus_cases"]
        observed = {family for case in cases for family in case["semantic_families"]}
        self.assertEqual(12, len(cases))
        self.assertTrue(REQUIRED_SEMANTIC_FAMILIES <= observed)
        self.assertEqual(
            len(cases),
            len({case["case_id"] for case in cases}),
        )

    def test_artifact_bytes_runtime_results_and_exceptions_match(self) -> None:
        BUILDER.verify_artifact_runtime_freeze()


if __name__ == "__main__":
    unittest.main()

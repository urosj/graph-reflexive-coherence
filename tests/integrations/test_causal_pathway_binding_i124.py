"""Validate I124 binder examples, guidance, and repository discovery links."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from typing import Any

from pygrc.causal_pathways import sha256_file

ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = ROOT / "examples/causal_pathway_binding"
REFERENCE = (
    ROOT / "docs/reference/GRC-LGRC-CausalPathwayBinding-ReferenceGuide.md"
)
USER_AGENT_GUIDE = (
    ROOT / "docs/reference/GRC-LGRC-CausalPathwayBinding-User-Agent-Guide.md"
)
EXAMPLE_SCRIPTS = (
    "admitted_pathway.py",
    "registered_composition.py",
    "dynamic_choice.py",
    "unregistered_candidate.py",
    "direct_unbound.py",
)


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return value


def _run_example(name: str, *arguments: str) -> dict[str, Any]:
    environment = dict(os.environ)
    environment["PYTHONPATH"] = os.pathsep.join(
        (str(ROOT / "src"), str(ROOT))
    )
    completed = subprocess.run(
        [sys.executable, str(EXAMPLES / name), *arguments],
        cwd=ROOT,
        env=environment,
        check=True,
        capture_output=True,
        text=True,
        timeout=60,
    )
    result = json.loads(completed.stdout)
    if not isinstance(result, dict):
        raise TypeError(f"{name} must print one JSON object")
    return result


class CausalPathwayBindingI124Test(unittest.TestCase):
    """Keep the stable documentation and five runnable examples honest."""

    def test_all_five_examples_execute_with_conservative_results(self) -> None:
        self.assertEqual(
            set(EXAMPLE_SCRIPTS),
            {path.name for path in EXAMPLES.glob("*.py") if not path.name.startswith("_")}
            - {"candidate_mechanism.py"},
        )
        results = {
            name: _run_example(name)
            for name in EXAMPLE_SCRIPTS
        }

        self.assertEqual(
            ["lgrc9v3.explicit_packet_transport"],
            results["admitted_pathway.py"]["actual_pathway_ids"],
        )
        self.assertEqual(
            ["CMP-02"],
            results["registered_composition.py"]["registered_composition_ids"],
        )
        self.assertEqual(
            "consumer",
            results["dynamic_choice.py"]["selection_performed_by"],
        )
        candidate = results["unregistered_candidate.py"]
        self.assertEqual("experimental_unregistered", candidate["claim_ceiling"])
        self.assertEqual("none", candidate["promotion_status"])
        direct = results["direct_unbound.py"]
        self.assertFalse(direct["direct_execution"]["claim_qualified"])
        self.assertTrue(direct["bound_execution"]["claim_qualified"])
        self.assertTrue(
            all(
                result.get("claim_scope") == "bound_invocations_only"
                or result.get("bound_execution", {}).get("claim_scope")
                == "bound_invocations_only"
                for result in results.values()
            )
        )

    def test_dynamic_example_runs_both_consumer_owned_branches(self) -> None:
        packet = _run_example("dynamic_choice.py", "--choice", "packet")
        snapshot = _run_example("dynamic_choice.py", "--choice", "snapshot")

        self.assertEqual(
            ["lgrc9v3.explicit_packet_transport"], packet["selected_pathway_ids"]
        )
        self.assertEqual(
            ["pygrc.restoration_replay_identity"],
            snapshot["selected_pathway_ids"],
        )

    def test_candidate_example_evidence_is_exactly_content_addressed(self) -> None:
        evidence_path = EXAMPLES / "candidate_mechanism_evidence.json"
        evidence = _load(evidence_path)
        symbol = evidence["executable_symbol"]
        source = ROOT / symbol["source_path"]

        self.assertEqual(
            "causal_pathway_candidate_mechanism_evidence_v2",
            evidence["schema_version"],
        )
        self.assertEqual(symbol["source_sha256"], sha256_file(source))
        self.assertEqual("module_function", symbol["call_kind"])
        self.assertEqual(
            "experimental_unregistered",
            _run_example("unregistered_candidate.py")["overall_claim_status"],
        )

    def test_guides_state_workflow_scope_and_final_candidate_contract(self) -> None:
        guide = USER_AGENT_GUIDE.read_text(encoding="utf-8")
        reference = REFERENCE.read_text(encoding="utf-8")

        for text in (guide, reference):
            self.assertIn("bound_invocations_only", text)
            self.assertIn("whole-run causal closure", text)
            self.assertIn("unbound influences", text)
        self.assertIn("select -> bind -> lock -> execute -> seal -> validate", guide)
        self.assertIn("selection remains consumer-owned", guide)
        self.assertIn("experimental_unregistered", guide)
        self.assertIn("source_result_parameter", guide)
        self.assertIn("actual Python", guide)
        self.assertIn("Tuple and list identity remain distinct", reference)
        for historical_label in ("R4-B01", "R5-B01", "R6-B01", "R7-B01", "R8-B01"):
            self.assertNotIn(historical_label, reference)

    def test_reference_lists_exact_lock_and_receipt_top_level_fields(self) -> None:
        reference = REFERENCE.read_text(encoding="utf-8")
        api_freeze = _load(
            ROOT
            / "implementation/evidence/causal-pathway-binding/i118/"
            "I118PublicAPICompatibilityFreeze.json"
        )
        lock = _load(
            ROOT
            / "implementation/evidence/causal-pathway-binding/i116/"
            "01-simple-native-pathway.lock.json"
        )
        receipt = _load(
            ROOT
            / "implementation/evidence/causal-pathway-binding/i116/"
            "01-simple-native-pathway.receipt.json"
        )

        self.assertIn("causal_pathways_binding_lock_v1", reference)
        self.assertIn("causal_pathways_binding_receipt_v1", reference)
        exports = api_freeze["public_api_contract"]["exports"]
        self.assertEqual(48, len(exports))
        for exported in exports:
            self.assertIn(f"`{exported['name']}`", reference)
        for field in (*lock.keys(), *receipt.keys()):
            self.assertIn(f"\n{field}\n", reference)

    def test_every_required_repository_index_discovers_i124_guidance(self) -> None:
        indexed_files = (
            ROOT / "README.md",
            ROOT / "docs/README.md",
            ROOT / "docs/reference/README.md",
            ROOT / "docs/reference/ClaimBoundaryIndex.md",
            ROOT / "examples/README.md",
            ROOT / "specs/README.md",
            ROOT / "implementation/Documentation-Checklist.md",
        )
        for path in indexed_files:
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertIn("GRC-LGRC-CausalPathwayBinding-User-Agent-Guide.md", text)
                self.assertIn("causal_pathway_binding/README.md", text)


if __name__ == "__main__":
    unittest.main()

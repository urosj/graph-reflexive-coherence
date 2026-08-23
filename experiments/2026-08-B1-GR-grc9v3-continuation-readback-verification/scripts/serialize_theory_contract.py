"""Serialize the binding Draft 3.4.1 theory records without interpretation."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
from typing import Any

from artifact_io import EXPERIMENT_ROOT, artifact_envelope, semantic_digest, sha256_file, write_json


SPEC_PATH = EXPERIMENT_ROOT / "implementation/GRC9V3ContinuationReadBackVerificationSpecification.md"
COMMAND = ".venv/bin/python experiments/2026-08-B1-GR-grc9v3-continuation-readback-verification/scripts/serialize_theory_contract.py"


def section(text: str, start: str, end: str) -> str:
    start_index = text.index(start)
    end_index = text.index(end, start_index + len(start))
    return text[start_index:end_index]


def markdown_table(section_text: str) -> list[dict[str, str]]:
    lines = section_text.splitlines()
    start = next(index for index, line in enumerate(lines) if line.startswith("|"))
    headers = [cell.strip() for cell in lines[start].strip("|").split("|")]
    rows: list[dict[str, str]] = []
    for line in lines[start + 2 :]:
        if not line.startswith("|"):
            break
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != len(headers):
            raise ValueError(f"malformed markdown table row: {line}")
        row = dict(zip(headers, cells, strict=True))
        for key, value in tuple(row.items()):
            if value.startswith("`") and value.endswith("`"):
                row[key] = value[1:-1]
        rows.append(row)
    return rows


def proof_notes(specification: str) -> list[dict[str, Any]]:
    appendix = specification[specification.index("# Appendix A") : specification.index("# Part II")]
    matches = list(re.finditer(r"^## A\.\d+ `(?P<id>PN-[^`]+)` — (?P<title>.+)$", appendix, re.MULTILINE))
    notes = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(appendix)
        body = appendix[match.end() : end].strip()
        notes.append({"proof_note_id": match.group("id"), "title": match.group("title"), "body_sha256": semantic_digest(body), "source_section": match.group(0)})
    return notes


def envelope(payload: Any, schema: str) -> dict[str, Any]:
    return artifact_envelope(
        payload,
        schema_version=schema,
        generating_command=COMMAND,
        metadata={"controlling_specification_path": "implementation/GRC9V3ContinuationReadBackVerificationSpecification.md", "controlling_specification_sha256": sha256_file(SPEC_PATH)},
    )


def serialize(output_root: Path) -> dict[str, str]:
    specification = SPEC_PATH.read_text(encoding="utf-8")
    claims = markdown_table(section(specification, "## 3.1 Claim ledger", "## 3.2 Decision use"))
    assumptions = markdown_table(section(specification, "## 2.4 Normative assumption registry", "### 2.4.1"))
    debts = markdown_table(section(specification, "## 9.1 Debt register", "## 9.2 Decision consequences"))
    traceability = markdown_table(section(specification, "# 10. Theory-to-test traceability", "# 11. Theory freeze"))
    notes = proof_notes(specification)
    part_i = section(specification, "# Part I", "# Part II")
    gate_ids = [f"GRV{index}" for index in range(9)]
    gate_map = {
        "gate_order": gate_ids,
        "dependencies": {gate: ([] if index == 0 else [gate_ids[index - 1]]) for index, gate in enumerate(gate_ids)},
        "authorization_rule": "accepted_anchor_required_not_receipt_alone",
        "transitive_invalidation_rule": "revision_distinct_baseline_supersedes_or_blocks_all_downstream_results_and_anchors_until_rerun",
        "positive_evidence_first_eligible_gate": "GRV2",
    }
    records = {
        "theory_claim_ledger.json": envelope({"records": claims, "positive_GRC9V3_status_assigned": False}, "b1_theory_claim_ledger_v1"),
        "theory_assumption_registry.json": envelope({"allowed_statuses": ["satisfied", "failed", "not_identifiable", "not_applicable", "deferred"], "records": [{**row, "GRV0_status": "deferred"} for row in assumptions]}, "b1_theory_assumption_registry_v1"),
        "theory_derivation_status.json": envelope({"permitted_statuses": ["inherited_explicit", "derived_with_sketch", "conditional_lemma", "candidate_witness_class", "open_problem", "realization_specific"], "proof_notes": notes}, "b1_theory_derivation_status_v1"),
        "theory_debt_register.json": envelope({"records": debts, "GRV0_resolution_allowed": False}, "b1_theory_debt_register_v1"),
        "theory_test_traceability.json": envelope({"records": traceability, "results_pending": True}, "b1_theory_test_traceability_v1"),
        "proof_note_registry.json": envelope({"records": notes}, "b1_proof_note_registry_v1"),
        "gate_dependency_map.json": envelope(gate_map, "b1_gate_dependency_map_v1"),
        "contradiction_register.json": envelope({"entries": [], "allowed_routes": ["substrate_nonrealization", "candidate_graph_mapping_error", "core_derived_claim_too_strong", "core_assumption_incompatible_with_this_realization", "construct_not_identifiable_with_available_interventions", "numerical_or_instrumentation_failure", "source_or_specification_mismatch"]}, "b1_contradiction_register_v1"),
        "theory_contract_identity.json": envelope({"part_i_and_appendix_a_sha256": semantic_digest(part_i), "controlling_specification_sha256": sha256_file(SPEC_PATH), "claim_count": len(claims), "assumption_count": len(assumptions), "debt_count": len(debts), "traceability_row_count": len(traceability), "proof_note_count": len(notes)}, "b1_theory_contract_identity_v1"),
    }
    digests: dict[str, str] = {}
    for name, record in records.items():
        path = output_root / name
        write_json(path, record)
        digests[name] = record["payload_sha256"]
    return digests


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=EXPERIMENT_ROOT / "outputs")
    args = parser.parse_args()
    serialize(args.output_root)


if __name__ == "__main__":
    main()

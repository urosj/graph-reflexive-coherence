#!/usr/bin/env python3
"""Focused ET-C1 adapter, discovery, and immutability fixture matrix."""

from __future__ import annotations

import copy
import sys
import tempfile
from dataclasses import replace
from pathlib import Path
from typing import Any, Callable


SCRIPT = Path(__file__).resolve()
TOOL_ROOT = SCRIPT.parents[1]
SIDE_TOOL_ROOT = SCRIPT.parents[2]
sys.path.insert(0, str(TOOL_ROOT / "src"))

from grcv4_explorer.adapters import adapt_source  # noqa: E402
from grcv4_explorer.bundle import build_source_bundle  # noqa: E402
from grcv4_explorer.canonical import (  # noqa: E402
    canonical_bytes,
    digest,
    file_sha256,
)
from grcv4_explorer.discovery import discover_sources  # noqa: E402
from grcv4_explorer.errors import SourceAdmissionError  # noqa: E402
from grcv4_explorer.paths import repository_root  # noqa: E402
from grcv4_explorer.source_contract import (  # noqa: E402
    admitted_rows,
    load_et_c0_contract,
)
from grcv4_explorer.validation import validate_cross_source_contract  # noqa: E402


DECISIONS_RELATIVE = Path(
    "implementation/investigations/grc9v4-constitutive-design/decisions"
)
FIXTURE_NAME = "D0TargetInheritanceAndClaimCeiling.json"


def expect_admission_error(label: str, operation: Callable[[], object]) -> None:
    try:
        operation()
    except SourceAdmissionError:
        return
    raise RuntimeError(f"fixture did not fail closed: {label}")


def fixture_record(
    *,
    schema: str = "grc9v4_constitutive_design_decision_v1",
    status: str = "accepted_bounded",
) -> dict[str, object]:
    value: dict[str, object] = {
        "schema_version": schema,
        "record_id": "FIXTURE-D0",
        "gate_id": "D0",
        "status": status,
        "predecessor_record_id": None,
        "decision_record_digest": None,
    }
    value["decision_record_digest"] = digest(
        {key: child for key, child in value.items() if key != "decision_record_digest"}
    )
    return value


def write_fixture(root: Path, value: object) -> tuple[Path, dict[str, object]]:
    decisions = root / DECISIONS_RELATIVE
    decisions.mkdir(parents=True, exist_ok=True)
    path = decisions / FIXTURE_NAME
    path.write_bytes(canonical_bytes(value) + b"\n")
    declared_digest = (
        value.get("decision_record_digest") if isinstance(value, dict) else None
    )
    admission: dict[str, object] = {
        "source_id": "FIXTURE-D0",
        "path": (DECISIONS_RELATIVE / FIXTURE_NAME).as_posix(),
        "expected_status": "accepted_bounded",
        "canonical_digest_field": "decision_record_digest",
        "canonical_digest": declared_digest,
        "file_sha256": file_sha256(path),
    }
    return path, admission


def discovery_matrix() -> None:
    with tempfile.TemporaryDirectory(prefix="grcv4-et-c1-discovery-") as temporary:
        base = Path(temporary)
        path, admission = write_fixture(base / "exact", fixture_record())
        assert (
            discover_sources(base / "exact", [admission])["state"]
            == "current_bundle_exact"
        )

        draft_root = base / "draft"
        _, draft_admission = write_fixture(draft_root, fixture_record())
        draft = draft_root / DECISIONS_RELATIVE / "FutureDraft.json"
        draft.write_text(
            '{"schema":"future_v1","status":"draft","record_id":"FUTURE"}\n'
        )
        draft_observation = discover_sources(draft_root, [draft_admission])
        assert draft_observation["state"] == "new_unprocessed_source_available"
        assert draft_observation["automatic_admission_allowed"] is False
        assert (
            draft_observation["added_unprocessed"][0]["observed_metadata"]["status"]
            == "draft"
        )

        accepted_root = base / "accepted"
        _, accepted_admission = write_fixture(accepted_root, fixture_record())
        accepted = accepted_root / DECISIONS_RELATIVE / "FutureAccepted.json"
        accepted.write_text(
            '{"schema":"future_v2","status":"accepted","record_id":"FUTURE-A"}\n'
        )
        accepted_observation = discover_sources(accepted_root, [accepted_admission])
        assert accepted_observation["state"] == "new_unprocessed_source_available"
        assert accepted_observation["live_rebuild_allowed"] is False

        changed_root = base / "changed"
        changed_path, changed_admission = write_fixture(changed_root, fixture_record())
        changed_path.write_bytes(changed_path.read_bytes() + b" ")
        assert (
            discover_sources(changed_root, [changed_admission])["state"]
            == "admitted_source_identity_changed"
        )

        missing_root = base / "missing"
        _, missing_admission = write_fixture(missing_root, fixture_record())
        (missing_root / DECISIONS_RELATIVE / FIXTURE_NAME).unlink()
        assert (
            discover_sources(missing_root, [missing_admission])["state"]
            == "admitted_source_missing"
        )

        unreadable_root = base / "unreadable"
        _, unreadable_admission = write_fixture(unreadable_root, fixture_record())
        unreadable = unreadable_root / DECISIONS_RELATIVE / "Unreadable.json"
        unreadable.write_bytes(b"not-json\xff")
        assert (
            discover_sources(unreadable_root, [unreadable_admission])["state"]
            == "source_observation_unreadable"
        )
        assert path.is_file()


def adapter_failure_matrix() -> None:
    with tempfile.TemporaryDirectory(prefix="grcv4-et-c1-adapters-") as temporary:
        base = Path(temporary)

        exact_root = base / "exact"
        _, exact_admission = write_fixture(exact_root, fixture_record())
        assert (
            adapt_source(exact_root, exact_admission).record_identifier == "FIXTURE-D0"
        )

        wrong_sha_root = base / "wrong-sha"
        _, wrong_sha = write_fixture(wrong_sha_root, fixture_record())
        wrong_sha["file_sha256"] = "0" * 64
        expect_admission_error(
            "wrong SHA", lambda: adapt_source(wrong_sha_root, wrong_sha)
        )

        wrong_digest_root = base / "wrong-digest"
        wrong_digest_value = fixture_record()
        wrong_digest_value["decision_record_digest"] = "0" * 64
        _, wrong_digest = write_fixture(wrong_digest_root, wrong_digest_value)
        expect_admission_error(
            "wrong digest", lambda: adapt_source(wrong_digest_root, wrong_digest)
        )

        status_root = base / "status"
        _, status_admission = write_fixture(status_root, fixture_record(status="draft"))
        expect_admission_error(
            "changed status", lambda: adapt_source(status_root, status_admission)
        )

        schema_root = base / "schema"
        _, schema_admission = write_fixture(
            schema_root, fixture_record(schema="unknown_v99")
        )
        expect_admission_error(
            "unknown schema", lambda: adapt_source(schema_root, schema_admission)
        )

        malformed_root = base / "malformed"
        _, malformed_admission = write_fixture(malformed_root, [])
        expect_admission_error(
            "malformed root", lambda: adapt_source(malformed_root, malformed_admission)
        )


def accepted_bundle_matrix(repo_root: Path) -> None:
    et_c0_path = SIDE_TOOL_ROOT / "records/ETC0SourceAndLayoutContract.json"
    et_c0 = load_et_c0_contract(et_c0_path)
    rows = admitted_rows(et_c0)
    before = {row["path"]: file_sha256(repo_root / row["path"]) for row in rows}
    first, first_observation = build_source_bundle(repo_root, et_c0_path)
    second, second_observation = build_source_bundle(repo_root, et_c0_path)
    assert canonical_bytes(first) == canonical_bytes(second)
    assert canonical_bytes(first_observation) == canonical_bytes(second_observation)
    after = {row["path"]: file_sha256(repo_root / row["path"]) for row in rows}
    assert before == after

    documents = [adapt_source(repo_root, row) for row in rows]

    def expect_mutation_error(
        filename: str,
        label: str,
        mutate: Callable[[dict[str, Any]], None],
    ) -> None:
        index = next(
            document_index
            for document_index, document in enumerate(documents)
            if document.filename == filename
        )
        document = documents[index]
        changed = copy.deepcopy(document.data)
        mutate(changed)
        changed_documents = list(documents)
        changed_documents[index] = replace(document, data=changed)
        expect_admission_error(
            label,
            lambda: validate_cross_source_contract(repo_root, changed_documents),
        )

    topology_index = next(
        index
        for index, document in enumerate(documents)
        if document.filename == "D10NormativeClaimTopology.json"
    )
    topology = documents[topology_index]
    bad_reference = copy.deepcopy(topology.data)
    bad_reference["claims"][0]["evidence_refs"] = ["MISSING-RECORD"]
    reference_documents = list(documents)
    reference_documents[topology_index] = replace(topology, data=bad_reference)
    expect_admission_error(
        "wrong reference",
        lambda: validate_cross_source_contract(repo_root, reference_documents),
    )

    duplicate = copy.deepcopy(topology.data)
    duplicate["claims"][1]["claim_id"] = duplicate["claims"][0]["claim_id"]
    duplicate_documents = list(documents)
    duplicate_documents[topology_index] = replace(topology, data=duplicate)
    expect_admission_error(
        "duplicate claim ID",
        lambda: validate_cross_source_contract(repo_root, duplicate_documents),
    )

    missing_documents = [
        document
        for document in documents
        if document.filename != "D10NormativeClaimTopology.json"
    ]
    expect_admission_error(
        "missing required cross-source document",
        lambda: validate_cross_source_contract(repo_root, missing_documents),
    )

    classification = copy.deepcopy(topology.data)
    classification["claims"][0]["claim_class"] = "optional"
    classification_documents = list(documents)
    classification_documents[topology_index] = replace(topology, data=classification)
    expect_admission_error(
        "claim-class authorization mismatch",
        lambda: validate_cross_source_contract(repo_root, classification_documents),
    )

    expect_mutation_error(
        "D10NormativeClaimTopology.json",
        "claim/debt reciprocal edge mismatch",
        lambda data: data["claim_debt_edges"][0]["edge_types"].append(
            "fixture_only_edge_type"
        ),
    )
    expect_mutation_error(
        "D10DebtClaimTransformationLedger.json",
        "debt claim reference unresolved",
        lambda data: data["debt_transformations"][0]["blocked_claim_ids"].append(
            "MISSING-CLAIM"
        ),
    )

    def break_verification_obligation(data: dict[str, Any]) -> None:
        row = next(
            item
            for item in data["debt_transformations"]
            if item["verification_obligation"] is not None
        )
        row["verification_obligation"] = "MISSING-OBLIGATION"

    expect_mutation_error(
        "D10DebtClaimTransformationLedger.json",
        "debt verification obligation unresolved",
        break_verification_obligation,
    )
    expect_mutation_error(
        "D10DebtClaimTransformationLedger.json",
        "debt evidence reference unresolved",
        lambda data: data["debt_transformations"][0]["evidence_refs"].append(
            "MISSING-EVIDENCE"
        ),
    )
    expect_mutation_error(
        "D2FormationRetentionReleaseAndWriteInterface.json",
        "predecessor digest unresolved",
        lambda data: data.update({"predecessor_decision_digest": "0" * 64}),
    )
    expect_mutation_error(
        "D9LifecycleCoverageMatrix.json",
        "lifecycle cell missing",
        lambda data: data["rows"][0]["cells"].pop(data["columns"][0]),
    )
    expect_mutation_error(
        "D9ResidualDebtLedger.json",
        "D9 obligation not carried into D10",
        lambda data: data["post_spec_verification_obligations"][0].update(
            {"obligation_id": "MISSING-D10-OBLIGATION"}
        ),
    )
    expect_mutation_error(
        "D10_2FullSubstrateProvenanceAndPromotionAudit.json",
        "contract parent unresolved",
        lambda data: data["normative_equation_contract_registry"][0][
            "parent_object_ids"
        ].append("MISSING-PARENT"),
    )
    expect_mutation_error(
        "D10_2FullSubstrateProvenanceAndPromotionAudit.json",
        "contract claim unresolved",
        lambda data: data["normative_equation_contract_registry"][0][
            "accepted_claim_ids"
        ].append("MISSING-CLAIM"),
    )

    def break_contract_profile(data: dict[str, Any]) -> None:
        row = next(
            item
            for item in data["normative_equation_contract_registry"]
            if item["profile_ids"]
        )
        row["profile_ids"].append("MISSING-PROFILE")

    expect_mutation_error(
        "D10_2FullSubstrateProvenanceAndPromotionAudit.json",
        "contract profile unresolved",
        break_contract_profile,
    )
    expect_mutation_error(
        "D10_2FullSubstrateProvenanceAndPromotionAudit.json",
        "parent coverage incomplete",
        lambda data: data["equation_contract_coverage"][
            "parent_object_ids_covered"
        ].pop(),
    )
    expect_mutation_error(
        "D10_2FullSubstrateProvenanceAndPromotionAudit.json",
        "claim coverage incomplete",
        lambda data: data["equation_contract_coverage"][
            "accepted_claim_ids_covered"
        ].pop(),
    )
    expect_mutation_error(
        "D10SpecificationAuthorizationProfile.json",
        "authorization duplicate within class",
        lambda data: data["normative_common_claim_ids"].append(
            data["normative_common_claim_ids"][0]
        ),
    )


def main() -> int:
    repo_root = repository_root()
    if Path(sys.prefix).resolve() != (repo_root / ".venv").resolve():
        raise RuntimeError("run this command with the repository .venv Python")
    discovery_matrix()
    adapter_failure_matrix()
    accepted_bundle_matrix(repo_root)
    print("ET_C1_ADAPTER_FIXTURE_MATRIX_PASS cases=29")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

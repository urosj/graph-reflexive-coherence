#!/usr/bin/env python3
"""Independently audit the ET-C1 source-adapter admission artifacts."""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterator, cast


SCRIPT = Path(__file__).resolve()
TOOL_ROOT = SCRIPT.parents[1]
SIDE_TOOL_ROOT = SCRIPT.parents[2]
sys.path.insert(0, str(TOOL_ROOT / "src"))

from grcv4_explorer.bundle import build_source_bundle  # noqa: E402
from grcv4_explorer.canonical import (  # noqa: E402
    canonical_bytes,
    digest,
    file_sha256,
    load_json_object,
    record_digest,
)
from grcv4_explorer.discovery import discover_sources  # noqa: E402
from grcv4_explorer.paths import repository_root  # noqa: E402
from grcv4_explorer.source_contract import (  # noqa: E402
    admitted_rows,
    load_et_c0_contract,
)


def walk_strings(value: Any) -> Iterator[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from walk_strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_strings(child)


def walk_objects(value: Any) -> Iterator[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk_objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_objects(child)


def is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def independently_derive_embedded_identities(
    repo_root: Path,
    admitted: list[dict[str, Any]],
) -> tuple[dict[str, int], int]:
    identities: set[tuple[str, str, str]] = set()
    local_identities: set[tuple[str, str, str]] = set()
    external_identities: set[tuple[str, str, str]] = set()
    source_records: list[dict[str, Any]] = []
    for admission in admitted:
        source = load_json_object(repo_root / admission["path"])
        source_records.append(source)
        for row in walk_objects(source):
            path_value = row.get("path")
            sha_value = row.get("file_sha256") or row.get("sha256")
            if not isinstance(path_value, str) or not isinstance(sha_value, str):
                continue
            repository = row.get("repository", "graph-reflexive-coherence")
            if not isinstance(repository, str):
                raise RuntimeError("ET-C1 audit found malformed source repository")
            if Path(path_value).is_absolute() or not is_sha256(sha_value):
                raise RuntimeError("ET-C1 audit found malformed embedded identity")
            identity = (repository, path_value, sha_value)
            identities.add(identity)
            if repository != "graph-reflexive-coherence" or path_value.startswith(
                "external:"
            ):
                external_identities.add(identity)
                continue
            local_identities.add(identity)
            target = repo_root / path_value
            if not target.is_file() or file_sha256(target) != sha_value:
                raise RuntimeError(
                    f"ET-C1 audit found local embedded identity mismatch: {path_value}"
                )
            declared_digests = {
                value
                for field in (
                    "source_digest",
                    "semantic_decision_digest",
                    "decision_digest",
                    "artifact_digest",
                )
                if isinstance((value := row.get(field)), str)
            }
            if declared_digests and target.suffix == ".json":
                target_data = load_json_object(target)
                target_digest = target_data.get(
                    "decision_record_digest"
                ) or target_data.get("artifact_digest")
                if declared_digests != {target_digest}:
                    raise RuntimeError(
                        "ET-C1 audit found local embedded digest mismatch: "
                        f"{path_value}"
                    )

    admitted_digests = {
        source.get("decision_record_digest") or source.get("artifact_digest")
        for source in source_records
    }
    external_predecessor_roots = sum(
        1
        for source in source_records
        if isinstance(source.get("predecessor_decision_digest"), str)
        and source["predecessor_decision_digest"] not in admitted_digests
    )
    return (
        {
            "total": len(identities),
            "local": len(local_identities),
            "external": len(external_identities),
        },
        external_predecessor_roots,
    )


def independently_verify_cross_source_relationships(
    repo_root: Path,
    admitted: list[dict[str, Any]],
) -> dict[str, Any]:
    assertions: list[str] = []
    relationship_witnesses: dict[str, list[list[str]]] = {}

    def witness(family: str, *parts: str) -> None:
        relationship_witnesses.setdefault(family, []).append(list(parts))

    def verify(name: str, condition: bool) -> None:
        if not condition:
            raise RuntimeError(f"ET-C1 independent relationship audit failed: {name}")
        assertions.append(name)

    def rows(value: Any, label: str) -> list[dict[str, Any]]:
        verify(
            f"rows:{label}",
            isinstance(value, list) and all(isinstance(row, dict) for row in value),
        )
        return cast(list[dict[str, Any]], value)

    def strings(value: Any, label: str) -> list[str]:
        verify(
            f"strings:{label}",
            isinstance(value, list) and all(isinstance(item, str) for item in value),
        )
        return cast(list[str], value)

    def identifiers(
        source_rows: list[dict[str, Any]], key: str, label: str
    ) -> list[str]:
        result: list[str] = []
        for index, row in enumerate(source_rows):
            value = row.get(key)
            verify(
                f"identifier:{label}:{index}", isinstance(value, str) and bool(value)
            )
            result.append(cast(str, value))
        verify(f"identifier_unique:{label}", len(result) == len(set(result)))
        return result

    sources: dict[str, dict[str, Any]] = {}
    source_identifiers: set[str] = set()
    source_digest_to_identifier: dict[str, str] = {}
    for admission in admitted:
        relative = admission["path"]
        verify("admitted_path_string", isinstance(relative, str))
        filename = Path(cast(str, relative)).name
        verify(f"source_filename_unique:{filename}", filename not in sources)
        source = load_json_object(repo_root / cast(str, relative))
        sources[filename] = source
        identifier = source.get("record_id") or source.get("artifact_id")
        declared_digest = source.get("decision_record_digest") or source.get(
            "artifact_digest"
        )
        verify(f"source_identifier:{filename}", isinstance(identifier, str))
        verify(f"source_digest:{filename}", is_sha256(declared_digest))
        verify(
            f"source_identifier_unique:{filename}",
            cast(str, identifier) not in source_identifiers,
        )
        verify(
            f"source_digest_unique:{filename}",
            cast(str, declared_digest) not in source_digest_to_identifier,
        )
        source_identifiers.add(cast(str, identifier))
        source_digest_to_identifier[cast(str, declared_digest)] = cast(str, identifier)

    required = {
        "D10NormativeClaimTopology.json",
        "D10DebtClaimTransformationLedger.json",
        "D10_2FullSubstrateProvenanceAndPromotionAudit.json",
        "D9ProfileStateLifecycleRegistry.json",
        "D9LifecycleCoverageMatrix.json",
        "D9ResidualDebtLedger.json",
        "D10SpecificationAuthorizationProfile.json",
    }
    verify("required_sources", required <= set(sources))
    topology = sources["D10NormativeClaimTopology.json"]
    debt = sources["D10DebtClaimTransformationLedger.json"]
    provenance = sources["D10_2FullSubstrateProvenanceAndPromotionAudit.json"]
    profile_registry = sources["D9ProfileStateLifecycleRegistry.json"]
    lifecycle_matrix = sources["D9LifecycleCoverageMatrix.json"]
    d9_debt = sources["D9ResidualDebtLedger.json"]
    authorization = sources["D10SpecificationAuthorizationProfile.json"]

    current_rows = rows(topology.get("claims"), "current_claims")
    historical_rows = rows(topology.get("historical_claim_nodes"), "historical_claims")
    current_ids = set(identifiers(current_rows, "claim_id", "current_claims"))
    historical_ids = set(identifiers(historical_rows, "claim_id", "historical_claims"))
    verify("claim_populations_disjoint", current_ids.isdisjoint(historical_ids))
    verify("current_claim_count_declared", len(current_ids) == topology["claim_count"])
    verify(
        "historical_claim_count_declared",
        len(historical_ids) == topology["historical_claim_count"],
    )

    debt_rows = rows(debt.get("debt_transformations"), "debt_transformations")
    debt_ids = set(identifiers(debt_rows, "debt_id", "debt_transformations"))
    obligation_rows = rows(
        debt.get("verification_obligations"), "verification_obligations"
    )
    obligation_ids = set(
        identifiers(obligation_rows, "obligation_id", "verification_obligations")
    )
    verify("debt_count_declared", len(debt_ids) == debt["debt_count"])
    verify(
        "obligation_count_declared",
        len(obligation_ids) == debt["verification_obligation_count"],
    )

    nested_edges: list[tuple[str, str, tuple[str, ...]]] = []
    evidence_reference_occurrences = 0
    for claim in [*current_rows, *historical_rows]:
        claim_id = cast(str, claim["claim_id"])
        evidence = strings(claim.get("evidence_refs"), f"claim_evidence:{claim_id}")
        for source_id in evidence:
            verify(
                f"claim_evidence_resolves:{claim_id}:{source_id}",
                source_id in source_identifiers,
            )
            evidence_reference_occurrences += 1
            witness("claim_evidence", claim_id, source_id)
        for edge in rows(claim.get("debt_edges"), f"claim_debt_edges:{claim_id}"):
            debt_id = edge.get("debt_id")
            verify(f"claim_debt_resolves:{claim_id}:{debt_id}", debt_id in debt_ids)
            edge_types = tuple(
                sorted(strings(edge.get("edge_types"), f"edge_types:{claim_id}"))
            )
            nested_edges.append((claim_id, cast(str, debt_id), edge_types))

    flat_edges: list[tuple[str, str, tuple[str, ...]]] = []
    for edge in rows(topology.get("claim_debt_edges"), "flat_claim_debt_edges"):
        flat_claim_value = edge.get("claim_id")
        flat_debt_value = edge.get("debt_id")
        verify(
            "flat_edge_claim_resolves",
            flat_claim_value in current_ids | historical_ids,
        )
        verify("flat_edge_debt_resolves", flat_debt_value in debt_ids)
        flat_edges.append(
            (
                cast(str, flat_claim_value),
                cast(str, flat_debt_value),
                tuple(sorted(strings(edge.get("edge_types"), "flat_edge_types"))),
            )
        )
    verify("claim_debt_edges_reciprocal", Counter(nested_edges) == Counter(flat_edges))
    verify(
        "claim_debt_edge_count_declared",
        len(flat_edges) == topology["claim_debt_edge_count"],
    )
    for claim_id, debt_id, edge_types in flat_edges:
        witness("claim_debt_edge", claim_id, debt_id, *edge_types)

    current_claim_fields = (
        "supported_claim_ids",
        "conditioned_claim_ids",
        "negative_successor_claim_ids",
        "routed_claim_ids",
        "successor_claim_ids",
    )
    for debt_row in debt_rows:
        debt_id = cast(str, debt_row["debt_id"])
        for claim_id in strings(
            debt_row.get("blocked_claim_ids"), f"blocked_claim_ids:{debt_id}"
        ):
            verify(
                f"blocked_claim_resolves:{debt_id}:{claim_id}",
                claim_id in current_ids | historical_ids,
            )
            witness("debt_claim_reference", debt_id, "blocked_claim_ids", claim_id)
        for field in current_claim_fields:
            for claim_id in strings(debt_row.get(field), f"{field}:{debt_id}"):
                verify(
                    f"current_claim_resolves:{field}:{debt_id}:{claim_id}",
                    claim_id in current_ids,
                )
                witness("debt_claim_reference", debt_id, field, claim_id)
        for claim_id in strings(
            debt_row.get("predecessor_claim_ids"),
            f"predecessor_claim_ids:{debt_id}",
        ):
            verify(
                f"historical_claim_resolves:{debt_id}:{claim_id}",
                claim_id in historical_ids,
            )
            witness("debt_claim_reference", debt_id, "predecessor_claim_ids", claim_id)
        verification = debt_row.get("verification_obligation")
        verify(
            f"verification_obligation_resolves:{debt_id}",
            verification is None or verification in obligation_ids,
        )
        if isinstance(verification, str):
            witness("debt_verification_obligation", debt_id, verification)
        for source_id in strings(
            debt_row.get("evidence_refs"), f"debt_evidence:{debt_id}"
        ):
            verify(
                f"debt_evidence_resolves:{debt_id}:{source_id}",
                source_id in source_identifiers,
            )
            evidence_reference_occurrences += 1
            witness("debt_evidence", debt_id, source_id)

    predecessor_link_count = 0
    external_predecessor_root_count = 0
    for filename, source in sources.items():
        predecessor_digest = source.get("predecessor_decision_digest")
        if not isinstance(predecessor_digest, str):
            continue
        predecessor_link_count += 1
        predecessor_identifier = source_digest_to_identifier.get(predecessor_digest)
        if predecessor_identifier is None:
            verify(
                f"external_predecessor_is_D0:{filename}",
                source.get("gate_id") == "D0"
                and source.get("predecessor_record_id") is None,
            )
            external_predecessor_root_count += 1
            witness(
                "predecessor",
                cast(str, source.get("record_id") or source.get("artifact_id")),
                "external_root",
                predecessor_digest,
            )
            continue
        declared_identifier = source.get("predecessor_record_id")
        verify(
            f"predecessor_pair:{filename}",
            declared_identifier is None
            or declared_identifier == predecessor_identifier,
        )
        witness(
            "predecessor",
            cast(str, source.get("record_id") or source.get("artifact_id")),
            predecessor_identifier,
            predecessor_digest,
        )

    profile_rows = rows(profile_registry.get("profiles"), "profiles")
    profile_ids = set(identifiers(profile_rows, "profile_id", "profiles"))
    population_contract = profile_registry.get("population_contract")
    verify("profile_population_contract_object", isinstance(population_contract, dict))
    verify(
        "profile_count_declared",
        len(profile_ids)
        == cast(dict[str, Any], population_contract).get("positive_profile_count"),
    )
    lifecycle_rows = rows(lifecycle_matrix.get("rows"), "lifecycle_rows")
    lifecycle_profile_ids = set(
        identifiers(lifecycle_rows, "profile_id", "lifecycle_rows")
    )
    lifecycle_columns = strings(lifecycle_matrix.get("columns"), "lifecycle_columns")
    verify(
        "lifecycle_columns_unique",
        len(lifecycle_columns) == len(set(lifecycle_columns)),
    )
    verify("lifecycle_profiles_exact", lifecycle_profile_ids == profile_ids)
    lifecycle_cell_count = 0
    for lifecycle_row in lifecycle_rows:
        cells = lifecycle_row.get("cells")
        verify("lifecycle_cells_object", isinstance(cells, dict))
        cell_map = cast(dict[str, Any], cells)
        verify("lifecycle_cell_keys_exact", set(cell_map) == set(lifecycle_columns))
        profile_id = cast(str, lifecycle_row["profile_id"])
        for column, value in sorted(cell_map.items()):
            verify("lifecycle_cell_nonblank", isinstance(value, str) and bool(value))
            lifecycle_cell_count += 1
            witness("lifecycle_cell", profile_id, column, cast(str, value))

    d9_obligation_rows = rows(
        d9_debt.get("post_spec_verification_obligations"), "D9_obligations"
    )
    d9_obligation_ids = set(
        identifiers(d9_obligation_rows, "obligation_id", "D9_obligations")
    )
    verify("D9_obligations_carried_to_D10", d9_obligation_ids <= obligation_ids)
    for obligation_id in sorted(d9_obligation_ids):
        witness("D9_obligation_carry", obligation_id)

    object_rows = rows(
        provenance.get("normatively_load_bearing_objects"), "parent_objects"
    )
    object_ids = set(identifiers(object_rows, "object_id", "parent_objects"))
    contract_rows = rows(
        provenance.get("normative_equation_contract_registry"), "equation_contracts"
    )
    contract_ids = set(
        identifiers(contract_rows, "equation_contract_id", "equation_contracts")
    )
    contract_parent_reference_count = 0
    contract_claim_reference_count = 0
    contract_profile_reference_count = 0
    for contract in contract_rows:
        contract_id = cast(str, contract["equation_contract_id"])
        for object_id in strings(
            contract.get("parent_object_ids"), f"contract_objects:{contract_id}"
        ):
            verify(
                f"contract_object_resolves:{contract_id}:{object_id}",
                object_id in object_ids,
            )
            contract_parent_reference_count += 1
            witness("contract_parent", contract_id, object_id)
        for claim_id in strings(
            contract.get("accepted_claim_ids"), f"contract_claims:{contract_id}"
        ):
            verify(
                f"contract_claim_resolves:{contract_id}:{claim_id}",
                claim_id in current_ids,
            )
            contract_claim_reference_count += 1
            witness("contract_claim", contract_id, claim_id)
        for profile_id in strings(
            contract.get("profile_ids"), f"contract_profiles:{contract_id}"
        ):
            verify(
                f"contract_profile_resolves:{contract_id}:{profile_id}",
                profile_id in profile_ids,
            )
            contract_profile_reference_count += 1
            witness("contract_profile", contract_id, profile_id)
    coverage = provenance.get("equation_contract_coverage")
    verify("coverage_object", isinstance(coverage, dict))
    coverage_map = cast(dict[str, Any], coverage)
    verify(
        "parent_object_count_declared",
        len(object_ids) == coverage_map.get("parent_atomic_contract_count"),
    )
    verify(
        "equation_contract_count_declared",
        len(contract_ids) == coverage_map.get("equation_contract_count"),
    )
    covered_object_ids = strings(
        coverage_map.get("parent_object_ids_covered"), "covered_objects"
    )
    verify(
        "parent_objects_covered",
        set(covered_object_ids) == object_ids,
    )
    for object_id in covered_object_ids:
        witness("coverage_parent", object_id)
    covered_claim_ids = strings(
        coverage_map.get("accepted_claim_ids_covered"), "covered_claims"
    )
    verify(
        "current_claims_covered",
        set(covered_claim_ids) == current_ids,
    )
    for claim_id in covered_claim_ids:
        witness("coverage_claim", claim_id)

    authorization_map = {
        "normative": "normative_common_claim_ids",
        "optional": "optional_profile_claim_ids",
        "conditional": "conditional_claim_ids",
        "open": "open_claim_ids",
        "negative": "negative_claim_ids",
    }
    authorization_sets: dict[str, set[str]] = {}
    for claim_class, field in authorization_map.items():
        claim_ids = strings(authorization.get(field), field)
        verify(
            f"authorization_unique:{claim_class}",
            len(claim_ids) == len(set(claim_ids)),
        )
        authorization_sets[claim_class] = set(claim_ids)
        for claim_id in claim_ids:
            witness("authorization_claim_class", claim_class, claim_id)
    authorization_occurrences = Counter(
        claim_id for values in authorization_sets.values() for claim_id in values
    )
    verify(
        "authorization_partition",
        authorization_occurrences == Counter({claim_id: 1 for claim_id in current_ids}),
    )
    topology_classes: dict[str, set[str]] = {
        claim_class: set() for claim_class in authorization_sets
    }
    for claim in current_rows:
        claim_class_value = claim.get("claim_class")
        verify(
            "topology_claim_class_known",
            isinstance(claim_class_value, str)
            and claim_class_value in topology_classes,
        )
        topology_classes[cast(str, claim_class_value)].add(cast(str, claim["claim_id"]))
    verify("claim_class_authorization_exact", topology_classes == authorization_sets)

    normalized_witnesses = {
        family: sorted(rows) for family, rows in sorted(relationship_witnesses.items())
    }
    relationship_witness = {
        "schema": "grcv4_explorer_relationship_witness_v1",
        "family_count": len(normalized_witnesses),
        "relationship_count": sum(len(rows) for rows in normalized_witnesses.values()),
        "families": {
            family: {"count": len(rows), "digest": digest(rows)}
            for family, rows in normalized_witnesses.items()
        },
        "witness_digest": digest(normalized_witnesses),
    }
    return {
        "assertion_count": len(assertions),
        "assertions_digest": digest(assertions),
        "claim_debt_edge_count": len(flat_edges),
        "evidence_reference_occurrence_count": evidence_reference_occurrences,
        "predecessor_link_count": predecessor_link_count,
        "external_predecessor_root_count": external_predecessor_root_count,
        "profile_count": len(profile_ids),
        "lifecycle_cell_count": lifecycle_cell_count,
        "D9_obligation_count": len(d9_obligation_ids),
        "parent_object_count": len(object_ids),
        "equation_contract_count": len(contract_ids),
        "contract_parent_reference_count": contract_parent_reference_count,
        "contract_claim_reference_count": contract_claim_reference_count,
        "contract_profile_reference_count": contract_profile_reference_count,
        "relationship_witness": relationship_witness,
    }


def main() -> int:
    repo_root = repository_root()
    if Path(sys.prefix).resolve() != (repo_root / ".venv").resolve():
        raise RuntimeError("run this command with the repository .venv Python")
    records_root = SIDE_TOOL_ROOT / "records"
    et_c0_path = records_root / "ETC0SourceAndLayoutContract.json"
    manifest_path = records_root / "ETC1SourceBundleManifest.json"
    admission_path = records_root / "ETC1SourceAdapterAdmission.json"
    report_path = records_root / "ETC1SourceAdapterAdmission.md"
    et_c0 = load_et_c0_contract(et_c0_path)
    manifest = load_json_object(manifest_path)
    admission = load_json_object(admission_path)
    checks: list[str] = []

    def check(name: str, condition: bool) -> None:
        if not condition:
            raise RuntimeError(f"ET-C1 audit failed: {name}")
        checks.append(name)

    check(
        "manifest_canonical_bytes",
        manifest_path.read_bytes() == canonical_bytes(manifest) + b"\n",
    )
    check(
        "admission_canonical_bytes",
        admission_path.read_bytes() == canonical_bytes(admission) + b"\n",
    )
    check(
        "manifest_digest",
        manifest.get("source_bundle_digest")
        == digest(
            {
                key: value
                for key, value in manifest.items()
                if key != "source_bundle_digest"
            }
        ),
    )
    check(
        "admission_digest",
        admission.get("record_digest") == record_digest(admission, "record_digest"),
    )
    check("admission_status", admission.get("status") == "accepted")
    check(
        "predecessor_digest",
        admission.get("predecessor", {}).get("record_digest") == et_c0["record_digest"],
    )
    check(
        "trust_boundary",
        admission.get("trust_boundary")
        == {
            "root": "human_accepted_ET_C0",
            "ET_C1_revalidates_ET_C0_status_and_digest": True,
            "ET_C1_does_not_rederive_human_acceptance": True,
            "browser_runtime_not_implemented": True,
        },
    )

    admitted = admitted_rows(et_c0)
    manifest_rows = manifest.get("records")
    check("manifest_rows", isinstance(manifest_rows, list))
    assert isinstance(manifest_rows, list)
    expected_by_path = {row["path"]: row for row in admitted}
    observed_by_path = {row["path"]: row for row in manifest_rows}
    check("source_path_population", set(observed_by_path) == set(expected_by_path))
    check("source_record_count", len(manifest_rows) == len(admitted) == 33)
    for relative, expected in expected_by_path.items():
        observed = observed_by_path[relative]
        check(
            f"source_identity:{relative}",
            observed["source_id"] == expected["source_id"]
            and observed["file_sha256"] == expected["file_sha256"]
            and observed["canonical_digest"] == expected["canonical_digest"],
        )
        check(
            f"source_bytes:{relative}",
            file_sha256(repo_root / relative) == expected["file_sha256"],
        )

    observation = discover_sources(repo_root, admitted)
    check("source_observation_exact", observation["state"] == "current_bundle_exact")
    check(
        "source_observation_bound",
        manifest.get("source_observation_digest") == observation["observation_digest"],
    )
    rebuilt, rebuilt_observation = build_source_bundle(repo_root, et_c0_path)
    check(
        "deterministic_manifest", canonical_bytes(rebuilt) == canonical_bytes(manifest)
    )
    check(
        "deterministic_observation",
        canonical_bytes(rebuilt_observation) == canonical_bytes(observation),
    )

    reference = manifest.get("reference_validation")
    check("reference_validation_object", isinstance(reference, dict))
    assert isinstance(reference, dict)
    expected_counts = {
        "current_claim_count": 39,
        "historical_claim_count": 29,
        "debt_transformation_count": 29,
        "verification_obligation_count": 11,
        "D9_predecessor_obligation_occurrence_count": 4,
        "profile_count": 10,
        "lifecycle_operation_count": 26,
        "lifecycle_cell_count": 260,
        "parent_object_count": 67,
        "equation_contract_count": 152,
    }
    for field, expected_count in expected_counts.items():
        check(f"population:{field}", reference.get(field) == expected_count)
    relationship_summary = independently_verify_cross_source_relationships(
        repo_root, admitted
    )
    check(
        "independent_relationship_assertions_executed",
        relationship_summary["assertion_count"] > 0,
    )
    check(
        "independent_relationship_witness_exact",
        relationship_summary["relationship_witness"]
        == reference.get("relationship_witness"),
    )
    check(
        "independent_relationship_population",
        relationship_summary["external_predecessor_root_count"] == 1
        and relationship_summary["profile_count"] == 10
        and relationship_summary["lifecycle_cell_count"] == 260
        and relationship_summary["D9_obligation_count"] == 4
        and relationship_summary["parent_object_count"] == 67
        and relationship_summary["equation_contract_count"] == 152,
    )
    identity_counts, external_predecessor_roots = (
        independently_derive_embedded_identities(repo_root, admitted)
    )
    check(
        "embedded_identity_total_independent",
        identity_counts["total"]
        == reference.get("embedded_source_identity_count")
        == 74,
    )
    check(
        "embedded_identity_local_independent",
        identity_counts["local"]
        == reference.get("embedded_local_source_identity_count")
        == 70,
    )
    check(
        "embedded_identity_external_independent",
        identity_counts["external"]
        == reference.get("embedded_external_source_attestation_count")
        == 4,
    )
    check(
        "external_predecessor_root_independent",
        external_predecessor_roots
        == reference.get("external_predecessor_root_count")
        == 1,
    )
    check("reference_checks_passed", reference.get("all_checks_passed") is True)
    decisions_root = repo_root / (
        "implementation/investigations/grc9v4-constitutive-design/decisions"
    )
    topology = load_json_object(decisions_root / "D10NormativeClaimTopology.json")
    authorization = load_json_object(
        decisions_root / "D10SpecificationAuthorizationProfile.json"
    )
    topology_classes: dict[str, set[str]] = {}
    for claim in topology["claims"]:
        topology_classes.setdefault(claim["claim_class"], set()).add(claim["claim_id"])
    authorization_classes = {
        "normative": set(authorization["normative_common_claim_ids"]),
        "optional": set(authorization["optional_profile_claim_ids"]),
        "conditional": set(authorization["conditional_claim_ids"]),
        "open": set(authorization["open_claim_ids"]),
        "negative": set(authorization["negative_claim_ids"]),
    }
    check(
        "claim_authority_classification_independent",
        topology_classes == authorization_classes,
    )
    claim_crosscheck = admission.get("claim_authority_crosscheck")
    check("claim_crosscheck_object", isinstance(claim_crosscheck, dict))
    assert isinstance(claim_crosscheck, dict)
    check(
        "claim_crosscheck_recorded",
        claim_crosscheck.get("topology_claim_class_matches_authorization_category")
        is True
        and claim_crosscheck.get("current_claim_count") == 39,
    )
    legacy_source = load_json_object(
        decisions_root / "D10_1PreliminarySubstrateProvenance.json"
    )
    check(
        "legacy_source_schema_absent",
        "schema_version" not in legacy_source and "record_type" not in legacy_source,
    )
    check(
        "legacy_schema_boundary_recorded",
        admission.get("schema_boundary")
        == {
            "schema_declared_record_count": 32,
            "filename_admitted_legacy_records": [
                "D10_1PreliminarySubstrateProvenance.json"
            ],
            "schema_addition_or_change_requires_readmission": True,
        },
    )
    check(
        "source_bytes_unchanged",
        manifest.get("source_hashes_unchanged_during_admission") is True,
    )
    authority = admission.get("authority")
    check("authority_object", isinstance(authority, dict))
    assert isinstance(authority, dict)
    check("graph_kernel_closed", authority.get("graph_kernel_implemented") is False)
    check("iteration_2_authorized", authority.get("iteration_2_authorized") is True)
    check(
        "accepted_sources_unmodified",
        authority.get("accepted_source_records_modified") is False,
    )
    check("no_scientific_claim", authority.get("scientific_claim_added") is False)
    report = report_path.read_text(encoding="utf-8")
    check("report_bundle_digest", str(manifest["source_bundle_digest"]) in report)
    check("report_record_digest", str(admission["record_digest"]) in report)
    for value in walk_strings([manifest, admission]):
        check(
            "no_absolute_path",
            not value.startswith("/") and re.match(r"^[A-Za-z]:[\\/]", value) is None,
        )
        check("no_machine_root", repo_root.as_posix() not in value)
    print(
        "ET_C1_AUDIT_PASS "
        f"checks={len(checks)} "
        f"relationship_assertions={relationship_summary['assertion_count']} "
        f"relationships={relationship_summary['assertions_digest']} "
        "relationship_witnesses="
        f"{relationship_summary['relationship_witness']['relationship_count']} "
        "witness_digest="
        f"{relationship_summary['relationship_witness']['witness_digest']} "
        f"bundle={manifest['source_bundle_digest']} "
        f"record={admission['record_digest']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

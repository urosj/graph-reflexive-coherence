"""Cross-source admission checks that stop before graph semantics."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any, Iterator, cast

from .adapters import SourceDocument
from .canonical import digest, file_sha256, load_json_object
from .errors import SourceAdmissionError


REQUIRED_CROSS_SOURCE_DOCUMENTS = {
    "D10NormativeClaimTopology.json",
    "D10DebtClaimTransformationLedger.json",
    "D10_2FullSubstrateProvenanceAndPromotionAudit.json",
    "D9ProfileStateLifecycleRegistry.json",
    "D9LifecycleCoverageMatrix.json",
    "D9ResidualDebtLedger.json",
    "D10SpecificationAuthorizationProfile.json",
}


def _relationship_witness_summary(
    witnesses: dict[str, list[list[str]]],
) -> dict[str, Any]:
    normalized = {family: sorted(rows) for family, rows in sorted(witnesses.items())}
    return {
        "schema": "grcv4_explorer_relationship_witness_v1",
        "family_count": len(normalized),
        "relationship_count": sum(len(rows) for rows in normalized.values()),
        "families": {
            family: {"count": len(rows), "digest": digest(rows)}
            for family, rows in normalized.items()
        },
        "witness_digest": digest(normalized),
    }


def _rows(value: Any, label: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not all(isinstance(row, dict) for row in value):
        raise SourceAdmissionError(f"malformed row collection: {label}")
    return cast(list[dict[str, Any]], value)


def _strings(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise SourceAdmissionError(f"malformed string collection: {label}")
    return cast(list[str], value)


def _ids(rows: list[dict[str, Any]], key: str, label: str) -> list[str]:
    result: list[str] = []
    for index, row in enumerate(rows):
        value = row.get(key)
        if not isinstance(value, str) or not value:
            raise SourceAdmissionError(f"missing ID: {label}/{index}/{key}")
        result.append(value)
    return result


def _unique(values: list[str], label: str) -> set[str]:
    if len(values) != len(set(values)):
        raise SourceAdmissionError(f"duplicate IDs: {label}")
    return set(values)


def _walk_objects(value: Any) -> Iterator[dict[str, Any]]:
    if isinstance(value, dict):
        row = cast(dict[str, Any], value)
        yield row
        for child in row.values():
            yield from _walk_objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_objects(child)


def _require(condition: bool, name: str, checks: list[str]) -> None:
    if not condition:
        raise SourceAdmissionError(f"cross-source admission failed: {name}")
    checks.append(name)


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _source_identity_checks(
    repo_root: Path,
    documents: list[SourceDocument],
    checks: list[str],
) -> dict[str, int]:
    seen: set[tuple[str, str, str]] = set()
    local_count = 0
    external_count = 0
    for document in documents:
        for row in _walk_objects(document.data):
            path_value = row.get("path")
            sha_value = row.get("file_sha256") or row.get("sha256")
            if not isinstance(path_value, str) or not isinstance(sha_value, str):
                continue
            repository = row.get("repository", "graph-reflexive-coherence")
            if not isinstance(repository, str):
                raise SourceAdmissionError("embedded source repository is malformed")
            identity = (repository, path_value, sha_value)
            first_occurrence = identity not in seen
            seen.add(identity)
            _require(_is_sha256(sha_value), "embedded_source_sha_well_formed", checks)
            _require(
                not Path(path_value).is_absolute(), "embedded_path_relative", checks
            )
            external = (
                repository != "graph-reflexive-coherence"
                or path_value.startswith("external:")
            )
            if external:
                _require(
                    repository != "graph-reflexive-coherence"
                    or path_value.startswith("external:"),
                    "external_source_explicitly_classified",
                    checks,
                )
                for digest_field in (
                    "source_digest",
                    "semantic_decision_digest",
                    "decision_digest",
                    "artifact_digest",
                ):
                    source_digest = row.get(digest_field)
                    if source_digest is not None:
                        _require(
                            _is_sha256(source_digest),
                            "external_source_digest_well_formed",
                            checks,
                        )
                if first_occurrence:
                    external_count += 1
                continue
            target = Path(path_value)
            target = repo_root / target
            _require(target.is_file(), "embedded_source_exists", checks)
            _require(
                file_sha256(target) == sha_value,
                "embedded_source_sha_exact",
                checks,
            )
            source_digests = {
                value
                for digest_field in (
                    "source_digest",
                    "semantic_decision_digest",
                    "decision_digest",
                    "artifact_digest",
                )
                if isinstance((value := row.get(digest_field)), str)
            }
            if source_digests and target.suffix == ".json":
                target_data = load_json_object(target)
                declared = target_data.get("decision_record_digest") or target_data.get(
                    "artifact_digest"
                )
                _require(
                    source_digests == {declared},
                    "embedded_source_digest_exact",
                    checks,
                )
            if first_occurrence:
                local_count += 1
    return {
        "total": local_count + external_count,
        "local_byte_verified": local_count,
        "external_attested": external_count,
    }


def validate_cross_source_contract(
    repo_root: Path,
    documents: list[SourceDocument],
) -> dict[str, Any]:
    checks: list[str] = []
    witnesses: dict[str, list[list[str]]] = {}

    def witness(family: str, *parts: str) -> None:
        witnesses.setdefault(family, []).append(list(parts))

    by_name = {document.filename: document for document in documents}
    _require(len(by_name) == len(documents), "source_filenames_unique", checks)
    _require(
        REQUIRED_CROSS_SOURCE_DOCUMENTS <= set(by_name),
        "required_cross_source_documents_present",
        checks,
    )

    topology = by_name["D10NormativeClaimTopology.json"].data
    debt = by_name["D10DebtClaimTransformationLedger.json"].data
    provenance = by_name["D10_2FullSubstrateProvenanceAndPromotionAudit.json"].data
    profile_registry = by_name["D9ProfileStateLifecycleRegistry.json"].data
    lifecycle_matrix = by_name["D9LifecycleCoverageMatrix.json"].data
    d9_debt = by_name["D9ResidualDebtLedger.json"].data
    authorization = by_name["D10SpecificationAuthorizationProfile.json"].data

    current_rows = _rows(topology.get("claims"), "claims")
    historical_rows = _rows(
        topology.get("historical_claim_nodes"), "historical_claim_nodes"
    )
    current_ids = _unique(_ids(current_rows, "claim_id", "claims"), "current claims")
    historical_ids = _unique(
        _ids(historical_rows, "claim_id", "historical_claim_nodes"),
        "historical claims",
    )
    _require(current_ids.isdisjoint(historical_ids), "claim_sets_disjoint", checks)
    _require(len(current_ids) == topology.get("claim_count"), "claim_count", checks)
    _require(
        len(historical_ids) == topology.get("historical_claim_count"),
        "historical_claim_count",
        checks,
    )

    debt_rows = _rows(debt.get("debt_transformations"), "debt_transformations")
    debt_ids = _unique(
        _ids(debt_rows, "debt_id", "debt_transformations"), "debt transformations"
    )
    obligation_rows = _rows(
        debt.get("verification_obligations"), "verification_obligations"
    )
    obligation_ids = _unique(
        _ids(obligation_rows, "obligation_id", "verification_obligations"),
        "verification obligations",
    )
    _require(len(debt_ids) == debt.get("debt_count"), "debt_count", checks)
    _require(
        len(obligation_ids) == debt.get("verification_obligation_count"),
        "verification_obligation_count",
        checks,
    )

    expanded_edges: list[tuple[str, str, tuple[str, ...]]] = []
    for claim in [*current_rows, *historical_rows]:
        claim_id = cast(str, claim["claim_id"])
        for edge in _rows(claim.get("debt_edges"), f"{claim_id}/debt_edges"):
            debt_id = edge.get("debt_id")
            _require(debt_id in debt_ids, "claim_debt_reference", checks)
            edge_types = tuple(sorted(_strings(edge.get("edge_types"), "edge_types")))
            expanded_edges.append((claim_id, cast(str, debt_id), edge_types))
    flat_edges = []
    for edge in _rows(topology.get("claim_debt_edges"), "claim_debt_edges"):
        flat_edges.append(
            (
                cast(str, edge.get("claim_id")),
                cast(str, edge.get("debt_id")),
                tuple(sorted(_strings(edge.get("edge_types"), "edge_types"))),
            )
        )
    _require(
        Counter(expanded_edges) == Counter(flat_edges),
        "claim_debt_edges_reciprocal",
        checks,
    )
    _require(
        len(flat_edges) == topology.get("claim_debt_edge_count"),
        "claim_debt_edge_count",
        checks,
    )
    for claim_id, debt_id, edge_types in flat_edges:
        witness("claim_debt_edge", claim_id, debt_id, *edge_types)

    for row in debt_rows:
        debt_id = cast(str, row["debt_id"])
        blocked_claim_ids = _strings(
            row.get("blocked_claim_ids"), f"{debt_id}/blocked_claim_ids"
        )
        _require(
            set(blocked_claim_ids) <= current_ids | historical_ids,
            "debt_blocked_claim_ids_resolve",
            checks,
        )
        for claim_id in blocked_claim_ids:
            witness("debt_claim_reference", debt_id, "blocked_claim_ids", claim_id)
        for field in (
            "supported_claim_ids",
            "conditioned_claim_ids",
            "negative_successor_claim_ids",
            "routed_claim_ids",
            "successor_claim_ids",
        ):
            claim_ids = _strings(row.get(field), f"{debt_id}/{field}")
            _require(
                set(claim_ids) <= current_ids,
                f"debt_{field}_resolve",
                checks,
            )
            for claim_id in claim_ids:
                witness("debt_claim_reference", debt_id, field, claim_id)
        predecessor_claim_ids = _strings(
            row.get("predecessor_claim_ids"), "predecessor_claim_ids"
        )
        _require(
            set(predecessor_claim_ids) <= historical_ids,
            "debt_predecessor_claim_ids_resolve",
            checks,
        )
        for claim_id in predecessor_claim_ids:
            witness("debt_claim_reference", debt_id, "predecessor_claim_ids", claim_id)
        verification = row.get("verification_obligation")
        _require(
            verification is None or verification in obligation_ids,
            "debt_verification_obligation_resolves",
            checks,
        )
        if isinstance(verification, str):
            witness("debt_verification_obligation", debt_id, verification)

    source_identifiers = {document.record_identifier for document in documents}
    for claim in [*current_rows, *historical_rows]:
        claim_id = cast(str, claim["claim_id"])
        evidence_refs = _strings(claim.get("evidence_refs"), "evidence_refs")
        _require(
            set(evidence_refs) <= source_identifiers,
            "claim_evidence_refs_resolve",
            checks,
        )
        for source_id in evidence_refs:
            witness("claim_evidence", claim_id, source_id)
    for row in debt_rows:
        debt_id = cast(str, row["debt_id"])
        evidence_refs = _strings(row.get("evidence_refs"), "evidence_refs")
        _require(
            set(evidence_refs) <= source_identifiers,
            "debt_evidence_refs_resolve",
            checks,
        )
        for source_id in evidence_refs:
            witness("debt_evidence", debt_id, source_id)

    digest_map = {document.declared_digest: document for document in documents}
    external_predecessor_count = 0
    for document in documents:
        predecessor_digest = document.data.get("predecessor_decision_digest")
        if not isinstance(predecessor_digest, str):
            continue
        predecessor = digest_map.get(predecessor_digest)
        if predecessor is None:
            _require(
                document.data.get("gate_id") == "D0"
                and document.data.get("predecessor_record_id") is None,
                "predecessor_digest_resolves",
                checks,
            )
            external_predecessor_count += 1
            witness(
                "predecessor",
                document.record_identifier,
                "external_root",
                predecessor_digest,
            )
            continue
        predecessor_id = document.data.get("predecessor_record_id")
        _require(
            predecessor_id is None or predecessor_id == predecessor.record_identifier,
            "predecessor_id_digest_pair_resolves",
            checks,
        )
        witness(
            "predecessor",
            document.record_identifier,
            predecessor.record_identifier,
            predecessor_digest,
        )

    profile_rows = _rows(profile_registry.get("profiles"), "profiles")
    profile_ids = _unique(_ids(profile_rows, "profile_id", "profiles"), "profiles")
    population_contract = cast(dict[str, Any], profile_registry["population_contract"])
    _require(
        len(profile_ids) == population_contract.get("positive_profile_count"),
        "profile_population_count",
        checks,
    )
    matrix_rows = _rows(lifecycle_matrix.get("rows"), "lifecycle rows")
    matrix_profile_ids = _unique(
        _ids(matrix_rows, "profile_id", "lifecycle rows"), "lifecycle profiles"
    )
    columns = set(_strings(lifecycle_matrix.get("columns"), "lifecycle columns"))
    _require(matrix_profile_ids == profile_ids, "lifecycle_profile_coverage", checks)
    for row in matrix_rows:
        cells = row.get("cells")
        _require(isinstance(cells, dict), "lifecycle_cells_object", checks)
        _require(
            set(cast(dict[str, Any], cells)) == columns, "lifecycle_cells_exact", checks
        )
        _require(
            all(
                isinstance(value, str) and value
                for value in cast(dict[str, Any], cells).values()
            ),
            "lifecycle_cells_nonblank",
            checks,
        )
        profile_id = cast(str, row["profile_id"])
        for column, value in sorted(cast(dict[str, Any], cells).items()):
            witness("lifecycle_cell", profile_id, column, cast(str, value))

    d9_obligations = _rows(
        d9_debt.get("post_spec_verification_obligations"),
        "post_spec_verification_obligations",
    )
    d9_obligation_ids = _unique(
        _ids(d9_obligations, "obligation_id", "D9 obligations"), "D9 obligations"
    )
    _require(
        d9_obligation_ids <= obligation_ids,
        "D9_obligations_carried_into_D10",
        checks,
    )
    for obligation_id in sorted(d9_obligation_ids):
        witness("D9_obligation_carry", obligation_id)

    object_rows = _rows(
        provenance.get("normatively_load_bearing_objects"), "parent objects"
    )
    object_ids = _unique(_ids(object_rows, "object_id", "objects"), "objects")
    contract_rows = _rows(
        provenance.get("normative_equation_contract_registry"), "contracts"
    )
    contract_ids = _unique(
        _ids(contract_rows, "equation_contract_id", "contracts"), "contracts"
    )
    for row in contract_rows:
        contract_id = cast(str, row["equation_contract_id"])
        parent_object_ids = _strings(row.get("parent_object_ids"), "parent_object_ids")
        _require(
            set(parent_object_ids) <= object_ids,
            "contract_parent_objects_resolve",
            checks,
        )
        for object_id in parent_object_ids:
            witness("contract_parent", contract_id, object_id)
        accepted_claim_ids = _strings(
            row.get("accepted_claim_ids"), "accepted_claim_ids"
        )
        _require(
            set(accepted_claim_ids) <= current_ids,
            "contract_claims_resolve",
            checks,
        )
        for claim_id in accepted_claim_ids:
            witness("contract_claim", contract_id, claim_id)
        contract_profile_ids = _strings(row.get("profile_ids"), "profile_ids")
        _require(
            set(contract_profile_ids) <= profile_ids,
            "contract_profiles_resolve",
            checks,
        )
        for profile_id in contract_profile_ids:
            witness("contract_profile", contract_id, profile_id)
    coverage = cast(dict[str, Any], provenance["equation_contract_coverage"])
    _require(
        len(object_ids) == coverage.get("parent_atomic_contract_count"),
        "parent_object_count",
        checks,
    )
    _require(
        len(contract_ids) == coverage.get("equation_contract_count"),
        "equation_contract_count",
        checks,
    )
    covered_object_ids = _strings(
        coverage.get("parent_object_ids_covered"), "covered objects"
    )
    _require(
        set(covered_object_ids) == object_ids,
        "all_parent_objects_covered",
        checks,
    )
    for object_id in covered_object_ids:
        witness("coverage_parent", object_id)
    covered_claim_ids = _strings(
        coverage.get("accepted_claim_ids_covered"), "covered claims"
    )
    _require(
        set(covered_claim_ids) == current_ids,
        "all_current_claims_covered",
        checks,
    )
    for claim_id in covered_claim_ids:
        witness("coverage_claim", claim_id)

    authorization_fields = (
        "normative_common_claim_ids",
        "optional_profile_claim_ids",
        "conditional_claim_ids",
        "open_claim_ids",
        "negative_claim_ids",
    )
    authorized_claim_ids: set[str] = set()
    authorization_class_sets: dict[str, set[str]] = {}
    authorization_classes = {
        "normative_common_claim_ids": "normative",
        "optional_profile_claim_ids": "optional",
        "conditional_claim_ids": "conditional",
        "open_claim_ids": "open",
        "negative_claim_ids": "negative",
    }
    for field in authorization_fields:
        value_rows = _strings(authorization.get(field), field)
        values = set(value_rows)
        _require(
            len(value_rows) == len(values),
            "authorization_claim_ids_unique_within_class",
            checks,
        )
        _require(values <= current_ids, "authorization_claim_ids_resolve", checks)
        authorized_claim_ids.update(values)
        claim_class = authorization_classes[field]
        authorization_class_sets[claim_class] = values
        for claim_id in value_rows:
            witness("authorization_claim_class", claim_class, claim_id)
    _require(
        authorized_claim_ids == current_ids,
        "authorization_covers_current_claim_population",
        checks,
    )
    authorization_occurrences = Counter(
        claim_id for values in authorization_class_sets.values() for claim_id in values
    )
    _require(
        authorization_occurrences == Counter({claim_id: 1 for claim_id in current_ids}),
        "authorization_claim_classes_partition_current_claims",
        checks,
    )
    topology_class_sets: dict[str, set[str]] = {
        claim_class: set() for claim_class in authorization_class_sets
    }
    for claim in current_rows:
        claim_class_value = claim.get("claim_class")
        _require(
            isinstance(claim_class_value, str)
            and claim_class_value in topology_class_sets,
            "topology_current_claim_class_admitted",
            checks,
        )
        topology_class_sets[cast(str, claim_class_value)].add(
            cast(str, claim["claim_id"])
        )
    _require(
        topology_class_sets == authorization_class_sets,
        "topology_claim_class_matches_authorization_category",
        checks,
    )

    embedded_identity_counts = _source_identity_checks(repo_root, documents, checks)
    relationship_witness = _relationship_witness_summary(witnesses)
    return {
        "schema": "grcv4_explorer_source_reference_validation_v1",
        "check_count": len(checks),
        "checks_digest": __import__("hashlib")
        .sha256("\n".join(checks).encode("utf-8"))
        .hexdigest(),
        "current_claim_count": len(current_ids),
        "historical_claim_count": len(historical_ids),
        "debt_transformation_count": len(debt_ids),
        "verification_obligation_count": len(obligation_ids),
        "D9_predecessor_obligation_occurrence_count": len(d9_obligation_ids),
        "profile_count": len(profile_ids),
        "lifecycle_operation_count": len(columns),
        "lifecycle_cell_count": len(profile_ids) * len(columns),
        "parent_object_count": len(object_ids),
        "equation_contract_count": len(contract_ids),
        "embedded_source_identity_count": embedded_identity_counts["total"],
        "embedded_local_source_identity_count": embedded_identity_counts[
            "local_byte_verified"
        ],
        "embedded_external_source_attestation_count": embedded_identity_counts[
            "external_attested"
        ],
        "external_predecessor_root_count": external_predecessor_count,
        "relationship_witness": relationship_witness,
        "all_checks_passed": True,
    }

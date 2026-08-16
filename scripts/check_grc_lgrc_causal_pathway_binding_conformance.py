#!/usr/bin/env python3
"""Validate GRC/LGRC binding locks, receipts, and claim provenance."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

RULES = [
    (
        "BCF-001",
        "Every admitted pathway binding must resolve exactly to the registry and binding map.",
    ),
    (
        "BCF-002",
        "Every registered composition binding must resolve exactly to the composition matrix.",
    ),
    (
        "BCF-003",
        "Unregistered relations require explicit candidate declarations and distinct graph identities.",
    ),
    (
        "BCF-004",
        "Candidate uses require current content-addressed mechanism evidence and scoped constituent execution while remaining experimental and unpromoted.",
    ),
    (
        "BCF-005",
        "Producer pathways and compositions must retain producer identity and authority cuts.",
    ),
    (
        "BCF-006",
        "Explicit-adapter compositions must retain adapter identity and non-native ownership.",
    ),
    (
        "BCF-007",
        "Diagnostic-only relations must not carry behavioral claims across the relation.",
    ),
    (
        "BCF-008",
        "Configured route semantics must not be widened to formed-route claims.",
    ),
    (
        "BCF-009",
        "Native arbitration must not be widened to native candidate formation.",
    ),
    (
        "BCF-010",
        "Unsupported missing crossings cannot be bound as admitted compositions.",
    ),
    (
        "BCF-011",
        "Invalid relabels cannot be bound, reused, or laundered through renamed candidates without a distinct mechanism.",
    ),
    (
        "BCF-012",
        "Locks and receipts must consume the accepted registry and knowledge-plane digests.",
    ),
    (
        "BCF-013",
        "Locks and receipts must consume the accepted composition-matrix digest.",
    ),
    (
        "BCF-014",
        "The binding map, concrete symbols, source hashes, and binding policy must be current.",
    ),
    (
        "BCF-015",
        "Receipts must match the exact lock and expose declared, actual, and unused links.",
    ),
    (
        "BCF-016",
        "Every wrapper invocation must retain the pathway and stage frozen for its symbol.",
    ),
    (
        "BCF-017",
        "Dynamic pathway choices must stay within an explicit allowed set and record actual use.",
    ),
    (
        "BCF-018",
        "The binder must not select or automatically resolve ambiguous registered crossings.",
    ),
    (
        "BCF-019",
        "Endpoint co-use and chained compositions must not synthesize edges or claim ceilings.",
    ),
    (
        "BCF-020",
        "Unbound execution cannot present itself as claim-qualified pathway evidence.",
    ),
]

AUTHORITY_PATHS = {
    "registry": "specs/grc-lgrc-causal-pathway-contracts.json",
    "crosswalk": "specs/grc-lgrc-causal-pathway-evidence-crosswalk.json",
    "matrix": "specs/grc-lgrc-causal-pathway-composition-matrix.json",
    "selector": "specs/grc-lgrc-causal-pathway-selection-guide.json",
    "consolidation_policy": "specs/grc-lgrc-causal-pathway-conformance.json",
    "bindings": "specs/grc-lgrc-causal-pathway-bindings.json",
}

EXECUTABLE_STATUSES = {
    "lawful_native",
    "lawful_with_explicit_adapter",
    "diagnostic_only",
    "producer_mediated",
}


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_digest(value: Any) -> str:
    return sha256_bytes(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    )


def digest_without(document: Mapping[str, Any], field: str) -> str:
    return canonical_digest(
        {key: value for key, value in document.items() if key != field}
    )


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return value


def load_bundle(
    root: Path,
    *,
    lock_path: Path,
    receipt_path: Path,
) -> dict[str, Any]:
    bundle = {
        name: load_json(root / relative) for name, relative in AUTHORITY_PATHS.items()
    }
    bundle["lock"] = load_json(lock_path)
    bundle["receipt"] = load_json(receipt_path)
    return bundle


def add_issue(
    issues: list[dict[str, str]],
    rule_id: str,
    location: str,
    message: str,
) -> None:
    issues.append({"rule_id": rule_id, "location": location, "message": message})


def _unique_index(
    records: Iterable[Mapping[str, Any]],
    key: str,
) -> tuple[dict[str, Mapping[str, Any]], bool]:
    index: dict[str, Mapping[str, Any]] = {}
    duplicate = False
    for record in records:
        identity = str(record.get(key, ""))
        if not identity or identity in index:
            duplicate = True
        else:
            index[identity] = record
    return index, duplicate


def _candidate_is_bounded(candidate: Mapping[str, Any]) -> bool:
    blocked = set(candidate.get("blocked_claims", []))
    return (
        candidate.get("claim_ceiling") == "experimental_unregistered"
        and candidate.get("promotion_status") == "none"
        and {
            "candidate relation is admitted",
            "candidate relation is native",
            "candidate declaration is promotion",
        }
        <= blocked
    )


def _normalized_claim_text(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", value.lower()))


def _candidate_evidence_issue(
    root: Path,
    candidate: Mapping[str, Any],
) -> str | None:
    evidence = candidate.get("mechanism_evidence")
    if not isinstance(evidence, Mapping):
        return "content-addressed mechanism evidence is absent"
    expected_fields = {"evidence_kind", "mechanism_id", "path", "sha256"}
    if set(evidence) != expected_fields:
        return "mechanism evidence fields are incomplete or widened"
    if evidence.get("evidence_kind") != "content_addressed_artifact":
        return "mechanism evidence kind is not content-addressed"
    mechanism_id = str(evidence.get("mechanism_id", ""))
    relative = Path(str(evidence.get("path", "")))
    expected_sha256 = str(evidence.get("sha256", ""))
    if (
        not mechanism_id
        or not str(relative)
        or relative.is_absolute()
        or ".." in relative.parts
        or re.fullmatch(r"[0-9a-f]{64}", expected_sha256) is None
    ):
        return "mechanism evidence identity, path, or SHA-256 is invalid"
    resolved_root = root.resolve()
    target = (resolved_root / relative).resolve()
    try:
        target.relative_to(resolved_root)
    except ValueError:
        return "mechanism evidence path escapes the repository"
    if not target.is_file() or target.stat().st_size == 0:
        return "mechanism evidence artifact is missing or empty"
    if sha256_file(target) != expected_sha256:
        return "mechanism evidence content address is stale"
    try:
        artifact = load_json(target)
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        return "mechanism evidence is not a JSON object"
    expected_artifact = {
        "artifact": "causal-pathway-candidate-mechanism-evidence",
        "schema_version": "causal_pathway_candidate_mechanism_evidence_v1",
        "mechanism_id": mechanism_id,
        "candidate_kind": candidate.get("candidate_kind"),
        "proposed_source_pathway_id": candidate.get("proposed_source_pathway_id"),
        "proposed_target_pathway_id": candidate.get("proposed_target_pathway_id"),
        "supported_relation": candidate.get("proposed_relation"),
    }
    mismatched = [
        field
        for field, value in expected_artifact.items()
        if artifact.get(field) != value
    ]
    if mismatched:
        return f"mechanism evidence mismatches declaration fields {mismatched}"
    return None


def validate_bundle(
    root: Path,
    bundle: dict[str, Any],
    policy: dict[str, Any],
    active_rule_ids: set[str] | None = None,
) -> dict[str, Any]:
    """Validate one exact lock/receipt pair against current authorities."""

    issues: list[dict[str, str]] = []
    registry = bundle["registry"]
    crosswalk = bundle["crosswalk"]
    matrix = bundle["matrix"]
    selector = bundle["selector"]
    consolidation_policy = bundle["consolidation_policy"]
    bindings = bundle["bindings"]
    lock = bundle["lock"]
    receipt = bundle["receipt"]

    pathways, duplicate_pathways = _unique_index(
        registry.get("pathways", []), "pathway_id"
    )
    compositions, duplicate_compositions = _unique_index(
        matrix.get("compositions", []), "composition_id"
    )
    if duplicate_pathways:
        add_issue(
            issues, "BCF-001", "registry.pathways", "pathway identities are not unique"
        )
    if duplicate_compositions:
        add_issue(
            issues,
            "BCF-002",
            "matrix.compositions",
            "composition identities are not unique",
        )

    binding_stages: dict[tuple[str, str], Mapping[str, Any]] = {}
    binding_symbols: dict[str, tuple[str, str, Mapping[str, Any]]] = {}
    for stage in bindings.get("stage_bindings", []):
        stage_key = (str(stage.get("pathway_id", "")), str(stage.get("stage_id", "")))
        if stage_key in binding_stages:
            add_issue(issues, "BCF-014", str(stage_key), "binding stage is duplicated")
        binding_stages[stage_key] = stage
        for symbol in stage.get("symbols", []):
            symbol_id = str(symbol.get("symbol_id", ""))
            if not symbol_id or symbol_id in binding_symbols:
                add_issue(
                    issues,
                    "BCF-014",
                    symbol_id or "<missing>",
                    "binding symbol is missing or duplicated",
                )
            else:
                binding_symbols[symbol_id] = (*stage_key, symbol)

    crossing_bindings, duplicate_crossing_bindings = _unique_index(
        bindings.get("composition_crossing_bindings", []),
        "composition_id",
    )
    if duplicate_crossing_bindings:
        add_issue(
            issues,
            "BCF-014",
            "bindings.composition_crossing_bindings",
            "composition crossing identities are missing or duplicated",
        )
    required_crossing_ids = {
        composition_id
        for composition_id, composition in compositions.items()
        if composition.get("composition_status") == "lawful_with_explicit_adapter"
    }
    if set(crossing_bindings) != required_crossing_ids or bindings.get(
        "composition_crossing_binding_count"
    ) != len(crossing_bindings):
        add_issue(
            issues,
            "BCF-006",
            "bindings.composition_crossing_bindings",
            "explicit-adapter crossing closure differs from the matrix",
        )
    crossing_symbols: dict[str, Mapping[str, Any]] = {}
    for composition_id, crossing in crossing_bindings.items():
        row = compositions.get(composition_id, {})
        symbol = crossing.get("symbol", {})
        symbol_id = str(symbol.get("symbol_id", ""))
        if (
            crossing.get("crossing_kind") != "explicit_adapter_callable"
            or crossing.get("source_pathway_id") != row.get("from_pathway_id")
            or not crossing.get("source_argument_name")
            or crossing.get("target_pathway_id") != row.get("to_pathway_id")
            or symbol.get("qualified_symbol") != row.get("adapter_id")
            or symbol.get("binding_role") != "composition_adapter_entrypoint"
            or symbol.get("call_kind") != "module_function"
        ):
            add_issue(
                issues,
                "BCF-006",
                composition_id,
                "composition crossing does not identify the matrix adapter",
            )
        if (
            not symbol_id
            or symbol_id in binding_symbols
            or symbol_id in crossing_symbols
        ):
            add_issue(
                issues,
                "BCF-014",
                symbol_id or composition_id,
                "composition crossing symbol is missing or duplicated",
            )
        else:
            crossing_symbols[symbol_id] = symbol
        relative = str(symbol.get("source_path", ""))
        target = root / relative
        if (
            not relative
            or Path(relative).is_absolute()
            or not target.is_file()
            or sha256_file(target) != symbol.get("source_sha256")
        ):
            add_issue(
                issues,
                "BCF-014",
                symbol_id or composition_id,
                "composition crossing source path or hash is stale",
            )

    expected_stage_keys = {
        (pathway_id, str(stage.get("stage_id", "")))
        for pathway_id, pathway in pathways.items()
        for stage in pathway.get("stage_sequence", [])
    }
    if set(binding_stages) != expected_stage_keys:
        add_issue(
            issues,
            "BCF-001",
            "bindings.stage_bindings",
            "binding-map stage closure differs from registry",
        )

    actual_authority_digests = {
        "registry_digest": digest_without(registry, "registry_digest"),
        "crosswalk_digest": digest_without(crosswalk, "crosswalk_digest"),
        "matrix_digest": digest_without(matrix, "matrix_digest"),
        "selector_digest": digest_without(selector, "selector_digest"),
        "consolidation_policy_digest": digest_without(
            consolidation_policy, "policy_digest"
        ),
        "binding_map_digest": digest_without(bindings, "binding_map_digest"),
    }
    declared_authority_digests = {
        "registry_digest": registry.get("registry_digest"),
        "crosswalk_digest": crosswalk.get("crosswalk_digest"),
        "matrix_digest": matrix.get("matrix_digest"),
        "selector_digest": selector.get("selector_digest"),
        "consolidation_policy_digest": consolidation_policy.get("policy_digest"),
        "binding_map_digest": bindings.get("binding_map_digest"),
    }
    for field in (
        "registry_digest",
        "crosswalk_digest",
        "selector_digest",
        "consolidation_policy_digest",
    ):
        expected = policy.get("accepted_digests", {}).get(field)
        if (
            actual_authority_digests[field] != expected
            or declared_authority_digests[field] != expected
        ):
            add_issue(
                issues, "BCF-012", field, "accepted knowledge-plane digest is stale"
            )
    expected_matrix = policy.get("accepted_digests", {}).get("matrix_digest")
    if (
        actual_authority_digests["matrix_digest"] != expected_matrix
        or declared_authority_digests["matrix_digest"] != expected_matrix
    ):
        add_issue(
            issues,
            "BCF-013",
            "matrix_digest",
            "accepted composition-matrix digest is stale",
        )
    expected_bindings = policy.get("accepted_digests", {}).get("binding_map_digest")
    if (
        actual_authority_digests["binding_map_digest"] != expected_bindings
        or declared_authority_digests["binding_map_digest"] != expected_bindings
    ):
        add_issue(
            issues,
            "BCF-014",
            "binding_map_digest",
            "accepted binding-map digest is stale",
        )

    expected_rules = [
        {"rule_id": rule_id, "description": description, "severity": "fail_closed"}
        for rule_id, description in RULES
    ]
    if (
        policy.get("schema_version")
        != "grc_lgrc_causal_pathway_binding_conformance_policy_v1"
        or policy.get("status") != "frozen"
        or policy.get("rules") != expected_rules
        or digest_without(policy, "policy_digest") != policy.get("policy_digest")
    ):
        add_issue(
            issues,
            "BCF-014",
            "binding_policy",
            "binding conformance policy is not current",
        )

    consumed = {
        "registry_digest": registry.get("registry_digest"),
        "crosswalk_digest": crosswalk.get("crosswalk_digest"),
        "matrix_digest": matrix.get("matrix_digest"),
        "selector_digest": selector.get("selector_digest"),
        "policy_digest": consolidation_policy.get("policy_digest"),
    }
    for field, expected in consumed.items():
        if bindings.get(field) != expected:
            rule = "BCF-013" if field == "matrix_digest" else "BCF-012"
            add_issue(
                issues,
                rule,
                f"bindings.{field}",
                "binding map consumes a stale authority",
            )

    for symbol_id, (_, _, symbol) in binding_symbols.items():
        relative = str(symbol.get("source_path", ""))
        target = root / relative
        if (
            not relative
            or Path(relative).is_absolute()
            or not target.is_file()
            or sha256_file(target) != symbol.get("source_sha256")
        ):
            add_issue(
                issues, "BCF-014", symbol_id, "bound source path or hash is stale"
            )

    artifact_expected = {
        "source_revision": bindings.get("source_revision"),
        "registry_digest": registry.get("registry_digest"),
        "crosswalk_digest": crosswalk.get("crosswalk_digest"),
        "matrix_digest": matrix.get("matrix_digest"),
        "selector_digest": selector.get("selector_digest"),
        "binding_map_digest": bindings.get("binding_map_digest"),
        "conformance_policy_digest": consolidation_policy.get("policy_digest"),
    }
    for artifact_name, artifact in (("lock", lock), ("receipt", receipt)):
        for field, expected in artifact_expected.items():
            if artifact.get(field) == expected:
                continue
            rule = (
                "BCF-013"
                if field == "matrix_digest"
                else "BCF-014"
                if field in {"binding_map_digest", "source_revision"}
                else "BCF-012"
            )
            add_issue(
                issues,
                rule,
                f"{artifact_name}.{field}",
                "artifact authority identity is stale",
            )

    lock_bindings, duplicate_lock_bindings = _unique_index(
        lock.get("declared_pathway_bindings", []), "binding_id"
    )
    if duplicate_lock_bindings:
        add_issue(
            issues,
            "BCF-015",
            "lock.declared_pathway_bindings",
            "binding IDs are missing or duplicated",
        )
    lock_links: dict[tuple[str, str], Mapping[str, Any]] = {}
    for binding_id, binding in lock_bindings.items():
        pathway_id = str(binding.get("pathway_id", ""))
        pathway = pathways.get(pathway_id)
        if pathway is None:
            add_issue(issues, "BCF-001", binding_id, "declared pathway is not admitted")
            continue
        registry_stages = {
            str(stage.get("stage_id", ""))
            for stage in pathway.get("stage_sequence", [])
        }
        declared_stages = set(binding.get("declared_stage_ids", []))
        if not declared_stages or not declared_stages <= registry_stages:
            add_issue(
                issues,
                "BCF-001",
                binding_id,
                "declared stages do not resolve to the pathway",
            )
        if (
            binding.get("mechanism_ownership") != pathway.get("mechanism_ownership")
            or binding.get("availability") != pathway.get("availability")
            or binding.get("activation") != pathway.get("activation")
            or binding.get("configured_residue") != pathway.get("configured_residue")
            or binding.get("producer_residue") != pathway.get("producer_residue")
        ):
            add_issue(
                issues,
                "BCF-001",
                binding_id,
                "pathway contract projection widened or drifted",
            )
        for link in binding.get("expected_concrete_symbols", []):
            symbol_id = str(link.get("symbol_id", ""))
            key = (binding_id, symbol_id)
            if key in lock_links:
                add_issue(
                    issues,
                    "BCF-015",
                    f"{binding_id}:{symbol_id}",
                    "lock link is duplicated",
                )
            lock_links[key] = link
            mapped = binding_symbols.get(symbol_id)
            if mapped is None:
                add_issue(
                    issues,
                    "BCF-014",
                    symbol_id,
                    "locked symbol is absent from binding map",
                )
                continue
            mapped_pathway, mapped_stage, source_symbol = mapped
            if (
                mapped_pathway != pathway_id
                or mapped_stage != link.get("stage_id")
                or link.get("stage_id") not in declared_stages
                or any(
                    link.get(field) != source_symbol.get(field)
                    for field in (
                        "module",
                        "qualified_symbol",
                        "binding_role",
                        "call_kind",
                        "source_path",
                        "source_sha256",
                    )
                )
            ):
                add_issue(
                    issues,
                    "BCF-016",
                    f"{binding_id}:{symbol_id}",
                    "locked wrapper identity differs from binding map",
                )
            callable_identity = link.get("callable_identity", {})
            if (
                not isinstance(callable_identity, Mapping)
                or any(
                    callable_identity.get(field) != source_symbol.get(field)
                    for field in (
                        "module",
                        "qualified_symbol",
                        "source_path",
                        "source_sha256",
                    )
                )
                or not isinstance(callable_identity.get("definition_first_line"), int)
                or not callable_identity.get("definition_source_sha256")
                or callable_identity.get("callable_identity_digest")
                != digest_without(callable_identity, "callable_identity_digest")
            ):
                add_issue(
                    issues,
                    "BCF-016",
                    f"{binding_id}:{symbol_id}",
                    "locked callable fingerprint is absent, stale, or inconsistent",
                )

    lock_compositions, duplicate_lock_compositions = _unique_index(
        lock.get("declared_composition_bindings", []), "binding_id"
    )
    if duplicate_lock_compositions:
        add_issue(
            issues,
            "BCF-015",
            "lock.declared_composition_bindings",
            "composition binding IDs are missing or duplicated",
        )
    for binding_id, declared in lock_compositions.items():
        composition_id = str(declared.get("composition_id", ""))
        composition_row = compositions.get(composition_id)
        if composition_row is None:
            add_issue(
                issues, "BCF-002", binding_id, "declared composition is not registered"
            )
            continue
        status = composition_row.get("composition_status")
        if status == "unsupported_missing_crossing":
            add_issue(
                issues,
                "BCF-010",
                binding_id,
                "unsupported crossing was bound as admitted",
            )
        if status == "invalid_relabel":
            add_issue(issues, "BCF-011", binding_id, "invalid relabel was bound")
        if status in EXECUTABLE_STATUSES:
            fields = (
                "composition_id",
                "from_pathway_id",
                "from_stage_ids",
                "to_pathway_id",
                "to_stage_ids",
                "composition_status",
                "adapter_id",
                "adapter_owner",
                "authority_retained",
                "authority_transferred",
                "information_lost_or_compressed",
                "claim_ceiling",
            )
            if any(
                declared.get(field) != composition_row.get(field) for field in fields
            ):
                add_issue(
                    issues,
                    "BCF-002",
                    binding_id,
                    "composition projection differs from matrix",
                )
        expected_crossing = declared.get("expected_crossing_callable")
        if status != "lawful_with_explicit_adapter":
            if expected_crossing is not None:
                add_issue(
                    issues,
                    "BCF-006",
                    binding_id,
                    "non-adapter composition freezes an adapter crossing",
                )
            continue
        mapped_crossing = crossing_bindings.get(composition_id)
        if not isinstance(expected_crossing, Mapping) or mapped_crossing is None:
            add_issue(
                issues,
                "BCF-006",
                binding_id,
                "explicit-adapter composition lacks its frozen crossing callable",
            )
            continue
        mapped_symbol = mapped_crossing.get("symbol", {})
        crossing_fields = (
            "crossing_kind",
            "source_pathway_id",
            "source_argument_name",
            "target_pathway_id",
        )
        symbol_fields = (
            "symbol_id",
            "module",
            "qualified_symbol",
            "binding_role",
            "call_kind",
            "source_path",
            "source_sha256",
        )
        source_binding = lock_bindings.get(
            str(expected_crossing.get("source_binding_id", "")),
            {},
        )
        target_binding = lock_bindings.get(
            str(expected_crossing.get("target_binding_id", "")),
            {},
        )
        if (
            expected_crossing.get("binding_id") != binding_id
            or expected_crossing.get("composition_id") != composition_id
            or any(
                expected_crossing.get(field) != mapped_crossing.get(field)
                for field in crossing_fields
            )
            or any(
                expected_crossing.get(field) != mapped_symbol.get(field)
                for field in symbol_fields
            )
            or source_binding.get("pathway_id")
            != composition_row.get("from_pathway_id")
            or source_binding.get("composition_ids") != [composition_id]
            or target_binding.get("pathway_id") != composition_row.get("to_pathway_id")
            or target_binding.get("composition_ids") != [composition_id]
            or expected_crossing.get("source_instance_binding")
            != "exact_declared_adapter_source_instance"
            or expected_crossing.get("target_instance_binding")
            != "exact_adapter_result_reference"
        ):
            add_issue(
                issues,
                "BCF-006",
                binding_id,
                "frozen crossing identity or endpoint binding differs from the map",
            )
        for endpoint_binding, expected_role in (
            (source_binding, "declared_adapter_source_instance"),
            (target_binding, "adapter_result_reference"),
        ):
            for link in endpoint_binding.get("expected_concrete_symbols", []):
                if (
                    link.get("call_kind") != "instance_method"
                    or link.get("composition_crossing_instance_role") != expected_role
                ):
                    add_issue(
                        issues,
                        "BCF-006",
                        binding_id,
                        "adapter endpoint is not bound to the declared object flow",
                    )
        callable_identity = expected_crossing.get("callable_identity", {})
        if (
            not isinstance(callable_identity, Mapping)
            or any(
                callable_identity.get(field) != mapped_symbol.get(field)
                for field in (
                    "module",
                    "qualified_symbol",
                    "source_path",
                    "source_sha256",
                )
            )
            or not isinstance(callable_identity.get("definition_first_line"), int)
            or not callable_identity.get("definition_source_sha256")
            or callable_identity.get("callable_identity_digest")
            != digest_without(callable_identity, "callable_identity_digest")
        ):
            add_issue(
                issues,
                "BCF-006",
                binding_id,
                "frozen adapter callable fingerprint is absent or inconsistent",
            )

    declared_candidates, duplicate_candidates = _unique_index(
        lock.get("candidate_declarations", []), "candidate_id"
    )
    if duplicate_candidates:
        add_issue(
            issues,
            "BCF-004",
            "lock.candidate_declarations",
            "candidate identities are missing or duplicated",
        )
    for candidate_id, candidate in declared_candidates.items():
        if candidate_id in pathways or candidate_id in compositions:
            rule = (
                "BCF-011"
                if candidate_id in compositions
                and compositions[candidate_id].get("composition_status")
                == "invalid_relabel"
                else "BCF-004"
            )
            add_issue(
                issues,
                rule,
                candidate_id,
                "candidate identity collides with canonical authority",
            )
        if not _candidate_is_bounded(candidate):
            add_issue(
                issues,
                "BCF-004",
                candidate_id,
                "candidate is described as admitted, native, or promoted",
            )
        if candidate.get("candidate_kind") == "composition" and (
            candidate.get("proposed_source_pathway_id") not in pathways
            or candidate.get("proposed_target_pathway_id") not in pathways
            or not candidate.get("proposed_relation")
        ):
            add_issue(
                issues,
                "BCF-011",
                candidate_id,
                "composition candidate lacks distinct endpoints or new relation",
            )
        evidence_issue = (
            _candidate_evidence_issue(root, candidate)
            if candidate.get("mechanism_evidence") is not None
            else None
        )
        if evidence_issue is not None:
            add_issue(issues, "BCF-004", candidate_id, evidence_issue)
        source_id = candidate.get("proposed_source_pathway_id")
        target_id = candidate.get("proposed_target_pathway_id")
        invalid_conflicts = sorted(
            (
                composition
                for composition in compositions.values()
                if composition.get("composition_status") == "invalid_relabel"
                and composition.get("from_pathway_id") == source_id
                and composition.get("to_pathway_id") == target_id
            ),
            key=lambda item: str(item.get("composition_id", "")),
        )
        expected_conflict_ids = [
            str(composition.get("composition_id", ""))
            for composition in invalid_conflicts
        ]
        if candidate.get("invalid_relabel_conflict_ids") != expected_conflict_ids:
            add_issue(
                issues,
                "BCF-011",
                candidate_id,
                "candidate does not disclose its exact invalid-relabel endpoint conflicts",
            )
        normalized_relation = _normalized_claim_text(
            str(candidate.get("proposed_relation", ""))
        )
        restated = sorted(
            str(relabel)
            for composition in invalid_conflicts
            for relabel in composition.get("blocked_relabels", [])
            if _normalized_claim_text(str(relabel)) in normalized_relation
        )
        if restated:
            add_issue(
                issues,
                "BCF-011",
                candidate_id,
                f"candidate restates registered invalid relabels {restated}",
            )
        evidence = candidate.get("mechanism_evidence")
        if invalid_conflicts and (
            not isinstance(evidence, Mapping)
            or evidence_issue is not None
            or evidence.get("mechanism_id") in expected_conflict_ids
        ):
            add_issue(
                issues,
                "BCF-011",
                candidate_id,
                "candidate over an invalid endpoint pair lacks a distinct current mechanism",
            )
        for pathway_id in candidate.get("consumed_admitted_pathway_ids", []):
            if pathway_id not in pathways:
                add_issue(
                    issues,
                    "BCF-004",
                    candidate_id,
                    "candidate consumes an unadmitted pathway",
                )
        if candidate.get("candidate_kind") == "composition" and not {
            source_id,
            target_id,
        } <= set(candidate.get("consumed_admitted_pathway_ids", [])):
            add_issue(
                issues,
                "BCF-004",
                candidate_id,
                "candidate endpoints are not explicit consumed admitted pathways",
            )
        for composition_id in candidate.get("consumed_admitted_composition_ids", []):
            if (
                composition_id not in compositions
                or compositions[composition_id].get("composition_status")
                not in EXECUTABLE_STATUSES
            ):
                add_issue(
                    issues,
                    "BCF-004",
                    candidate_id,
                    "candidate consumes a non-executable composition",
                )

    lock_digest = digest_without(lock, "lock_digest")
    if lock.get("lock_digest") != lock_digest:
        add_issue(issues, "BCF-015", "lock.lock_digest", "lock content digest is stale")
    receipt_digest = digest_without(receipt, "receipt_digest")
    if receipt.get("receipt_digest") != receipt_digest:
        add_issue(
            issues,
            "BCF-015",
            "receipt.receipt_digest",
            "receipt content digest is stale",
        )
    if receipt.get("binding_lock_digest") != lock.get("lock_digest"):
        add_issue(
            issues,
            "BCF-015",
            "receipt.binding_lock_digest",
            "receipt does not identify the exact lock",
        )

    invocations = receipt.get("actual_stage_symbol_invocations", [])
    returned_binding_ids: set[str] = set()
    returned_stage_symbols: dict[str, list[tuple[str, str]]] = {}
    execution_event_orders: list[int] = []
    for invocation_index, invocation in enumerate(invocations):
        binding_id = str(invocation.get("binding_id", ""))
        symbol_id = str(invocation.get("symbol_id", ""))
        event_order = invocation.get("execution_event_order")
        if (
            invocation.get("invocation_index") != invocation_index
            or not isinstance(event_order, int)
            or event_order < 0
        ):
            add_issue(
                issues,
                "BCF-015",
                f"receipt.actual_stage_symbol_invocations[{invocation_index}]",
                "stage invocation index or execution order is invalid",
            )
        else:
            execution_event_orders.append(event_order)
        locked_link = lock_links.get((binding_id, symbol_id))
        if locked_link is None:
            add_issue(
                issues,
                "BCF-015",
                f"{binding_id}:{symbol_id}",
                "receipt invocation was not declared in the lock",
            )
            continue
        locked_binding = lock_bindings.get(binding_id, {})
        if (
            invocation.get("pathway_id") != locked_binding.get("pathway_id")
            or invocation.get("stage_id") != locked_link.get("stage_id")
            or invocation.get("composition_ids")
            != locked_binding.get("composition_ids")
            or invocation.get("callable_identity")
            != locked_link.get("callable_identity")
        ):
            add_issue(
                issues,
                "BCF-016",
                f"{binding_id}:{symbol_id}",
                "wrapper invocation changed its frozen pathway, stage, composition, "
                "or callable identity",
            )
        if invocation.get("outcome") not in {"returned", "raised"}:
            add_issue(
                issues,
                "BCF-015",
                f"{binding_id}:{symbol_id}",
                "invocation outcome is invalid",
            )
        if invocation.get("outcome") == "returned":
            returned_binding_ids.add(binding_id)
            returned_stage_symbols.setdefault(binding_id, []).append(
                (str(invocation.get("stage_id", "")), symbol_id)
            )

    actual_bindings, duplicate_actual_bindings = _unique_index(
        receipt.get("actual_bound_pathways_used", []), "binding_id"
    )
    if duplicate_actual_bindings or set(actual_bindings) != returned_binding_ids:
        add_issue(
            issues,
            "BCF-015",
            "receipt.actual_bound_pathways_used",
            "successful actual bindings do not match returned invocations",
        )
    for binding_id, actual in actual_bindings.items():
        locked = lock_bindings.get(binding_id)
        if locked is None:
            add_issue(
                issues, "BCF-015", binding_id, "actual binding is absent from lock"
            )
            continue
        for field in locked:
            if actual.get(field) != locked.get(field):
                add_issue(
                    issues,
                    "BCF-015",
                    binding_id,
                    f"actual binding changed locked field {field}",
                )
        stage_symbols = returned_stage_symbols.get(binding_id, [])
        expected_stages = list(dict.fromkeys(stage for stage, _ in stage_symbols))
        expected_symbols = list(dict.fromkeys(symbol for _, symbol in stage_symbols))
        if (
            actual.get("actual_stage_ids") != expected_stages
            or actual.get("actual_symbol_ids") != expected_symbols
        ):
            add_issue(
                issues,
                "BCF-015",
                binding_id,
                "actual stage/symbol summary differs from invocations",
            )

    crossing_invocations = receipt.get(
        "actual_composition_crossing_invocations",
        [],
    )
    for crossing_index, invocation in enumerate(crossing_invocations):
        binding_id = str(invocation.get("binding_id", ""))
        declared = lock_compositions.get(binding_id, {})
        expected_crossing = declared.get("expected_crossing_callable")
        event_order = invocation.get("execution_event_order")
        if (
            invocation.get("crossing_invocation_index") != crossing_index
            or not isinstance(event_order, int)
            or event_order < 0
        ):
            add_issue(
                issues,
                "BCF-015",
                f"receipt.actual_composition_crossing_invocations[{crossing_index}]",
                "crossing invocation index or execution order is invalid",
            )
        else:
            execution_event_orders.append(event_order)
        exact_fields = (
            "binding_id",
            "composition_id",
            "symbol_id",
            "source_binding_id",
            "target_binding_id",
            "callable_identity",
        )
        if not isinstance(expected_crossing, Mapping) or any(
            invocation.get(field) != expected_crossing.get(field)
            for field in exact_fields
        ):
            add_issue(
                issues,
                "BCF-006",
                f"{binding_id}:crossing:{crossing_index}",
                "adapter invocation differs from its frozen crossing callable",
            )
        if not invocation.get("crossing_scope_id") or invocation.get("outcome") not in {
            "returned",
            "raised",
        }:
            add_issue(
                issues,
                "BCF-015",
                f"{binding_id}:crossing:{crossing_index}",
                "adapter invocation lacks a scope or valid outcome",
            )

    if len(execution_event_orders) != len(set(execution_event_orders)) or sorted(
        execution_event_orders
    ) != list(range(len(execution_event_orders))):
        add_issue(
            issues,
            "BCF-015",
            "receipt.execution_event_order",
            "stage and crossing invocation order is not one complete sequence",
        )

    witnesses, duplicate_witnesses = _unique_index(
        receipt.get("composition_crossing_witnesses", []),
        "binding_id",
    )
    if duplicate_witnesses:
        add_issue(
            issues,
            "BCF-019",
            "receipt.composition_crossing_witnesses",
            "composition evidence witnesses are missing identities or duplicated",
        )
    valid_witness_ids: set[str] = set()
    for binding_id, witness in witnesses.items():
        witness_declaration = lock_compositions.get(binding_id)
        if witness_declaration is None:
            add_issue(
                issues,
                "BCF-019",
                binding_id,
                "composition witness is absent from the lock",
            )
            continue
        composition_id = str(witness_declaration.get("composition_id", ""))
        witness_row = compositions.get(composition_id)
        scope_id = witness.get("crossing_scope_id")
        if (
            witness_row is None
            or not scope_id
            or witness.get("composition_id") != composition_id
        ):
            add_issue(
                issues,
                "BCF-019",
                binding_id,
                "composition witness identity is invalid",
            )
            continue

        endpoint_binding_ids: dict[str, str] = {}
        endpoint_binding_ambiguous = False
        for pathway_id in {
            witness_row["from_pathway_id"],
            witness_row["to_pathway_id"],
        }:
            matches = [
                candidate_id
                for candidate_id, candidate in lock_bindings.items()
                if candidate.get("pathway_id") == pathway_id
                and candidate.get("composition_ids") == [composition_id]
            ]
            if len(matches) != 1:
                endpoint_binding_ambiguous = True
            else:
                endpoint_binding_ids[str(pathway_id)] = matches[0]

        from_indices = witness.get("from_invocation_indices", [])
        to_indices = witness.get("to_invocation_indices", [])
        crossing_indices = witness.get("crossing_invocation_indices", [])

        def selected_stage_invocations(
            indices: Any,
            *,
            binding_id: str | None,
            pathway_id: str,
            stage_ids: list[str],
            expected_scope_id: object,
        ) -> list[Mapping[str, Any]] | None:
            if (
                not isinstance(indices, list)
                or len(indices) != len(stage_ids)
                or any(not isinstance(index, int) for index in indices)
                or any(index < 0 or index >= len(invocations) for index in indices)
            ):
                return None
            selected = [invocations[index] for index in indices]
            if any(
                invocation.get("binding_id") != binding_id
                or invocation.get("pathway_id") != pathway_id
                or invocation.get("stage_id") != stage_id
                or invocation.get("outcome") != "returned"
                or invocation.get("crossing_scope_id") != expected_scope_id
                for invocation, stage_id in zip(selected, stage_ids, strict=True)
            ):
                return None
            return selected

        selected_from = selected_stage_invocations(
            from_indices,
            binding_id=endpoint_binding_ids.get(str(witness_row["from_pathway_id"])),
            pathway_id=str(witness_row["from_pathway_id"]),
            stage_ids=[str(item) for item in witness_row["from_stage_ids"]],
            expected_scope_id=scope_id,
        )
        selected_to = selected_stage_invocations(
            to_indices,
            binding_id=endpoint_binding_ids.get(str(witness_row["to_pathway_id"])),
            pathway_id=str(witness_row["to_pathway_id"]),
            stage_ids=[str(item) for item in witness_row["to_stage_ids"]],
            expected_scope_id=scope_id,
        )
        adapter_required = (
            witness_row.get("composition_status") == "lawful_with_explicit_adapter"
        )
        expected_ordering_rule = (
            "all_from_stages_before_crossing_before_all_to_stages"
            if adapter_required
            else "all_from_stages_before_all_to_stages"
        )
        selected_crossings: list[Mapping[str, Any]] | None = None
        if (
            isinstance(crossing_indices, list)
            and all(isinstance(index, int) for index in crossing_indices)
            and all(
                0 <= index < len(crossing_invocations) for index in crossing_indices
            )
        ):
            selected_crossings = [
                crossing_invocations[index] for index in crossing_indices
            ]
        structurally_valid = (
            not endpoint_binding_ambiguous
            and selected_from is not None
            and selected_to is not None
            and witness.get("ordering_rule") == expected_ordering_rule
            and witness.get("explicit_adapter_required") is adapter_required
            and witness.get("explicit_adapter_observed") is adapter_required
            and selected_crossings is not None
            and len(selected_crossings) == (1 if adapter_required else 0)
        )
        if structurally_valid:
            from_orders = [
                int(invocation["execution_event_order"])
                for invocation in selected_from or []
            ]
            to_orders = [
                int(invocation["execution_event_order"])
                for invocation in selected_to or []
            ]
            structurally_valid = max(from_orders) < min(to_orders)
            if adapter_required and selected_crossings:
                crossing = selected_crossings[0]
                structurally_valid = structurally_valid and (
                    crossing.get("binding_id") == binding_id
                    and crossing.get("composition_id") == composition_id
                    and crossing.get("crossing_scope_id") == scope_id
                    and crossing.get("outcome") == "returned"
                    and max(from_orders)
                    < int(crossing.get("execution_event_order", -1))
                    < min(to_orders)
                )
        if not structurally_valid:
            add_issue(
                issues,
                "BCF-019",
                binding_id,
                "composition witness lacks exact scoped endpoints or crossing order",
            )
            continue
        valid_witness_ids.add(binding_id)

    expected_exercised_ids = valid_witness_ids
    exercised, duplicate_exercised = _unique_index(
        receipt.get("registered_compositions_exercised", []), "binding_id"
    )
    if duplicate_exercised or set(exercised) != expected_exercised_ids:
        add_issue(
            issues,
            "BCF-015",
            "receipt.registered_compositions_exercised",
            "exercised compositions differ from valid scoped crossing witnesses",
        )
    for binding_id, exercised_record in exercised.items():
        if exercised_record != lock_compositions.get(binding_id):
            add_issue(
                issues,
                "BCF-002",
                binding_id,
                "exercised composition differs from its frozen declaration",
            )

    used_candidates, duplicate_used_candidates = _unique_index(
        receipt.get("candidate_relations_exercised", []), "candidate_id"
    )
    if duplicate_used_candidates:
        add_issue(
            issues,
            "BCF-004",
            "receipt.candidate_relations_exercised",
            "candidate use identities are duplicated",
        )
    for candidate_id, candidate in used_candidates.items():
        declared_candidate = declared_candidates.get(candidate_id)
        if declared_candidate is None:
            add_issue(
                issues,
                "BCF-003",
                candidate_id,
                "candidate use lacks a lock declaration",
            )
        elif any(
            candidate.get(field) != declared_candidate.get(field)
            for field in declared_candidate
        ):
            add_issue(
                issues, "BCF-004", candidate_id, "candidate use widened its declaration"
            )
        evidence_issue = _candidate_evidence_issue(root, candidate)
        if evidence_issue is not None:
            add_issue(
                issues,
                "BCF-004",
                candidate_id,
                evidence_issue,
            )
        candidate_witness = candidate.get("candidate_execution_witness")
        structurally_valid = isinstance(candidate_witness, Mapping)
        if isinstance(candidate_witness, Mapping):
            scope_id = candidate_witness.get("candidate_scope_id")
            structurally_valid = bool(scope_id) and (
                candidate_witness.get("candidate_id") == candidate_id
            )

        def selected_candidate_invocations(
            indices: object,
            *,
            scope_id: object,
            pathway_id: object | None = None,
            binding_id: object | None = None,
        ) -> list[Mapping[str, Any]] | None:
            if (
                not isinstance(indices, list)
                or not indices
                or any(not isinstance(index, int) for index in indices)
                or len(indices) != len(set(indices))
            ):
                return None
            try:
                selected = [invocations[index] for index in indices]
            except (IndexError, TypeError):
                return None
            if any(
                invocation.get("outcome") != "returned"
                or invocation.get("candidate_scope_id") != scope_id
                or (
                    pathway_id is not None
                    and invocation.get("pathway_id") != pathway_id
                )
                or (
                    binding_id is not None
                    and invocation.get("binding_id") != binding_id
                )
                for invocation in selected
            ):
                return None
            return selected

        if structurally_valid and isinstance(candidate_witness, Mapping):
            scope_id = candidate_witness.get("candidate_scope_id")
            if candidate.get("candidate_kind") == "composition":
                source_invocations = selected_candidate_invocations(
                    candidate_witness.get("source_invocation_indices"),
                    scope_id=scope_id,
                    pathway_id=candidate.get("proposed_source_pathway_id"),
                    binding_id=candidate_witness.get("source_binding_id"),
                )
                target_invocations = selected_candidate_invocations(
                    candidate_witness.get("target_invocation_indices"),
                    scope_id=scope_id,
                    pathway_id=candidate.get("proposed_target_pathway_id"),
                    binding_id=candidate_witness.get("target_binding_id"),
                )
                structurally_valid = (
                    candidate_witness.get("witness_kind")
                    == "content_addressed_source_before_target"
                    and candidate_witness.get("source_pathway_id")
                    == candidate.get("proposed_source_pathway_id")
                    and candidate_witness.get("target_pathway_id")
                    == candidate.get("proposed_target_pathway_id")
                    and candidate_witness.get("ordering_rule")
                    == "all_source_invocations_before_all_target_invocations"
                    and source_invocations is not None
                    and target_invocations is not None
                    and max(
                        int(item.get("execution_event_order", -1))
                        for item in source_invocations
                    )
                    < min(
                        int(item.get("execution_event_order", -1))
                        for item in target_invocations
                    )
                )
            else:
                constituent = selected_candidate_invocations(
                    candidate_witness.get("constituent_invocation_indices"),
                    scope_id=scope_id,
                )
                structurally_valid = (
                    candidate_witness.get("witness_kind")
                    == "content_addressed_constituent_execution"
                    and constituent is not None
                    and all(
                        item.get("pathway_id")
                        in candidate.get("consumed_admitted_pathway_ids", [])
                        for item in constituent
                    )
                )
        if not structurally_valid:
            add_issue(
                issues,
                "BCF-004",
                candidate_id,
                "candidate use lacks an exact scoped constituent-execution witness",
            )

    expected_unused = {
        "pathway_binding_ids": sorted(set(lock_bindings) - returned_binding_ids),
        "composition_binding_ids": sorted(set(lock_compositions) - set(exercised)),
        "candidate_ids": sorted(set(declared_candidates) - set(used_candidates)),
    }
    if receipt.get("declared_but_unused") != expected_unused:
        add_issue(
            issues,
            "BCF-015",
            "receipt.declared_but_unused",
            "declared-but-unused summary is incomplete",
        )
    if receipt.get("undeclared_use_violations") != []:
        add_issue(
            issues,
            "BCF-015",
            "receipt.undeclared_use_violations",
            "accepted receipt contains undeclared use",
        )

    graph = receipt.get("pathway_use_graph", {})
    graph_nodes = graph.get("nodes", [])
    graph_edges = graph.get("edges", [])
    graph_admitted_ids = {
        str(node.get("node_id", ""))
        for node in graph_nodes
        if node.get("node_kind") == "admitted_pathway"
    }
    if graph_admitted_ids != set(actual_bindings):
        add_issue(
            issues,
            "BCF-015",
            "receipt.pathway_use_graph.nodes",
            "admitted graph nodes differ from actual bindings",
        )
    for node in graph_nodes:
        if node.get("node_kind") == "admitted_pathway":
            binding = actual_bindings.get(str(node.get("node_id", "")), {})
            pathway = pathways.get(str(node.get("pathway_id", "")))
            if pathway is None or node.get("pathway_id") != binding.get("pathway_id"):
                add_issue(
                    issues,
                    "BCF-001",
                    str(node.get("node_id", "")),
                    "graph pathway node is not admitted",
                )
            elif (
                node.get("configured_residue") != pathway.get("configured_residue")
                or node.get("producer_residue") != pathway.get("producer_residue")
                or node.get("source_bindings_used") != binding.get("actual_symbol_ids")
            ):
                add_issue(
                    issues,
                    "BCF-001",
                    str(node.get("node_id", "")),
                    "graph pathway projection drifted",
                )
        elif node.get("node_kind") == "experimental_unregistered_candidate":
            candidate_id = str(node.get("candidate_id", ""))
            used_candidate = used_candidates.get(candidate_id)
            if (
                used_candidate is None
                or not _candidate_is_bounded(node)
                or node.get("mechanism_evidence")
                != used_candidate.get("mechanism_evidence")
                or node.get("candidate_execution_witness")
                != used_candidate.get("candidate_execution_witness")
            ):
                add_issue(
                    issues,
                    "BCF-003",
                    candidate_id,
                    "candidate graph node is undeclared or widened",
                )
        else:
            add_issue(
                issues,
                "BCF-003",
                str(node.get("node_id", "")),
                "graph node has no admitted or candidate identity",
            )

    graph_registered_ids: set[str] = set()
    graph_candidate_ids: set[str] = set()
    for edge in graph_edges:
        if edge.get("edge_kind") == "registered_composition":
            binding_id = str(edge.get("edge_id", ""))
            graph_registered_ids.add(binding_id)
            graph_exercised_record = exercised.get(binding_id)
            graph_row = compositions.get(str(edge.get("composition_id", "")))
            if graph_exercised_record is None or graph_row is None:
                add_issue(
                    issues,
                    "BCF-002",
                    binding_id,
                    "registered graph edge is not exercised and registered",
                )
                continue
            if edge.get("composition_status") != graph_row.get(
                "composition_status"
            ) or edge.get("claim_ceiling") != graph_row.get("claim_ceiling"):
                add_issue(
                    issues,
                    "BCF-002",
                    binding_id,
                    "registered edge widened matrix status or ceiling",
                )
            if graph_row.get("composition_status") == "producer_mediated" and (
                edge.get("producer_owner") != graph_row.get("adapter_owner")
                or edge.get("adapter_id") != graph_row.get("adapter_id")
            ):
                add_issue(
                    issues,
                    "BCF-005",
                    binding_id,
                    "producer graph edge erased producer identity",
                )
            if graph_row.get(
                "composition_status"
            ) == "lawful_with_explicit_adapter" and (
                edge.get("adapter_id") != graph_row.get("adapter_id")
                or edge.get("adapter_owner") != graph_row.get("adapter_owner")
                or edge.get("adapter_owner") in {None, "none", "native"}
            ):
                add_issue(
                    issues,
                    "BCF-006",
                    binding_id,
                    "adapter graph edge erased non-native ownership",
                )
        elif edge.get("edge_kind") == "experimental_unregistered_candidate":
            candidate_id = str(edge.get("candidate_id", ""))
            graph_candidate_ids.add(candidate_id)
            used_candidate = used_candidates.get(candidate_id)
            witness = (
                used_candidate.get("candidate_execution_witness", {})
                if used_candidate is not None
                else {}
            )
            if (
                used_candidate is None
                or not _candidate_is_bounded(edge)
                or edge.get("mechanism_evidence")
                != used_candidate.get("mechanism_evidence")
                or edge.get("candidate_execution_witness") != witness
                or edge.get("source_node_id") != witness.get("source_binding_id")
                or edge.get("target_node_id") != witness.get("target_binding_id")
            ):
                add_issue(
                    issues,
                    "BCF-003",
                    candidate_id,
                    "candidate graph edge is undeclared or widened",
                )
        else:
            add_issue(
                issues,
                "BCF-003",
                str(edge.get("edge_id", "")),
                "unregistered graph relation lacks candidate identity",
            )
    if graph_registered_ids != set(exercised):
        add_issue(
            issues,
            "BCF-015",
            "receipt.pathway_use_graph.edges",
            "registered graph edges differ from exercised compositions",
        )
    expected_candidate_edge_ids = {
        candidate_id
        for candidate_id, candidate in used_candidates.items()
        if candidate.get("candidate_kind") == "composition"
    }
    if graph_candidate_ids != expected_candidate_edge_ids:
        add_issue(
            issues,
            "BCF-003",
            "receipt.pathway_use_graph.edges",
            "candidate graph edges differ from candidate composition uses",
        )

    def validate_envelope(
        envelope: Mapping[str, Any],
        *,
        expected_pathway_binding_ids: set[str],
        expected_composition_binding_ids: set[str],
        expected_candidate_ids: set[str],
        location: str,
    ) -> None:
        pathway_claims, duplicate_claims = _unique_index(
            envelope.get("constituent_pathway_claim_ceilings", []), "binding_id"
        )
        if duplicate_claims or set(pathway_claims) != expected_pathway_binding_ids:
            add_issue(
                issues,
                "BCF-001",
                location,
                "pathway claim constituents differ from bound pathways",
            )
        for binding_id, claim in pathway_claims.items():
            binding = lock_bindings.get(binding_id, {})
            pathway = pathways.get(str(binding.get("pathway_id", "")))
            if pathway is None:
                continue
            if (
                claim.get("pathway_id") != binding.get("pathway_id")
                or claim.get("constituent_claim_ceiling")
                != pathway.get("supported_claims")
                or claim.get("blocked_claims") != pathway.get("blocked_claims")
            ):
                add_issue(
                    issues,
                    "BCF-001",
                    f"{location}:{binding_id}",
                    "pathway claim ceiling widened beyond registry",
                )
            qualifiers = claim.get("required_qualifiers", {})
            if qualifiers.get("configured_residue") != pathway.get(
                "configured_residue"
            ):
                add_issue(
                    issues,
                    "BCF-008",
                    f"{location}:{binding_id}",
                    "configured semantics were presented as formed",
                )
            if claim.get(
                "pathway_id"
            ) == "lgrc9v3.native_route_arbitration" and qualifiers.get(
                "producer_residue"
            ) != pathway.get("producer_residue"):
                add_issue(
                    issues,
                    "BCF-009",
                    f"{location}:{binding_id}",
                    "native arbitration was widened to candidate formation",
                )

        composition_claims, duplicate_composition_claims = _unique_index(
            envelope.get("constituent_composition_claim_ceilings", []), "binding_id"
        )
        if (
            duplicate_composition_claims
            or set(composition_claims) != expected_composition_binding_ids
        ):
            add_issue(
                issues,
                "BCF-002",
                location,
                "composition claim constituents differ from bound compositions",
            )
        for binding_id, claim in composition_claims.items():
            declared = lock_compositions.get(binding_id, {})
            row = compositions.get(str(declared.get("composition_id", "")))
            if row is None:
                continue
            if (
                claim.get("composition_id") != row.get("composition_id")
                or claim.get("composition_status") != row.get("composition_status")
                or claim.get("constituent_claim_ceiling") != row.get("claim_ceiling")
                or claim.get("blocked_claims") != row.get("blocked_relabels")
            ):
                rule = (
                    "BCF-007"
                    if row.get("composition_status") == "diagnostic_only"
                    else "BCF-002"
                )
                add_issue(
                    issues,
                    rule,
                    f"{location}:{binding_id}",
                    "composition claim differs from matrix ceiling",
                )

        qualifiers = envelope.get("required_qualifiers", {})
        configured = qualifiers.get("configured_semantics", [])
        for binding_id in expected_pathway_binding_ids:
            pathway_id = str(lock_bindings.get(binding_id, {}).get("pathway_id", ""))
            pathway = pathways.get(pathway_id, {})
            if pathway.get("configured_residue") and not any(
                item.get("pathway_id") == pathway_id
                and item.get("residue") == pathway.get("configured_residue")
                for item in configured
            ):
                add_issue(
                    issues,
                    "BCF-008",
                    f"{location}:{binding_id}",
                    "configured residue qualifier is absent",
                )
        if "lgrc9v3.native_route_arbitration" in {
            lock_bindings.get(binding_id, {}).get("pathway_id")
            for binding_id in expected_pathway_binding_ids
        } and not any(
            item.get("pathway_id") == "lgrc9v3.native_route_arbitration"
            and "candidate and score formation when experiment supplied"
            in item.get("producer_owned_authorities", [])
            for item in qualifiers.get("producer_cuts", [])
        ):
            add_issue(
                issues,
                "BCF-009",
                location,
                "arbitration candidate-formation producer cut is absent",
            )

        for binding_id in expected_composition_binding_ids:
            row = compositions.get(
                str(lock_compositions.get(binding_id, {}).get("composition_id", "")), {}
            )
            if row.get("composition_status") == "producer_mediated":
                found = any(
                    item.get("composition_id") == row.get("composition_id")
                    and item.get("producer_identity") == row.get("adapter_id")
                    and item.get("producer_owner") == row.get("adapter_owner")
                    and item.get("producer_owned_authorities")
                    == row.get("authority_transferred")
                    for item in qualifiers.get("producer_cuts", [])
                )
                if not found or envelope.get("contains_producer_cut") is not True:
                    add_issue(
                        issues,
                        "BCF-005",
                        f"{location}:{binding_id}",
                        "producer cut is absent from claim envelope",
                    )
            if row.get("composition_status") == "lawful_with_explicit_adapter":
                found = any(
                    item.get("composition_id") == row.get("composition_id")
                    and item.get("adapter_id") == row.get("adapter_id")
                    and item.get("adapter_owner") == row.get("adapter_owner")
                    for item in qualifiers.get("adapter_cuts", [])
                )
                if not found or envelope.get("contains_adapter_cut") is not True:
                    add_issue(
                        issues,
                        "BCF-006",
                        f"{location}:{binding_id}",
                        "adapter cut is absent from claim envelope",
                    )
            if row.get("composition_status") == "diagnostic_only":
                found = any(
                    item.get("kind") == "composition"
                    and item.get("identity") == row.get("composition_id")
                    for item in qualifiers.get("diagnostic_only_relations", [])
                )
                if (
                    not found
                    or envelope.get("contains_diagnostic_only_relation") is not True
                ):
                    add_issue(
                        issues,
                        "BCF-007",
                        f"{location}:{binding_id}",
                        "diagnostic boundary was erased",
                    )

        candidate_claims, duplicate_candidate_claims = _unique_index(
            qualifiers.get("candidate_relations", []), "candidate_id"
        )
        if (
            duplicate_candidate_claims
            or set(candidate_claims) != expected_candidate_ids
        ):
            add_issue(
                issues,
                "BCF-004",
                location,
                "candidate claim constituents differ from candidate use",
            )
        for candidate_id, candidate in candidate_claims.items():
            if not _candidate_is_bounded(candidate):
                add_issue(
                    issues,
                    "BCF-004",
                    f"{location}:{candidate_id}",
                    "candidate claim was widened",
                )
        if expected_candidate_ids and (
            envelope.get("experimental_unregistered") is not True
            or envelope.get("overall_claim_status") != "experimental_unregistered"
        ):
            add_issue(
                issues,
                "BCF-004",
                location,
                "candidate-containing envelope claims admission",
            )
        if envelope.get("composition_status_is_maturity_score") is not False:
            add_issue(
                issues,
                "BCF-019",
                location,
                "composition status became a scalar maturity score",
            )
        if envelope.get("synthesized_chain_claim") is not False:
            add_issue(
                issues,
                "BCF-019",
                location,
                "registered edges synthesized an unregistered chain claim",
            )

    validate_envelope(
        lock.get("pre_execution_claim_envelope", {}),
        expected_pathway_binding_ids=set(lock_bindings),
        expected_composition_binding_ids=set(lock_compositions),
        expected_candidate_ids=set(declared_candidates),
        location="lock.pre_execution_claim_envelope",
    )
    validate_envelope(
        receipt.get("claim_envelope", {}),
        expected_pathway_binding_ids=set(actual_bindings),
        expected_composition_binding_ids=set(exercised),
        expected_candidate_ids=set(used_candidates),
        location="receipt.claim_envelope",
    )

    alternatives, duplicate_alternatives = _unique_index(
        lock.get("allowed_pathway_alternatives", []), "alternative_set_id"
    )
    actual_alternatives, duplicate_actual_alternatives = _unique_index(
        receipt.get("allowed_pathway_alternatives_actual_use", []), "alternative_set_id"
    )
    if (
        duplicate_alternatives
        or duplicate_actual_alternatives
        or set(alternatives) != set(actual_alternatives)
    ):
        add_issue(
            issues,
            "BCF-017",
            "allowed_pathway_alternatives",
            "dynamic alternative declarations and receipt differ",
        )
    actual_pathway_ids = {
        str(binding.get("pathway_id", "")) for binding in actual_bindings.values()
    }
    declared_pathway_ids = {
        str(binding.get("pathway_id", "")) for binding in lock_bindings.values()
    }
    for alternative_id, alternatives_record in alternatives.items():
        allowed = list(alternatives_record.get("pathway_ids", []))
        actual_record = actual_alternatives.get(alternative_id, {})
        expected_actual = [
            pathway_id for pathway_id in allowed if pathway_id in actual_pathway_ids
        ]
        if (
            len(allowed) < 2
            or any(
                pathway_id not in pathways or pathway_id not in declared_pathway_ids
                for pathway_id in allowed
            )
            or not alternatives_record.get("selection_authority")
            or actual_record.get("allowed_pathway_ids") != allowed
            or actual_record.get("selection_authority")
            != alternatives_record.get("selection_authority")
            or actual_record.get("actual_pathway_ids_used") != expected_actual
        ):
            add_issue(
                issues,
                "BCF-017",
                alternative_id,
                "dynamic choice was undeclared, selected by binder, or misreported",
            )

    if (
        lock.get("semantic_selection_performed_by_binder") is not False
        or receipt.get("semantic_selection_performed_by_binder") is not False
    ):
        add_issue(
            issues,
            "BCF-018",
            "semantic_selection_performed_by_binder",
            "binder selected pathway or crossing semantics",
        )
    if lock.get("unregistered_relation_bound_without_candidate") is not False:
        add_issue(
            issues,
            "BCF-003",
            "lock.unregistered_relation_bound_without_candidate",
            "lock admits an unregistered relation",
        )
    if (
        graph.get("unregistered_edge_synthesized_from_endpoint_co_use") is not False
        or graph.get("larger_chain_claim_synthesized") is not False
    ):
        add_issue(
            issues,
            "BCF-019",
            "receipt.pathway_use_graph",
            "co-use synthesized an edge or larger chain claim",
        )

    any_success = bool(returned_binding_ids or used_candidates)
    if receipt.get("claim_qualified") is not any_success:
        add_issue(
            issues,
            "BCF-020",
            "receipt.claim_qualified",
            "claim qualification does not match successful bound use",
        )
    if (
        lock.get("claim_scope") != "bound_invocations_only"
        or receipt.get("claim_scope") != "bound_invocations_only"
        or lock.get("whole_run_causal_closure_claimed") is not False
        or receipt.get("whole_run_causal_closure_claimed") is not False
        or lock.get("untracked_execution_observable_by_binding_plane") is not False
        or receipt.get("untracked_execution_observable_by_binding_plane") is not False
        or receipt.get("external_or_untracked_causal_input")
        != "not_observable_by_binding_plane"
    ):
        add_issue(
            issues,
            "BCF-020",
            "receipt.claim_scope",
            "receipt does not preserve the operation-scoped untracked-execution boundary",
        )
    if receipt.get("unbound_execution_accepted_as_evidence") is not False:
        add_issue(
            issues,
            "BCF-020",
            "receipt.unbound_execution_accepted_as_evidence",
            "unbound execution was accepted as evidence",
        )

    known_rule_ids = {rule_id for rule_id, _ in RULES}
    active_rules = known_rule_ids if active_rule_ids is None else active_rule_ids
    if not active_rules or not active_rules <= known_rule_ids:
        raise ValueError("active_rule_ids must be a non-empty subset of known rules")
    issues = [issue for issue in issues if issue["rule_id"] in active_rules]
    rule_results = []
    for rule_id, description in RULES:
        if rule_id not in active_rules:
            continue
        matching = [issue for issue in issues if issue["rule_id"] == rule_id]
        rule_results.append(
            {
                "rule_id": rule_id,
                "description": description,
                "status": "passed" if not matching else "failed_closed",
                "issue_count": len(matching),
            }
        )
    binding_drift = any(issue["rule_id"] == "BCF-014" for issue in issues)
    return {
        "status": "passed" if not issues else "failed_closed",
        "validation_scope": "full_conformance"
        if active_rule_ids is None
        else "isolated_rules",
        "active_rule_ids": sorted(active_rules),
        "rule_count": len(active_rules),
        "passed_rule_count": sum(row["status"] == "passed" for row in rule_results),
        "failed_rule_count": sum(row["status"] != "passed" for row in rule_results),
        "issue_count": len(issues),
        "rule_results": rule_results,
        "issues": issues,
        "binding_staleness_state": "stale_pending_review"
        if binding_drift
        else "current",
        "claim_qualified_artifacts_blocked": binding_drift,
        "actual_authority_digests": actual_authority_digests,
        "pathway_binding_count": len(lock_bindings),
        "composition_binding_count": len(lock_compositions),
        "candidate_declaration_count": len(declared_candidates),
        "actual_invocation_count": len(invocations),
    }


def main() -> int:
    root_default = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=root_default)
    parser.add_argument(
        "--policy",
        type=Path,
        default=Path("specs/grc-lgrc-causal-pathway-binding-conformance.json"),
    )
    parser.add_argument(
        "--lock",
        type=Path,
        default=Path(
            "implementation/evidence/causal-pathway-binding/i115-native-pathway.lock.json"
        ),
    )
    parser.add_argument(
        "--receipt",
        type=Path,
        default=Path(
            "implementation/evidence/causal-pathway-binding/i115-native-pathway.receipt.json"
        ),
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--active-rule",
        action="append",
        choices=[rule_id for rule_id, _ in RULES],
    )
    args = parser.parse_args()
    root = args.root.resolve()

    def resolve(path: Path) -> Path:
        return path if path.is_absolute() else root / path

    policy = load_json(resolve(args.policy))
    bundle = load_bundle(
        root,
        lock_path=resolve(args.lock),
        receipt_path=resolve(args.receipt),
    )
    result = validate_bundle(
        root,
        bundle,
        policy,
        active_rule_ids=set(args.active_rule) if args.active_rule else None,
    )
    result["policy_digest"] = policy.get("policy_digest")
    result["conformance_digest"] = canonical_digest(result)
    rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        resolve(args.output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

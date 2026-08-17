#!/usr/bin/env python3
"""Validate GRC/LGRC binding locks, receipts, and claim provenance."""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
import re
from collections.abc import Iterable, Mapping
from functools import lru_cache
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
        (
            "Candidate uses require a current distinct executable identity and its "
            "exact scoped invocation while remaining experimental and unpromoted."
        ),
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
        (
            "Invalid relabels cannot be bound, semantically restated, or laundered; "
            "conflicting candidates require an independently reviewed structural "
            "distinction, a non-no-op executable result, and exact source-dependent "
            "flow through the frozen source-result parameter to the candidate "
            "result and target request, using its recursively type-preserving "
            "frozen callable default for the omission counterfactual, in the "
            "externally trusted raw transcript, plus every structured block."
        ),
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
        "The binding map, concrete symbols, source hashes, and binding policy must match an independently supplied acceptance anchor.",
    ),
    (
        "BCF-015",
        (
            "Locks and receipts must expose exact declared, actual, and unused links "
            "and match independently canonicalized claim envelopes."
        ),
    ),
    (
        "BCF-016",
        "Every wrapper invocation must retain the pathway and stage frozen for its symbol.",
    ),
    (
        "BCF-017",
        "Dynamic pathway choices require explicit consumer-owned scopes that reject out-of-set or second-branch calls while leaving unscoped work unrelated.",
    ),
    (
        "BCF-018",
        "The binder must not select or automatically resolve ambiguous registered crossings.",
    ),
    (
        "BCF-019",
        (
            "Registered composition edges require exact scoped order, a row-specific "
            "runtime object-flow contract, and an independently trusted execution "
            "transcript; endpoint co-use and chains must not synthesize edges or "
            "claim ceilings."
        ),
    ),
    (
        "BCF-020",
        "Only trusted symbol-specific committed or observed effects can present as claim-qualified pathway evidence.",
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

RETURN_CATEGORIES = {"false", "true", "none", "empty", "other"}
EFFECT_OUTCOMES = {"committed", "observed", "rejected", "no_op", "unknown"}

CANDIDATE_DECLARATION_FIELDS = (
    "candidate_id",
    "candidate_kind",
    "purpose",
    "owner",
    "consumed_admitted_pathway_ids",
    "consumed_admitted_composition_ids",
    "proposed_source_pathway_id",
    "proposed_target_pathway_id",
    "proposed_relation",
    "authority",
    "producer_residue",
    "adapter_residue",
    "configured_residue",
    "evidence_owner",
    "mechanism_evidence",
    "candidate_mechanism_link",
    "invalid_relabel_conflict_ids",
    "invalid_relabel_blocked_claims",
    "invalid_relabel_relation_review",
    "invalid_relabel_relation_review_trust_requirement",
    "proposed_relation_claim_status",
    "claim_ceiling",
    "blocked_claims",
    "promotion_status",
)
CLAIM_QUALIFYING_EFFECT_OUTCOMES = {"committed", "observed"}
EXPLICIT_ADAPTER_DATAFLOW = "exact_explicit_adapter_result_reference"
ATTESTED_OBJECT_FLOW_DATAFLOW = "externally_attested_runtime_object_flow"
EXECUTION_TRANSCRIPT_TRUST_REQUIREMENT = (
    "externally_supplied_digest_for_registered_composition_or_reviewed_candidate"
)
INVALID_RELABEL_CANDIDATE_REVIEW_TRUST_REQUIREMENT = (
    "externally_supplied_digest_for_invalid_relabel_candidate_review"
)
REVIEWED_STRUCTURAL_DISTINCTION = {
    "distinction_kind": "reviewed_external_adapter",
    "source_binding": "candidate_callable_consumes_source_result",
    "mechanism_effect": "distinct_nonempty_mapping_result",
    "target_binding": "candidate_result_supplies_follow_on_request",
}

SPECIAL_COMPOSITION_DATAFLOW_PORTS = {
    "CMP-01": (
        "transport_rebuild",
        "argument:state",
        "continuity_and_invariants",
        "receiver_state",
    ),
    "CMP-02": (
        "source_debit",
        "argument:state",
        "target_credit",
        "argument:state",
    ),
    "CMP-03": (
        "transport_rebuild",
        "argument:state",
        "packet_schedule",
        "receiver_base_state",
    ),
    "CMP-04": (
        "diagnostic_model_construction",
        "result_base_state",
        "diagnostic_rebuild",
        "receiver_state",
    ),
    "CMP-17": (
        "assemble_causal_annotation",
        "result",
        "transport_rebuild",
        "argument:evolution",
    ),
    "CMP-21": (
        "target_credit",
        "result",
        "surface_row_emission",
        "argument:processing_result",
    ),
}


def composition_dataflow_contract(
    composition_id: str,
    *,
    explicit_adapter: bool,
) -> dict[str, str]:
    """Independently derive the exact flow predicate for one matrix row."""

    if explicit_adapter:
        return {
            "contract_id": f"{composition_id}:explicit-adapter-result:v1",
            "continuity_kind": "exact_adapter_reference",
            "source_stage_id": "*",
            "source_port": "declared_adapter_source_instance",
            "target_stage_id": "*",
            "target_port": "adapter_result_reference",
        }
    ports = SPECIAL_COMPOSITION_DATAFLOW_PORTS.get(composition_id)
    if ports is None:
        ports = ("*", "receiver", "*", "receiver")
    source_stage_id, source_port, target_stage_id, target_port = ports
    return {
        "contract_id": f"{composition_id}:runtime-object-flow:v1",
        "continuity_kind": (
            "consumer_bound_equivalent_state_copy"
            if composition_id == "CMP-04"
            else "exact_object_identity"
        ),
        "source_stage_id": source_stage_id,
        "source_port": source_port,
        "target_stage_id": target_stage_id,
        "target_port": target_port,
    }


def composition_dataflow_policy_record() -> dict[str, Any]:
    """Return the frozen machine-readable family of per-row flow predicates."""

    return {
        "default_non_adapter": {
            "continuity_kind": "exact_object_identity",
            "source_stage_id": "*",
            "source_port": "receiver",
            "target_stage_id": "*",
            "target_port": "receiver",
        },
        "explicit_adapter": {
            "continuity_kind": "exact_adapter_reference",
            "source_stage_id": "*",
            "source_port": "declared_adapter_source_instance",
            "target_stage_id": "*",
            "target_port": "adapter_result_reference",
        },
        "specialized_non_adapter": {
            composition_id: {
                "continuity_kind": (
                    "consumer_bound_equivalent_state_copy"
                    if composition_id == "CMP-04"
                    else "exact_object_identity"
                ),
                "source_stage_id": ports[0],
                "source_port": ports[1],
                "target_stage_id": ports[2],
                "target_port": ports[3],
            }
            for composition_id, ports in sorted(
                SPECIAL_COMPOSITION_DATAFLOW_PORTS.items()
            )
        },
    }


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


@lru_cache(maxsize=256)
def source_symbol_parameter_names(
    root: Path,
    relative: str,
    qualified_symbol: str,
    source_sha256: str,
) -> frozenset[str]:
    """Read one source-pinned callable signature without importing runtime code."""

    del source_sha256  # Cache identity binds the parse to the declared source.
    target = root / relative
    if not relative or not qualified_symbol or not target.is_file():
        return frozenset()
    try:
        tree = ast.parse(target.read_text(encoding="utf-8"))
    except (OSError, SyntaxError, UnicodeError):
        return frozenset()
    body: list[ast.stmt] = tree.body
    parts = qualified_symbol.split(".")
    for index, part in enumerate(parts):
        matches = [
            node
            for node in body
            if isinstance(
                node,
                (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef),
            )
            and node.name == part
        ]
        if len(matches) != 1:
            return frozenset()
        selected = matches[0]
        if index == len(parts) - 1:
            if not isinstance(
                selected,
                (ast.FunctionDef, ast.AsyncFunctionDef),
            ):
                return frozenset()
            arguments = selected.args
            return frozenset(
                argument.arg
                for argument in (
                    *arguments.posonlyargs,
                    *arguments.args,
                    *arguments.kwonlyargs,
                )
            )
        if not isinstance(selected, ast.ClassDef):
            return frozenset()
        body = selected.body
    return frozenset()


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


def _source_default_payload(value: Any) -> dict[str, Any]:
    """Independently preserve Python types in one admitted default."""

    value_type = type(value)
    if value is None:
        return {"python_type": "none"}
    if value_type is bool:
        return {"python_type": "bool", "value": value}
    if value_type is int:
        return {"python_type": "int", "value": value}
    if value_type is float:
        return {"python_type": "float", "value": value}
    if value_type is str:
        return {"python_type": "str", "value": value}
    if value_type is list:
        return {
            "python_type": "list",
            "items": [_source_default_payload(item) for item in value],
        }
    if value_type is tuple:
        return {
            "python_type": "tuple",
            "items": [_source_default_payload(item) for item in value],
        }
    if value_type is dict:
        if not all(type(key) is str for key in value):
            raise ValueError
        return {
            "python_type": "dict",
            "items": {
                key: _source_default_payload(item)
                for key, item in value.items()
            },
        }
    raise ValueError


def _source_default_digest(value: Any) -> str:
    """Digest an admitted default without JSON type collapse."""

    return canonical_digest(_source_default_payload(value))


def digest_without(document: Mapping[str, Any], field: str) -> str:
    return canonical_digest(
        {key: value for key, value in document.items() if key != field}
    )


def execution_transcript_digest(
    *,
    binding_lock_digest: str,
    stage_invocations: list[Mapping[str, Any]],
    crossing_invocations: list[Mapping[str, Any]],
    candidate_mechanism_invocations: list[Mapping[str, Any]],
) -> str:
    """Digest the raw event transcript independently of derived claims."""

    return canonical_digest(
        {
            "schema_version": "causal_pathway_execution_transcript_v1",
            "binding_lock_digest": binding_lock_digest,
            "stage_invocations": stage_invocations,
            "crossing_invocations": crossing_invocations,
            "candidate_mechanism_invocations": candidate_mechanism_invocations,
        }
    )


_BINDING_SEMANTIC_SYMBOL_FIELDS = (
    "symbol_id",
    "module",
    "qualified_symbol",
    "binding_role",
    "call_kind",
    "required_keyword_arguments",
)


def binding_semantics_digest(bindings: Mapping[str, Any]) -> str:
    """Digest exact stage/crossing semantics without source-file hashes."""

    def semantic_symbol(symbol: Mapping[str, Any]) -> dict[str, Any]:
        return {
            field: copy.deepcopy(
                symbol.get(field, {} if field.endswith("arguments") else "")
            )
            for field in _BINDING_SEMANTIC_SYMBOL_FIELDS
        }

    def symbol_sort_key(symbol: Mapping[str, Any]) -> str:
        return str(symbol.get("symbol_id", ""))

    def semantic_symbols(stage: Mapping[str, Any]) -> list[dict[str, Any]]:
        symbols: list[dict[str, Any]] = [
            semantic_symbol(symbol)
            for symbol in stage.get("symbols", [])
            if isinstance(symbol, Mapping)
        ]
        return sorted(symbols, key=symbol_sort_key)

    stage_bindings = [
        {
            "pathway_id": str(stage.get("pathway_id", "")),
            "stage_id": str(stage.get("stage_id", "")),
            "symbols": semantic_symbols(stage),
        }
        for stage in bindings.get("stage_bindings", [])
        if isinstance(stage, Mapping)
    ]
    stage_bindings.sort(
        key=lambda stage: (str(stage["pathway_id"]), str(stage["stage_id"]))
    )
    crossing_bindings = []
    for crossing in bindings.get("composition_crossing_bindings", []):
        if not isinstance(crossing, Mapping):
            continue
        symbol = crossing.get("symbol", {})
        crossing_bindings.append(
            {
                "composition_id": str(crossing.get("composition_id", "")),
                "crossing_kind": str(crossing.get("crossing_kind", "")),
                "source_pathway_id": str(crossing.get("source_pathway_id", "")),
                "source_argument_name": str(
                    crossing.get("source_argument_name", "")
                ),
                "target_pathway_id": str(crossing.get("target_pathway_id", "")),
                "symbol": semantic_symbol(symbol)
                if isinstance(symbol, Mapping)
                else {},
            }
        )
    crossing_bindings.sort(key=lambda crossing: str(crossing["composition_id"]))
    return canonical_digest(
        {
            "stage_bindings": stage_bindings,
            "composition_crossing_bindings": crossing_bindings,
        }
    )


def binding_source_manifest_digest(bindings: Mapping[str, Any]) -> str:
    """Digest the exact source paths and content hashes consumed by a map."""

    source_records: set[tuple[str, str]] = set()
    for stage in bindings.get("stage_bindings", []):
        if not isinstance(stage, Mapping):
            continue
        for symbol in stage.get("symbols", []):
            if isinstance(symbol, Mapping):
                source_records.add(
                    (
                        str(symbol.get("source_path", "")),
                        str(symbol.get("source_sha256", "")),
                    )
                )
    for crossing in bindings.get("composition_crossing_bindings", []):
        if not isinstance(crossing, Mapping):
            continue
        symbol = crossing.get("symbol", {})
        if isinstance(symbol, Mapping):
            source_records.add(
                (
                    str(symbol.get("source_path", "")),
                    str(symbol.get("source_sha256", "")),
                )
            )
    return canonical_digest(
        [
            {"source_path": path, "source_sha256": digest}
            for path, digest in sorted(source_records)
        ]
    )


def _effect_outcome_contracts(
    acceptance_anchor: Mapping[str, Any],
) -> tuple[dict[str, Mapping[str, Any]], str | None]:
    """Return exact trusted contracts or the reason the set is invalid."""

    raw_contracts = acceptance_anchor.get("effect_outcome_contracts")
    if not isinstance(raw_contracts, list):
        return {}, "binding-acceptance anchor lacks effect-outcome contracts"
    contracts: dict[str, Mapping[str, Any]] = {}
    contract_ids: set[str] = set()
    for index, contract in enumerate(raw_contracts):
        if not isinstance(contract, Mapping):
            return {}, f"effect-outcome contract {index} is not an object"
        return_outcomes = contract.get("return_outcomes")
        qualifying = contract.get("claim_qualifying_outcomes")
        effect_probe = contract.get("effect_probe")
        contract_id = str(contract.get("contract_id", ""))
        symbol_id = str(contract.get("symbol_id", ""))
        effect_kind = str(contract.get("effect_kind", ""))
        contract_digest = str(contract.get("effect_contract_digest", ""))
        probe_outcomes: set[Any] = set()
        probe_is_valid = effect_probe is None
        if isinstance(effect_probe, Mapping):
            probe_kind = effect_probe.get("kind")
            if probe_kind == "boolean_attribute":
                probe_is_valid = (
                    set(effect_probe)
                    == {"kind", "attribute", "true_outcome", "false_outcome"}
                    and isinstance(effect_probe.get("attribute"), str)
                    and bool(effect_probe.get("attribute"))
                    and effect_probe.get("true_outcome") in EFFECT_OUTCOMES
                    and effect_probe.get("false_outcome") in EFFECT_OUTCOMES
                )
                probe_outcomes = {
                    effect_probe.get("true_outcome"),
                    effect_probe.get("false_outcome"),
                }
            elif probe_kind == "bound_instance_snapshot_digest":
                probe_is_valid = (
                    set(effect_probe)
                    == {
                        "kind",
                        "snapshot_method",
                        "changed_outcome",
                        "unchanged_outcome",
                    }
                    and isinstance(effect_probe.get("snapshot_method"), str)
                    and bool(effect_probe.get("snapshot_method"))
                    and effect_probe.get("changed_outcome") in EFFECT_OUTCOMES
                    and effect_probe.get("unchanged_outcome") in EFFECT_OUTCOMES
                )
                probe_outcomes = {
                    effect_probe.get("changed_outcome"),
                    effect_probe.get("unchanged_outcome"),
                }
        if (
            not isinstance(return_outcomes, Mapping)
            or set(return_outcomes) != RETURN_CATEGORIES
            or any(outcome not in EFFECT_OUTCOMES for outcome in return_outcomes.values())
            or not isinstance(qualifying, list)
            or len(qualifying) != len(set(qualifying))
            or not set(qualifying) <= CLAIM_QUALIFYING_EFFECT_OUTCOMES
            or not set(qualifying)
            <= (set(return_outcomes.values()) | probe_outcomes)
            or not contract_id
            or not symbol_id
            or not effect_kind
            or not probe_is_valid
            or symbol_id in contracts
            or contract_id in contract_ids
            or re.fullmatch(r"[0-9a-f]{64}", contract_digest) is None
            or digest_without(contract, "effect_contract_digest") != contract_digest
        ):
            return {}, f"effect-outcome contract {index} is invalid or duplicated"
        contracts[symbol_id] = contract
        contract_ids.add(contract_id)
    expected_digest = canonical_digest(
        [contracts[symbol_id] for symbol_id in sorted(contracts)]
    )
    if (
        acceptance_anchor.get("effect_outcome_contract_count") != len(contracts)
        or acceptance_anchor.get("effect_outcome_contracts_digest")
        != expected_digest
    ):
        return {}, "binding-acceptance effect-outcome contract set is stale"
    return contracts, None


def _invocation_effect_issue(
    invocation: Mapping[str, Any],
    contract: Mapping[str, Any] | None,
) -> str | None:
    """Validate a receipt outcome against one exact trusted symbol contract."""

    outcome = invocation.get("outcome")
    expected_contract_id = contract.get("contract_id") if contract is not None else None
    expected_effect_kind = (
        contract.get("effect_kind") if contract is not None else "unreviewed"
    )
    if outcome == "raised":
        expected = {
            "return_category": None,
            "effect_contract_id": expected_contract_id,
            "effect_kind": expected_effect_kind,
            "effect_outcome": "unknown",
            "claim_qualifying_effect": False,
            "effect_evidence": None,
        }
    elif outcome == "returned":
        category = invocation.get("return_category")
        if category not in RETURN_CATEGORIES:
            return "returned invocation lacks a stable return category"
        expected_effect_outcome = (
            contract.get("return_outcomes", {}).get(category)
            if contract is not None
            else "unknown"
        )
        qualifying_outcomes = (
            set(contract.get("claim_qualifying_outcomes", []))
            if contract is not None
            else set()
        )
        effect_probe = contract.get("effect_probe") if contract is not None else None
        expected_effect_evidence: Mapping[str, Any] | None = None
        if (
            isinstance(effect_probe, Mapping)
            and effect_probe.get("kind") == "boolean_attribute"
        ):
            actual_effect_evidence = invocation.get("effect_evidence")
            if not isinstance(actual_effect_evidence, Mapping):
                return "probe-governed invocation lacks effect evidence"
            observed_boolean = actual_effect_evidence.get("observed_boolean")
            expected_effect_evidence = {
                "kind": "boolean_attribute",
                "attribute": effect_probe.get("attribute"),
                "observed_boolean": observed_boolean,
            }
            if observed_boolean is True:
                expected_effect_outcome = effect_probe.get("true_outcome")
            elif observed_boolean is False:
                expected_effect_outcome = effect_probe.get("false_outcome")
            elif observed_boolean is None:
                expected_effect_outcome = "unknown"
            else:
                return "effect probe observation is not boolean or unknown"
        elif (
            isinstance(effect_probe, Mapping)
            and effect_probe.get("kind")
            == "bound_instance_snapshot_digest"
        ):
            actual_effect_evidence = invocation.get("effect_evidence")
            if (
                not isinstance(actual_effect_evidence, Mapping)
                or set(actual_effect_evidence)
                != {
                    "kind",
                    "snapshot_method",
                    "before_digest",
                    "after_digest",
                    "changed",
                }
                or actual_effect_evidence.get("kind")
                != "bound_instance_snapshot_digest"
                or actual_effect_evidence.get("snapshot_method")
                != effect_probe.get("snapshot_method")
            ):
                return "snapshot-governed invocation lacks exact effect evidence"
            before_digest = actual_effect_evidence.get("before_digest")
            after_digest = actual_effect_evidence.get("after_digest")
            if any(
                digest is not None
                and (
                    not isinstance(digest, str)
                    or re.fullmatch(r"[0-9a-f]{64}", digest) is None
                )
                for digest in (before_digest, after_digest)
            ):
                return "snapshot effect evidence contains an invalid digest"
            expected_changed = (
                before_digest != after_digest
                if isinstance(before_digest, str)
                and isinstance(after_digest, str)
                else None
            )
            if actual_effect_evidence.get("changed") is not expected_changed:
                return "snapshot effect evidence change flag is inconsistent"
            expected_effect_evidence = {
                "kind": "bound_instance_snapshot_digest",
                "snapshot_method": effect_probe.get("snapshot_method"),
                "before_digest": before_digest,
                "after_digest": after_digest,
                "changed": expected_changed,
            }
            if expected_changed is True:
                expected_effect_outcome = effect_probe.get("changed_outcome")
            elif expected_changed is False:
                expected_effect_outcome = effect_probe.get("unchanged_outcome")
            else:
                expected_effect_outcome = "unknown"
        expected = {
            "return_category": category,
            "effect_contract_id": expected_contract_id,
            "effect_kind": expected_effect_kind,
            "effect_outcome": expected_effect_outcome,
            "claim_qualifying_effect": (
                expected_effect_outcome in qualifying_outcomes
            ),
            "effect_evidence": expected_effect_evidence,
        }
    else:
        return "invocation outcome is neither returned nor raised"
    mismatched = [
        field for field, value in expected.items() if invocation.get(field) != value
    ]
    if mismatched:
        return f"effect outcome differs from trusted contract fields {mismatched}"
    return None


def binding_acceptance_issue(
    bindings: Mapping[str, Any],
    acceptance_anchor: Mapping[str, Any] | None,
    trusted_anchor_digest: str | None,
) -> str | None:
    """Return why an external anchor does not accept this candidate map."""

    if acceptance_anchor is None or trusted_anchor_digest is None:
        return "independently supplied binding-acceptance anchor is absent"
    if re.fullmatch(r"[0-9a-f]{64}", trusted_anchor_digest) is None:
        return "trusted binding-acceptance anchor digest is malformed"
    declared_digest = str(acceptance_anchor.get("anchor_digest", ""))
    if (
        declared_digest != trusted_anchor_digest
        or digest_without(acceptance_anchor, "anchor_digest") != declared_digest
    ):
        return "binding-acceptance anchor does not match the external trust root"
    expected_header = {
        "artifact": "causal-pathway-binding-acceptance-anchor",
        "schema_version": "causal_pathway_binding_acceptance_anchor_v1",
        "status": "accepted",
        "automatic_re_admission": False,
        "candidate_bundle_auto_discovery": False,
    }
    if any(
        acceptance_anchor.get(field) != value
        for field, value in expected_header.items()
    ):
        return "binding-acceptance anchor header or review status is invalid"
    anchor_id = str(acceptance_anchor.get("anchor_id", ""))
    hash_fields = (
        "accepted_binding_map_digest",
        "accepted_binding_semantics_digest",
        "accepted_source_manifest_digest",
    )
    if not anchor_id or any(
        re.fullmatch(r"[0-9a-f]{64}", str(acceptance_anchor.get(field, "")))
        is None
        for field in hash_fields
    ):
        return "binding-acceptance anchor identities are missing or malformed"
    if (
        re.fullmatch(
            r"[0-9a-f]{40}",
            str(acceptance_anchor.get("accepted_source_revision", "")),
        )
        is None
    ):
        return "binding-acceptance anchor source revision is malformed"
    contracts, contracts_issue = _effect_outcome_contracts(acceptance_anchor)
    if contracts_issue is not None:
        return contracts_issue
    known_symbol_ids = {
        str(symbol.get("symbol_id", ""))
        for stage in bindings.get("stage_bindings", [])
        if isinstance(stage, Mapping)
        for symbol in stage.get("symbols", [])
        if isinstance(symbol, Mapping)
    }
    known_symbol_ids.update(
        str(symbol.get("symbol_id", ""))
        for crossing in bindings.get("composition_crossing_bindings", [])
        if isinstance(crossing, Mapping)
        for symbol in (crossing.get("symbol", {}),)
        if isinstance(symbol, Mapping)
    )
    if set(contracts) - known_symbol_ids:
        return "binding-acceptance anchor contracts refer to unknown symbols"
    actual = {
        "accepted_binding_map_digest": bindings.get("binding_map_digest"),
        "accepted_source_revision": bindings.get("source_revision"),
        "accepted_binding_semantics_digest": binding_semantics_digest(bindings),
        "accepted_source_manifest_digest": binding_source_manifest_digest(bindings),
    }
    mismatched = [
        field
        for field, value in actual.items()
        if acceptance_anchor.get(field) != value
    ]
    if mismatched:
        return (
            "self-consistent binding map is pending independent review; "
            f"anchor mismatches {mismatched}"
        )
    return None


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


def _runtime_object_flow_issue(value: Any) -> str | None:
    """Validate one exact raw receiver/argument/result object-flow record."""

    expected_fields = {
        "receiver",
        "receiver_state",
        "receiver_base_state",
        "arguments",
        "result",
        "result_state",
        "result_base_state",
        "flow_derivation",
    }
    if not isinstance(value, Mapping) or set(value) != expected_fields:
        return "runtime object-flow fields are incomplete or widened"

    def descriptor_issue(descriptor: Any) -> bool:
        return descriptor is not None and (
            not isinstance(descriptor, Mapping)
            or set(descriptor) != {"object_id", "type"}
            or re.fullmatch(
                r"runtime-object:[0-9]+",
                str(descriptor.get("object_id", "")),
            )
            is None
            or not isinstance(descriptor.get("type"), str)
            or not descriptor.get("type")
        )

    arguments = value.get("arguments")
    if not isinstance(arguments, Mapping) or any(
        not isinstance(name, str) or not name or descriptor_issue(descriptor)
        for name, descriptor in arguments.items()
    ):
        return "runtime object-flow argument descriptors are invalid"
    descriptor_fields = expected_fields - {"arguments", "flow_derivation"}
    if any(
        descriptor_issue(value.get(field))
        for field in descriptor_fields
    ):
        return "runtime object-flow descriptors are invalid"
    derivation = value.get("flow_derivation")
    if derivation is not None and (
        not isinstance(derivation, Mapping)
        or set(derivation)
        != {
            "contract_id",
            "derivation_kind",
            "source_invocation_index",
            "source_port",
            "source_object",
            "source_value_digest",
            "target_port",
            "target_object",
            "target_value_digest",
        }
        or derivation.get("derivation_kind")
        != "consumer_bound_equivalent_state_copy"
        or not isinstance(derivation.get("source_invocation_index"), int)
        or descriptor_issue(derivation.get("source_object"))
        or descriptor_issue(derivation.get("target_object"))
        or any(
            re.fullmatch(r"[0-9a-f]{64}", str(derivation.get(field, "")))
            is None
            for field in ("source_value_digest", "target_value_digest")
        )
    ):
        return "runtime object-flow derivation is invalid"
    return None


def _candidate_request_flow_issue(value: Any) -> str | None:
    """Validate one raw reviewed-candidate target-request derivation."""

    if value is None:
        return None
    expected_fields = {
        "schema_version",
        "binding_rule",
        "candidate_scope_id",
        "candidate_id",
        "candidate_mechanism_invocation_index",
        "candidate_result",
        "candidate_result_request_path",
        "candidate_result_request_digest",
        "target_bound_arguments_digest",
        "source_dependency_proof",
        "target_binding_id",
        "target_pathway_id",
        "target_symbol_id",
    }
    descriptor = value.get("candidate_result") if isinstance(value, Mapping) else None
    request_path = (
        value.get("candidate_result_request_path")
        if isinstance(value, Mapping)
        else None
    )
    digest_fields = (
        "candidate_result_request_digest",
        "target_bound_arguments_digest",
    )
    dependency = (
        value.get("source_dependency_proof")
        if isinstance(value, Mapping)
        else None
    )
    dependency_fields = {
        "schema_version",
        "proof_kind",
        "source_result_parameter",
        "candidate_result_request_path",
        "source_parameter_default_digest",
        "source_present_request_digest",
        "source_omitted_request_digest",
    }
    if (
        not isinstance(value, Mapping)
        or set(value) != expected_fields
        or value.get("schema_version")
        != "reviewed_candidate_target_request_flow_v1"
        or value.get("binding_rule")
        != "candidate_result_mapping_supplies_complete_target_keyword_request"
        or any(
            not isinstance(value.get(field), str) or not value.get(field)
            for field in (
                "candidate_scope_id",
                "candidate_id",
                "target_binding_id",
                "target_pathway_id",
                "target_symbol_id",
            )
        )
        or not isinstance(
            value.get("candidate_mechanism_invocation_index"),
            int,
        )
        or value.get("candidate_mechanism_invocation_index", -1) < 0
        or not isinstance(descriptor, Mapping)
        or set(descriptor) != {"object_id", "type"}
        or re.fullmatch(
            r"runtime-object:[0-9]+",
            str(descriptor.get("object_id", "")),
        )
        is None
        or not isinstance(descriptor.get("type"), str)
        or not descriptor.get("type")
        or not isinstance(request_path, list)
        or any(not isinstance(item, str) or not item for item in request_path)
        or any(
            re.fullmatch(r"[0-9a-f]{64}", str(value.get(field, ""))) is None
            for field in digest_fields
        )
        or value.get("candidate_result_request_digest")
        != value.get("target_bound_arguments_digest")
        or not isinstance(dependency, Mapping)
        or set(dependency) != dependency_fields
        or dependency.get("schema_version")
        != "reviewed_candidate_source_dependency_v2"
        or dependency.get("proof_kind")
        != "source_presence_changes_exact_target_request"
        or re.fullmatch(
            r"[A-Za-z_][A-Za-z0-9_]*",
            str(dependency.get("source_result_parameter", "")),
        )
        is None
        or dependency.get("candidate_result_request_path") != request_path
        or any(
            re.fullmatch(r"[0-9a-f]{64}", str(dependency.get(field, "")))
            is None
            for field in (
                "source_parameter_default_digest",
                "source_present_request_digest",
                "source_omitted_request_digest",
            )
        )
        or dependency.get("source_present_request_digest")
        != value.get("candidate_result_request_digest")
        or dependency.get("source_present_request_digest")
        == dependency.get("source_omitted_request_digest")
    ):
        return "candidate target-request flow is incomplete or invalid"
    return None


def _flow_port(
    invocation: Mapping[str, Any],
    port: str,
) -> Mapping[str, Any] | None:
    flow = invocation.get("runtime_object_flow")
    if not isinstance(flow, Mapping):
        return None
    if port.startswith("argument:"):
        arguments = flow.get("arguments")
        value = (
            arguments.get(port.removeprefix("argument:"))
            if isinstance(arguments, Mapping)
            else None
        )
    else:
        value = flow.get(port)
    return value if isinstance(value, Mapping) else None


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


def _claim_semantic_tokens(value: str) -> set[str]:
    stopwords = {"a", "an", "and", "as", "from", "is", "of", "or", "the", "to"}
    return set(_normalized_claim_text(value).split()) - stopwords


def _restates_blocked_relabel(relation: str, blocked_relabel: str) -> bool:
    normalized_relation = _normalized_claim_text(relation)
    normalized_blocked = _normalized_claim_text(blocked_relabel)
    blocked_tokens = _claim_semantic_tokens(blocked_relabel)
    return normalized_blocked in normalized_relation or (
        bool(blocked_tokens) and blocked_tokens <= _claim_semantic_tokens(relation)
    )


def _function_body_contains_yield(definition: ast.FunctionDef) -> bool:
    """Return whether the entrypoint itself, rather than a nested body, yields."""

    pending: list[ast.AST] = list(definition.body)
    while pending:
        node = pending.pop()
        if isinstance(node, (ast.Yield, ast.YieldFrom)):
            return True
        pending.extend(
            child
            for child in ast.iter_child_nodes(node)
            if not isinstance(
                child,
                (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef),
            )
        )
    return False


def _function_returns_distinct_nonempty_mapping(
    definition: ast.FunctionDef,
    *,
    source_result_parameter: str,
) -> bool:
    """Prove the narrow reviewed-adapter result shape from source structure."""

    executable_body = list(definition.body)
    if (
        executable_body
        and isinstance(executable_body[0], ast.Expr)
        and isinstance(executable_body[0].value, ast.Constant)
        and isinstance(executable_body[0].value.value, str)
    ):
        executable_body = executable_body[1:]
    parameter_names = {
        argument.arg
        for argument in (
            *definition.args.posonlyargs,
            *definition.args.args,
            *definition.args.kwonlyargs,
        )
    }
    if definition.args.vararg is not None:
        parameter_names.add(definition.args.vararg.arg)
    if definition.args.kwarg is not None:
        parameter_names.add(definition.args.kwarg.arg)
    try:
        source_default = _safe_source_parameter_default(
            definition.args,
            source_result_parameter=source_result_parameter,
        )
        _source_default_digest(source_default)
    except (ArithmeticError, TypeError, ValueError):
        return False
    return (
        not definition.decorator_list
        and
        len(executable_body) == 1
        and isinstance(executable_body[0], ast.Return)
        and isinstance(executable_body[0].value, ast.Dict)
        and bool(executable_body[0].value.keys)
        and all(key is not None for key in executable_body[0].value.keys)
        and source_result_parameter in parameter_names
        and any(
            isinstance(node, ast.Name) and node.id == source_result_parameter
            for node in ast.walk(executable_body[0].value)
        )
    )


def _safe_source_expression(
    node: ast.expr,
    *,
    source_result_parameter: str,
    source_value: object,
) -> Any:
    """Independently evaluate the pure reviewed source-expression subset."""

    def evaluate(child: ast.expr) -> Any:
        return _safe_source_expression(
            child,
            source_result_parameter=source_result_parameter,
            source_value=source_value,
        )

    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name) and node.id == source_result_parameter:
        return source_value
    if isinstance(node, ast.Dict):
        if any(key is None for key in node.keys):
            raise ValueError
        keys = [evaluate(key) for key in node.keys if key is not None]
        if not all(isinstance(key, str) for key in keys) or len(set(keys)) != len(keys):
            raise ValueError
        return {
            key: evaluate(value)
            for key, value in zip(keys, node.values, strict=True)
        }
    if isinstance(node, ast.List):
        return [evaluate(item) for item in node.elts]
    if isinstance(node, ast.Tuple):
        return tuple(evaluate(item) for item in node.elts)
    if isinstance(node, ast.IfExp):
        return evaluate(node.body if bool(evaluate(node.test)) else node.orelse)
    if isinstance(node, ast.Compare) and len(node.ops) == len(node.comparators) == 1:
        left = evaluate(node.left)
        right = evaluate(node.comparators[0])
        operator = node.ops[0]
        if isinstance(operator, ast.Is):
            return left is right
        if isinstance(operator, ast.IsNot):
            return left is not right
        if isinstance(operator, ast.Eq):
            return left == right
        if isinstance(operator, ast.NotEq):
            return left != right
    if isinstance(node, ast.UnaryOp):
        operand = evaluate(node.operand)
        if isinstance(node.op, ast.Not):
            return not operand
        if isinstance(node.op, ast.UAdd):
            return +operand
        if isinstance(node.op, ast.USub):
            return -operand
    if isinstance(node, ast.BoolOp):
        result = evaluate(node.values[0])
        if isinstance(node.op, ast.And):
            for item in node.values[1:]:
                if not bool(result):
                    return result
                result = evaluate(item)
            return result
        if isinstance(node.op, ast.Or):
            for item in node.values[1:]:
                if bool(result):
                    return result
                result = evaluate(item)
            return result
    if isinstance(node, ast.BinOp):
        left = evaluate(node.left)
        right = evaluate(node.right)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            return left / right
        if isinstance(node.op, ast.FloorDiv):
            return left // right
        if isinstance(node.op, ast.Mod):
            return left % right
    raise ValueError


def _safe_source_parameter_default(
    arguments: ast.arguments,
    *,
    source_result_parameter: str,
) -> Any:
    """Independently derive the default used by source-argument omission."""

    positional = [*arguments.posonlyargs, *arguments.args]
    default_offset = len(positional) - len(arguments.defaults)
    for index, argument in enumerate(positional):
        if argument.arg != source_result_parameter:
            continue
        if index < default_offset:
            raise ValueError
        return _safe_source_expression(
            arguments.defaults[index - default_offset],
            source_result_parameter="",
            source_value=None,
        )
    for argument, default in zip(
        arguments.kwonlyargs,
        arguments.kw_defaults,
        strict=True,
    ):
        if argument.arg != source_result_parameter:
            continue
        if default is None:
            raise ValueError
        return _safe_source_expression(
            default,
            source_result_parameter="",
            source_value=None,
        )
    raise ValueError


def _source_dependency_proof(
    definition: ast.FunctionDef,
    *,
    source_result_parameter: str,
    request_path: list[str],
) -> dict[str, Any] | None:
    """Reconstruct source-presence dependency for the exact target request."""

    body = list(definition.body)
    if (
        body
        and isinstance(body[0], ast.Expr)
        and isinstance(body[0].value, ast.Constant)
        and isinstance(body[0].value.value, str)
    ):
        body = body[1:]
    if len(body) != 1 or not isinstance(body[0], ast.Return):
        return None
    expression = body[0].value
    if expression is None:
        return None
    for segment in request_path:
        if not isinstance(expression, ast.Dict):
            return None
        matches = [
            value
            for key, value in zip(expression.keys, expression.values, strict=True)
            if isinstance(key, ast.Constant) and key.value == segment
        ]
        if len(matches) != 1:
            return None
        expression = matches[0]
    source_present = object()
    try:
        source_default = _safe_source_parameter_default(
            definition.args,
            source_result_parameter=source_result_parameter,
        )
        source_default_digest = _source_default_digest(source_default)
        present = _safe_source_expression(
            expression,
            source_result_parameter=source_result_parameter,
            source_value=source_present,
        )
        omitted = _safe_source_expression(
            expression,
            source_result_parameter=source_result_parameter,
            source_value=source_default,
        )
        present_digest = canonical_digest(present)
        omitted_digest = canonical_digest(omitted)
    except (ArithmeticError, TypeError, ValueError):
        return None
    if (
        not isinstance(present, dict)
        or not present
        or not isinstance(omitted, dict)
        or not omitted
        or present_digest == omitted_digest
    ):
        return None
    return {
        "schema_version": "reviewed_candidate_source_dependency_v2",
        "proof_kind": "source_presence_changes_exact_target_request",
        "source_result_parameter": source_result_parameter,
        "candidate_result_request_path": request_path,
        "source_parameter_default_digest": source_default_digest,
        "source_present_request_digest": present_digest,
        "source_omitted_request_digest": omitted_digest,
    }


def _candidate_source_dependency_proof(
    root: Path,
    candidate: Mapping[str, Any],
    *,
    request_path: list[str],
) -> dict[str, Any] | None:
    """Load the pinned candidate and independently derive its path proof."""

    evidence = candidate.get("mechanism_evidence")
    review = candidate.get("invalid_relabel_relation_review")
    if not isinstance(evidence, Mapping) or not isinstance(review, Mapping):
        return None
    try:
        artifact = load_json(root / str(evidence["path"]))
        executable = artifact["executable_symbol"]
        source = root / str(executable["source_path"])
        tree = ast.parse(source.read_text(encoding="utf-8"))
    except (KeyError, OSError, SyntaxError, TypeError, UnicodeDecodeError):
        return None
    definitions = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == executable.get("qualified_symbol")
    ]
    if len(definitions) != 1:
        return None
    return _source_dependency_proof(
        definitions[0],
        source_result_parameter=str(review.get("source_result_parameter", "")),
        request_path=request_path,
    )


def _candidate_evidence_issue(
    root: Path,
    candidate: Mapping[str, Any],
) -> str | None:
    evidence = candidate.get("mechanism_evidence")
    if not isinstance(evidence, Mapping):
        return "executable candidate mechanism evidence is absent"
    expected_fields = {"evidence_kind", "mechanism_id", "path", "sha256"}
    if set(evidence) != expected_fields:
        return "mechanism evidence fields are incomplete or widened"
    if evidence.get("evidence_kind") != "executable_candidate_mechanism":
        return "mechanism evidence kind is not executable candidate evidence"
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
        "schema_version": "causal_pathway_candidate_mechanism_evidence_v2",
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
    if set(artifact) != {*expected_artifact, "executable_symbol"}:
        return "mechanism evidence artifact fields are incomplete or widened"
    executable = artifact.get("executable_symbol")
    expected_symbol_fields = {
        "symbol_id",
        "module",
        "qualified_symbol",
        "binding_role",
        "call_kind",
        "source_path",
        "source_sha256",
    }
    if not isinstance(executable, Mapping) or set(executable) != expected_symbol_fields:
        return "mechanism evidence lacks one exact executable symbol"
    if (
        executable.get("symbol_id") != f"candidate-mechanism:{mechanism_id}"
        or executable.get("binding_role") != "candidate_mechanism_entrypoint"
        or executable.get("call_kind") != "module_function"
    ):
        return "candidate executable identity or binding role is invalid"
    source_relative = Path(str(executable.get("source_path", "")))
    source_digest = str(executable.get("source_sha256", ""))
    module = str(executable.get("module", ""))
    qualified_symbol = str(executable.get("qualified_symbol", ""))
    if (
        not str(source_relative)
        or source_relative.is_absolute()
        or ".." in source_relative.parts
        or re.fullmatch(r"[0-9a-f]{64}", source_digest) is None
        or re.fullmatch(
            r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*",
            module,
        )
        is None
        or re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", qualified_symbol) is None
    ):
        return "candidate executable source identity is malformed"
    source = (resolved_root / source_relative).resolve()
    try:
        source.relative_to(resolved_root)
    except ValueError:
        return "candidate executable source path escapes the repository"
    if not source.is_file() or sha256_file(source) != source_digest:
        return "candidate executable source is absent or stale"
    try:
        source_text = source.read_text(encoding="utf-8")
        module_tree = ast.parse(source_text)
    except (OSError, UnicodeDecodeError, SyntaxError):
        return "candidate executable source is not parseable Python"
    definitions = [
        node
        for node in module_tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == qualified_symbol
    ]
    if len(definitions) != 1 or definitions[0].end_lineno is None:
        return "candidate executable symbol is absent or ambiguous"
    definition = definitions[0]
    if _function_body_contains_yield(definition):
        return "candidate executable must run as one synchronous function call"
    relation_review = candidate.get("invalid_relabel_relation_review")
    source_result_parameter = (
        str(relation_review.get("source_result_parameter", ""))
        if isinstance(relation_review, Mapping)
        else ""
    )
    if (
        candidate.get("invalid_relabel_conflict_ids")
        and relation_review is not None
        and not _function_returns_distinct_nonempty_mapping(
            definition,
            source_result_parameter=source_result_parameter,
        )
    ):
        return (
            "reviewed invalid-pair executable does not structurally return one "
            "distinct nonempty mapping from its frozen source-result parameter"
        )
    first_line = min(
        [definition.lineno, *(item.lineno for item in definition.decorator_list)]
    )
    source_lines = source_text.splitlines(keepends=True)
    definition_digest = hashlib.sha256(
        "".join(source_lines[first_line - 1 : definition.end_lineno]).encode("utf-8")
    ).hexdigest()
    link = candidate.get("candidate_mechanism_link")
    expected_link = {
        "mechanism_id": mechanism_id,
        **dict(executable),
    }
    if not isinstance(link, Mapping) or any(
        link.get(field) != value for field, value in expected_link.items()
    ):
        return "candidate declaration does not freeze its executable symbol"
    if set(link) != {*expected_link, "callable_identity"}:
        return "candidate executable link fields are incomplete or widened"
    callable_identity = link.get("callable_identity")
    expected_identity = {
        "module": module,
        "qualified_symbol": qualified_symbol,
        "source_path": source_relative.as_posix(),
        "source_sha256": source_digest,
        "definition_first_line": first_line,
        "definition_source_sha256": definition_digest,
    }
    if (
        not isinstance(callable_identity, Mapping)
        or any(
            callable_identity.get(field) != value
            for field, value in expected_identity.items()
        )
        or set(callable_identity) != {*expected_identity, "callable_identity_digest"}
        or callable_identity.get("callable_identity_digest")
        != digest_without(callable_identity, "callable_identity_digest")
    ):
        return "candidate executable callable identity is stale or inconsistent"
    return None


def _candidate_relation_review_issue(
    candidate: Mapping[str, Any],
    *,
    trusted_review_digests: set[str],
) -> str | None:
    """Validate a separately trusted review of an invalid-pair distinction."""

    conflict_ids = candidate.get("invalid_relabel_conflict_ids")
    has_conflicts = isinstance(conflict_ids, list) and bool(conflict_ids)
    review = candidate.get("invalid_relabel_relation_review")
    requirement = candidate.get(
        "invalid_relabel_relation_review_trust_requirement"
    )
    if not has_conflicts:
        if review is not None or requirement is not None:
            return "relation review is present without an invalid endpoint conflict"
        return None
    if requirement != INVALID_RELABEL_CANDIDATE_REVIEW_TRUST_REQUIREMENT:
        return "invalid-pair relation review lacks its external trust requirement"
    expected_fields = {
        "artifact",
        "schema_version",
        "review_id",
        "reviewer",
        "review_status",
        "candidate_id",
        "candidate_kind",
        "proposed_source_pathway_id",
        "proposed_target_pathway_id",
        "proposed_relation",
        "invalid_relabel_conflict_ids",
        "invalid_relabel_blocked_claims",
        "mechanism_evidence",
        "source_result_parameter",
        "structural_distinction",
        "review_digest",
    }
    if not isinstance(review, Mapping) or set(review) != expected_fields:
        return "invalid-pair relation review fields are absent, incomplete, or widened"
    review_digest = str(review.get("review_digest", ""))
    if (
        review.get("artifact")
        != "causal-pathway-candidate-relation-review"
        or review.get("schema_version")
        != "causal_pathway_candidate_relation_review_v2"
        or review.get("review_status") != "accepted_structural_distinction"
        or not str(review.get("review_id", ""))
        or not str(review.get("reviewer", ""))
        or re.fullmatch(
            r"[A-Za-z_][A-Za-z0-9_]*",
            str(review.get("source_result_parameter", "")),
        )
        is None
        or re.fullmatch(r"[0-9a-f]{64}", review_digest) is None
        or digest_without(review, "review_digest") != review_digest
    ):
        return "invalid-pair relation review is malformed or self-inconsistent"
    if review_digest not in trusted_review_digests:
        return "invalid-pair relation review digest is not independently trusted"
    exact_candidate_fields = (
        "candidate_id",
        "candidate_kind",
        "proposed_source_pathway_id",
        "proposed_target_pathway_id",
        "proposed_relation",
        "invalid_relabel_conflict_ids",
        "invalid_relabel_blocked_claims",
    )
    if any(
        review.get(field) != candidate.get(field)
        for field in exact_candidate_fields
    ):
        return "trusted relation review does not bind the exact candidate declaration"
    evidence = candidate.get("mechanism_evidence")
    expected_mechanism = (
        {
            "mechanism_id": evidence.get("mechanism_id"),
            "path": evidence.get("path"),
            "sha256": evidence.get("sha256"),
        }
        if isinstance(evidence, Mapping)
        else None
    )
    if (
        review.get("mechanism_evidence") != expected_mechanism
        or review.get("structural_distinction")
        != REVIEWED_STRUCTURAL_DISTINCTION
    ):
        return "trusted relation review lacks the exact structural distinction contract"
    return None


def _canonical_claim_envelope(
    *,
    pathways: Mapping[str, Mapping[str, Any]],
    compositions: Mapping[str, Mapping[str, Any]],
    pathway_bindings: Mapping[str, Mapping[str, Any]],
    composition_bindings: Mapping[str, Mapping[str, Any]],
    candidates: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    """Independently derive the complete conservative claim envelope."""

    pathway_claims: list[dict[str, Any]] = []
    composition_claims: list[dict[str, Any]] = []
    producer_cuts: list[dict[str, Any]] = []
    adapter_cuts: list[dict[str, Any]] = []
    diagnostic_relations: list[dict[str, str]] = []
    configured_semantics: list[dict[str, Any]] = []
    blocked_claims: list[str] = []

    ordered_pathway_bindings = sorted(
        pathway_bindings.items(),
        key=lambda item: item[0],
    )
    for binding_id, binding in ordered_pathway_bindings:
        pathway_id = str(binding.get("pathway_id", ""))
        pathway = pathways.get(pathway_id, {})
        supported_claims = list(pathway.get("supported_claims", []))
        configured_residue = list(pathway.get("configured_residue", []))
        producer_residue = list(pathway.get("producer_residue", []))
        naturalization_debt = list(pathway.get("naturalization_debt", []))
        pathway_blocks = [str(item) for item in pathway.get("blocked_claims", [])]
        mechanism_ownership = pathway.get("mechanism_ownership")
        pathway_claims.append(
            {
                "binding_id": binding_id,
                "pathway_id": pathway_id,
                "constituent_claim_ceiling": supported_claims,
                "mechanism_ownership": mechanism_ownership,
                "required_qualifiers": {
                    "configured_residue": configured_residue,
                    "producer_residue": producer_residue,
                    "naturalization_debt": naturalization_debt,
                },
                "blocked_claims": pathway_blocks,
            }
        )
        if configured_residue:
            configured_semantics.append(
                {
                    "pathway_id": pathway_id,
                    "residue": configured_residue,
                }
            )
        if producer_residue or mechanism_ownership == "producer":
            producer_cuts.append(
                {
                    "pathway_id": pathway_id,
                    "producer_identity": pathway.get("trigger_surface"),
                    "producer_owned_authorities": producer_residue,
                }
            )
        if mechanism_ownership == "diagnostic":
            diagnostic_relations.append(
                {
                    "kind": "pathway",
                    "identity": pathway_id,
                }
            )
        blocked_claims.extend(pathway_blocks)

    ordered_composition_bindings = sorted(
        composition_bindings.items(),
        key=lambda item: (
            str(item[1].get("composition_id", "")),
            item[0],
        ),
    )
    for binding_id, binding in ordered_composition_bindings:
        composition_id = str(binding.get("composition_id", ""))
        composition = compositions.get(composition_id, {})
        status = str(composition.get("composition_status", ""))
        composition_blocks = [
            str(item) for item in composition.get("blocked_relabels", [])
        ]
        authority_retained = list(composition.get("authority_retained", []))
        authority_transferred = list(
            composition.get("authority_transferred", [])
        )
        composition_claims.append(
            {
                "binding_id": binding_id,
                "composition_id": composition_id,
                "composition_status": status,
                "constituent_claim_ceiling": composition.get("claim_ceiling"),
                "adapter_id": composition.get("adapter_id"),
                "adapter_owner": composition.get("adapter_owner"),
                "authority_retained": authority_retained,
                "authority_transferred": authority_transferred,
                "blocked_claims": composition_blocks,
            }
        )
        if status == "producer_mediated":
            producer_cuts.append(
                {
                    "composition_id": composition_id,
                    "producer_identity": composition.get("adapter_id"),
                    "producer_owner": composition.get("adapter_owner"),
                    "producer_owned_authorities": authority_transferred,
                }
            )
        if status == "lawful_with_explicit_adapter":
            adapter_cuts.append(
                {
                    "composition_id": composition_id,
                    "adapter_id": composition.get("adapter_id"),
                    "adapter_owner": composition.get("adapter_owner"),
                }
            )
        if status == "diagnostic_only":
            diagnostic_relations.append(
                {
                    "kind": "composition",
                    "identity": composition_id,
                }
            )
        blocked_claims.extend(composition_blocks)

    candidate_records = [
        {
            field: copy.deepcopy(candidate.get(field))
            for field in CANDIDATE_DECLARATION_FIELDS
        }
        for _, candidate in sorted(candidates.items(), key=lambda item: item[0])
    ]
    for candidate in candidate_records:
        candidate_blocks = candidate.get("blocked_claims")
        if isinstance(candidate_blocks, list):
            blocked_claims.extend(str(item) for item in candidate_blocks)

    if candidate_records:
        overall_status = "experimental_unregistered"
    elif diagnostic_relations:
        overall_status = "bounded_with_diagnostic_cut"
    elif producer_cuts or adapter_cuts:
        overall_status = "bounded_with_explicit_ownership_cuts"
    else:
        overall_status = "admitted_bounded"

    return {
        "constituent_pathway_claim_ceilings": pathway_claims,
        "constituent_composition_claim_ceilings": composition_claims,
        "required_qualifiers": {
            "configured_semantics": configured_semantics,
            "producer_cuts": producer_cuts,
            "adapter_cuts": adapter_cuts,
            "diagnostic_only_relations": diagnostic_relations,
            "candidate_relations": candidate_records,
        },
        "contains_producer_cut": bool(producer_cuts),
        "contains_adapter_cut": bool(adapter_cuts),
        "contains_diagnostic_only_relation": bool(diagnostic_relations),
        "experimental_unregistered": bool(candidate_records),
        "blocked_claims": list(dict.fromkeys(blocked_claims)),
        "overall_claim_status": overall_status,
        "composition_status_is_maturity_score": False,
        "synthesized_chain_claim": False,
    }


def validate_bundle(
    root: Path,
    bundle: dict[str, Any],
    policy: dict[str, Any],
    active_rule_ids: set[str] | None = None,
    *,
    acceptance_anchor: Mapping[str, Any] | None = None,
    trusted_anchor_digest: str | None = None,
    trusted_execution_transcript_digest: str | None = None,
    trusted_candidate_review_digests: Iterable[str] = (),
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
    trusted_review_digests = set(trusted_candidate_review_digests)

    if (
        policy.get("execution_transcript_trust_requirement")
        != EXECUTION_TRANSCRIPT_TRUST_REQUIREMENT
        or policy.get("composition_dataflow_contract_policy")
        != composition_dataflow_policy_record()
    ):
        add_issue(
            issues,
            "BCF-019",
            "policy.composition_dataflow_contract_policy",
            "binding policy lacks the exact transcript trust and row-specific flow contracts",
        )
    if (
        policy.get("invalid_relabel_candidate_review_trust_requirement")
        != INVALID_RELABEL_CANDIDATE_REVIEW_TRUST_REQUIREMENT
    ):
        add_issue(
            issues,
            "BCF-011",
            "policy.invalid_relabel_candidate_review_trust_requirement",
            "binding policy lacks the external invalid-pair review trust contract",
        )

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

    def port_is_representable(
        pathway_id: str,
        stage_id: str,
        port: str,
    ) -> bool:
        stage = binding_stages.get((pathway_id, stage_id), {})
        symbols = stage.get("symbols", [])
        if not isinstance(symbols, list) or not symbols:
            return False
        if port in {"receiver", "receiver_state", "receiver_base_state"}:
            return any(
                isinstance(symbol, Mapping)
                and symbol.get("call_kind") == "instance_method"
                for symbol in symbols
            )
        if port.startswith("argument:"):
            argument_name = port.removeprefix("argument:")
            return any(
                isinstance(symbol, Mapping)
                and argument_name
                in source_symbol_parameter_names(
                    root,
                    str(symbol.get("source_path", "")),
                    str(symbol.get("qualified_symbol", "")),
                    str(symbol.get("source_sha256", "")),
                )
                for symbol in symbols
            )
        return port in {"result", "result_state", "result_base_state"}

    for composition_id, composition in compositions.items():
        status = composition.get("composition_status")
        if status not in EXECUTABLE_STATUSES or status == "lawful_with_explicit_adapter":
            continue
        contract = composition_dataflow_contract(
            composition_id,
            explicit_adapter=False,
        )
        source_stages = (
            list(composition.get("from_stage_ids", []))
            if contract["source_stage_id"] == "*"
            else [contract["source_stage_id"]]
        )
        target_stages = (
            list(composition.get("to_stage_ids", []))
            if contract["target_stage_id"] == "*"
            else [contract["target_stage_id"]]
        )
        source_representable = any(
            stage_id in composition.get("from_stage_ids", [])
            and port_is_representable(
                str(composition.get("from_pathway_id", "")),
                str(stage_id),
                contract["source_port"],
            )
            for stage_id in source_stages
        )
        target_representable = any(
            stage_id in composition.get("to_stage_ids", [])
            and port_is_representable(
                str(composition.get("to_pathway_id", "")),
                str(stage_id),
                contract["target_port"],
            )
            for stage_id in target_stages
        )
        if not source_representable or not target_representable:
            add_issue(
                issues,
                "BCF-019",
                composition_id,
                "registered composition lacks a representable runtime object-flow contract",
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
        "binding_semantics_digest": binding_semantics_digest(bindings),
        "binding_source_manifest_digest": binding_source_manifest_digest(bindings),
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

    acceptance_issue = binding_acceptance_issue(
        bindings,
        acceptance_anchor,
        trusted_anchor_digest,
    )
    if acceptance_issue is not None:
        add_issue(
            issues,
            "BCF-014",
            "binding_acceptance_anchor",
            acceptance_issue,
        )
    effect_outcome_contracts, _ = (
        _effect_outcome_contracts(acceptance_anchor)
        if acceptance_anchor is not None
        else ({}, "binding-acceptance anchor is absent")
    )
    effect_contracts_available = acceptance_issue is None

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
        "binding_acceptance_status": "accepted",
        "binding_acceptance_anchor_digest": trusted_anchor_digest,
        "effect_outcome_contracts_digest": (
            acceptance_anchor.get("effect_outcome_contracts_digest")
            if acceptance_anchor is not None
            else None
        ),
    }
    for artifact_name, artifact in (("lock", lock), ("receipt", receipt)):
        for field, expected in artifact_expected.items():
            if artifact.get(field) == expected:
                continue
            rule = (
                "BCF-013"
                if field == "matrix_digest"
                else "BCF-014"
                if field
                in {
                    "binding_map_digest",
                    "source_revision",
                    "binding_acceptance_status",
                    "binding_acceptance_anchor_digest",
                    "effect_outcome_contracts_digest",
                }
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
            if effect_contracts_available and link.get(
                "effect_outcome_contract"
            ) != effect_outcome_contracts.get(symbol_id):
                add_issue(
                    issues,
                    "BCF-020",
                    f"{binding_id}:{symbol_id}",
                    "locked effect-outcome contract differs from the trusted anchor",
                )
            runtime_instance = link.get("runtime_instance_binding")
            if runtime_instance is not None and (
                link.get("call_kind") != "instance_method"
                or not isinstance(runtime_instance, Mapping)
                or set(runtime_instance) != {"kind", "instance_id"}
                or runtime_instance.get("kind")
                not in {
                    "direct_bound_instance",
                    "adapter_result_reference",
                    "flow_derived_instance_reference",
                }
                or not isinstance(runtime_instance.get("instance_id"), str)
                or not runtime_instance.get("instance_id")
                or (
                    runtime_instance.get("kind") == "direct_bound_instance"
                    and re.fullmatch(
                        r"session-instance:[0-9]+",
                        str(runtime_instance.get("instance_id")),
                    )
                    is None
                )
                or (
                    runtime_instance.get("kind") == "adapter_result_reference"
                    and re.fullmatch(
                        r"adapter-result:CMP-[0-9]+",
                        str(runtime_instance.get("instance_id")),
                    )
                    is None
                )
                or (
                    runtime_instance.get("kind")
                    == "flow_derived_instance_reference"
                    and re.fullmatch(
                        r"flow-result:CMP-[0-9]+",
                        str(runtime_instance.get("instance_id")),
                    )
                    is None
                )
            ):
                add_issue(
                    issues,
                    "BCF-019",
                    f"{binding_id}:{symbol_id}",
                    "locked runtime-instance identity is malformed",
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
        explicit_adapter = status == "lawful_with_explicit_adapter"
        expected_dataflow_requirement = (
            EXPLICIT_ADAPTER_DATAFLOW
            if explicit_adapter
            else ATTESTED_OBJECT_FLOW_DATAFLOW
        )
        expected_dataflow_contract = composition_dataflow_contract(
            composition_id,
            explicit_adapter=explicit_adapter,
        )
        if (
            declared.get("runtime_dataflow_requirement")
            != expected_dataflow_requirement
            or declared.get("runtime_dataflow_contract")
            != expected_dataflow_contract
        ):
            add_issue(
                issues,
                "BCF-019",
                binding_id,
                "composition does not freeze its exact runtime dataflow contract",
            )
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
        crossing_symbol_id = str(expected_crossing.get("symbol_id", ""))
        if effect_contracts_available and expected_crossing.get(
            "effect_outcome_contract"
        ) != effect_outcome_contracts.get(crossing_symbol_id):
            add_issue(
                issues,
                "BCF-020",
                f"{binding_id}:{crossing_symbol_id}",
                "frozen crossing effect-outcome contract differs from the trusted anchor",
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
    registered_callable_identities = {
        (
            str(symbol.get("module", "")),
            str(symbol.get("qualified_symbol", "")),
        )
        for stage in bindings.get("stage_bindings", [])
        if isinstance(stage, Mapping)
        for symbol in stage.get("symbols", [])
        if isinstance(symbol, Mapping)
    }
    registered_callable_identities.update(
        (
            str(symbol.get("module", "")),
            str(symbol.get("qualified_symbol", "")),
        )
        for crossing in bindings.get("composition_crossing_bindings", [])
        if isinstance(crossing, Mapping)
        for symbol in (crossing.get("symbol"),)
        if isinstance(symbol, Mapping)
    )
    registered_callable_sources = {
        (
            str((root.resolve() / str(symbol.get("source_path", ""))).resolve()),
            str(symbol.get("qualified_symbol", "")),
        )
        for stage in bindings.get("stage_bindings", [])
        if isinstance(stage, Mapping)
        for symbol in stage.get("symbols", [])
        if isinstance(symbol, Mapping)
    }
    registered_callable_sources.update(
        (
            str((root.resolve() / str(symbol.get("source_path", ""))).resolve()),
            str(symbol.get("qualified_symbol", "")),
        )
        for crossing in bindings.get("composition_crossing_bindings", [])
        if isinstance(crossing, Mapping)
        for symbol in (crossing.get("symbol"),)
        if isinstance(symbol, Mapping)
    )
    for candidate_id, candidate in declared_candidates.items():
        if set(candidate) != set(CANDIDATE_DECLARATION_FIELDS):
            add_issue(
                issues,
                "BCF-004",
                candidate_id,
                "candidate declaration fields are incomplete or widened",
            )
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
        mechanism_link = candidate.get("candidate_mechanism_link")
        if candidate.get("mechanism_evidence") is None:
            if mechanism_link is not None:
                add_issue(
                    issues,
                    "BCF-004",
                    candidate_id,
                    "candidate freezes an executable without mechanism evidence",
                )
        elif isinstance(mechanism_link, Mapping) and (
            (
                str(mechanism_link.get("module", "")),
                str(mechanism_link.get("qualified_symbol", "")),
            )
            in registered_callable_identities
            or (
                str(
                    (
                        root.resolve()
                        / str(mechanism_link.get("source_path", ""))
                    ).resolve()
                ),
                str(mechanism_link.get("qualified_symbol", "")),
            )
            in registered_callable_sources
        ):
            add_issue(
                issues,
                "BCF-004",
                candidate_id,
                "candidate executable aliases a registered callable",
            )
        expected_relation_status = (
            "descriptive_unreviewed_not_claim_qualified"
            if candidate.get("proposed_relation") is not None
            else None
        )
        if candidate.get("proposed_relation_claim_status") != expected_relation_status:
            add_issue(
                issues,
                "BCF-011",
                candidate_id,
                "candidate prose is presented as a claim-qualified relation",
            )
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
        expected_invalid_blocks = list(
            dict.fromkeys(
                str(relabel)
                for composition in invalid_conflicts
                for relabel in composition.get("blocked_relabels", [])
            )
        )
        if (
            candidate.get("invalid_relabel_blocked_claims")
            != expected_invalid_blocks
            or not set(expected_invalid_blocks)
            <= set(candidate.get("blocked_claims", []))
        ):
            add_issue(
                issues,
                "BCF-011",
                candidate_id,
                "candidate does not retain every conflicting invalid-row block",
            )
        proposed_relation = str(candidate.get("proposed_relation", ""))
        restated = sorted(
            str(relabel)
            for composition in invalid_conflicts
            for relabel in composition.get("blocked_relabels", [])
            if _restates_blocked_relabel(proposed_relation, str(relabel))
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
        relation_review_issue = _candidate_relation_review_issue(
            candidate,
            trusted_review_digests=trusted_review_digests,
        )
        if relation_review_issue is not None:
            add_issue(
                issues,
                "BCF-011",
                candidate_id,
                relation_review_issue,
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
    if (
        lock.get("execution_transcript_trust_requirement")
        != EXECUTION_TRANSCRIPT_TRUST_REQUIREMENT
        or receipt.get("execution_transcript_trust_requirement")
        != EXECUTION_TRANSCRIPT_TRUST_REQUIREMENT
    ):
        add_issue(
            issues,
            "BCF-019",
            "execution_transcript_trust_requirement",
            "lock and receipt do not require an external composition-or-reviewed-candidate transcript digest",
        )

    invocations = receipt.get("actual_stage_symbol_invocations", [])
    qualifying_binding_ids: set[str] = set()
    qualifying_stage_symbols: dict[str, list[tuple[str, str]]] = {}
    valid_qualifying_invocation_indices: set[int] = set()
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
        alternative_scope_id = invocation.get("alternative_selection_scope_id")
        if "alternative_selection_scope_id" not in invocation or not (
            alternative_scope_id is None
            or isinstance(alternative_scope_id, str)
            and bool(alternative_scope_id)
        ):
            add_issue(
                issues,
                "BCF-017",
                f"receipt.actual_stage_symbol_invocations[{invocation_index}]",
                "invocation has an invalid alternative-selection scope identity",
            )
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
        effect_issue = (
            _invocation_effect_issue(
                invocation,
                effect_outcome_contracts.get(symbol_id),
            )
            if effect_contracts_available
            else None
        )
        if effect_issue is not None:
            add_issue(
                issues,
                "BCF-020",
                f"{binding_id}:{symbol_id}",
                effect_issue,
            )
        flow_issue = _runtime_object_flow_issue(
            invocation.get("runtime_object_flow")
        )
        if flow_issue is not None:
            add_issue(
                issues,
                "BCF-019",
                f"{binding_id}:{symbol_id}",
                flow_issue,
            )
        candidate_request_flow = invocation.get("candidate_request_flow")
        candidate_request_issue = _candidate_request_flow_issue(
            candidate_request_flow
        )
        if candidate_request_issue is not None:
            add_issue(
                issues,
                "BCF-019",
                f"{binding_id}:{symbol_id}",
                candidate_request_issue,
            )
        elif isinstance(candidate_request_flow, Mapping):
            flow_candidate = declared_candidates.get(
                str(candidate_request_flow.get("candidate_id", "")),
                {},
            )
            if (
                not isinstance(
                    flow_candidate.get("invalid_relabel_relation_review"),
                    Mapping,
                )
                or invocation.get("candidate_scope_id")
                != candidate_request_flow.get("candidate_scope_id")
                or candidate_request_flow.get("target_binding_id") != binding_id
                or candidate_request_flow.get("target_pathway_id")
                != invocation.get("pathway_id")
                or candidate_request_flow.get("target_pathway_id")
                != flow_candidate.get("proposed_target_pathway_id")
                or candidate_request_flow.get("target_symbol_id") != symbol_id
            ):
                add_issue(
                    issues,
                    "BCF-011",
                    f"{binding_id}:{symbol_id}",
                    "candidate target-request flow does not match its reviewed target invocation",
                )
        if (
            invocation.get("claim_qualifying_effect") is True
            and effect_issue is None
            and flow_issue is None
        ):
            qualifying_binding_ids.add(binding_id)
            valid_qualifying_invocation_indices.add(invocation_index)
            qualifying_stage_symbols.setdefault(binding_id, []).append(
                (str(invocation.get("stage_id", "")), symbol_id)
            )

    candidate_mechanism_invocations = receipt.get(
        "actual_candidate_mechanism_invocations",
        [],
    )
    for mechanism_index, invocation in enumerate(candidate_mechanism_invocations):
        candidate_id = str(invocation.get("candidate_id", ""))
        declared_candidate = declared_candidates.get(candidate_id, {})
        mechanism_link = declared_candidate.get("candidate_mechanism_link")
        event_order = invocation.get("execution_event_order")
        if (
            invocation.get("candidate_mechanism_invocation_index")
            != mechanism_index
            or not isinstance(event_order, int)
            or event_order < 0
        ):
            add_issue(
                issues,
                "BCF-015",
                f"receipt.actual_candidate_mechanism_invocations[{mechanism_index}]",
                "candidate mechanism index or execution order is invalid",
            )
        else:
            execution_event_orders.append(event_order)
        candidate_exact_fields = (
            "mechanism_id",
            "symbol_id",
            "callable_identity",
        )
        if (
            not isinstance(mechanism_link, Mapping)
            or invocation.get("candidate_id") != candidate_id
            or any(
                invocation.get(field) != mechanism_link.get(field)
                for field in candidate_exact_fields
            )
        ):
            add_issue(
                issues,
                "BCF-004",
                f"{candidate_id}:mechanism:{mechanism_index}",
                "candidate mechanism invocation differs from its frozen executable",
            )
        outcome = invocation.get("outcome")
        valid_result = (
            outcome == "returned"
            and isinstance(invocation.get("result_type"), str)
            and bool(invocation.get("result_type"))
            and invocation.get("error_type") is None
        ) or (
            outcome == "raised"
            and invocation.get("result_type") is None
            and isinstance(invocation.get("error_type"), str)
            and bool(invocation.get("error_type"))
        )
        if not invocation.get("candidate_scope_id") or not valid_result:
            add_issue(
                issues,
                "BCF-004",
                f"{candidate_id}:mechanism:{mechanism_index}",
                "candidate mechanism lacks an exact scope or execution outcome",
            )
        relation_review = declared_candidate.get(
            "invalid_relabel_relation_review"
        )
        if isinstance(relation_review, Mapping):
            expected_structural_result = outcome == "returned"
            if (
                invocation.get("relation_review_digest")
                != relation_review.get("review_digest")
                or invocation.get("structural_result_observed")
                is not expected_structural_result
            ):
                add_issue(
                    issues,
                    "BCF-011",
                    f"{candidate_id}:mechanism:{mechanism_index}",
                    "reviewed candidate invocation lacks its structural result",
                )
        elif (
            invocation.get("relation_review_digest") is not None
            or invocation.get("structural_result_observed") is not None
        ):
            add_issue(
                issues,
                "BCF-011",
                f"{candidate_id}:mechanism:{mechanism_index}",
                "unreviewed candidate invocation claims a reviewed structural result",
            )
        mechanism_flow_issue = _runtime_object_flow_issue(
            invocation.get("runtime_object_flow")
        )
        if mechanism_flow_issue is not None:
            add_issue(
                issues,
                "BCF-019",
                f"{candidate_id}:mechanism:{mechanism_index}",
                mechanism_flow_issue,
            )
    actual_bindings, duplicate_actual_bindings = _unique_index(
        receipt.get("actual_bound_pathways_used", []), "binding_id"
    )
    if duplicate_actual_bindings or set(actual_bindings) != qualifying_binding_ids:
        add_issue(
            issues,
            "BCF-015",
            "receipt.actual_bound_pathways_used",
            "actual bindings do not match claim-qualifying effects",
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
        stage_symbols = qualifying_stage_symbols.get(binding_id, [])
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
    valid_qualifying_crossing_indices: set[int] = set()
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
        crossing_exact_fields = (
            "binding_id",
            "composition_id",
            "symbol_id",
            "source_binding_id",
            "target_binding_id",
            "callable_identity",
        )
        if not isinstance(expected_crossing, Mapping) or any(
            invocation.get(field) != expected_crossing.get(field)
            for field in crossing_exact_fields
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
        effect_issue = (
            _invocation_effect_issue(
                invocation,
                effect_outcome_contracts.get(
                    str(invocation.get("symbol_id", ""))
                ),
            )
            if effect_contracts_available
            else None
        )
        if effect_issue is not None:
            add_issue(
                issues,
                "BCF-020",
                f"{binding_id}:crossing:{crossing_index}",
                effect_issue,
            )
        elif invocation.get("claim_qualifying_effect") is True:
            valid_qualifying_crossing_indices.add(crossing_index)

    derived_execution_transcript_digest = execution_transcript_digest(
        binding_lock_digest=str(receipt.get("binding_lock_digest", "")),
        stage_invocations=list(invocations),
        crossing_invocations=list(crossing_invocations),
        candidate_mechanism_invocations=list(candidate_mechanism_invocations),
    )
    submitted_execution_transcript_digest = receipt.get(
        "execution_transcript_digest"
    )
    transcript_is_self_consistent = (
        submitted_execution_transcript_digest
        == derived_execution_transcript_digest
    )
    if not transcript_is_self_consistent:
        add_issue(
            issues,
            "BCF-019",
            "receipt.execution_transcript_digest",
            "execution transcript digest differs from the raw invocation transcript",
        )
    transcript_is_independently_trusted = (
        transcript_is_self_consistent
        and re.fullmatch(
            r"[0-9a-f]{64}",
            str(trusted_execution_transcript_digest or ""),
        )
        is not None
        and trusted_execution_transcript_digest
        == submitted_execution_transcript_digest
    )

    expected_effect_outcome_summary = {
        "stage_invocation_counts": {
            outcome: sum(
                invocation.get("effect_outcome") == outcome
                for invocation in invocations
            )
            for outcome in sorted(EFFECT_OUTCOMES)
        },
        "claim_qualifying_stage_invocation_indices": [
            index
            for index, invocation in enumerate(invocations)
            if invocation.get("claim_qualifying_effect") is True
        ],
        "non_qualifying_returned_stage_invocation_indices": [
            index
            for index, invocation in enumerate(invocations)
            if invocation.get("outcome") == "returned"
            and invocation.get("claim_qualifying_effect") is not True
        ],
        "raised_stage_invocation_indices": [
            index
            for index, invocation in enumerate(invocations)
            if invocation.get("outcome") == "raised"
        ],
        "crossing_invocation_counts": {
            outcome: sum(
                invocation.get("effect_outcome") == outcome
                for invocation in crossing_invocations
            )
            for outcome in sorted(EFFECT_OUTCOMES)
        },
        "claim_qualifying_crossing_invocation_indices": [
            index
            for index, invocation in enumerate(crossing_invocations)
            if invocation.get("claim_qualifying_effect") is True
        ],
        "non_qualifying_returned_crossing_invocation_indices": [
            index
            for index, invocation in enumerate(crossing_invocations)
            if invocation.get("outcome") == "returned"
            and invocation.get("claim_qualifying_effect") is not True
        ],
        "raised_crossing_invocation_indices": [
            index
            for index, invocation in enumerate(crossing_invocations)
            if invocation.get("outcome") == "raised"
        ],
    }
    if receipt.get("effect_outcome_summary") != expected_effect_outcome_summary:
        add_issue(
            issues,
            "BCF-020",
            "receipt.effect_outcome_summary",
            "effect outcome summary differs from exact invocation records",
        )

    if len(execution_event_orders) != len(set(execution_event_orders)) or sorted(
        execution_event_orders
    ) != list(range(len(execution_event_orders))):
        add_issue(
            issues,
            "BCF-015",
            "receipt.execution_event_order",
            "stage, crossing, and candidate invocation order is not one complete sequence",
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
                or any(
                    index not in valid_qualifying_invocation_indices
                    for index in indices
                )
            ):
                return None
            selected = [invocations[index] for index in indices]
            if any(
                invocation.get("binding_id") != binding_id
                or invocation.get("pathway_id") != pathway_id
                or invocation.get("stage_id") != stage_id
                or invocation.get("claim_qualifying_effect") is not True
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
        expected_dataflow_requirement = (
            EXPLICIT_ADAPTER_DATAFLOW
            if adapter_required
            else ATTESTED_OBJECT_FLOW_DATAFLOW
        )
        expected_dataflow_contract = composition_dataflow_contract(
            composition_id,
            explicit_adapter=adapter_required,
        )
        dataflow_witness = witness.get("dataflow_witness")
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
            and witness.get("dataflow_requirement")
            == expected_dataflow_requirement
            and witness_declaration.get("runtime_dataflow_requirement")
            == expected_dataflow_requirement
            and witness_declaration.get("runtime_dataflow_contract")
            == expected_dataflow_contract
            and isinstance(dataflow_witness, Mapping)
            and selected_crossings is not None
            and len(selected_crossings) == (1 if adapter_required else 0)
            and transcript_is_independently_trusted
            and (
                not adapter_required
                or all(
                    index in valid_qualifying_crossing_indices
                    for index in crossing_indices
                )
            )
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
                    and crossing.get("claim_qualifying_effect") is True
                    and max(from_orders)
                    < int(crossing.get("execution_event_order", -1))
                    < min(to_orders)
                )
            if not isinstance(dataflow_witness, Mapping):
                structurally_valid = False
            elif structurally_valid and adapter_required:
                structurally_valid = (
                    set(dataflow_witness)
                    == {
                        "witness_kind",
                        "crossing_invocation_index",
                        "source_instance_role",
                        "target_instance_role",
                    }
                    and dataflow_witness.get("witness_kind")
                    == EXPLICIT_ADAPTER_DATAFLOW
                    and dataflow_witness.get("crossing_invocation_index")
                    == crossing_indices[0]
                    and dataflow_witness.get("source_instance_role")
                    == "declared_adapter_source_instance"
                    and dataflow_witness.get("target_instance_role")
                    == "adapter_result_reference"
                )
            elif structurally_valid:
                source_flow_index = dataflow_witness.get("source_invocation_index")
                target_flow_index = dataflow_witness.get("target_invocation_index")
                source_flow = (
                    invocations[source_flow_index]
                    if isinstance(source_flow_index, int)
                    and source_flow_index in from_indices
                    else None
                )
                target_flow = (
                    invocations[target_flow_index]
                    if isinstance(target_flow_index, int)
                    and target_flow_index in to_indices
                    else None
                )

                source_descriptor = (
                    _flow_port(source_flow, expected_dataflow_contract["source_port"])
                    if source_flow is not None
                    else None
                )
                target_descriptor = (
                    _flow_port(target_flow, expected_dataflow_contract["target_port"])
                    if target_flow is not None
                    else None
                )
                common_flow_valid = (
                    dataflow_witness.get("witness_kind")
                    == ATTESTED_OBJECT_FLOW_DATAFLOW
                    and dataflow_witness.get("dataflow_contract_id")
                    == expected_dataflow_contract["contract_id"]
                    and dataflow_witness.get("continuity_kind")
                    == expected_dataflow_contract["continuity_kind"]
                    and source_flow is not None
                    and target_flow is not None
                    and expected_dataflow_contract["source_stage_id"]
                    in {"*", source_flow.get("stage_id")}
                    and expected_dataflow_contract["target_stage_id"]
                    in {"*", target_flow.get("stage_id")}
                    and dataflow_witness.get("source_symbol_id")
                    == source_flow.get("symbol_id")
                    and dataflow_witness.get("source_port")
                    == expected_dataflow_contract["source_port"]
                    and dataflow_witness.get("target_symbol_id")
                    == target_flow.get("symbol_id")
                    and dataflow_witness.get("target_port")
                    == expected_dataflow_contract["target_port"]
                    and source_descriptor is not None
                    and target_descriptor is not None
                )
                source_object_id = (
                    source_descriptor.get("object_id")
                    if isinstance(source_descriptor, Mapping)
                    else None
                )
                target_object_id = (
                    target_descriptor.get("object_id")
                    if isinstance(target_descriptor, Mapping)
                    else None
                )
                continuity_kind = expected_dataflow_contract["continuity_kind"]
                if continuity_kind == "exact_object_identity":
                    structurally_valid = common_flow_valid and (
                        set(dataflow_witness)
                        == {
                            "witness_kind",
                            "dataflow_contract_id",
                            "continuity_kind",
                            "runtime_object_id",
                            "source_invocation_index",
                            "source_symbol_id",
                            "source_port",
                            "target_invocation_index",
                            "target_symbol_id",
                            "target_port",
                        }
                        and source_descriptor == target_descriptor
                        and dataflow_witness.get("runtime_object_id")
                        == source_object_id
                    )
                else:
                    target_runtime_flow = (
                        target_flow.get("runtime_object_flow", {})
                        if isinstance(target_flow, Mapping)
                        else {}
                    )
                    derivation = (
                        target_runtime_flow.get("flow_derivation")
                        if isinstance(target_runtime_flow, Mapping)
                        else None
                    )
                    structurally_valid = common_flow_valid and (
                        continuity_kind
                        == "consumer_bound_equivalent_state_copy"
                        and set(dataflow_witness)
                        == {
                            "witness_kind",
                            "dataflow_contract_id",
                            "continuity_kind",
                            "source_runtime_object_id",
                            "target_runtime_object_id",
                            "state_value_digest",
                            "source_invocation_index",
                            "source_symbol_id",
                            "source_port",
                            "target_invocation_index",
                            "target_symbol_id",
                            "target_port",
                        }
                        and isinstance(derivation, Mapping)
                        and derivation.get("contract_id")
                        == expected_dataflow_contract["contract_id"]
                        and derivation.get("derivation_kind") == continuity_kind
                        and derivation.get("source_invocation_index")
                        == source_flow_index
                        and derivation.get("source_port")
                        == expected_dataflow_contract["source_port"]
                        and derivation.get("target_port")
                        == expected_dataflow_contract["target_port"]
                        and derivation.get("source_object") == source_descriptor
                        and derivation.get("target_object") == target_descriptor
                        and derivation.get("source_value_digest")
                        == derivation.get("target_value_digest")
                        == dataflow_witness.get("state_value_digest")
                        and dataflow_witness.get("source_runtime_object_id")
                        == source_object_id
                        and dataflow_witness.get("target_runtime_object_id")
                        == target_object_id
                    )
        if not structurally_valid:
            if not transcript_is_independently_trusted:
                add_issue(
                    issues,
                    "BCF-019",
                    binding_id,
                    "composition witness lacks its independently trusted execution transcript digest",
                )
            add_issue(
                issues,
                "BCF-019",
                binding_id,
                "composition witness lacks exact scoped endpoints, order, or runtime dataflow closure",
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
    witnessed_candidate_mechanism_indices: set[int] = set()
    valid_used_candidate_ids: set[str] = set()
    for candidate_id, candidate in used_candidates.items():
        locked_candidate = declared_candidates.get(candidate_id)
        candidate_declaration_valid = locked_candidate is not None
        if locked_candidate is None:
            add_issue(
                issues,
                "BCF-003",
                candidate_id,
                "candidate use lacks a lock declaration",
            )
        elif set(candidate) != {*locked_candidate, "candidate_execution_witness"} or any(
            candidate.get(field) != locked_candidate.get(field)
            for field in locked_candidate
        ):
            candidate_declaration_valid = False
            add_issue(
                issues, "BCF-004", candidate_id, "candidate use widened its declaration"
            )
        evidence_issue = _candidate_evidence_issue(root, candidate)
        if evidence_issue is not None:
            candidate_declaration_valid = False
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
            allow_empty: bool = False,
        ) -> list[Mapping[str, Any]] | None:
            if (
                not isinstance(indices, list)
                or (not indices and not allow_empty)
                or any(not isinstance(index, int) for index in indices)
                or len(indices) != len(set(indices))
                or any(
                    index not in valid_qualifying_invocation_indices
                    for index in indices
                )
            ):
                return None
            try:
                selected = [invocations[index] for index in indices]
            except (IndexError, TypeError):
                return None
            if any(
                invocation.get("claim_qualifying_effect") is not True
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
            witness_mechanism_index = candidate_witness.get(
                "candidate_mechanism_invocation_index"
            )
            mechanism_invocation = (
                candidate_mechanism_invocations[witness_mechanism_index]
                if isinstance(witness_mechanism_index, int)
                and 0
                <= witness_mechanism_index
                < len(candidate_mechanism_invocations)
                else None
            )
            mechanism_link = candidate.get("candidate_mechanism_link")
            structurally_valid = (
                mechanism_invocation is not None
                and isinstance(mechanism_link, Mapping)
                and mechanism_invocation.get("candidate_id") == candidate_id
                and mechanism_invocation.get("candidate_scope_id") == scope_id
                and mechanism_invocation.get("outcome") == "returned"
                and candidate_witness.get("candidate_mechanism_symbol_id")
                == mechanism_link.get("symbol_id")
                == mechanism_invocation.get("symbol_id")
            )
            relation_review = candidate.get(
                "invalid_relabel_relation_review"
            )
            if isinstance(relation_review, Mapping):
                reviewed_structure_is_valid = (
                    mechanism_invocation is not None
                    and mechanism_invocation.get("relation_review_digest")
                    == relation_review.get("review_digest")
                    and mechanism_invocation.get("structural_result_observed")
                    is True
                    and transcript_is_independently_trusted
                )
                structurally_valid = (
                    structurally_valid and reviewed_structure_is_valid
                )
                if not transcript_is_independently_trusted:
                    add_issue(
                        issues,
                        "BCF-011",
                        candidate_id,
                        "reviewed invalid-pair witness lacks its independently trusted execution transcript digest",
                    )
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
                expected_witness_fields = {
                    "candidate_scope_id",
                    "candidate_id",
                    "witness_kind",
                    "candidate_mechanism_invocation_index",
                    "candidate_mechanism_symbol_id",
                    "source_pathway_id",
                    "source_binding_id",
                    "source_invocation_indices",
                    "target_pathway_id",
                    "target_binding_id",
                    "target_invocation_indices",
                    "ordering_rule",
                }
                reviewed_dataflow_is_valid = True
                if isinstance(relation_review, Mapping):
                    expected_witness_fields.add("candidate_dataflow_witness")
                    dataflow_witness = candidate_witness.get(
                        "candidate_dataflow_witness"
                    )
                    dataflow_fields = {
                        "witness_kind",
                        "source_invocation_index",
                        "source_result",
                        "candidate_argument_name",
                        "candidate_mechanism_invocation_index",
                        "candidate_result",
                        "candidate_result_request_path",
                        "target_invocation_index",
                        "target_request_digest",
                    }
                    source_flow_invocation = None
                    target_flow_invocation = None
                    if isinstance(dataflow_witness, Mapping):
                        source_flow_index = dataflow_witness.get(
                            "source_invocation_index"
                        )
                        target_flow_index = dataflow_witness.get(
                            "target_invocation_index"
                        )
                        if (
                            isinstance(source_flow_index, int)
                            and 0 <= source_flow_index < len(invocations)
                            and source_flow_index
                            in candidate_witness.get(
                                "source_invocation_indices",
                                [],
                            )
                        ):
                            source_flow_invocation = invocations[source_flow_index]
                        if (
                            isinstance(target_flow_index, int)
                            and 0 <= target_flow_index < len(invocations)
                            and target_flow_index
                            in candidate_witness.get(
                                "target_invocation_indices",
                                [],
                            )
                        ):
                            target_flow_invocation = invocations[target_flow_index]
                    mechanism_flow = (
                        mechanism_invocation.get("runtime_object_flow", {})
                        if isinstance(mechanism_invocation, Mapping)
                        else {}
                    )
                    candidate_arguments = mechanism_flow.get("arguments", {})
                    candidate_argument_name = (
                        dataflow_witness.get("candidate_argument_name")
                        if isinstance(dataflow_witness, Mapping)
                        else None
                    )
                    source_result = (
                        source_flow_invocation.get("runtime_object_flow", {}).get(
                            "result"
                        )
                        if isinstance(source_flow_invocation, Mapping)
                        else None
                    )
                    target_request_flow = (
                        target_flow_invocation.get("candidate_request_flow")
                        if isinstance(target_flow_invocation, Mapping)
                        else None
                    )
                    request_path = (
                        target_request_flow.get("candidate_result_request_path")
                        if isinstance(target_request_flow, Mapping)
                        else None
                    )
                    expected_dependency_proof = (
                        _candidate_source_dependency_proof(
                            root,
                            candidate,
                            request_path=request_path,
                        )
                        if isinstance(request_path, list)
                        and all(
                            isinstance(segment, str) and segment
                            for segment in request_path
                        )
                        else None
                    )
                    candidate_result = mechanism_flow.get("result")
                    reviewed_dataflow_is_valid = (
                        isinstance(dataflow_witness, Mapping)
                        and set(dataflow_witness) == dataflow_fields
                        and dataflow_witness.get("witness_kind")
                        == "externally_attested_candidate_request_flow"
                        and isinstance(candidate_argument_name, str)
                        and bool(candidate_argument_name)
                        and candidate_argument_name
                        == relation_review.get("source_result_parameter")
                        and isinstance(candidate_arguments, Mapping)
                        and candidate_arguments.get(candidate_argument_name)
                        == source_result
                        == dataflow_witness.get("source_result")
                        and isinstance(candidate_result, Mapping)
                        and dataflow_witness.get("candidate_result")
                        == candidate_result
                        and dataflow_witness.get(
                            "candidate_mechanism_invocation_index"
                        )
                        == witness_mechanism_index
                        and isinstance(target_request_flow, Mapping)
                        and _candidate_request_flow_issue(target_request_flow)
                        is None
                        and target_request_flow.get("candidate_scope_id")
                        == scope_id
                        and target_request_flow.get("candidate_id")
                        == candidate_id
                        and target_request_flow.get(
                            "candidate_mechanism_invocation_index"
                        )
                        == witness_mechanism_index
                        and target_request_flow.get("candidate_result")
                        == candidate_result
                        and target_request_flow.get(
                            "candidate_result_request_path"
                        )
                        == dataflow_witness.get(
                            "candidate_result_request_path"
                        )
                        and target_request_flow.get(
                            "target_bound_arguments_digest"
                        )
                        == dataflow_witness.get("target_request_digest")
                        and expected_dependency_proof is not None
                        and target_request_flow.get("source_dependency_proof")
                        == expected_dependency_proof
                    )
                structurally_valid = (
                    structurally_valid
                    and set(candidate_witness) == expected_witness_fields
                    and
                    candidate_witness.get("witness_kind")
                    == "identity_verified_candidate_crossing_execution"
                    and candidate_witness.get("source_pathway_id")
                    == candidate.get("proposed_source_pathway_id")
                    and candidate_witness.get("target_pathway_id")
                    == candidate.get("proposed_target_pathway_id")
                    and candidate_witness.get("ordering_rule")
                    == (
                        "all_source_invocations_before_candidate_mechanism_before_"
                        "all_target_invocations"
                    )
                    and source_invocations is not None
                    and target_invocations is not None
                    and max(
                        int(item.get("execution_event_order", -1))
                        for item in source_invocations
                    )
                    < int(
                        mechanism_invocation.get("execution_event_order", -1)
                        if mechanism_invocation is not None
                        else -1
                    )
                    < min(
                        int(item.get("execution_event_order", -1))
                        for item in target_invocations
                    )
                    and reviewed_dataflow_is_valid
                )
            else:
                consumed_pathways = candidate.get(
                    "consumed_admitted_pathway_ids",
                    [],
                )
                constituent = selected_candidate_invocations(
                    candidate_witness.get("constituent_invocation_indices"),
                    scope_id=scope_id,
                    allow_empty=not consumed_pathways,
                )
                structurally_valid = (
                    structurally_valid
                    and set(candidate_witness)
                    == {
                        "candidate_scope_id",
                        "candidate_id",
                        "witness_kind",
                        "candidate_mechanism_invocation_index",
                        "candidate_mechanism_symbol_id",
                        "constituent_invocation_indices",
                    }
                    and
                    candidate_witness.get("witness_kind")
                    == "identity_verified_candidate_mechanism_execution"
                    and constituent is not None
                    and all(
                        item.get("pathway_id")
                        in consumed_pathways
                        for item in constituent
                    )
                )
        if not structurally_valid:
            add_issue(
                issues,
                "BCF-004",
                candidate_id,
                "candidate use lacks exact identity-verified mechanism execution",
            )
        elif isinstance(candidate_witness, Mapping) and candidate_declaration_valid:
            valid_used_candidate_ids.add(candidate_id)
            witnessed_mechanism_index = candidate_witness.get(
                "candidate_mechanism_invocation_index"
            )
            if isinstance(witnessed_mechanism_index, int):
                witnessed_candidate_mechanism_indices.add(witnessed_mechanism_index)

    returned_candidate_mechanism_indices = {
        index
        for index, invocation in enumerate(candidate_mechanism_invocations)
        if invocation.get("outcome") == "returned"
    }
    if witnessed_candidate_mechanism_indices != returned_candidate_mechanism_indices:
        add_issue(
            issues,
            "BCF-004",
            "receipt.actual_candidate_mechanism_invocations",
            "returned candidate mechanisms differ from exact candidate-use witnesses",
        )

    expected_unused = {
        "pathway_binding_ids": sorted(set(lock_bindings) - qualifying_binding_ids),
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
            if used_candidate is not None and (
                node.get("invalid_relabel_conflict_ids")
                != used_candidate.get("invalid_relabel_conflict_ids")
                or node.get("invalid_relabel_blocked_claims")
                != used_candidate.get("invalid_relabel_blocked_claims")
                or node.get("invalid_relabel_relation_review")
                != used_candidate.get("invalid_relabel_relation_review")
                or node.get(
                    "invalid_relabel_relation_review_trust_requirement"
                )
                != used_candidate.get(
                    "invalid_relabel_relation_review_trust_requirement"
                )
                or node.get("blocked_claims")
                != used_candidate.get("blocked_claims")
            ):
                add_issue(
                    issues,
                    "BCF-011",
                    candidate_id,
                    "candidate graph node erased structured invalid-row blocks",
                )
            if (
                used_candidate is None
                or not _candidate_is_bounded(node)
                or node.get("mechanism_evidence")
                != used_candidate.get("mechanism_evidence")
                or node.get("candidate_mechanism_link")
                != used_candidate.get("candidate_mechanism_link")
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
            if used_candidate is not None and (
                edge.get("invalid_relabel_conflict_ids")
                != used_candidate.get("invalid_relabel_conflict_ids")
                or edge.get("invalid_relabel_blocked_claims")
                != used_candidate.get("invalid_relabel_blocked_claims")
                or edge.get("invalid_relabel_relation_review")
                != used_candidate.get("invalid_relabel_relation_review")
                or edge.get(
                    "invalid_relabel_relation_review_trust_requirement"
                )
                != used_candidate.get(
                    "invalid_relabel_relation_review_trust_requirement"
                )
                or edge.get("blocked_claims")
                != used_candidate.get("blocked_claims")
            ):
                add_issue(
                    issues,
                    "BCF-011",
                    candidate_id,
                    "candidate graph edge erased structured invalid-row blocks",
                )
            if (
                used_candidate is None
                or not _candidate_is_bounded(edge)
                or edge.get("mechanism_evidence")
                != used_candidate.get("mechanism_evidence")
                or edge.get("candidate_mechanism_link")
                != used_candidate.get("candidate_mechanism_link")
                or edge.get("candidate_execution_witness") != witness
                or edge.get("proposed_relation")
                != used_candidate.get("proposed_relation")
                or edge.get("proposed_relation_claim_status")
                != "descriptive_unreviewed_not_claim_qualified"
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

    expected_lock_envelope = _canonical_claim_envelope(
        pathways=pathways,
        compositions=compositions,
        pathway_bindings=lock_bindings,
        composition_bindings=lock_compositions,
        candidates=declared_candidates,
    )
    expected_receipt_pathways = {
        binding_id: lock_bindings[binding_id]
        for binding_id in sorted(qualifying_binding_ids)
        if binding_id in lock_bindings
    }
    expected_receipt_compositions = {
        binding_id: lock_compositions[binding_id]
        for binding_id in sorted(valid_witness_ids)
        if binding_id in lock_compositions
    }
    expected_receipt_candidates = {
        candidate_id: declared_candidates[candidate_id]
        for candidate_id in sorted(valid_used_candidate_ids)
        if candidate_id in declared_candidates
    }
    expected_receipt_envelope = _canonical_claim_envelope(
        pathways=pathways,
        compositions=compositions,
        pathway_bindings=expected_receipt_pathways,
        composition_bindings=expected_receipt_compositions,
        candidates=expected_receipt_candidates,
    )
    if lock.get("pre_execution_claim_envelope") != expected_lock_envelope:
        add_issue(
            issues,
            "BCF-015",
            "lock.pre_execution_claim_envelope",
            "pre-execution claim envelope differs from independent canonical derivation",
        )
    if receipt.get("claim_envelope") != expected_receipt_envelope:
        add_issue(
            issues,
            "BCF-015",
            "receipt.claim_envelope",
            "receipt claim envelope differs from independent canonical derivation",
        )
    if (
        lock.get("blocked_claims") != expected_lock_envelope["blocked_claims"]
        or lock.get("explicit_producers")
        != expected_lock_envelope["required_qualifiers"]["producer_cuts"]
        or lock.get("explicit_adapters")
        != expected_lock_envelope["required_qualifiers"]["adapter_cuts"]
    ):
        add_issue(
            issues,
            "BCF-015",
            "lock.claim_envelope_projections",
            "lock claim projections differ from the canonical envelope",
        )
    if (
        receipt.get("blocked_claims") != expected_receipt_envelope["blocked_claims"]
        or receipt.get("producer_cuts_used")
        != expected_receipt_envelope["required_qualifiers"]["producer_cuts"]
        or receipt.get("adapters_used")
        != expected_receipt_envelope["required_qualifiers"]["adapter_cuts"]
    ):
        add_issue(
            issues,
            "BCF-015",
            "receipt.claim_envelope_projections",
            "receipt claim projections differ from the canonical envelope",
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
    declared_pathway_ids = {
        str(binding.get("pathway_id", "")) for binding in lock_bindings.values()
    }
    witnessed_invocation_indices: set[int] = set()
    witnessed_scope_ids: set[str] = set()
    for alternative_id, alternatives_record in alternatives.items():
        allowed = list(alternatives_record.get("pathway_ids", []))
        actual_record = actual_alternatives.get(alternative_id, {})
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
        ):
            add_issue(
                issues,
                "BCF-017",
                alternative_id,
                "dynamic choice was undeclared, selected by binder, or misreported",
            )

        raw_scopes = actual_record.get("selection_scopes", [])
        if not isinstance(raw_scopes, list):
            raw_scopes = []
            add_issue(
                issues,
                "BCF-017",
                alternative_id,
                "dynamic choice scopes are not a list",
            )
        selected_pathway_ids: list[str] = []
        qualifying_pathway_ids: list[str] = []
        for scope_index, selection_scope in enumerate(raw_scopes):
            location = f"{alternative_id}:selection_scopes[{scope_index}]"
            if not isinstance(selection_scope, Mapping):
                add_issue(
                    issues,
                    "BCF-017",
                    location,
                    "dynamic choice scope is not an object",
                )
                continue
            scope_id = str(selection_scope.get("selection_scope_id", ""))
            selected_pathway_id = str(selection_scope.get("selected_pathway_id", ""))
            invocation_indices = selection_scope.get("invocation_indices", [])
            returned_indices = selection_scope.get("returned_invocation_indices", [])
            qualifying_indices = selection_scope.get(
                "claim_qualifying_invocation_indices", []
            )
            structurally_valid = (
                bool(scope_id)
                and scope_id not in witnessed_scope_ids
                and selection_scope.get("alternative_set_id") == alternative_id
                and selection_scope.get("selection_authority")
                == alternatives_record.get("selection_authority")
                and selection_scope.get("selection_performed_by") == "consumer"
                and selected_pathway_id in allowed
                and isinstance(invocation_indices, list)
                and bool(invocation_indices)
                and all(isinstance(index, int) for index in invocation_indices)
                and len(invocation_indices) == len(set(invocation_indices))
                and isinstance(returned_indices, list)
                and all(isinstance(index, int) for index in returned_indices)
                and len(returned_indices) == len(set(returned_indices))
                and isinstance(qualifying_indices, list)
                and all(isinstance(index, int) for index in qualifying_indices)
                and len(qualifying_indices) == len(set(qualifying_indices))
            )
            selected_invocations: list[Mapping[str, Any]] = []
            if structurally_valid:
                try:
                    selected_invocations = [
                        invocations[index] for index in invocation_indices
                    ]
                except (IndexError, TypeError):
                    structurally_valid = False
            expected_returned_indices: list[int] = []
            expected_qualifying_indices: list[int] = []
            if structurally_valid:
                expected_returned_indices = [
                    index
                    for index, invocation in zip(
                        invocation_indices,
                        selected_invocations,
                        strict=True,
                    )
                    if invocation.get("outcome") == "returned"
                ]
                expected_qualifying_indices = [
                    index
                    for index, invocation in zip(
                        invocation_indices,
                        selected_invocations,
                        strict=True,
                    )
                    if invocation.get("claim_qualifying_effect") is True
                ]
            if structurally_valid and (
                any(
                    invocation.get("alternative_selection_scope_id") != scope_id
                    or invocation.get("pathway_id") != selected_pathway_id
                    for invocation in selected_invocations
                )
                or expected_returned_indices != returned_indices
                or expected_qualifying_indices != qualifying_indices
                or any(
                    index in witnessed_invocation_indices
                    for index in invocation_indices
                )
            ):
                structurally_valid = False
            if not structurally_valid:
                add_issue(
                    issues,
                    "BCF-017",
                    location,
                    "dynamic choice scope is forged, out of set, or spans branches",
                )
                continue
            witnessed_scope_ids.add(scope_id)
            witnessed_invocation_indices.update(invocation_indices)
            if selected_pathway_id not in selected_pathway_ids:
                selected_pathway_ids.append(selected_pathway_id)
            if (
                qualifying_indices
                and selected_pathway_id not in qualifying_pathway_ids
            ):
                qualifying_pathway_ids.append(selected_pathway_id)
        if (
            actual_record.get("selected_pathway_ids") != selected_pathway_ids
            or actual_record.get("actual_pathway_ids_used") != qualifying_pathway_ids
        ):
            add_issue(
                issues,
                "BCF-017",
                alternative_id,
                "dynamic choice aggregate differs from its scoped witnesses",
            )

    scoped_invocation_indices = {
        index
        for index, invocation in enumerate(invocations)
        if invocation.get("alternative_selection_scope_id") is not None
    }
    if scoped_invocation_indices != witnessed_invocation_indices:
        add_issue(
            issues,
            "BCF-017",
            "receipt.actual_stage_symbol_invocations",
            "alternative-scoped invocations differ from exact selection witnesses",
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

    any_success = bool(qualifying_binding_ids or valid_used_candidate_ids)
    if receipt.get("claim_qualified") is not any_success:
        add_issue(
            issues,
            "BCF-020",
            "receipt.claim_qualified",
            "claim qualification does not match contract-qualified bound effects",
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
        "binding_acceptance_status": "stale_pending_review"
        if binding_drift
        else "accepted",
        "binding_acceptance_anchor_digest": trusted_anchor_digest,
        "trusted_execution_transcript_digest": (
            trusted_execution_transcript_digest
        ),
        "trusted_candidate_review_digests": sorted(trusted_review_digests),
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
    parser.add_argument(
        "--acceptance-anchor",
        type=Path,
        help="independently supplied binding/source acceptance-anchor record",
    )
    parser.add_argument(
        "--trusted-anchor-digest",
        help="externally trusted SHA-256 of the acceptance-anchor record",
    )
    parser.add_argument(
        "--trusted-execution-transcript-digest",
        help=(
            "externally frozen SHA-256 of this receipt's raw execution transcript; "
            "required for registered composition and reviewed-candidate claims"
        ),
    )
    parser.add_argument(
        "--trusted-candidate-review-digest",
        action="append",
        default=[],
        help="externally trusted SHA-256 of an invalid-pair candidate review",
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
        acceptance_anchor=(
            load_json(resolve(args.acceptance_anchor))
            if args.acceptance_anchor is not None
            else None
        ),
        trusted_anchor_digest=args.trusted_anchor_digest,
        trusted_execution_transcript_digest=(
            args.trusted_execution_transcript_digest
        ),
        trusted_candidate_review_digests=(
            args.trusted_candidate_review_digest
        ),
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

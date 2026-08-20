"""Canonical binding locks, receipts, graphs, and claim envelopes.

Artifact derivation is deliberately session-independent. The builders consume
authority lookups, immutable binding/candidate records, and frozen runtime
ledger snapshots; they do not mutate binding or execution state.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from copy import deepcopy
from pathlib import Path
from types import MappingProxyType
from typing import Any, Final, Protocol

from .authority import CausalPathwayAuthority
from .candidates import (
    INVALID_RELABEL_CANDIDATE_REVIEW_TRUST_REQUIREMENT,
    CandidateDeclaration,
    CandidateUseRecord,
)
from .effects import EFFECT_OUTCOMES
from .identity import _canonical_value_digest, canonical_digest
from .scopes import (
    ATTESTED_OBJECT_FLOW_DATAFLOW,
    EXPLICIT_ADAPTER_DATAFLOW,
    AllowedPathwayAlternatives,
    BindingStateError,
    CandidateMechanismInvocationRecord,
    CrossingInvocationRecord,
    InvocationRecord,
    composition_dataflow_contract,
)

CLAIM_SCOPE_BOUND_INVOCATIONS: Final[str] = "bound_invocations_only"
UNTRACKED_EXECUTION_STATUS: Final[str] = "not_observable_by_binding_plane"
EXECUTION_TRANSCRIPT_TRUST_REQUIREMENT: Final[str] = (
    "externally_supplied_digest_for_registered_composition_or_reviewed_candidate"
)


class _BoundPathway(Protocol):
    binding_id: str
    pathway_id: str
    stage_ids: tuple[str, ...]
    composition_ids: tuple[str, ...]


class _BoundComposition(Protocol):
    binding_id: str
    composition_id: str

    @property
    def contract(self) -> Mapping[str, Any]: ...

    @property
    def endpoint_bindings(self) -> tuple[_BoundPathway, ...]: ...


def execution_transcript_digest(
    *,
    binding_lock_digest: str,
    stage_invocations: Sequence[Mapping[str, Any]],
    crossing_invocations: Sequence[Mapping[str, Any]],
    candidate_mechanism_invocations: Sequence[Mapping[str, Any]],
) -> str:
    """Digest only raw live-execution records, not their derived claims."""

    return _canonical_value_digest(
        {
            "schema_version": "causal_pathway_execution_transcript_v1",
            "binding_lock_digest": binding_lock_digest,
            "stage_invocations": list(stage_invocations),
            "crossing_invocations": list(crossing_invocations),
            "candidate_mechanism_invocations": list(candidate_mechanism_invocations),
        }
    )


class BindingArtifact:
    """Immutable canonical JSON artifact with a content digest."""

    def __init__(self, record: Mapping[str, Any], *, digest_field: str) -> None:
        self._record = deepcopy(dict(record))
        self._digest_field = digest_field

    @property
    def digest(self) -> str:
        return str(self._record[self._digest_field])

    def to_record(self) -> dict[str, Any]:
        return deepcopy(self._record)

    def write(self, path: str | Path) -> None:
        target = Path(path)
        target.write_text(
            json.dumps(self._record, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )


class BindingLock(BindingArtifact):
    """Exact pre-execution pathway declaration and claim envelope."""

    def __init__(self, record: Mapping[str, Any]) -> None:
        super().__init__(record, digest_field="lock_digest")

    def contains_link(
        self,
        *,
        binding_id: str,
        pathway_id: str,
        stage_id: str,
        symbol_id: str,
        composition_ids: Sequence[str],
    ) -> bool:
        """Return whether this lock freezes one exact callable link."""

        record = self.to_record()
        for binding in record["declared_pathway_bindings"]:
            if (
                binding["binding_id"] != binding_id
                or binding["pathway_id"] != pathway_id
                or binding["composition_ids"] != list(composition_ids)
            ):
                continue
            return any(
                link["stage_id"] == stage_id and link["symbol_id"] == symbol_id
                for link in binding["expected_concrete_symbols"]
            )
        return False

    def contains_crossing_link(
        self,
        *,
        binding_id: str,
        composition_id: str,
        symbol_id: str,
    ) -> bool:
        """Return whether the lock freezes one explicit crossing callable."""

        for binding in self.to_record()["declared_composition_bindings"]:
            crossing = binding.get("expected_crossing_callable")
            if (
                binding.get("binding_id") == binding_id
                and binding.get("composition_id") == composition_id
                and isinstance(crossing, dict)
                and crossing.get("symbol_id") == symbol_id
            ):
                return True
        return False

    def contains_candidate_mechanism_link(
        self,
        *,
        candidate_id: str,
        symbol_id: str,
    ) -> bool:
        """Return whether the lock freezes one exact candidate callable."""

        for candidate in self.to_record()["candidate_declarations"]:
            link = candidate.get("candidate_mechanism_link")
            if candidate.get("candidate_id") == candidate_id and isinstance(
                link, Mapping
            ):
                return link.get("symbol_id") == symbol_id
        return False


class BindingReceipt(BindingArtifact):
    """Exact post-use receipt linked to one binding lock."""

    def __init__(self, record: Mapping[str, Any]) -> None:
        super().__init__(record, digest_field="receipt_digest")


def _binding_record(
    authority: CausalPathwayAuthority,
    binding: _BoundPathway,
    linked_symbols: Mapping[tuple[str, str], Mapping[str, Any]],
) -> dict[str, Any]:
    contract = authority.pathway(binding.pathway_id)
    expected_symbols = sorted(
        (
            deepcopy(link)
            for (binding_id, _), link in linked_symbols.items()
            if binding_id == binding.binding_id
        ),
        key=lambda item: str(item["symbol_id"]),
    )
    return {
        "binding_id": binding.binding_id,
        "pathway_id": binding.pathway_id,
        "declared_stage_ids": list(binding.stage_ids),
        "composition_ids": list(binding.composition_ids),
        "mechanism_ownership": contract["mechanism_ownership"],
        "availability": contract["availability"],
        "activation": contract["activation"],
        "configured_residue": list(contract["configured_residue"]),
        "producer_residue": list(contract["producer_residue"]),
        "expected_concrete_symbols": expected_symbols,
    }


def _composition_record(
    binding: _BoundComposition,
    crossing_links: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    contract = binding.contract
    explicit_adapter = contract["composition_status"] == "lawful_with_explicit_adapter"
    dataflow_requirement = (
        EXPLICIT_ADAPTER_DATAFLOW if explicit_adapter else ATTESTED_OBJECT_FLOW_DATAFLOW
    )
    return {
        "binding_id": binding.binding_id,
        "composition_id": binding.composition_id,
        "from_pathway_id": contract["from_pathway_id"],
        "from_stage_ids": list(contract["from_stage_ids"]),
        "to_pathway_id": contract["to_pathway_id"],
        "to_stage_ids": list(contract["to_stage_ids"]),
        "composition_status": contract["composition_status"],
        "adapter_id": contract["adapter_id"],
        "adapter_owner": contract["adapter_owner"],
        "authority_retained": list(contract["authority_retained"]),
        "authority_transferred": list(contract["authority_transferred"]),
        "information_lost_or_compressed": contract["information_lost_or_compressed"],
        "claim_ceiling": contract["claim_ceiling"],
        "blocked_relabels": list(contract["blocked_relabels"]),
        "runtime_dataflow_requirement": dataflow_requirement,
        "runtime_dataflow_contract": composition_dataflow_contract(
            binding.composition_id,
            explicit_adapter=explicit_adapter,
        ),
        "expected_crossing_callable": deepcopy(crossing_links.get(binding.binding_id)),
    }


def _derive_claim_envelope(
    authority: CausalPathwayAuthority,
    *,
    pathway_bindings: Sequence[_BoundPathway],
    composition_bindings: Sequence[_BoundComposition],
    candidates: Sequence[CandidateDeclaration],
) -> dict[str, Any]:
    pathway_claims: list[dict[str, Any]] = []
    composition_claims: list[dict[str, Any]] = []
    producer_cuts: list[dict[str, Any]] = []
    adapter_cuts: list[dict[str, Any]] = []
    diagnostic_relations: list[dict[str, str]] = []
    configured_semantics: list[dict[str, Any]] = []
    blocked_claims: list[str] = []

    for pathway_binding in sorted(pathway_bindings, key=lambda item: item.binding_id):
        contract = authority.pathway(pathway_binding.pathway_id)
        pathway_claims.append(
            {
                "binding_id": pathway_binding.binding_id,
                "pathway_id": pathway_binding.pathway_id,
                "constituent_claim_ceiling": list(contract["supported_claims"]),
                "mechanism_ownership": contract["mechanism_ownership"],
                "required_qualifiers": {
                    "configured_residue": list(contract["configured_residue"]),
                    "producer_residue": list(contract["producer_residue"]),
                    "naturalization_debt": list(contract["naturalization_debt"]),
                },
                "blocked_claims": list(contract["blocked_claims"]),
            }
        )
        if contract["configured_residue"]:
            configured_semantics.append(
                {
                    "pathway_id": pathway_binding.pathway_id,
                    "residue": list(contract["configured_residue"]),
                }
            )
        if (
            contract["producer_residue"]
            or contract["mechanism_ownership"] == "producer"
        ):
            producer_cuts.append(
                {
                    "pathway_id": pathway_binding.pathway_id,
                    "producer_identity": contract["trigger_surface"],
                    "producer_owned_authorities": list(contract["producer_residue"]),
                }
            )
        if contract["mechanism_ownership"] == "diagnostic":
            diagnostic_relations.append(
                {"kind": "pathway", "identity": pathway_binding.pathway_id}
            )
        blocked_claims.extend(str(item) for item in contract["blocked_claims"])

    for composition_binding in sorted(
        composition_bindings,
        key=lambda item: (item.composition_id, item.binding_id),
    ):
        contract = composition_binding.contract
        status = str(contract["composition_status"])
        composition_claims.append(
            {
                "binding_id": composition_binding.binding_id,
                "composition_id": composition_binding.composition_id,
                "composition_status": status,
                "constituent_claim_ceiling": contract["claim_ceiling"],
                "adapter_id": contract["adapter_id"],
                "adapter_owner": contract["adapter_owner"],
                "authority_retained": list(contract["authority_retained"]),
                "authority_transferred": list(contract["authority_transferred"]),
                "blocked_claims": list(contract["blocked_relabels"]),
            }
        )
        if status == "producer_mediated":
            producer_cuts.append(
                {
                    "composition_id": composition_binding.composition_id,
                    "producer_identity": contract["adapter_id"],
                    "producer_owner": contract["adapter_owner"],
                    "producer_owned_authorities": list(
                        contract["authority_transferred"]
                    ),
                }
            )
        if status == "lawful_with_explicit_adapter":
            adapter_cuts.append(
                {
                    "composition_id": composition_binding.composition_id,
                    "adapter_id": contract["adapter_id"],
                    "adapter_owner": contract["adapter_owner"],
                }
            )
        if status == "diagnostic_only":
            diagnostic_relations.append(
                {"kind": "composition", "identity": composition_binding.composition_id}
            )
        blocked_claims.extend(str(item) for item in contract["blocked_relabels"])

    ordered_candidates = sorted(candidates, key=lambda item: item.candidate_id)
    candidate_records = [candidate.to_record() for candidate in ordered_candidates]
    for candidate in ordered_candidates:
        blocked_claims.extend(candidate.blocked_claims)
    if candidates:
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
        "experimental_unregistered": bool(candidates),
        "blocked_claims": list(dict.fromkeys(blocked_claims)),
        "overall_claim_status": overall_status,
        "composition_status_is_maturity_score": False,
        "synthesized_chain_claim": False,
    }


def _candidate_graph_record(
    candidate: CandidateDeclaration,
    use: CandidateUseRecord,
) -> dict[str, Any]:
    return {
        "candidate_id": candidate.candidate_id,
        "claim_ceiling": candidate.claim_ceiling,
        "promotion_status": candidate.promotion_status,
        "mechanism_evidence": dict(use.mechanism_evidence),
        "candidate_mechanism_link": dict(candidate.mechanism_link or {}),
        "candidate_execution_witness": dict(use.execution_witness),
        "authority": dict(candidate.authority),
        "producer_residue": list(candidate.producer_residue),
        "adapter_residue": list(candidate.adapter_residue),
        "configured_residue": list(candidate.configured_residue),
        "invalid_relabel_conflict_ids": list(candidate.invalid_relabel_conflict_ids),
        "invalid_relabel_blocked_claims": list(
            candidate.invalid_relabel_blocked_claims
        ),
        "invalid_relabel_relation_review": (
            candidate.invalid_relabel_relation_review.to_record()
            if candidate.invalid_relabel_relation_review is not None
            else None
        ),
        "invalid_relabel_relation_review_trust_requirement": (
            INVALID_RELABEL_CANDIDATE_REVIEW_TRUST_REQUIREMENT
            if candidate.invalid_relabel_relation_review is not None
            else None
        ),
        "blocked_claims": list(candidate.blocked_claims),
    }


def _use_graph(
    authority: CausalPathwayAuthority,
    *,
    actual_bindings: Sequence[_BoundPathway],
    exercised_compositions: Sequence[_BoundComposition],
    candidates: Mapping[str, CandidateDeclaration],
    candidate_uses: Sequence[CandidateUseRecord],
    invocations: Sequence[InvocationRecord],
) -> dict[str, Any]:
    successful = [record for record in invocations if record.claim_qualifying_effect]
    nodes: list[dict[str, Any]] = []
    for pathway_binding in sorted(actual_bindings, key=lambda item: item.binding_id):
        contract = authority.pathway(pathway_binding.pathway_id)
        uses = [
            record
            for record in successful
            if record.binding_id == pathway_binding.binding_id
        ]
        nodes.append(
            {
                "node_id": pathway_binding.binding_id,
                "node_kind": "admitted_pathway",
                "pathway_id": pathway_binding.pathway_id,
                "pathway_status": {
                    "availability": contract["availability"],
                    "activation": contract["activation"],
                    "staleness_state": contract["staleness_state"],
                    "mechanism_ownership": contract["mechanism_ownership"],
                },
                "stage_ids_used": list(
                    dict.fromkeys(record.stage_id for record in uses)
                ),
                "mechanism_ownership": contract["mechanism_ownership"],
                "configured_residue": list(contract["configured_residue"]),
                "producer_residue": list(contract["producer_residue"]),
                "source_bindings_used": list(
                    dict.fromkeys(record.symbol_id for record in uses)
                ),
            }
        )
    edges: list[dict[str, Any]] = []
    for composition_binding in sorted(
        exercised_compositions, key=lambda item: item.composition_id
    ):
        contract = composition_binding.contract
        endpoint_ids = {
            endpoint.pathway_id: endpoint.binding_id
            for endpoint in composition_binding.endpoint_bindings
        }
        edges.append(
            {
                "edge_id": composition_binding.binding_id,
                "edge_kind": "registered_composition",
                "composition_id": composition_binding.composition_id,
                "source_node_id": endpoint_ids[str(contract["from_pathway_id"])],
                "target_node_id": endpoint_ids[str(contract["to_pathway_id"])],
                "composition_status": contract["composition_status"],
                "adapter_id": contract["adapter_id"],
                "adapter_owner": contract["adapter_owner"],
                "producer_owner": (
                    contract["adapter_owner"]
                    if contract["composition_status"] == "producer_mediated"
                    else None
                ),
                "authority_retained": list(contract["authority_retained"]),
                "authority_transferred": list(contract["authority_transferred"]),
                "information_lost_or_compressed": contract[
                    "information_lost_or_compressed"
                ],
                "claim_ceiling": contract["claim_ceiling"],
                "blocked_claims": list(contract["blocked_relabels"]),
            }
        )
    actual_by_pathway: dict[str, str] = {}
    for binding in actual_bindings:
        actual_by_pathway.setdefault(binding.pathway_id, binding.binding_id)
    actual_binding_ids = {binding.binding_id for binding in actual_bindings}
    for use in candidate_uses:
        candidate = candidates[use.candidate_id]
        common = _candidate_graph_record(candidate, use)
        if candidate.candidate_kind == "pathway":
            nodes.append(
                {
                    "node_id": f"candidate:{candidate.candidate_id}",
                    "node_kind": "experimental_unregistered_candidate",
                    **common,
                }
            )
            continue
        assert candidate.proposed_source_pathway_id is not None
        assert candidate.proposed_target_pathway_id is not None
        source_binding_id = str(use.execution_witness.get("source_binding_id", ""))
        target_binding_id = str(use.execution_witness.get("target_binding_id", ""))
        if (
            candidate.proposed_source_pathway_id not in actual_by_pathway
            or candidate.proposed_target_pathway_id not in actual_by_pathway
            or source_binding_id not in actual_binding_ids
            or target_binding_id not in actual_binding_ids
        ):
            raise BindingStateError(
                f"used candidate {candidate.candidate_id!r} lacks actual bound "
                "source or target pathway use"
            )
        edges.append(
            {
                "edge_id": f"candidate:{candidate.candidate_id}",
                "edge_kind": "experimental_unregistered_candidate",
                "source_node_id": source_binding_id,
                "target_node_id": target_binding_id,
                "proposed_relation": candidate.proposed_relation,
                "proposed_relation_claim_status": (
                    "descriptive_unreviewed_not_claim_qualified"
                ),
                **common,
            }
        )
    return {
        "nodes": nodes,
        "edges": edges,
        "unregistered_edge_synthesized_from_endpoint_co_use": False,
        "larger_chain_claim_synthesized": False,
    }


def _stage_invocation_records(
    invocations: Sequence[InvocationRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "invocation_index": index,
            "binding_id": item.binding_id,
            "pathway_id": item.pathway_id,
            "stage_id": item.stage_id,
            "symbol_id": item.symbol_id,
            "composition_ids": list(item.composition_ids),
            "outcome": item.outcome,
            "return_category": item.return_category,
            "effect_contract_id": item.effect_contract_id,
            "effect_kind": item.effect_kind,
            "effect_outcome": item.effect_outcome,
            "claim_qualifying_effect": item.claim_qualifying_effect,
            "effect_evidence": (
                None if item.effect_evidence is None else dict(item.effect_evidence)
            ),
            "result_type": item.result_type,
            "error_type": item.error_type,
            "callable_identity": dict(item.callable_identity),
            "runtime_object_flow": deepcopy(item.runtime_object_flow),
            "candidate_request_flow": (
                None
                if item.candidate_request_flow is None
                else deepcopy(item.candidate_request_flow)
            ),
            "execution_event_order": item.execution_event_order,
            "crossing_scope_id": item.crossing_scope_id,
            "candidate_scope_id": item.candidate_scope_id,
            "alternative_selection_scope_id": item.alternative_selection_scope_id,
        }
        for index, item in enumerate(invocations)
    ]


def _crossing_invocation_records(
    invocations: Sequence[CrossingInvocationRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "crossing_invocation_index": index,
            "crossing_scope_id": item.crossing_scope_id,
            "binding_id": item.binding_id,
            "composition_id": item.composition_id,
            "symbol_id": item.symbol_id,
            "source_binding_id": item.source_binding_id,
            "target_binding_id": item.target_binding_id,
            "outcome": item.outcome,
            "return_category": item.return_category,
            "effect_contract_id": item.effect_contract_id,
            "effect_kind": item.effect_kind,
            "effect_outcome": item.effect_outcome,
            "claim_qualifying_effect": item.claim_qualifying_effect,
            "effect_evidence": (
                None if item.effect_evidence is None else dict(item.effect_evidence)
            ),
            "result_type": item.result_type,
            "error_type": item.error_type,
            "callable_identity": dict(item.callable_identity),
            "execution_event_order": item.execution_event_order,
        }
        for index, item in enumerate(invocations)
    ]


def _candidate_mechanism_invocation_records(
    invocations: Sequence[CandidateMechanismInvocationRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "candidate_mechanism_invocation_index": index,
            "candidate_scope_id": item.candidate_scope_id,
            "candidate_id": item.candidate_id,
            "mechanism_id": item.mechanism_id,
            "symbol_id": item.symbol_id,
            "outcome": item.outcome,
            "result_type": item.result_type,
            "error_type": item.error_type,
            "callable_identity": dict(item.callable_identity),
            "relation_review_digest": item.relation_review_digest,
            "structural_result_observed": item.structural_result_observed,
            "runtime_object_flow": deepcopy(item.runtime_object_flow),
            "execution_event_order": item.execution_event_order,
        }
        for index, item in enumerate(invocations)
    ]


def _alternative_use_records(
    alternatives: Sequence[AllowedPathwayAlternatives],
    witnesses: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for declaration in sorted(alternatives, key=lambda item: item.alternative_set_id):
        scopes = [
            witness
            for witness in witnesses
            if witness["alternative_set_id"] == declaration.alternative_set_id
        ]
        qualifying_pathway_ids = [
            str(witness["selected_pathway_id"])
            for witness in scopes
            if witness["claim_qualifying_invocation_indices"]
        ]
        records.append(
            {
                "alternative_set_id": declaration.alternative_set_id,
                "selection_authority": declaration.selection_authority,
                "allowed_pathway_ids": list(declaration.pathway_ids),
                "selected_pathway_ids": list(
                    dict.fromkeys(
                        str(witness["selected_pathway_id"]) for witness in scopes
                    )
                ),
                "actual_pathway_ids_used": list(dict.fromkeys(qualifying_pathway_ids)),
                "selection_scopes": [deepcopy(witness) for witness in scopes],
            }
        )
    return records


def _effect_outcome_summary(
    invocations: Sequence[InvocationRecord],
    crossing_invocations: Sequence[CrossingInvocationRecord],
) -> dict[str, Any]:
    return {
        "stage_invocation_counts": {
            outcome: sum(item.effect_outcome == outcome for item in invocations)
            for outcome in sorted(EFFECT_OUTCOMES)
        },
        "claim_qualifying_stage_invocation_indices": [
            index
            for index, item in enumerate(invocations)
            if item.claim_qualifying_effect
        ],
        "non_qualifying_returned_stage_invocation_indices": [
            index
            for index, item in enumerate(invocations)
            if item.outcome == "returned" and not item.claim_qualifying_effect
        ],
        "raised_stage_invocation_indices": [
            index for index, item in enumerate(invocations) if item.outcome == "raised"
        ],
        "crossing_invocation_counts": {
            outcome: sum(
                item.effect_outcome == outcome for item in crossing_invocations
            )
            for outcome in sorted(EFFECT_OUTCOMES)
        },
        "claim_qualifying_crossing_invocation_indices": [
            index
            for index, item in enumerate(crossing_invocations)
            if item.claim_qualifying_effect
        ],
        "non_qualifying_returned_crossing_invocation_indices": [
            index
            for index, item in enumerate(crossing_invocations)
            if item.outcome == "returned" and not item.claim_qualifying_effect
        ],
        "raised_crossing_invocation_indices": [
            index
            for index, item in enumerate(crossing_invocations)
            if item.outcome == "raised"
        ],
    }


def build_binding_lock(
    *,
    authority: CausalPathwayAuthority,
    bindings: Sequence[_BoundPathway],
    composition_bindings: Sequence[_BoundComposition],
    alternatives: Sequence[AllowedPathwayAlternatives],
    candidates: Sequence[CandidateDeclaration],
    linked_symbols: Mapping[tuple[str, str], Mapping[str, Any]],
    crossing_links: Mapping[str, Mapping[str, Any]],
) -> BindingLock:
    """Build one canonical pre-execution lock from frozen declarations."""

    claim_envelope = _derive_claim_envelope(
        authority,
        pathway_bindings=bindings,
        composition_bindings=composition_bindings,
        candidates=candidates,
    )
    record: dict[str, Any] = {
        "artifact": "causal-pathways-binding-lock",
        "schema_version": "causal_pathways_binding_lock_v1",
        **dict(authority.artifact_identities()),
        "declared_pathway_bindings": [
            _binding_record(authority, binding, linked_symbols)
            for binding in sorted(bindings, key=lambda item: item.binding_id)
        ],
        "declared_composition_bindings": [
            _composition_record(binding, crossing_links)
            for binding in sorted(
                composition_bindings, key=lambda item: item.composition_id
            )
        ],
        "allowed_pathway_alternatives": [
            {
                "alternative_set_id": item.alternative_set_id,
                "pathway_ids": list(item.pathway_ids),
                "selection_authority": item.selection_authority,
            }
            for item in sorted(alternatives, key=lambda item: item.alternative_set_id)
        ],
        "candidate_declarations": [
            item.to_record()
            for item in sorted(candidates, key=lambda item: item.candidate_id)
        ],
        "explicit_producers": deepcopy(
            claim_envelope["required_qualifiers"]["producer_cuts"]
        ),
        "explicit_adapters": deepcopy(
            claim_envelope["required_qualifiers"]["adapter_cuts"]
        ),
        "pre_execution_claim_envelope": claim_envelope,
        "blocked_claims": list(claim_envelope["blocked_claims"]),
        "execution_transcript_trust_requirement": (
            EXECUTION_TRANSCRIPT_TRUST_REQUIREMENT
        ),
        "claim_scope": CLAIM_SCOPE_BOUND_INVOCATIONS,
        "whole_run_causal_closure_claimed": False,
        "untracked_execution_observable_by_binding_plane": False,
        "semantic_selection_performed_by_binder": False,
        "unregistered_relation_bound_without_candidate": False,
        "lock_digest": "",
    }
    record["lock_digest"] = canonical_digest(record, excluding="lock_digest")
    return BindingLock(record)


def build_binding_receipt(
    *,
    authority: CausalPathwayAuthority,
    lock: BindingLock,
    all_bindings: Sequence[_BoundPathway],
    actual_bindings: Sequence[_BoundPathway],
    composition_bindings: Sequence[_BoundComposition],
    exercised_compositions: Sequence[_BoundComposition],
    candidates: Mapping[str, CandidateDeclaration],
    candidate_uses: Sequence[CandidateUseRecord],
    alternatives: Sequence[AllowedPathwayAlternatives],
    linked_symbols: Mapping[tuple[str, str], Mapping[str, Any]],
    crossing_links: Mapping[str, Mapping[str, Any]],
    invocations: Sequence[InvocationRecord],
    crossing_invocations: Sequence[CrossingInvocationRecord],
    candidate_mechanism_invocations: Sequence[CandidateMechanismInvocationRecord],
    composition_witnesses: Sequence[Mapping[str, Any]],
    alternative_selection_witnesses: Sequence[Mapping[str, Any]],
) -> BindingReceipt:
    """Build one canonical post-execution receipt from frozen runtime inputs."""

    used_candidate_ids = {item.candidate_id for item in candidate_uses}
    used_candidates = tuple(
        candidates[candidate_id] for candidate_id in sorted(used_candidate_ids)
    )
    graph = _use_graph(
        authority,
        actual_bindings=actual_bindings,
        exercised_compositions=exercised_compositions,
        candidates=candidates,
        candidate_uses=candidate_uses,
        invocations=invocations,
    )
    claim_envelope = _derive_claim_envelope(
        authority,
        pathway_bindings=actual_bindings,
        composition_bindings=exercised_compositions,
        candidates=used_candidates,
    )
    successful_binding_ids = {binding.binding_id for binding in actual_bindings}
    declared_but_unused = {
        "pathway_binding_ids": sorted(
            binding.binding_id
            for binding in all_bindings
            if binding.binding_id not in successful_binding_ids
        ),
        "composition_binding_ids": sorted(
            binding.binding_id
            for binding in composition_bindings
            if binding not in exercised_compositions
        ),
        "candidate_ids": sorted(set(candidates) - used_candidate_ids),
    }
    actual_uses = _stage_invocation_records(invocations)
    crossing_uses = _crossing_invocation_records(crossing_invocations)
    candidate_mechanism_uses = _candidate_mechanism_invocation_records(
        candidate_mechanism_invocations
    )
    transcript_digest = execution_transcript_digest(
        binding_lock_digest=lock.digest,
        stage_invocations=actual_uses,
        crossing_invocations=crossing_uses,
        candidate_mechanism_invocations=candidate_mechanism_uses,
    )
    record: dict[str, Any] = {
        "artifact": "causal-pathways-binding-receipt",
        "schema_version": "causal_pathways_binding_receipt_v1",
        "binding_lock_digest": lock.digest,
        **dict(authority.artifact_identities()),
        "actual_bound_pathways_used": [
            {
                **_binding_record(authority, binding, linked_symbols),
                "actual_stage_ids": list(
                    dict.fromkeys(
                        item.stage_id
                        for item in invocations
                        if item.binding_id == binding.binding_id
                        and item.claim_qualifying_effect
                    )
                ),
                "actual_symbol_ids": list(
                    dict.fromkeys(
                        item.symbol_id
                        for item in invocations
                        if item.binding_id == binding.binding_id
                        and item.claim_qualifying_effect
                    )
                ),
            }
            for binding in sorted(actual_bindings, key=lambda item: item.binding_id)
        ],
        "actual_stage_symbol_invocations": actual_uses,
        "actual_composition_crossing_invocations": crossing_uses,
        "actual_candidate_mechanism_invocations": candidate_mechanism_uses,
        "execution_transcript_digest": transcript_digest,
        "execution_transcript_trust_requirement": (
            EXECUTION_TRANSCRIPT_TRUST_REQUIREMENT
        ),
        "composition_crossing_witnesses": list(composition_witnesses),
        "allowed_pathway_alternatives_actual_use": _alternative_use_records(
            alternatives, alternative_selection_witnesses
        ),
        "registered_compositions_exercised": [
            _composition_record(binding, crossing_links)
            for binding in exercised_compositions
        ],
        "adapters_used": deepcopy(
            claim_envelope["required_qualifiers"]["adapter_cuts"]
        ),
        "producer_cuts_used": deepcopy(
            claim_envelope["required_qualifiers"]["producer_cuts"]
        ),
        "candidate_relations_exercised": [
            {
                **candidates[item.candidate_id].to_record(),
                "candidate_execution_witness": dict(item.execution_witness),
            }
            for item in candidate_uses
        ],
        "declared_but_unused": declared_but_unused,
        "effect_outcome_summary": _effect_outcome_summary(
            invocations, crossing_invocations
        ),
        "pathway_use_graph": graph,
        "claim_envelope": claim_envelope,
        "blocked_claims": list(claim_envelope["blocked_claims"]),
        "undeclared_use_violations": [],
        "claim_qualified": bool(actual_bindings or candidate_uses),
        "claim_scope": CLAIM_SCOPE_BOUND_INVOCATIONS,
        "whole_run_causal_closure_claimed": False,
        "untracked_execution_observable_by_binding_plane": False,
        "external_or_untracked_causal_input": UNTRACKED_EXECUTION_STATUS,
        "unbound_execution_accepted_as_evidence": False,
        "semantic_selection_performed_by_binder": False,
        "receipt_digest": "",
    }
    record["receipt_digest"] = canonical_digest(record, excluding="receipt_digest")
    return BindingReceipt(record)


def unbound_execution_classification() -> Mapping[str, Any]:
    """Return the mandatory provenance classification for legacy direct calls."""

    return MappingProxyType(
        {
            "causal_pathway_provenance": "unbound",
            "claim_qualified": False,
            "accepted_binding_receipt": False,
        }
    )


__all__ = [
    "EXECUTION_TRANSCRIPT_TRUST_REQUIREMENT",
    "BindingLock",
    "BindingReceipt",
    "execution_transcript_digest",
    "unbound_execution_classification",
]

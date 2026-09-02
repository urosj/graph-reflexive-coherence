"""Bounded structural counterfactuals over accepted ET-C2/ET-C3 authority."""

from __future__ import annotations

from collections import defaultdict, deque
from pathlib import Path
from typing import Any, Iterable, cast

from .canonical import digest, load_json_object, record_digest
from .errors import MutationValidationError, SourceAdmissionError
from .forensic import ForensicContext, load_forensic_context


MUTATION_SCHEMA = "grcv4_explorer_ET_C4_mutation_v1"
RESULT_SCHEMA = "grcv4_explorer_ET_C4_counterfactual_result_v1"
RESULT_CLASS = "speculative_structural_counterfactual"
ET_C3_SCHEMA = "grcv4_explorer_ET_C3_forensic_reconstruction_admission_v1"

TARGET_KINDS = {
    "equation_contract": "equation_contract",
    "normative_object": "normative_object",
    "gate_record": "gate_record",
    "candidate": "candidate",
}

MUTATION_TARGETS = {
    "remove_term": {"equation_contract", "normative_object"},
    "replace_operator": {"equation_contract", "normative_object"},
    "change_authority": {
        "equation_contract",
        "normative_object",
        "gate_record",
        "candidate",
    },
    "change_stage": {"equation_contract", "normative_object", "gate_record"},
    "change_normalization": {"equation_contract", "normative_object"},
    "change_profile_parameterization": {
        "equation_contract",
        "normative_object",
    },
    "add_derivation": {"equation_contract", "normative_object", "candidate"},
    "remove_derivation": {"equation_contract", "normative_object", "candidate"},
    "change_candidate_disposition": {"gate_record", "candidate"},
}

PAYLOAD_FIELDS = {
    "remove_term": {"term_id"},
    "replace_operator": {"replacement_operator_id"},
    "change_authority": {"proposed_authority"},
    "change_stage": {"proposed_stage"},
    "change_normalization": {"surface", "neutralizes_source_lock"},
    "change_profile_parameterization": {"parameter_id", "qualitative_change"},
    "add_derivation": {"derivation_id"},
    "remove_derivation": {"derivation_id"},
    "change_candidate_disposition": {"proposed_disposition"},
}

RESULT_STATUSES = {
    "exact_invalidation",
    "exact_debt_reactivation",
    "exact_negative_activation",
    "exact_route_change",
    "no_propagation_bearing_effect",
    "requires_reexecution_from_gate",
    "unknown_beyond_evidence_frontier",
    "indeterminate_requires_review",
    "invalid_mutation",
}

CONFORMANCE_FIXTURE_ID = "ET-C4-CONFORMANCE-NONLOADBEARING-CONTRACT"


def load_counterfactual_context(
    repo_root: Path, side_tool_root: Path
) -> ForensicContext:
    """Load ET-C3 as the accepted predecessor, then revalidate ET-C1/ET-C2."""

    et_c3 = load_json_object(
        side_tool_root / "records/ETC3ForensicReconstructionSurface.json"
    )
    if et_c3.get("schema") != ET_C3_SCHEMA or et_c3.get("status") != "accepted":
        raise SourceAdmissionError("ET-C3 is not accepted")
    if et_c3.get("record_digest") != record_digest(et_c3, "record_digest"):
        raise SourceAdmissionError("ET-C3 accepted record digest mismatch")
    if et_c3.get("authority", {}).get("iteration_4_authorized") is not True:
        raise SourceAdmissionError("ET-C3 does not authorize Iteration 4")
    context = load_forensic_context(repo_root, side_tool_root)
    predecessor = et_c3.get("predecessor", {})
    if (
        predecessor.get("graph_digest") != context.graph_digest
        or predecessor.get("source_bundle_digest") != context.source_bundle_digest
    ):
        raise SourceAdmissionError("ET-C3 predecessor identities no longer match")
    return context


def _contains_number(value: Any) -> bool:
    if isinstance(value, bool) or value is None or isinstance(value, str):
        return False
    if isinstance(value, (int, float)):
        return True
    if isinstance(value, dict):
        return any(_contains_number(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_number(item) for item in value)
    return True


def _string_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise MutationValidationError(f"{field}_must_be_a_string_list")
    if len(value) != len(set(value)):
        raise MutationValidationError(f"{field}_contains_duplicates")
    return cast(list[str], value)


def _mutation_payload(value: dict[str, Any]) -> dict[str, Any]:
    return {key: item for key, item in value.items() if key != "mutation_id"}


def make_mutation(
    context: ForensicContext,
    *,
    target_id: str,
    target_kind: str,
    mutation_type: str,
    baseline_record_id: str,
    profile_scope: list[str],
    candidate_scope: list[str],
    realization_scope: list[str],
    declared_payload: dict[str, Any],
) -> dict[str, Any]:
    """Create one canonical typed mutation and validate it immediately."""

    baseline = context.documents_by_record.get(baseline_record_id)
    if baseline is None:
        raise MutationValidationError("baseline_record_is_not_admitted")
    mutation: dict[str, Any] = {
        "schema": MUTATION_SCHEMA,
        "mutation_id": None,
        "target_id": target_id,
        "target_kind": target_kind,
        "mutation_type": mutation_type,
        "baseline_record_id": baseline_record_id,
        "baseline_record_digest": baseline.declared_digest,
        "profile_scope": sorted(profile_scope),
        "candidate_scope": sorted(candidate_scope),
        "realization_scope": sorted(realization_scope),
        "declared_payload": declared_payload,
    }
    mutation["mutation_id"] = f"ET-C4-MUT-{digest(_mutation_payload(mutation))}"
    validate_mutation(context, mutation)
    return mutation


def _target_node_id(target_kind: str, target_id: str) -> str:
    return f"{TARGET_KINDS[target_kind]}:{target_id}"


def _candidate_mentions(document: Any, candidate_id: str) -> bool:
    def walk(value: Any) -> bool:
        if value == candidate_id:
            return True
        if isinstance(value, dict):
            return any(walk(item) for item in value.values())
        if isinstance(value, list):
            return any(walk(item) for item in value)
        return False

    return walk(document.data)


def _is_common_contract(attributes: dict[str, Any]) -> bool:
    return (
        not attributes.get("profile_ids")
        and (
            "common" in str(attributes.get("specification_destination", ""))
            or str(attributes.get("contract_scope", "")).startswith("parent_")
            or "specification_meta" in str(attributes.get("substrate_disposition", ""))
        )
    )


def validate_mutation(
    context: ForensicContext,
    mutation: dict[str, Any],
    *,
    conformance_fixture: bool = False,
) -> dict[str, Any]:
    """Fail closed on stale identities, arbitrary patches, and scope leakage."""

    required = {
        "schema",
        "mutation_id",
        "target_id",
        "target_kind",
        "mutation_type",
        "baseline_record_id",
        "baseline_record_digest",
        "profile_scope",
        "candidate_scope",
        "realization_scope",
        "declared_payload",
    }
    if set(mutation) != required:
        missing = sorted(required - set(mutation))
        extra = sorted(set(mutation) - required)
        raise MutationValidationError(f"mutation_fields_mismatch:{missing}:{extra}")
    if mutation.get("schema") != MUTATION_SCHEMA:
        raise MutationValidationError("mutation_schema_not_admitted")
    target_kind = mutation.get("target_kind")
    mutation_type = mutation.get("mutation_type")
    if target_kind not in TARGET_KINDS:
        raise MutationValidationError("target_kind_not_admitted")
    if mutation_type not in MUTATION_TARGETS:
        raise MutationValidationError("mutation_type_not_admitted")
    if target_kind not in MUTATION_TARGETS[cast(str, mutation_type)]:
        raise MutationValidationError("mutation_type_target_kind_mismatch")
    for field in ("target_id", "baseline_record_id", "baseline_record_digest"):
        if not isinstance(mutation.get(field), str) or not mutation[field]:
            raise MutationValidationError(f"{field}_must_be_a_string")
    baseline = context.documents_by_record.get(cast(str, mutation["baseline_record_id"]))
    if baseline is None or baseline.declared_digest != mutation["baseline_record_digest"]:
        raise MutationValidationError("baseline_record_identity_is_stale")
    profile_scope = _string_list(mutation.get("profile_scope"), "profile_scope")
    candidate_scope = _string_list(mutation.get("candidate_scope"), "candidate_scope")
    realization_scope = _string_list(
        mutation.get("realization_scope"), "realization_scope"
    )
    payload = mutation.get("declared_payload")
    if not isinstance(payload, dict):
        raise MutationValidationError("declared_payload_must_be_an_object")
    expected_payload = PAYLOAD_FIELDS[cast(str, mutation_type)]
    if set(payload) != expected_payload:
        raise MutationValidationError("declared_payload_fields_not_admitted")
    if _contains_number(payload):
        raise MutationValidationError("numeric_effect_injection_forbidden")
    if any(not isinstance(value, (str, bool)) for value in payload.values()):
        raise MutationValidationError("declared_payload_values_not_structural")
    expected_id = f"ET-C4-MUT-{digest(_mutation_payload(mutation))}"
    if mutation.get("mutation_id") != expected_id:
        raise MutationValidationError("mutation_id_digest_mismatch")

    target_id = cast(str, mutation["target_id"])
    fixture = conformance_fixture and target_id == CONFORMANCE_FIXTURE_ID
    node = context.nodes.get(_target_node_id(cast(str, target_kind), target_id))
    if node is None and not fixture:
        raise MutationValidationError("target_is_not_an_admitted_graph_node")
    if fixture:
        if target_kind != "equation_contract" or mutation_type != "remove_term":
            raise MutationValidationError("conformance_fixture_shape_mismatch")
        return {"target_node": None, "fixture": True}
    assert node is not None

    source_record_id = cast(str, node["source_record_id"])
    if target_kind in {"equation_contract", "normative_object", "gate_record"}:
        if source_record_id != mutation["baseline_record_id"]:
            raise MutationValidationError("target_and_baseline_record_disagree")
    elif not _candidate_mentions(baseline, target_id):
        raise MutationValidationError("candidate_is_not_present_in_baseline_record")

    attributes = cast(dict[str, Any], node["attributes"])
    source_profiles = set(cast(list[str], attributes.get("profile_ids", [])))
    known_profiles = {
        cast(str, row["identifier"])
        for row in context.nodes.values()
        if row["kind"] == "profile"
    }
    if not set(profile_scope) <= known_profiles:
        raise MutationValidationError("profile_scope_contains_unknown_profile")
    if source_profiles and not profile_scope:
        raise MutationValidationError("profile_scope_is_required")
    if source_profiles and not set(profile_scope) <= source_profiles:
        raise MutationValidationError("profile_scope_exceeds_source_scope")
    if not source_profiles and profile_scope and not _is_common_contract(attributes):
        raise MutationValidationError("empty_source_profile_scope_is_not_common")

    known_candidates = {
        cast(str, row["identifier"])
        for row in context.nodes.values()
        if row["kind"] == "candidate"
    }
    if not set(candidate_scope) <= known_candidates:
        raise MutationValidationError("candidate_scope_contains_unknown_candidate")
    linked_candidates = {
        cast(str, edge["target"]).split(":", 1)[1]
        for edge in context.propagation_edges
        if edge["source"] == node["node_id"]
        and edge["relation"] == "candidate_scope"
    }
    profile_candidates = {
        cast(str, edge["target"]).split(":", 1)[1]
        for edge in context.propagation_edges
        if edge["source"] in {f"profile:{profile}" for profile in source_profiles}
        and edge["relation"] == "candidate_scope"
    }
    linked_candidates.update(profile_candidates)
    if source_profiles and profile_candidates and not candidate_scope:
        raise MutationValidationError("candidate_scope_is_required_for_profile")
    if linked_candidates and not set(candidate_scope) <= linked_candidates:
        raise MutationValidationError("candidate_scope_exceeds_source_scope")
    if target_kind == "candidate" and candidate_scope != [target_id]:
        raise MutationValidationError("candidate_target_requires_exact_candidate_scope")

    known_realizations = {
        cast(str, row["identifier"])
        for row in context.nodes.values()
        if row["kind"] == "realization"
    }
    if not set(realization_scope) <= known_realizations:
        raise MutationValidationError("realization_scope_contains_unknown_realization")
    realization_candidates = {
        cast(str, context.nodes[f"realization:{realization}"]["attributes"].get(
            "candidate", ""
        ))
        for realization in realization_scope
    } - {""}
    if realization_candidates and not realization_candidates <= set(candidate_scope):
        raise MutationValidationError("realization_scope_exceeds_candidate_scope")
    return {"target_node": node, "fixture": False}


def evaluate_support_predicate(
    support_edges: list[dict[str, Any]], removed_edge_ids: set[str]
) -> str:
    """Evaluate only support logic explicitly encoded by ET-C2 semantics."""

    removed = [row for row in support_edges if row["edge_id"] in removed_edge_ids]
    if not removed:
        return "supported"
    if any(row["support_semantic"] == "required" for row in removed):
        return "exact_invalidation"
    one_of_all = [row for row in support_edges if row["support_semantic"] == "one_of"]
    if any(row["support_semantic"] == "one_of" for row in removed):
        if any(row["edge_id"] not in removed_edge_ids for row in one_of_all):
            return "supported"
        return "exact_invalidation"
    if any(row["support_semantic"] == "conditional" for row in removed):
        return "requires_reexecution_from_gate"
    if any(
        row["support_semantic"] == "negative_boundary" for row in removed
    ):
        return "requires_reexecution_from_gate"
    return "indeterminate_requires_review"


def mutation_falsifies_closing_precondition(
    mutation: dict[str, Any], precondition: Any
) -> bool:
    """Recognize only the frozen, explicit ET-C4 closing-precondition shape."""

    if not isinstance(precondition, dict) or set(precondition) != {
        "target_id",
        "mutation_type",
        "required_payload",
    }:
        return False
    required_payload = precondition.get("required_payload")
    if not isinstance(required_payload, dict):
        return False
    if (
        mutation.get("target_id") != precondition.get("target_id")
        or mutation.get("mutation_type") != precondition.get("mutation_type")
    ):
        return False
    payload = mutation.get("declared_payload")
    if not isinstance(payload, dict):
        return False
    return any(payload.get(key) != value for key, value in required_payload.items())


def mutation_satisfies_activation_condition(
    mutation: dict[str, Any], activation_condition: Any
) -> bool:
    """Recognize exact negative activation only from a typed source condition."""

    if not isinstance(activation_condition, dict) or set(activation_condition) != {
        "target_id",
        "mutation_type",
        "required_payload",
    }:
        return False
    required_payload = activation_condition.get("required_payload")
    payload = mutation.get("declared_payload")
    return (
        isinstance(required_payload, dict)
        and isinstance(payload, dict)
        and mutation.get("target_id") == activation_condition.get("target_id")
        and mutation.get("mutation_type") == activation_condition.get("mutation_type")
        and all(payload.get(key) == value for key, value in required_payload.items())
    )


def _edge_ref(context: ForensicContext, edge: dict[str, Any]) -> dict[str, Any]:
    source = context.documents_by_record[cast(str, edge["source_record_id"])]
    return {
        "edge_id": edge["edge_id"],
        "source": edge["source"],
        "target": edge["target"],
        "relation": edge["relation"],
        "support_semantic": edge["support_semantic"],
        "source_record_id": edge["source_record_id"],
        "source_record_digest": source.declared_digest,
        "source_json_pointer": edge["source_json_pointer"],
    }


def _gate_adjacency(context: ForensicContext) -> dict[str, set[str]]:
    result: dict[str, set[str]] = defaultdict(set)
    for edge in context.propagation_edges:
        if edge["relation"] not in {"predecessor_record", "superseded_by"}:
            continue
        source = cast(str, edge["source"])
        target = cast(str, edge["target"])
        if source.startswith("gate_record:") and target.startswith("gate_record:"):
            result[source].add(target)
    return result


def _reachable(adjacency: dict[str, set[str]], roots: Iterable[str]) -> set[str]:
    reached = set(roots)
    queue = deque(sorted(reached))
    while queue:
        source = queue.popleft()
        for target in sorted(adjacency.get(source, set())):
            if target not in reached:
                reached.add(target)
                queue.append(target)
    return reached


def _minimal_gate_antichain(
    context: ForensicContext, gate_record_ids: Iterable[str]
) -> list[str]:
    adjacency = _gate_adjacency(context)
    nodes = sorted(
        {
            f"gate_record:{record_id}"
            for record_id in gate_record_ids
            if f"gate_record:{record_id}" in context.nodes
        }
    )
    minimal = [
        node
        for node in nodes
        if not any(
            node in _reachable(adjacency, [other])
            for other in nodes
            if other != node
        )
    ]
    return [node.split(":", 1)[1] for node in minimal]


def _target_edges(
    context: ForensicContext, node_id: str
) -> list[dict[str, Any]]:
    return [
        edge
        for edge in context.propagation_edges
        if edge["source"] == node_id or edge["target"] == node_id
    ]


def _source_gate_roots(
    context: ForensicContext,
    node: dict[str, Any],
    baseline_record_id: str,
) -> list[str]:
    attributes = cast(dict[str, Any], node["attributes"])
    lineage = [
        value
        for value in cast(list[str], attributes.get("source_lineage", []))
        if f"gate_record:{value}" in context.nodes
    ]
    if not lineage and f"gate_record:{baseline_record_id}" in context.nodes:
        lineage = [baseline_record_id]
    return _minimal_gate_antichain(context, lineage)


def _claim_rows(context: ForensicContext) -> dict[str, dict[str, Any]]:
    return {
        cast(str, row["identifier"]): cast(dict[str, Any], row["attributes"])
        for row in context.nodes.values()
        if row["kind"] in {"current_claim", "historical_claim"}
    }


def _claim_candidate_scope(claim: dict[str, Any]) -> set[str]:
    statement = str(claim.get("statement", ""))
    mapping = {
        "Candidate_A": "V4-A-temporalized-W",
        "Candidate_B": "V4-B-independent-derived-carrier",
        "Candidate_C": "V4-C-constitutive-C-sector",
        "Candidate_D": "V4-D-source-admitted-structural",
        "V4_D": "V4-D-source-admitted-structural",
    }
    return {
        candidate
        for token, candidate in mapping.items()
        if statement.startswith(token)
    }


def _claim_predicate_witness(
    context: ForensicContext,
    claim_id: str,
    mutation: dict[str, Any],
    *,
    impacted_debt_ids: set[str],
    impacted_gate_ids: set[str],
    removed_contract_edge_ids: set[str],
) -> dict[str, Any]:
    claim_nodes = [
        context.nodes.get(f"current_claim:{claim_id}"),
        context.nodes.get(f"historical_claim:{claim_id}"),
    ]
    node = next((row for row in claim_nodes if row is not None), None)
    if node is None:
        raise RuntimeError(f"claim predicate references unknown claim: {claim_id}")
    attributes = cast(dict[str, Any], node["attributes"])
    candidate_scope = _claim_candidate_scope(attributes)
    mutation_candidates = set(cast(list[str], mutation["candidate_scope"]))
    candidate_disjoint = bool(
        candidate_scope and mutation_candidates and candidate_scope.isdisjoint(mutation_candidates)
    )
    evidence = []
    for record_id in cast(list[str], attributes.get("evidence_refs", [])):
        gate_exists = f"gate_record:{record_id}" in context.nodes
        evidence.append(
            {
                "record_id": record_id,
                "accepted_gate_exists": gate_exists,
                "affected_by_mutation": (
                    record_id in impacted_gate_ids and not candidate_disjoint
                ),
            }
        )
    debts = []
    for debt_id in cast(list[str], attributes.get("bearing_debt_ids", [])):
        debt_node = context.nodes.get(f"debt_transformation:{debt_id}")
        debts.append(
            {
                "debt_id": debt_id,
                "transformation": (
                    debt_node["attributes"].get("transformation")
                    if debt_node is not None
                    else None
                ),
                "accepted_transformation_exists": debt_node is not None,
                "affected_by_mutation": debt_id in impacted_debt_ids,
            }
        )
    support_edges = [
        edge
        for edge in context.propagation_edges
        if edge["target"] == node["node_id"] and edge["relation"] == "accepted_claim"
    ]
    support_disposition = evaluate_support_predicate(
        support_edges, removed_contract_edge_ids
    )
    activation_condition = attributes.get("activation_condition")
    exact_negative_activation = (
        attributes.get("claim_class") == "negative"
        and mutation_satisfies_activation_condition(mutation, activation_condition)
        and not candidate_disjoint
    )
    evidence_affected = any(row["affected_by_mutation"] for row in evidence)
    debt_affected = any(row["affected_by_mutation"] for row in debts)
    references_resolve = all(row["accepted_gate_exists"] for row in evidence) and all(
        row["accepted_transformation_exists"] for row in debts
    )
    if exact_negative_activation:
        disposition = "exact_negative_activation"
    elif candidate_disjoint and references_resolve:
        disposition = "supported_current_source_candidate_disjoint"
    elif debt_affected or evidence_affected:
        disposition = "requires_reexecution_from_gate"
    elif support_disposition != "supported":
        disposition = support_disposition
    elif references_resolve:
        disposition = "supported_current_source"
    else:
        disposition = "indeterminate_requires_review"
    return {
        "claim_id": claim_id,
        "claim_source_ref": _source_ref_for_node(context, node),
        "claim_class": attributes.get("claim_class"),
        "candidate_scope_from_source_statement": sorted(candidate_scope),
        "candidate_scope_disjoint_from_mutation": candidate_disjoint,
        "activation_condition": activation_condition,
        "evidence_refs": evidence,
        "debt_transformations": debts,
        "contract_support_edge_ids": sorted(
            cast(str, edge["edge_id"]) for edge in support_edges
        ),
        "contract_support_disposition": support_disposition,
        "predicate_disposition": disposition,
    }


def _candidate_debt_ids(
    context: ForensicContext, candidate_id: str
) -> set[str]:
    result: set[str] = set()

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            debt_id = value.get("debt_id")
            scope = value.get("candidate_scope")
            if isinstance(debt_id, str) and (
                scope == candidate_id
                or (isinstance(scope, list) and candidate_id in scope)
            ):
                if f"debt_transformation:{debt_id}" in context.nodes:
                    result.add(debt_id)
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    for document in context.documents:
        walk(document.data)
    return result


def _candidate_baseline_row(
    context: ForensicContext, record_id: str, candidate_id: str
) -> dict[str, Any] | None:
    document = context.documents_by_record[record_id]

    def walk(value: Any) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        if isinstance(value, dict):
            if value.get("candidate_id") == candidate_id:
                rows.append(value)
            for child in value.values():
                rows.extend(walk(child))
        elif isinstance(value, list):
            for child in value:
                rows.extend(walk(child))
        return rows

    rows = walk(document.data)
    if not rows:
        return None
    return max(rows, key=len)


def _source_ref_for_node(
    context: ForensicContext, node: dict[str, Any]
) -> dict[str, Any]:
    record_id = cast(str, node["source_record_id"])
    source = context.documents_by_record[record_id]
    return {
        "record_id": record_id,
        "record_digest": source.declared_digest,
        "source_json_pointer": node["source_json_pointer"],
        "path": source.admission["path"],
    }


def _result(
    context: ForensicContext,
    mutation: dict[str, Any],
    *,
    statuses: Iterable[str],
    payload: dict[str, Any],
) -> dict[str, Any]:
    ordered_statuses = sorted(set(statuses))
    if not set(ordered_statuses) <= RESULT_STATUSES:
        raise RuntimeError("counterfactual result used an unknown status")
    result: dict[str, Any] = {
        "schema": RESULT_SCHEMA,
        "output_class": RESULT_CLASS,
        "mutation": mutation,
        "result_statuses": ordered_statuses,
        "source_bundle_digest": context.source_bundle_digest,
        "graph_digest": context.graph_digest,
        "structural_result": payload,
        "claim_boundary": {
            "creates_scientific_evidence": False,
            "predicts_reexecuted_gate_outcome": False,
            "numeric_effect_prediction": False,
            "positive_claim_beyond_frontier": False,
        },
        "result_digest": None,
    }
    result["result_digest"] = digest(
        {key: value for key, value in result.items() if key != "result_digest"}
    )
    return result


def _invalid_result(
    context: ForensicContext, mutation: dict[str, Any], reason: str
) -> dict[str, Any]:
    return _result(
        context,
        mutation,
        statuses=["invalid_mutation"],
        payload={
            "invalid_reason": reason,
            "claims_invalidated": [],
            "debts_reactivated": [],
            "negative_claims_activated": [],
            "routes_changed": [],
            "earliest_gates_to_reopen": [],
            "unknown_beyond_evidence_frontier": [],
            "blocked_overreads_at_risk": [],
            "verification_obligations_at_risk": [],
            "source_edge_refs": [],
        },
    )


def evaluate_mutation(
    context: ForensicContext,
    mutation: dict[str, Any],
    *,
    conformance_fixture: bool = False,
) -> dict[str, Any]:
    """Evaluate a typed mutation only to the accepted evidence frontier."""

    try:
        validation = validate_mutation(
            context, mutation, conformance_fixture=conformance_fixture
        )
    except MutationValidationError as error:
        return _invalid_result(context, mutation, str(error))

    if validation["fixture"]:
        return _result(
            context,
            mutation,
            statuses=["no_propagation_bearing_effect"],
            payload={
                "fixture_id": CONFORMANCE_FIXTURE_ID,
                "fixture_authority": "investigation_local_conformance_only",
                "claims_invalidated": [],
                "claims_requiring_reexecution": [],
                "debts_reactivated": [],
                "negative_claims_activated": [],
                "routes_changed": [],
                "earliest_gates_to_reopen": [],
                "known_through_evidence_frontier": [],
                "unknown_beyond_evidence_frontier": [],
                "profiles_affected": [],
                "candidates_affected": [],
                "realizations_affected": [],
                "blocked_overreads_at_risk": [],
                "verification_obligations_at_risk": [],
                "source_edge_refs": [],
            },
        )

    node = cast(dict[str, Any], validation["target_node"])
    node_id = cast(str, node["node_id"])
    target_edges = _target_edges(context, node_id)
    source_edge_refs = sorted(
        [_edge_ref(context, edge) for edge in target_edges],
        key=lambda row: cast(str, row["edge_id"]),
    )
    statuses: set[str] = set()
    claims_invalidated: set[str] = set()
    claims_reexecution: set[str] = set()
    claims_known: set[str] = set()
    debts_reactivated: set[str] = set()
    routes_changed: set[str] = set()
    negative_activated: set[str] = set()
    obligations_at_risk: set[str] = set()
    blocked_overreads: list[dict[str, Any]] = []
    missing_work: list[dict[str, Any]] = []
    predicate_witnesses: list[dict[str, Any]] = []
    candidate_scope = cast(list[str], mutation["candidate_scope"])
    mutation_type = cast(str, mutation["mutation_type"])
    target_kind = cast(str, mutation["target_kind"])

    direct_claim_edges: list[dict[str, Any]] = []
    if target_kind == "equation_contract":
        direct_claim_edges = [
            edge
            for edge in target_edges
            if edge["source"] == node_id and edge["relation"] == "accepted_claim"
        ]
    elif target_kind == "normative_object":
        contract_nodes = {
            cast(str, edge["source"])
            for edge in target_edges
            if edge["target"] == node_id and edge["relation"] == "parent_object"
        }
        direct_claim_edges = [
            edge
            for edge in context.propagation_edges
            if edge["source"] in contract_nodes and edge["relation"] == "accepted_claim"
        ]
        source_edge_refs.extend(
            _edge_ref(context, edge)
            for edge in context.propagation_edges
            if edge["source"] in contract_nodes
        )

    for edge in direct_claim_edges:
        claim_node = cast(str, edge["target"])
        support_edges = [
            row
            for row in context.propagation_edges
            if row["target"] == claim_node and row["relation"] == "accepted_claim"
        ]
        disposition = evaluate_support_predicate(support_edges, {cast(str, edge["edge_id"])})
        claim_id = claim_node.split(":", 1)[1]
        if disposition == "exact_invalidation":
            claims_invalidated.add(claim_id)
            statuses.add("exact_invalidation")
        elif disposition == "supported":
            claims_known.add(claim_id)
        elif disposition == "requires_reexecution_from_gate":
            claims_reexecution.add(claim_id)
            statuses.add("requires_reexecution_from_gate")
        else:
            claims_reexecution.add(claim_id)
            statuses.add("indeterminate_requires_review")

    baseline_record_id = cast(str, mutation["baseline_record_id"])
    roots = _source_gate_roots(context, node, baseline_record_id)

    if mutation_type == "change_candidate_disposition" and candidate_scope:
        candidate_id = candidate_scope[0]
        candidate_debts = _candidate_debt_ids(context, candidate_id)
        claim_rows = _claim_rows(context)
        for debt_id in sorted(candidate_debts):
            debt_node = f"debt_transformation:{debt_id}"
            debt = context.nodes[debt_node]["attributes"]
            if debt.get("transformation") == "routed":
                routes_changed.add(debt_id)
                statuses.add("exact_route_change")
            if mutation_falsifies_closing_precondition(
                mutation, debt.get("conditional_closing_precondition")
            ):
                debts_reactivated.add(debt_id)
                statuses.add("exact_debt_reactivation")
            else:
                statuses.add("requires_reexecution_from_gate")
            for claim_id, claim in claim_rows.items():
                if debt_id in claim.get("bearing_debt_ids", []):
                    claims_reexecution.add(claim_id)
            source_edge_refs.extend(
                _edge_ref(context, edge)
                for edge in _target_edges(context, debt_node)
            )
        baseline_row = _candidate_baseline_row(
            context, baseline_record_id, candidate_id
        )
        if baseline_row is not None:
            missing = baseline_row.get("missing_load_bearing_arrow")
            interpretation = baseline_row.get("scientific_interpretation")
            if missing:
                missing_work.append(
                    {"kind": "source_recorded_missing_work", "payload": missing}
                )
            if isinstance(interpretation, dict) and interpretation.get(
                "reopening_condition"
            ):
                missing_work.append(
                    {
                        "kind": "source_recorded_reopening_condition",
                        "payload": interpretation["reopening_condition"],
                    }
                )
        if target_kind == "gate_record":
            roots = [cast(str, mutation["target_id"])]
        elif candidate_id == "V4-D-source-admitted-structural":
            roots = _minimal_gate_antichain(context, ["GRC9V4-CD-D0-v1"])
            claims_reexecution.clear()
            routes_changed.clear()
            statuses = {"requires_reexecution_from_gate"}
            if baseline_row and baseline_row.get("reopening_rule"):
                missing_work.append(
                    {
                        "kind": "source_recorded_reopening_condition",
                        "payload": baseline_row["reopening_rule"],
                    }
                )

    attributes = cast(dict[str, Any], node["attributes"])
    blocked = attributes.get("blocked_overread")
    if isinstance(blocked, str) and mutation_type in {
        "change_normalization",
        "change_authority",
        "remove_term",
        "replace_operator",
        "remove_derivation",
    }:
        blocked_overreads.append(
            {
                "blocked_overread": blocked,
                "risk_status": "lock_premise_neutralized_not_claim_activated",
                "source_ref": _source_ref_for_node(context, node),
            }
        )

    if (
        target_kind in {"equation_contract", "normative_object"}
        and not direct_claim_edges
        and not blocked_overreads
    ):
        return _result(
            context,
            mutation,
            statuses=["no_propagation_bearing_effect"],
            payload={
                "target_source_ref": _source_ref_for_node(context, node),
                "claims_invalidated": [],
                "claims_requiring_reexecution": [],
                "debts_reactivated": [],
                "negative_claims_activated": [],
                "routes_changed": [],
                "earliest_gates_to_reopen": [],
                "known_through_evidence_frontier": [],
                "unknown_beyond_evidence_frontier": [],
                "profiles_affected": sorted(
                    cast(list[str], mutation["profile_scope"])
                ),
                "candidates_affected": sorted(candidate_scope),
                "realizations_affected": sorted(
                    cast(list[str], mutation["realization_scope"])
                ),
                "source_recorded_missing_work": [],
                "claim_predicate_witnesses": [],
                "blocked_overreads_at_risk": [],
                "verification_obligations_at_risk": [],
                "source_edge_refs": source_edge_refs,
                "historical_must_close_before_D10_used_as_current_authority": False,
                "fabricated_successor_claims": [],
            },
        )

    claim_rows = _claim_rows(context)
    if candidate_scope:
        candidate_debts = _candidate_debt_ids(context, candidate_scope[0])
        for claim_id, claim in claim_rows.items():
            if (
                _claim_candidate_scope(claim)
                and set(candidate_scope).isdisjoint(_claim_candidate_scope(claim))
                and not set(claim.get("bearing_debt_ids", [])) & candidate_debts
            ):
                claims_known.add(claim_id)
    removed_contract_edge_ids = {
        cast(str, edge["edge_id"]) for edge in direct_claim_edges
    }
    impacted_debts = routes_changed | debts_reactivated
    impacted_claim_ids = claims_reexecution | claims_invalidated | claims_known
    for claim_id, claim in claim_rows.items():
        candidate_match = bool(
            set(candidate_scope) & _claim_candidate_scope(claim)
        )
        activation_match = (
            claim.get("claim_class") == "negative"
            and mutation_satisfies_activation_condition(
                mutation, claim.get("activation_condition")
            )
        )
        if claim_id not in impacted_claim_ids and not candidate_match and not activation_match:
            continue
        witness = _claim_predicate_witness(
            context,
            claim_id,
            mutation,
            impacted_debt_ids=impacted_debts,
            impacted_gate_ids=set(roots),
            removed_contract_edge_ids=removed_contract_edge_ids,
        )
        predicate_witnesses.append(witness)
        disposition = witness["predicate_disposition"]
        if disposition == "exact_negative_activation":
            negative_activated.add(claim_id)
            statuses.add("exact_negative_activation")
        elif disposition.startswith("supported_current_source"):
            claims_known.add(claim_id)
            claims_reexecution.discard(claim_id)
        elif disposition == "requires_reexecution_from_gate":
            claims_reexecution.add(claim_id)
            statuses.add("requires_reexecution_from_gate")
        elif disposition == "indeterminate_requires_review":
            statuses.add("indeterminate_requires_review")

    affected_nodes = {
        f"current_claim:{claim_id}" for claim_id in claims_reexecution | claims_invalidated
    } | {
        f"historical_claim:{claim_id}"
        for claim_id in claims_reexecution | claims_invalidated
    } | {f"debt_transformation:{debt_id}" for debt_id in routes_changed | debts_reactivated}
    for edge in context.propagation_edges:
        if (
            edge["relation"] == "requires_verification_from"
            and edge["source"] in affected_nodes
        ):
            obligations_at_risk.add(cast(str, edge["target"]).split(":", 1)[1])

    gate_adjacency = _gate_adjacency(context)
    gate_roots = [f"gate_record:{record_id}" for record_id in roots]
    gate_frontier = _reachable(gate_adjacency, gate_roots) if gate_roots else set()
    unknown = {
        node_id.split(":", 1)[1]
        for node_id in gate_frontier
        if node_id not in gate_roots
    } | claims_reexecution
    if unknown:
        statuses.add("unknown_beyond_evidence_frontier")
    if not statuses:
        statuses.add("no_propagation_bearing_effect")

    source_edge_refs = sorted(
        {row["edge_id"]: row for row in source_edge_refs}.values(),
        key=lambda row: cast(str, row["edge_id"]),
    )
    return _result(
        context,
        mutation,
        statuses=statuses,
        payload={
            "target_source_ref": _source_ref_for_node(context, node),
            "claims_invalidated": sorted(claims_invalidated),
            "claims_requiring_reexecution": sorted(claims_reexecution),
            "debts_reactivated": sorted(debts_reactivated),
            "negative_claims_activated": sorted(negative_activated),
            "routes_changed": sorted(routes_changed),
            "earliest_gates_to_reopen": sorted(roots),
            "known_through_evidence_frontier": sorted(claims_known),
            "unknown_beyond_evidence_frontier": sorted(unknown),
            "profiles_affected": sorted(cast(list[str], mutation["profile_scope"])),
            "candidates_affected": sorted(candidate_scope),
            "realizations_affected": sorted(
                cast(list[str], mutation["realization_scope"])
            ),
            "source_recorded_missing_work": missing_work,
            "claim_predicate_witnesses": sorted(
                predicate_witnesses, key=lambda row: cast(str, row["claim_id"])
            ),
            "blocked_overreads_at_risk": blocked_overreads,
            "verification_obligations_at_risk": sorted(obligations_at_risk),
            "source_edge_refs": source_edge_refs,
            "historical_must_close_before_D10_used_as_current_authority": False,
            "fabricated_successor_claims": [],
        },
    )

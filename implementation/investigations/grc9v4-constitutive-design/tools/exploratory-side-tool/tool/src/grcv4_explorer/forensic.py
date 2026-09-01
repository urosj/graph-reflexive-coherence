"""Pure, source-exact forensic reconstruction over the accepted ET-C2 graph."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, cast

from .adapters import SourceDocument, adapt_source
from .bundle import build_source_bundle
from .canonical import canonical_bytes, digest, load_json_object, record_digest
from .errors import GraphInvariantError, SourceAdmissionError
from .kernel import validate_graph_snapshot
from .source_contract import admitted_rows, load_et_c0_contract


TRACE_SCHEMA = "grcv4_explorer_forensic_evidence_trace_v1"
TRACE_CLASS = "forensic_evidence_trace"
ET_C2_GATE_SCHEMA = "grcv4_explorer_ET_C2_validated_graph_admission_v1"


@dataclass(frozen=True)
class ForensicContext:
    """Accepted graph plus the exact ET-C1-admitted source documents."""

    graph: dict[str, Any]
    graph_digest: str
    source_bundle_digest: str
    et_c2_record_digest: str
    documents: tuple[SourceDocument, ...]
    documents_by_record: dict[str, SourceDocument]
    nodes: dict[str, dict[str, Any]]
    propagation_edges: tuple[dict[str, Any], ...]


def _require_accepted_record(path: Path, schema: str) -> dict[str, Any]:
    record = load_json_object(path)
    if record.get("schema") != schema or record.get("status") != "accepted":
        raise SourceAdmissionError(f"accepted record is unavailable: {path.name}")
    declared = record.get("record_digest")
    if not isinstance(declared, str) or declared != record_digest(
        record, "record_digest"
    ):
        raise SourceAdmissionError(f"accepted record digest mismatch: {path.name}")
    return record


def load_forensic_context(repo_root: Path, side_tool_root: Path) -> ForensicContext:
    """Load and revalidate the accepted ET-C1/ET-C2 context without mutation."""

    records = side_tool_root / "records"
    et_c2 = _require_accepted_record(
        records / "ETC2ValidatedGraphKernel.json", ET_C2_GATE_SCHEMA
    )
    graph = load_json_object(records / "ETC2GraphSnapshot.json")
    validate_graph_snapshot(graph)
    graph_digest = cast(str, graph["graph_digest"])
    if graph_digest != et_c2["graph_snapshot"]["graph_digest"]:
        raise GraphInvariantError("ET-C2 gate and graph snapshot disagree")

    et_c0_path = records / "ETC0SourceAndLayoutContract.json"
    et_c0 = load_et_c0_contract(et_c0_path)
    rebuilt_manifest, observation = build_source_bundle(repo_root, et_c0_path)
    accepted_manifest = load_json_object(records / "ETC1SourceBundleManifest.json")
    if canonical_bytes(rebuilt_manifest) != canonical_bytes(accepted_manifest):
        raise SourceAdmissionError("accepted ET-C1 source bundle no longer rebuilds")
    if observation.get("state") != "current_bundle_exact":
        raise SourceAdmissionError("accepted source bundle is not current")
    source_bundle_digest = cast(str, rebuilt_manifest["source_bundle_digest"])
    if graph.get("source_bundle_digest") != source_bundle_digest:
        raise GraphInvariantError("ET-C2 graph is not bound to accepted ET-C1")

    documents = tuple(
        adapt_source(repo_root, row) for row in admitted_rows(et_c0)
    )
    documents_by_record = {row.record_identifier: row for row in documents}
    if len(documents_by_record) != len(documents):
        raise SourceAdmissionError("forensic source record IDs are not unique")
    nodes = {
        cast(str, row["node_id"]): row
        for row in cast(list[dict[str, Any]], graph["nodes"])
    }
    return ForensicContext(
        graph=graph,
        graph_digest=graph_digest,
        source_bundle_digest=source_bundle_digest,
        et_c2_record_digest=cast(str, et_c2["record_digest"]),
        documents=documents,
        documents_by_record=documents_by_record,
        nodes=nodes,
        propagation_edges=tuple(
            cast(list[dict[str, Any]], graph["propagation_edges"])
        ),
    )


def _escape_pointer(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


def _walk(value: Any, pointer: str = "") -> Iterable[tuple[str, Any]]:
    yield pointer or "/", value
    if isinstance(value, dict):
        for key in sorted(value):
            child = f"{pointer}/{_escape_pointer(str(key))}"
            yield from _walk(value[key], child)
    elif isinstance(value, list):
        for index, child_value in enumerate(value):
            yield from _walk(child_value, f"{pointer}/{index}")


def _matching_rows(
    document: SourceDocument,
    key: str,
    value: str,
) -> list[tuple[str, dict[str, Any]]]:
    return [
        (pointer, row)
        for pointer, row in _walk(document.data)
        if isinstance(row, dict) and row.get(key) == value
    ]


def _source_ref(
    context: ForensicContext,
    record_id: str,
    pointer: str,
) -> dict[str, Any]:
    document = context.documents_by_record.get(record_id)
    if document is None:
        raise SourceAdmissionError(f"record is outside the admitted bundle: {record_id}")
    return {
        "record_id": record_id,
        "record_digest": document.declared_digest,
        "source_json_pointer": pointer,
        "path": cast(str, document.admission["path"]),
    }


def _edge_ref(context: ForensicContext, edge: dict[str, Any]) -> dict[str, Any]:
    record_id = cast(str, edge["source_record_id"])
    document = context.documents_by_record.get(record_id)
    if document is None:
        raise SourceAdmissionError(f"edge source is outside admitted bundle: {record_id}")
    return {
        "edge_id": edge["edge_id"],
        "source": edge["source"],
        "target": edge["target"],
        "relation": edge["relation"],
        "support_semantic": edge["support_semantic"],
        "source_record_id": record_id,
        "source_record_digest": document.declared_digest,
        "source_json_pointer": edge["source_json_pointer"],
    }


def _edges(
    context: ForensicContext,
    predicate: Callable[[dict[str, Any]], bool],
) -> list[dict[str, Any]]:
    return [
        _edge_ref(context, edge)
        for edge in context.propagation_edges
        if predicate(edge)
    ]


def _node_edges(context: ForensicContext, *node_ids: str) -> list[dict[str, Any]]:
    wanted = set(node_ids)
    return _edges(
        context,
        lambda edge: edge["source"] in wanted or edge["target"] in wanted,
    )


def _record_edges(context: ForensicContext, record_id: str) -> list[dict[str, Any]]:
    gate = f"gate_record:{record_id}"
    rows = _node_edges(context, gate) if gate in context.nodes else []
    if rows:
        return rows
    return _edges(context, lambda edge: edge["source_record_id"] == record_id)[:1]


def _row(
    context: ForensicContext,
    *,
    row_id: str,
    classification: str,
    payload: Any,
    record_id: str,
    pointer: str,
    edge_refs: list[dict[str, Any]],
) -> dict[str, Any]:
    if not edge_refs:
        edge_refs = _record_edges(context, record_id)
    if not edge_refs:
        raise GraphInvariantError(f"forensic row has no exact graph edge: {row_id}")
    return {
        "row_id": row_id,
        "classification": classification,
        "payload": payload,
        "source_ref": _source_ref(context, record_id, pointer),
        "edge_refs": sorted(edge_refs, key=lambda item: cast(str, item["edge_id"])),
    }


def _trace(
    context: ForensicContext,
    operation: str,
    query: dict[str, Any],
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema": TRACE_SCHEMA,
        "output_class": TRACE_CLASS,
        "operation": operation,
        "query": query,
        "source_bundle_digest": context.source_bundle_digest,
        "graph_digest": context.graph_digest,
        "ET_C2_record_digest": context.et_c2_record_digest,
        "row_count": len(rows),
        "rows": rows,
        "trace_digest": None,
    }
    payload["trace_digest"] = digest(
        {key: value for key, value in payload.items() if key != "trace_digest"}
    )
    return payload


def _document(context: ForensicContext, record_id: str) -> SourceDocument:
    document = context.documents_by_record.get(record_id)
    if document is None:
        raise KeyError(f"unknown admitted record: {record_id}")
    return document


def gate_act(context: ForensicContext, record_id: str) -> dict[str, Any]:
    """Return the exact accepted act and authority boundary of one gate."""

    document = _document(context, record_id)
    data = document.data
    summary = {
        key: data[key]
        for key in (
            "record_id",
            "artifact_id",
            "gate_id",
            "status",
            "predecessor_record_id",
            "predecessor_decision_digest",
            "authorization_effect",
            "claim_ceiling",
        )
        if key in data
    }
    rows = [
        _row(
            context,
            row_id=f"{record_id}:accepted_act",
            classification="accepted_gate_act",
            payload=summary,
            record_id=record_id,
            pointer="/",
            edge_refs=_record_edges(context, record_id),
        )
    ]
    decision = data.get("decision")
    if isinstance(decision, dict):
        decision_summary = {
            key: decision[key]
            for key in (
                "gate_role",
                "scope",
                "claim_ceiling",
                "architecture_selected",
                "candidate_ranking_performed",
                "candidate_partition_before_D7v2",
                "candidate_partition_after_D7v2",
            )
            if key in decision
        }
        rows.append(
            _row(
                context,
                row_id=f"{record_id}:decision",
                classification="accepted_authority",
                payload=decision_summary,
                record_id=record_id,
                pointer="/decision",
                edge_refs=_record_edges(context, record_id),
            )
        )
    return _trace(context, "gate_act", {"record_id": record_id}, rows)


def debt_lifecycle(context: ForensicContext, debt_id: str) -> dict[str, Any]:
    """Return one D10 transformation without flattening its predecessor history."""

    node_id = f"debt_transformation:{debt_id}"
    if node_id not in context.nodes:
        raise KeyError(f"unknown debt transformation: {debt_id}")
    matches: list[tuple[SourceDocument, str, dict[str, Any]]] = []
    for document in context.documents:
        for pointer, row in _matching_rows(document, "debt_id", debt_id):
            if "transformation" in row and "successor_claim_ids" in row:
                matches.append((document, pointer, row))
    if len(matches) != 1:
        raise SourceAdmissionError(f"debt transformation is not unique: {debt_id}")
    document, pointer, payload = matches[0]
    rows = [
        _row(
            context,
            row_id=debt_id,
            classification=cast(str, payload["transformation"]),
            payload=payload,
            record_id=document.record_identifier,
            pointer=pointer,
            edge_refs=_node_edges(context, node_id),
        )
    ]
    obligation_id = payload.get("verification_obligation")
    if isinstance(obligation_id, str):
        obligation_node = f"verification_obligation:{obligation_id}"
        for source in context.documents:
            for obligation_pointer, obligation in _matching_rows(
                source, "obligation_id", obligation_id
            ):
                rows.append(
                    _row(
                        context,
                        row_id=obligation_id,
                        classification="forward_verification_routing",
                        payload=obligation,
                        record_id=source.record_identifier,
                        pointer=obligation_pointer,
                        edge_refs=_node_edges(context, obligation_node),
                    )
                )
                break
    return _trace(context, "debt_lifecycle", {"debt_id": debt_id}, rows)


def _reconstruction_nodes(context: ForensicContext, claim_node: str) -> set[str]:
    first = {
        cast(str, edge["source"])
        for edge in context.propagation_edges
        if edge["target"] == claim_node
        and edge["relation"] != "requires_verification_from"
    } | {
        cast(str, edge["target"])
        for edge in context.propagation_edges
        if edge["source"] == claim_node
        and edge["relation"] != "requires_verification_from"
        and not cast(str, edge["target"]).startswith("verification_obligation:")
    }
    reached = {claim_node, *first}
    expandable = {
        "debt_transformation",
        "equation_contract",
        "normative_object",
        "gate_record",
        "profile",
        "candidate",
        "realization",
    }
    for node_id in sorted(first):
        node = context.nodes.get(node_id)
        if node is None or node["kind"] not in expandable:
            continue
        for edge in context.propagation_edges:
            if edge["relation"] == "requires_verification_from":
                continue
            if edge["source"] == node_id:
                reached.add(cast(str, edge["target"]))
            if edge["target"] == node_id and edge["relation"] in {
                "transformed_from",
                "predecessor_claim",
                "accepted_claim",
            }:
                reached.add(cast(str, edge["source"]))
    return reached


def reconstruction_path(context: ForensicContext, claim_id: str) -> dict[str, Any]:
    """Reconstruct accepted support while excluding forward-only obligations."""

    claim_nodes = [
        node_id
        for node_id in (
            f"current_claim:{claim_id}",
            f"historical_claim:{claim_id}",
        )
        if node_id in context.nodes
    ]
    if len(claim_nodes) != 1:
        raise KeyError(f"unknown or ambiguous claim: {claim_id}")
    reached = _reconstruction_nodes(context, claim_nodes[0])
    edges = _edges(
        context,
        lambda edge: edge["relation"] != "requires_verification_from"
        and edge["source"] in reached
        and edge["target"] in reached,
    )
    nodes = [context.nodes[node_id] for node_id in sorted(reached)]
    source = context.nodes[claim_nodes[0]]
    rows = [
        _row(
            context,
            row_id=claim_id,
            classification="accepted_backward_reconstruction",
            payload={
                "start_node": claim_nodes[0],
                "nodes": nodes,
                "verification_obligations_excluded": True,
            },
            record_id=cast(str, source["source_record_id"]),
            pointer=cast(str, source["source_json_pointer"]),
            edge_refs=edges,
        )
    ]
    return _trace(context, "reconstruction_path", {"claim_id": claim_id}, rows)


_CAREER_FIELDS = (
    "candidate_id",
    "candidate_status",
    "status",
    "terminal_disposition",
    "complete_candidate_local_transition",
    "D7G_eligible",
    "candidate_rejected",
    "ontology_rejected",
    "reason",
    "reopen_rule",
    "reopening_rule",
    "rejection_reason",
    "missing_load_bearing_arrow",
    "scientific_interpretation",
    "claim_ceiling",
)


def candidate_career(context: ForensicContext, candidate_id: str) -> dict[str, Any]:
    """Trace candidate dispositions without equating routing and rejection."""

    candidate_node = f"candidate:{candidate_id}"
    if candidate_node not in context.nodes:
        raise KeyError(f"unknown candidate: {candidate_id}")
    rows: list[dict[str, Any]] = []
    for document in context.documents:
        candidates = _matching_rows(document, "candidate_id", candidate_id)
        semantic = [
            (pointer, item)
            for pointer, item in candidates
            if any(key in item for key in _CAREER_FIELDS[1:])
        ]
        if not semantic:
            continue
        pointer, item = max(semantic, key=lambda pair: len(pair[1]))
        excerpt = {key: item[key] for key in _CAREER_FIELDS if key in item}
        disposition = str(
            item.get("terminal_disposition")
            or item.get("candidate_status")
            or item.get("status")
            or "source_recorded_candidate_state"
        )
        rows.append(
            _row(
                context,
                row_id=f"{document.record_identifier}:{candidate_id}",
                classification=disposition,
                payload=excerpt,
                record_id=document.record_identifier,
                pointer=pointer,
                edge_refs=_node_edges(context, candidate_node),
            )
        )
    realization_nodes = sorted(
        {
            cast(str, edge["source"])
            for edge in context.propagation_edges
            if edge["target"] == candidate_node
            and cast(str, edge["source"]).startswith("realization:")
        }
    )
    profile_nodes = sorted(
        {
            cast(str, edge["source"])
            for edge in context.propagation_edges
            if edge["target"] == candidate_node
            and cast(str, edge["source"]).startswith("profile:")
        }
    )
    candidate_source = context.nodes[candidate_node]
    rows.append(
        _row(
            context,
            row_id=f"{candidate_id}:realization_branches",
            classification="parallel_realization_branches",
            payload={
                "realization_nodes": realization_nodes,
                "profile_nodes": profile_nodes,
                "realization_row_count": len(realization_nodes),
                "profile_count": len(profile_nodes),
                "branches_are_parallel_not_ranked": True,
            },
            record_id=cast(str, candidate_source["source_record_id"]),
            pointer=cast(str, candidate_source["source_json_pointer"]),
            edge_refs=_node_edges(context, candidate_node),
        )
    )
    if candidate_id == "V4-A-temporalized-W":
        provenance = _document(context, "GRC9V4-CD-D10.2-v1")
        value = provenance.data["targeted_type_and_provenance_hardening"]
        rows.append(
            _row(
                context,
                row_id=f"{candidate_id}:promotion_boundary",
                classification="narrowed",
                payload={
                    "Candidate_A_profile_scope": value["Candidate_A_profile_scope"],
                    "Candidate_A_future_curvature_rule": value[
                        "Candidate_A_future_curvature_rule"
                    ],
                },
                record_id=provenance.record_identifier,
                pointer="/targeted_type_and_provenance_hardening",
                edge_refs=_record_edges(context, provenance.record_identifier),
            )
        )
    return _trace(
        context, "candidate_career", {"candidate_id": candidate_id}, rows
    )


def pruned_choices_at(context: ForensicContext, record_id: str) -> dict[str, Any]:
    """Return only source-recorded exclusions, alternatives, and relabel locks."""

    document = _document(context, record_id)
    rows: list[dict[str, Any]] = []
    for field, classification in (
        ("rejected_alternatives", "pruned_alternative"),
        ("blocked_relabels", "blocked_relabel"),
    ):
        values = document.data.get(field, [])
        if not isinstance(values, list):
            raise SourceAdmissionError(f"malformed {field}: {record_id}")
        for index, value in enumerate(values):
            rows.append(
                _row(
                    context,
                    row_id=f"{record_id}:{field}:{index}",
                    classification=classification,
                    payload=value,
                    record_id=record_id,
                    pointer=f"/{field}/{index}",
                    edge_refs=_record_edges(context, record_id),
                )
            )
    if record_id == "GRC9V4-CD-D1-v1":
        matches = _matching_rows(
            document, "candidate_id", "V4-D-source-admitted-structural"
        )
        ontology_matches = [
            (pointer, value)
            for pointer, value in matches
            if value.get("candidate_status")
            == "rejected_on_ontology_uninstantiated_admission_slot"
        ]
        if len(ontology_matches) != 1:
            raise SourceAdmissionError("V4-D ontology row is not unique")
        pointer, value = ontology_matches[0]
        rows.insert(
            0,
            _row(
                context,
                row_id="V4-D-source-admitted-structural",
                classification="resolved_negative_uninstantiated_slot",
                payload=value,
                record_id=record_id,
                pointer=pointer,
                edge_refs=_node_edges(
                    context, "candidate:V4-D-source-admitted-structural"
                ),
            ),
        )
    return _trace(context, "pruned_choices_at", {"record_id": record_id}, rows)


def negative_claims(context: ForensicContext) -> dict[str, Any]:
    """Return accepted negative claims plus exact provenance hardening locks."""

    topology = _document(context, "GRC9V4-D10-CLAIM-TOPOLOGY-v2")
    rows: list[dict[str, Any]] = []
    claims = cast(list[dict[str, Any]], topology.data["claims"])
    for index, claim in enumerate(claims):
        if claim.get("claim_class") != "negative":
            continue
        claim_id = cast(str, claim["claim_id"])
        rows.append(
            _row(
                context,
                row_id=claim_id,
                classification="resolved_negative",
                payload=claim,
                record_id=topology.record_identifier,
                pointer=f"/claims/{index}",
                edge_refs=_node_edges(context, f"current_claim:{claim_id}"),
            )
        )
    provenance = _document(context, "GRC9V4-CD-D10.2-v1")
    hardening = cast(
        dict[str, Any], provenance.data["targeted_type_and_provenance_hardening"]
    )
    for key in sorted(hardening):
        rows.append(
            _row(
                context,
                row_id=f"D10.2-hardening:{key}",
                classification="conditioned",
                payload={"hardening_key": key, "hardening_value": hardening[key]},
                record_id=provenance.record_identifier,
                pointer=f"/targeted_type_and_provenance_hardening/{_escape_pointer(key)}",
                edge_refs=_record_edges(context, provenance.record_identifier),
            )
        )
    return _trace(context, "negative_claims", {}, rows)


def object_dependents(context: ForensicContext, object_id: str) -> dict[str, Any]:
    """Return exact graph dependents of one normative parent object."""

    node_id = f"normative_object:{object_id}"
    node = context.nodes.get(node_id)
    if node is None:
        raise KeyError(f"unknown normative object: {object_id}")
    direct_contracts = {
        cast(str, edge["source"])
        for edge in context.propagation_edges
        if edge["target"] == node_id and edge["relation"] == "parent_object"
    }
    selected_edges = _node_edges(context, node_id, *sorted(direct_contracts))
    dependent_nodes = sorted(
        {
            cast(str, edge[key])
            for edge in context.propagation_edges
            if edge["source"] in direct_contracts or edge["target"] in direct_contracts
            for key in ("source", "target")
        }
        | direct_contracts
    )
    rows = [
        _row(
            context,
            row_id=object_id,
            classification="source_exact_object_dependents",
            payload={
                "object": node,
                "direct_contract_nodes": sorted(direct_contracts),
                "dependent_nodes": dependent_nodes,
                "dependency_reach_is_not_importance_or_ranking": True,
            },
            record_id=cast(str, node["source_record_id"]),
            pointer=cast(str, node["source_json_pointer"]),
            edge_refs=selected_edges,
        )
    ]
    return _trace(context, "object_dependents", {"object_id": object_id}, rows)


def contract_provenance(context: ForensicContext, contract_id: str) -> dict[str, Any]:
    """Return source lineage and admitted scopes for one equation contract."""

    node_id = f"equation_contract:{contract_id}"
    node = context.nodes.get(node_id)
    if node is None:
        raise KeyError(f"unknown equation contract: {contract_id}")
    edge_refs = _node_edges(context, node_id)
    semantics = sorted(
        {
            cast(str, edge["support_semantic"])
            for edge in edge_refs
            if edge["relation"] == "accepted_claim"
        }
    )
    rows = [
        _row(
            context,
            row_id=contract_id,
            classification="source_exact_contract_provenance",
            payload={
                "contract": node,
                "accepted_claim_support_semantics": semantics,
                "support_disposition": (
                    "indeterminate_requires_review"
                    if not semantics or "indeterminate_requires_review" in semantics
                    else semantics
                ),
            },
            record_id=cast(str, node["source_record_id"]),
            pointer=cast(str, node["source_json_pointer"]),
            edge_refs=edge_refs,
        )
    ]
    return _trace(
        context, "contract_provenance", {"contract_id": contract_id}, rows
    )


def gate_contribution(context: ForensicContext, record_id: str) -> dict[str, Any]:
    """Classify one gate's source-recorded additions, inheritance, and routing."""

    document = _document(context, record_id)
    rows: list[dict[str, Any]] = []
    source_identities = document.data.get("source_identities", [])
    if isinstance(source_identities, list):
        for index, value in enumerate(source_identities):
            rows.append(
                _row(
                    context,
                    row_id=f"{record_id}:inherited:{index}",
                    classification="inherited",
                    payload=value,
                    record_id=record_id,
                    pointer=f"/source_identities/{index}",
                    edge_refs=_record_edges(context, record_id),
                )
            )
    supersedes = document.data.get("supersedes")
    if supersedes:
        rows.append(
            _row(
                context,
                row_id=f"{record_id}:supersedes",
                classification="superseded",
                payload=supersedes,
                record_id=record_id,
                pointer="/supersedes",
                edge_refs=_record_edges(context, record_id),
            )
        )
    decision = document.data.get("decision")
    if isinstance(decision, dict):
        registry = decision.get("candidate_transition_registry", [])
        if isinstance(registry, list):
            for index, value in enumerate(registry):
                if not isinstance(value, dict):
                    continue
                candidate_id = str(value.get("candidate_id", index))
                if value.get("terminal_disposition") == (
                    "current_tranche_closed_missing_constitutive_derivation"
                ):
                    classification = "routed"
                elif value.get("registry_entry_role", "").startswith("immutable"):
                    classification = "inherited"
                else:
                    classification = "added"
                rows.append(
                    _row(
                        context,
                        row_id=f"{record_id}:{candidate_id}",
                        classification=classification,
                        payload=value,
                        record_id=record_id,
                        pointer=f"/decision/candidate_transition_registry/{index}",
                        edge_refs=_node_edges(context, f"candidate:{candidate_id}"),
                    )
                )
    return _trace(context, "gate_contribution", {"record_id": record_id}, rows)


def write_trace(path: Path, trace: dict[str, Any]) -> None:
    """Write one canonical trace. Callers own the destination envelope."""

    if trace.get("output_class") != TRACE_CLASS:
        raise ValueError("only forensic evidence traces may use write_trace")
    if trace.get("trace_digest") != digest(
        {key: value for key, value in trace.items() if key != "trace_digest"}
    ):
        raise ValueError("forensic trace digest mismatch")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(trace) + b"\n")

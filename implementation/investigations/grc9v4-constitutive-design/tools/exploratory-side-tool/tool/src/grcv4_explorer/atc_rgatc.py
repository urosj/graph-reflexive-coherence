"""Append-only paired A_RG2b research admission; never native ATC authority."""
from dataclasses import replace
from pathlib import Path

from . import atc, atc_cip as predecessor
from .adapters import SourceDocument
from .canonical import digest, file_sha256, load_json_object, record_digest
from .errors import SourceAdmissionError
from .forensic import _row, _trace, _edges
from .successor import _Overlay, _source_node_id

EVIDENCE = atc.INV + "/evidence/atc-rgatc"
ADMISSION_EVIDENCE = atc.INV + "/evidence/atc-rgatc-admission"
LEDGER = ADMISSION_EVIDENCE + "/ATCRGATCClaimDebtLedger.json"
RECORD_ID = "GRCV4-ATC-RGATC-LEDGER-v1"
ADMISSION = "ATCRGATCResearchAdmission.json"
ADMISSION_DIGEST = "41525026bc6e41ef21164619fc2a5d97e95f1307a9f721139d26da47739e8803"
LEDGER_DIGEST = "74c13669b4a37151cab10f8dbdbe521487e0350fdf45859c54a869a5aab1540c"
CLAIMS = ["RGATC-T-SECTION","RGATC-A-COMPLETION","RGATC-A-RATES","RGATC-A-ANCHOR","RGATC-A-NONCI","RGATC-E-WITNESS","RGATC-R-REFERENCE"]
INHERITED = ("ATC-CI-DOMAIN-02", "ATC-LSF-G56-CL-02", "ATC-LSF-G56-CL-03")
PARENTS = [[],["RGATC-T-SECTION"],["ATC-CI-DOMAIN-02","ATC-LSF-G56-CL-02","ATC-LSF-G56-CL-03"],["RGATC-A-COMPLETION","RGATC-A-RATES"],["RGATC-A-ANCHOR","RGATC-A-RATES"],["RGATC-A-ANCHOR"],["RGATC-T-SECTION","RGATC-E-WITNESS"]]
_require, _path, _pointer = atc._require, atc._path, atc._pointer


def _inventory(root):
    # Bind package READMEs too: they belong to its portable scientific manifest.
    # Only the outer navigation README is mutable outside source authority.
    return sorted(p.relative_to(root).as_posix()
        for directory in (EVIDENCE, ADMISSION_EVIDENCE)
        for p in (root / directory).rglob("*")
        if p.is_file() and p.suffix in (".json", ".md", ".py")
        and p.relative_to(root).as_posix() != EVIDENCE + "/README.md"
        and "__pycache__" not in p.parts)


def observe_sources(root, admission):
    expected, actual = admission["evidence_files"], _inventory(root)
    missing = sorted(p for p in expected if not _path(root, p).is_file())
    added = sorted(set(actual) - set(expected))
    changed = sorted(p for p in expected if p not in missing
                     and file_sha256(_path(root, p)) != expected[p])
    # All package code, bundled dependencies and manifests are in the exact
    # inventory. Package-relative source bindings must not be read as repo paths.
    support_changed = sorted({r["path"] for r in admission["support_files"]
        if not _path(root, r["path"]).is_file()
        or file_sha256(_path(root, r["path"])) != r["sha256"]})
    state = ("admitted_source_missing" if missing else
             "admitted_source_identity_changed" if changed or support_changed else
             "new_unprocessed_source_available" if added else "current_bundle_exact")
    value = dict(schema="grcv4_atc_rgatc_source_observation_v1", state=state,
        missing_admitted=missing, added_unprocessed=added, changed_admitted=changed,
        changed_support=support_changed, automatic_admission_allowed=False)
    value["observation_digest"] = digest(value)
    return value


def _checked_ref(root, ref):
    path = _path(root, ref["path"])
    _require(path.is_file(), "RGATC source reference missing")
    _require(file_sha256(path) == ref["sha256"], "RGATC source reference drift")
    if path.suffix == ".json":
        try:
            return _pointer(load_json_object(path), ref["json_pointer"])
        except (KeyError, IndexError, ValueError, TypeError) as exc:
            raise SourceAdmissionError("RGATC source pointer does not resolve") from exc
    _require(ref["json_pointer"] == "/", "non-JSON RGATC pointer")


def _validate_ledger(root, ledger):
    _require(ledger.get("schema") == "grcv4_atc_rgatc_claim_debt_ledger_v1"
        and ledger.get("record_id") == RECORD_ID
        and ledger.get("record_digest") == record_digest(ledger, "record_digest") == LEDGER_DIGEST,
        "RGATC ledger is not the exact adjudicated decision")
    _require(ledger["status"] == "accepted_bounded_research_reconciliation"
        and ledger["profile_scope"] == ["A_RG2b"]
        and all(ledger[k] is False for k in ("native_authority", "ATC2_closed", "ATC3_closed")),
        "RGATC research ceiling widened")
    origin = _checked_ref(root, ledger["origin_ref"])
    intake = _checked_ref(root, ledger["intake_ref"])
    _checked_ref(root, ledger["accepted_scope_ref"])
    profile = _checked_ref(root, ledger["contract_ref"])
    _require(profile["completion"] == "rgatc_paired_floor_preserving_completion_v1_proposed"
        and profile["delta"] == "1/33554432" and profile["kappa_H"] == "1/4294967296"
        and profile["native_authority"] is False, "RGATC frozen profile changed")
    for ref in ledger["review_refs"]:
        _checked_ref(root, ref)
    _require(ledger["review_disposition"] == dict(scientific_core="user_reported_independent_PASS",
        retained_record_integrity="local_PASS",
        independent_retained_record_comparison="not_supplied_not_claimed",
        ER_full_local_rerun=False), "RGATC review class widened")
    _require([c["claim_id"] for c in ledger["claims"]] == CLAIMS
        == [c["handle"] for c in intake["proposed_claims"]], "RGATC claim roster changed")
    claims = {c["claim_id"]: c for c in ledger["claims"]}
    debts = {d["origin_debt_id"]: d for d in ledger["debts"]}
    _require(len(debts) == len(ledger["debts"]) == 28
        and set(debts) == {d["id"] for d in origin["debts"]}, "RGATC debt roster changed")
    seen = set(INHERITED)
    for i, c in enumerate(ledger["claims"]):
        _require(c["claim_class"] == "conditional" and c["profile_scope"] == ["A_RG2b"]
            and c["status"] == "accepted_bounded_A_RG2b_research"
            and c["native_authority"] is False, "RGATC claim ceiling widened")
        row = _checked_ref(root, c["source_ref"])
        _require(row["handle"] == c["claim_id"] and c["predecessor_claim_ids"] == PARENTS[i]
            and set(c["predecessor_claim_ids"]) <= seen
            and set(c["origin_claim_ids"]) <= {o["id"] for o in origin["claims"]},
            "RGATC source/ancestry changed")
        _require(c["predecessor_contract_ids"] ==
            (["D10.2-EC-PARENT-REAL-RG2B"] if i == 0 else []),
            "RGATC predecessor contract changed")
        for ref in c["evidence_refs"]:
            _checked_ref(root, ref)
        _require(c["debt_ids"] == [d["origin_debt_id"] for d in ledger["debts"]
            if c["claim_id"] in d["successor_claim_ids"]], "RGATC debt reciprocity changed")
        seen.add(c["claim_id"])
    for d in debts.values():
        old = _checked_ref(root, d["origin_ref"])
        _require(old["id"] == d["origin_debt_id"] and old["status"] == d["origin_status"]
            and all(old[k] == d[k] for k in ("title", "activation", "closure_requirement"))
            and d["global_discharged"] is False
            and d["blocks_paired_research_acceptance"] is False,
            "RGATC origin debt meaning changed")
        _require(d["A_RG2b_research_status"] in ("closed", "partial", "not_activated")
            and d["transformation"] == "scoped_" + d["A_RG2b_research_status"]
            and d["admission_evidence"] == (d["origin_debt_id"] == "ATC7-DB-24")
            and len(d["successor_claim_ids"]) == len(set(d["successor_claim_ids"]))
            and all(c in claims and d["origin_debt_id"] in claims[c]["debt_ids"]
                    for c in d["successor_claim_ids"]), "RGATC scoped debt routing changed")
    _require(ledger["classifications"] == {s: sum(d["A_RG2b_research_status"] == s
        for d in debts.values()) for s in ("closed", "partial", "not_activated")},
        "RGATC debt counts changed")


def _build_context(root, side, admission):
    old = predecessor.load_current_forensic_context(root, side)
    _require(admission["historical_graph_digest"] == old.graph_digest
        and admission["historical_authority_extension_digest"] == old.authority_extension_digest,
        "RGATC historical authority changed")
    observation = observe_sources(root, admission)
    _require(observation["state"] == "current_bundle_exact", "RGATC source set: " + observation["state"])
    ledger = load_json_object(root / LEDGER)
    _validate_ledger(root, ledger)
    row = dict(source_id=RECORD_ID, path=LEDGER, file_sha256=file_sha256(root / LEDGER))
    doc = SourceDocument(Path(LEDGER).name, root / LEDGER, ledger, row,
                         "atc_rgatc_research_v1", RECORD_ID, ledger["schema"], "record_digest", {})
    overlay = _Overlay(old.graph)
    source = _source_node_id(doc)
    overlay.add_node("source_record", source.split(":", 1)[1], doc, "/", row)
    def node(kind, identifier, pointer, attributes):
        key = overlay.add_node(kind, identifier, doc, pointer, attributes)
        overlay.add_edge(key, source, "source_identity", doc, pointer)
        return key
    for i, c in enumerate(ledger["claims"]):
        target = node("current_claim", c["claim_id"], f"/claims/{i}", c)
        for j, cid in enumerate(c["predecessor_claim_ids"]):
            overlay.add_edge("current_claim:" + cid, target, "predecessor_claim", doc,
                f"/claims/{i}/predecessor_claim_ids/{j}", support_semantic="conditioned",
                attributes={"lineage_not_sufficient_proof": True})
        for j, cid in enumerate(c["predecessor_contract_ids"]):
            overlay.add_edge("equation_contract:" + cid, target,
                "conditioned_contract_provenance", doc,
                f"/claims/{i}/predecessor_contract_ids/{j}", support_semantic="conditioned",
                attributes={"lineage_not_sufficient_proof": True})
        for j, cid in enumerate(c["origin_claim_ids"]):
            overlay.add_edge("proposal_claim:" + cid, target, "proposal_provenance_not_support", doc,
                             f"/claims/{i}/origin_claim_ids/{j}")
    for i, c in enumerate(ledger["historical_controls"]):
        node("historical_control", c["claim_id"], f"/historical_controls/{i}", c)
    for i, d in enumerate(ledger["debts"]):
        key = node("scoped_debt_transformation", "A_RG2b:" + d["origin_debt_id"], f"/debts/{i}", d)
        overlay.add_edge("debt_transformation:" + d["origin_debt_id"], key,
            "parallel_scope_not_global_discharge", doc, f"/debts/{i}/origin_debt_id")
        for j, cid in enumerate(d["successor_claim_ids"]):
            overlay.add_edge(key, "current_claim:" + cid, "scoped_debt_bearing", doc,
                f"/debts/{i}/successor_claim_ids/{j}", support_semantic="conditioned")
        if d["admission_evidence"]:
            overlay.add_edge(key, source, "scoped_source_admission", doc, f"/debts/{i}/admission_evidence")
    _require(all(e[k] in overlay.nodes for e in overlay.propagation_edges.values() for k in ("source", "target")),
             "RGATC graph has unresolved endpoints")
    bundle = digest(dict(historical_source_bundle_digest=old.source_bundle_digest,
        evidence_files=admission["evidence_files"], support_files=admission["support_files"]))
    graph = dict(schema="grcv4_atc_rgatc_research_graph_v1", historical_graph_digest=old.graph_digest,
        source_bundle_digest=bundle, nodes=sorted(overlay.nodes.values(), key=lambda r:r["node_id"]),
        propagation_edges=sorted(overlay.propagation_edges.values(), key=lambda r:r["edge_id"]),
        annotation_edges=old.graph["annotation_edges"])
    graph["graph_digest"] = digest(graph)
    return replace(old, graph=graph, graph_digest=graph["graph_digest"], source_bundle_digest=bundle,
        documents=(*old.documents, doc), documents_by_record={**old.documents_by_record, RECORD_ID:doc},
        nodes=overlay.nodes, propagation_edges=tuple(graph["propagation_edges"]),
        authority_extension_digest=admission.get("record_digest"))


def pinned_admission(side):
    value = load_json_object(side / "records" / ADMISSION)
    _require(value.get("schema") == "grcv4_atc_rgatc_research_admission_v1"
        and value.get("status") == "accepted_bounded_research_source_admission"
        and value.get("record_digest") == record_digest(value, "record_digest") == ADMISSION_DIGEST,
        "RGATC admission is not pinned")
    return value


def load_current_forensic_context(root, side):
    admission = pinned_admission(side)
    context = _build_context(root, side, admission)
    _require(context.graph_digest == admission["graph_digest"], "RGATC graph no longer rebuilds exactly")
    return context


def reconstruction_path(context, claim_id):
    start = "current_claim:" + claim_id
    if start not in context.nodes or context.nodes[start]["source_record_id"] != RECORD_ID:
        return predecessor.reconstruction_path(context, claim_id)
    reached = {start}
    while True:
        parents = {e["source"] for e in context.propagation_edges
                   if e["target"] in reached and e["relation"] == "predecessor_claim"}
        if parents <= reached:
            break
        reached |= parents
    origins = {e["source"] for e in context.propagation_edges if e["target"] in reached
               and e["relation"] == "proposal_provenance_not_support"}
    contracts = {e["source"] for e in context.propagation_edges if e["target"] in reached
                 and e["relation"] == "conditioned_contract_provenance"}
    edges = _edges(context, lambda e:e["source"] in reached | origins | contracts
        and e["target"] in reached and e["relation"] in
        ("predecessor_claim", "proposal_provenance_not_support", "conditioned_contract_provenance"))
    payload = dict(start_node=start, nodes=[context.nodes[n] for n in sorted(reached)],
        predecessor_contracts_not_sufficient_proof=[context.nodes[n] for n in sorted(contracts)],
        proposed_origins_not_support=[context.nodes[n] for n in sorted(origins)],
        claim_class="conditional", support_disposition="accepted_bounded_A_RG2b_research",
        profile_scope=["A_RG2b"], native_authority=False, domain_widening_inferred=False,
        verification_obligations_excluded=True, historical_controls_excluded=True,
        full_transitive_research_ancestry=True)
    n = context.nodes[start]
    return _trace(context, "reconstruction_path", {"claim_id": claim_id}, [_row(context,
        row_id=claim_id, classification="accepted_bounded_research_reconstruction", payload=payload,
        record_id=RECORD_ID, pointer=n["source_json_pointer"], edge_refs=edges)])


def debt_lifecycle(context, debt_id):
    """RG2b-local disposition; all four predecessor realization scopes stay separate."""
    key = "scoped_debt_transformation:A_RG2b:" + debt_id
    if key not in context.nodes:
        raise KeyError("unknown A_RG2b debt transformation: " + debt_id)
    n = context.nodes[key]
    return _trace(context, "debt_lifecycle", {"debt_id": debt_id, "profile_scope": "A_RG2b"}, [_row(context,
        row_id=debt_id, classification=n["attributes"]["transformation"], payload=n["attributes"],
        record_id=RECORD_ID, pointer=n["source_json_pointer"],
        edge_refs=_edges(context, lambda e:key in (e["source"], e["target"])))])


def candidate_a_closure(context):
    """Derive five bounded program closures, never universal/native support."""
    from . import atc_pc, atc_ci
    modules = (atc, atc_ci, atc_pc, predecessor)
    rosters = [(m.RECORD_ID, p) for m, p in zip(modules,
        ("A_OS", "A_CI", "A_PC", "A_CI_PC"), strict=True)] + [(RECORD_ID, "A_RG2b")]
    rows = []
    for record_id, profile in rosters:
        doc = context.documents_by_record[record_id]
        ledger = doc.data
        _require(ledger["status"] == "accepted_bounded_research_reconciliation"
            and len(ledger["debts"]) == 28
            and all(ledger[k] is False for k in ("native_authority", "ATC2_closed", "ATC3_closed"))
            and all(d["global_discharged"] is False for d in ledger["debts"])
            and all(c["status"] == "accepted_bounded_" + profile + "_research"
                and c["claim_class"] in ("conditional", "negative") for c in ledger["claims"]),
            "Candidate-A closeout does not have five bounded accepted ledgers")
        rows.append(_row(context, row_id=profile, classification="closed_bounded_research_program",
            payload=dict(profile_scope=[profile], research_program_closed=True,
                accepted_research_claims=len(ledger["claims"]),
                claim_classes={kind: sum(c["claim_class"] == kind for c in ledger["claims"])
                               for kind in ("conditional", "negative")},
                debt_statuses=ledger["classifications"], origin_debts_globally_closed=False,
                universal_realization_support=False, native_authority=False,
                ATC2_closed=False, ATC3_closed=False),
            record_id=record_id, pointer="/", edge_refs=[]))
    return _trace(context, "candidate_a_research_closure",
        {"profile_scope": [p for _, p in rosters]}, rows)

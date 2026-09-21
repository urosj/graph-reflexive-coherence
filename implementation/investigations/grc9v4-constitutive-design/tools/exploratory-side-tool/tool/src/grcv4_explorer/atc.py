"""Pinned, append-only bounded A_OS research admission, not native ATC support.

The initializer context remains the historical baseline. This explicit
successor admits research provenance without changing any older node or edge.
"""
from dataclasses import replace
from pathlib import Path

from .a_initializer import load_current_forensic_context as load_pre_atc_context
from .adapters import SourceDocument
from .canonical import digest, file_sha256, load_json_object, record_digest
from .errors import SourceAdmissionError
from .forensic import _row, _trace, _edges
from .forensic import debt_lifecycle, reconstruction_path as historical_reconstruction
from .successor import _Overlay, _source_node_id

INV = "implementation/investigations/grc9v4-constitutive-design"
EVIDENCE = INV + "/evidence/autonomous-topology-change"
LEDGER = EVIDENCE + "/ATCAOSClaimDebtLedger.json"
ADMISSION = "ATCAOSResearchAdmission.json"
RECORD_ID = "GRCV4-ATC-AOS-LEDGER-v1"
ADMISSION_DIGEST = "40f6a361c3a00ae629bc413a62688d6f1d13de0f6311772f188c5a164a953a4b"
STAGES = (
    "ATCSectorConstitutiveAdjudication.json",
    "ATCSectorReadBackPointAdjudication.json",
    "ATCSectorReadBackBoxAdjudication.json",
    "ATCSectorStateDomainAdjudication.json",
    "ATCSectorChannelsAdjudication.json",
    "ATCSectorReferenceAdjudication.json",
)


def _require(condition, message):
    if not condition:
        raise SourceAdmissionError(message)


def _path(root, relative):
    value = Path(relative)
    _require(not value.is_absolute() and ".." not in value.parts,
             "ATC source path must be repository-relative")
    path = root / value
    _require(path.resolve().is_relative_to(root.resolve()), "ATC source escaped repository")
    return path


def _inventory(root):
    return sorted(p.relative_to(root).as_posix()
                  for p in (root / EVIDENCE).rglob("*")
                  if p.is_file() and p.suffix in (".json", ".md", ".py")
                  and p.name != "README.md" and "__pycache__" not in p.parts)


def _pointer(value, pointer):
    if pointer in ("", "/"):
        return value
    for part in pointer.strip("/").split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value


def observe_sources(root, admission):
    """Observe the ATC inventory; never classify fresh source as authority."""
    expected = admission["evidence_files"]
    actual = _inventory(root)
    missing = sorted(set(expected) - set(actual))
    added = sorted(set(actual) - set(expected))
    changed = [path for path in actual if path in expected
               and file_sha256(_path(root, path)) != expected[path]]
    support_changed = [r["path"] for r in admission["support_files"]
                       if not _path(root, r["path"]).is_file()
                       or file_sha256(_path(root, r["path"])) != r["sha256"]]
    state = ("admitted_source_missing" if missing else
             "admitted_source_identity_changed" if changed or support_changed else
             "new_unprocessed_source_available" if added else "current_bundle_exact")
    result = dict(schema="grcv4_atc_source_observation_v1", state=state,
                  added_unprocessed=added, missing_admitted=missing,
                  changed_admitted=changed, changed_support=support_changed,
                  automatic_admission_allowed=False)
    result["observation_digest"] = digest(result)
    return result


def _validate_ledger(root, ledger):
    _require(ledger.get("schema") == "grcv4_atc_aos_claim_debt_ledger_v1"
             and ledger.get("record_id") == RECORD_ID
             and ledger.get("record_digest") == record_digest(ledger, "record_digest"),
             "ATC ledger identity/schema mismatch")
    _require(ledger.get("status") == "accepted_bounded_research_reconciliation"
             and ledger.get("A_OS_G1_G7_research_program_accepted") is True
             and all(ledger.get(k) is False for k in ("native_authority", "ATC2_closed", "ATC3_closed")),
             "ATC research ceiling widened")
    origin = load_json_object(root / EVIDENCE / "proposal_index.json")
    _require(ledger["origin_claims"] == origin["claims"], "ATC origin proposals changed")
    origin_claims = {c["id"]: c for c in origin["claims"]}
    origin_debts = {d["id"]: d for d in origin["debts"]}
    lhs = {(c["id"], e["debt_id"], e["relation"], e["activation"])
           for c in origin["claims"] for e in c["debt_edges"]}
    rhs = {(e["claim_id"], d["id"], e["relation"], e["activation"])
           for d in origin["debts"] for e in d["claim_edges"]}
    _require(len(origin_claims) == 35 and len(origin_debts) == 28 and len(lhs) == 165 and lhs == rhs,
             "ATC origin claim/debt reciprocity changed")
    stages = [load_json_object(root / EVIDENCE / n) for n in STAGES]
    expected_claims = {}
    for i, stage in enumerate(stages):
        _require(stage["record_digest"] == record_digest(stage, "record_digest")
                 and stage["scientific_acceptance"] is True, "ATC stage identity/acceptance changed")
        if i:
            _require(stage["predecessor_adjudication"] == stages[i-1]["record_digest"],
                     "ATC stage predecessor chain changed")
        _require(ledger["accepted_sequence"][i] == dict(
            source=EVIDENCE + "/" + STAGES[i], record_id=stage["record_id"], record_digest=stage["record_digest"]),
            "ATC stage roster changed")
        for c in stage["claims"]:
            _require(c["id"] not in expected_claims, "duplicate accepted ATC claim")
            expected_claims[c["id"]] = c
    claims = {c["claim_id"]: c for c in ledger["claims"]}
    debts = {d["debt_id"]: d for d in ledger["debts"]}
    _require(len(claims) == len(ledger["claims"]) == 36 and set(claims) == set(expected_claims),
             "ATC accepted claim roster changed")
    _require(len(debts) == len(ledger["debts"]) == 28 and set(debts) == set(origin_debts),
             "ATC debt roster changed")
    seen = set()
    for c in ledger["claims"]:
        cid = c["claim_id"]
        _require(c["source_claim"] == expected_claims[cid], "ATC source claim changed")
        _require(c["claim_class"] == ("negative" if cid == "ATC-LSF-G14-CL-05" else "conditional")
                 and c["status"] == "accepted_bounded_A_OS_research"
                 and c["profile_scope"] == ["A_OS"] and c["native_authority"] is False,
                 "ATC claim class/scope widened")
        _require(c["predecessor_claim_ids"] == expected_claims[cid].get("predecessor_claim_refs", [])
                 and set(c["predecessor_claim_ids"]) <= seen
                 and c["origin_claim_ids"] == expected_claims[cid].get("origin_claim_refs", [])
                 and set(c["origin_claim_ids"]) <= set(origin_claims), "ATC claim ancestry changed")
        for key in ("source_ref", "accepted_scope_ref"):
            ref = c[key]; path = _path(root, ref["path"])
            _require(file_sha256(path) == ref["sha256"], "ATC claim source drift")
            resolved = _pointer(load_json_object(path), ref["json_pointer"])
            if key == "source_ref":
                _require(resolved == c["source_claim"], "ATC claim pointer mismatch")
        seen.add(cid)
    for did, d in debts.items():
        old = origin_debts[did]
        _require(d["activation"] == old["activation"] and d["closure_requirement"] == old["closure_requirement"]
                 and d["origin_status"] == old["status"] and d["global_discharged"] is False
                 and d["blocks_G1_G7_research_acceptance"] is False,
                 "ATC origin debt meaning/ceiling changed")
        _require(d["A_OS_research_status"] in ("closed", "partial", "not_activated"), "unknown ATC debt disposition")
        for cid in d["successor_claim_ids"]:
            _require(cid in claims and did in claims[cid]["debt_ids"], "nonreciprocal ATC debt support")
    for cid, c in claims.items():
        for did in c["debt_ids"]:
            _require(did in debts and cid in debts[did]["successor_claim_ids"], "nonreciprocal ATC claim debt")
    _require(ledger["classifications"] == {s: sum(d["A_OS_research_status"] == s for d in debts.values())
        for s in ("closed", "partial", "not_activated")}, "ATC status summary mismatch")
    return claims, debts


def _build_context(root, side, admission):
    old = load_pre_atc_context(root, side)
    _require(admission["historical_graph_digest"] == old.graph_digest
             and admission["historical_authority_extension_digest"] == old.authority_extension_digest,
             "ATC historical authority mismatch")
    observation = observe_sources(root, admission)
    _require(observation["state"] == "current_bundle_exact", "ATC source set: " + observation["state"])
    ledger = load_json_object(root / LEDGER)
    _validate_ledger(root, ledger)
    # All retained scientific source bindings are checked; historical intake
    # repository_sources describe a past baseline, not a current-file assertion.
    for name in admission["evidence_files"]:
        if not name.endswith('.json'):
            continue
        data = load_json_object(root / name)
        if "record_digest" in data:
            _require(data["record_digest"] == record_digest(data, "record_digest"), "ATC evidence digest drift: " + name)
        for row in data.get("source_bindings", []):
            _require(file_sha256(_path(root, row["path"])) == row["sha256"], "ATC evidence binding drift: " + row["path"])
    row = dict(source_id=RECORD_ID, path=LEDGER, file_sha256=file_sha256(root / LEDGER))
    doc = SourceDocument(Path(LEDGER).name, root / LEDGER, ledger, row,
                         "atc_aos_research_v1", RECORD_ID, ledger["schema"], "record_digest", {})
    overlay = _Overlay(old.graph)
    source = _source_node_id(doc)
    overlay.add_node("source_record", source.split(":", 1)[1], doc, "/", row)
    def node(kind, identifier, pointer, attributes):
        result = overlay.add_node(kind, identifier, doc, pointer, attributes)
        overlay.add_edge(result, source, "source_identity", doc, pointer)
        return result
    for i, c in enumerate(ledger["origin_claims"]):
        node("proposal_claim", c["id"], f"/origin_claims/{i}", c)
    for i, c in enumerate(ledger["claims"]):
        node("current_claim", c["claim_id"], f"/claims/{i}", c)
    for i, d in enumerate(ledger["debts"]):
        node("debt_transformation", d["debt_id"], f"/debts/{i}", d)
    for i, v in enumerate(ledger["forward_obligations"]):
        node("verification_obligation", v["obligation_id"], f"/forward_obligations/{i}", v)
    for i, c in enumerate(ledger["claims"]):
        target = "current_claim:" + c["claim_id"]
        for j, ancestor in enumerate(c["predecessor_claim_ids"]):
            overlay.add_edge("current_claim:" + ancestor, target, "predecessor_claim", doc,
                             f"/claims/{i}/predecessor_claim_ids/{j}", support_semantic="conditioned",
                             attributes={"lineage_not_sufficient_proof": True})
        for j, origin in enumerate(c["origin_claim_ids"]):
            overlay.add_edge("proposal_claim:" + origin, target, "proposal_provenance_not_support", doc,
                             f"/claims/{i}/origin_claim_ids/{j}")
    for i, d in enumerate(ledger["debts"]):
        source_debt = "debt_transformation:" + d["debt_id"]
        for j, cid in enumerate(d["successor_claim_ids"]):
            overlay.add_edge(source_debt, "current_claim:" + cid, "scoped_debt_bearing", doc,
                             f"/debts/{i}/successor_claim_ids/{j}", support_semantic="conditioned")
        if d["verification_obligation"]:
            overlay.add_edge(source_debt, "verification_obligation:" + d["verification_obligation"],
                             "requires_verification_from", doc, f"/debts/{i}/verification_obligation")
    _require(all(e[k] in overlay.nodes for e in overlay.propagation_edges.values() for k in ("source", "target")),
             "ATC graph has unresolved endpoints")
    bundle = digest(dict(historical_source_bundle_digest=old.source_bundle_digest,
                         evidence_files=admission["evidence_files"], support_files=admission["support_files"]))
    graph = dict(schema="grcv4_atc_aos_research_graph_v1", historical_graph_digest=old.graph_digest,
                 source_bundle_digest=bundle, nodes=sorted(overlay.nodes.values(), key=lambda r:r["node_id"]),
                 propagation_edges=sorted(overlay.propagation_edges.values(), key=lambda r:r["edge_id"]),
                 annotation_edges=old.graph["annotation_edges"])
    graph["graph_digest"] = digest(graph)
    return replace(old, graph=graph, graph_digest=graph["graph_digest"], source_bundle_digest=bundle,
                   documents=(*old.documents, doc), documents_by_record={**old.documents_by_record, RECORD_ID:doc},
                   nodes=overlay.nodes, propagation_edges=tuple(graph["propagation_edges"]),
                   authority_extension_digest=admission.get("record_digest"))


def load_current_forensic_context(root, side):
    admission = load_json_object(side / "records" / ADMISSION)
    _require(admission.get("schema") == "grcv4_atc_aos_research_admission_v1"
             and admission.get("status") == "accepted_bounded_research_source_admission"
             and admission.get("record_digest") == record_digest(admission, "record_digest") == ADMISSION_DIGEST,
             "ATC admission is not pinned")
    context = _build_context(root, side, admission)
    _require(context.graph_digest == admission["graph_digest"], "ATC graph no longer rebuilds exactly")
    return context


def reconstruction_path(context, claim_id):
    """Full research ancestry; proposals and forward work never become proof."""
    proposal = "proposal_claim:" + claim_id
    if proposal in context.nodes:
        n = context.nodes[proposal]
        return _trace(context, "reconstruction_path", {"claim_id":claim_id}, [_row(context,
            row_id=claim_id, classification="proposed_origin_not_accepted",
            payload=n["attributes"], record_id=RECORD_ID, pointer=n["source_json_pointer"], edge_refs=[])])
    start = "current_claim:" + claim_id
    if start not in context.nodes or context.nodes[start]["source_record_id"] != RECORD_ID:
        return historical_reconstruction(context, claim_id)
    reached = {start}
    while True:
        predecessors = {e["source"] for e in context.propagation_edges
                        if e["target"] in reached and e["relation"] == "predecessor_claim"}
        if predecessors <= reached:
            break
        reached |= predecessors
    origins = {e["source"] for e in context.propagation_edges if e["target"] in reached
               and e["relation"] == "proposal_provenance_not_support"}
    edges = _edges(context, lambda e:e["source"] in reached | origins and e["target"] in reached
                   and e["relation"] in ("predecessor_claim", "proposal_provenance_not_support"))
    payload = dict(start_node=start, nodes=[context.nodes[n] for n in sorted(reached)],
                   proposed_origins_not_support=[context.nodes[n] for n in sorted(origins)],
                   verification_obligations_excluded=True, native_authority=False,
                   domain_widening_inferred=False, full_transitive_research_ancestry=True)
    n = context.nodes[start]
    return _trace(context, "reconstruction_path", {"claim_id":claim_id}, [_row(context,
        row_id=claim_id, classification="accepted_bounded_research_reconstruction", payload=payload,
        record_id=RECORD_ID, pointer=n["source_json_pointer"], edge_refs=edges)])

"""Append-only paired A_CI_PC research admission; never native ATC authority."""
from dataclasses import replace
from pathlib import Path

from . import atc, atc_ci as predecessor
from .adapters import SourceDocument
from .canonical import digest, file_sha256, load_json_object, record_digest
from .errors import SourceAdmissionError
from .forensic import _row, _trace, _edges
from .successor import _Overlay, _source_node_id

EVIDENCE = atc.INV + "/evidence/atc-cip"
SUCCESSOR = atc.INV + "/evidence/atc-cip-successor"
REVIEW = atc.INV + "/evidence/atc-cip-review"
ADMISSION_EVIDENCE = atc.INV + "/evidence/atc-cip-admission"
LEDGER = atc.INV + "/evidence/atc-cip-admission/ATCCIPClaimDebtLedger.json"
RECORD_ID = "GRCV4-ATC-CIP-LEDGER-v1"
ADMISSION = "ATCCIPResearchAdmission.json"
ADMISSION_DIGEST = "f98cb10a902dd11b6df76a36fae60aa23c55b648b8ddeee8df64b2b411c610cc"
CLAIMS = ("ATC-CIP-ROOT-00", "ATC-CIP-CHAIN-01", "ATC-CIP-REFERENCE-02")
INHERITED = ("ATC-CI-DOMAIN-02", "ATC-CI-REFERENCE-03",
             "ATC-PC-CARRIER-03", "ATC-PC-DOMAIN-04")
PARENTS = (list(INHERITED), [CLAIMS[0], INHERITED[0], INHERITED[2]],
           [CLAIMS[0], CLAIMS[1]])
_require, _path, _pointer = atc._require, atc._path, atc._pointer


def _inventory(root):
    return sorted([p.relative_to(root).as_posix()
        for directory in (EVIDENCE, SUCCESSOR, REVIEW, ADMISSION_EVIDENCE)
        for p in (root / directory).rglob("*") if p.is_file()
        and p.suffix in (".json", ".md", ".py") and p.name != "README.md"
        and "__pycache__" not in p.parts])


def observe_sources(root, admission):
    expected, actual = admission["evidence_files"], _inventory(root)
    missing = sorted(p for p in expected if not _path(root, p).is_file())
    added = sorted(set(actual) - set(expected))
    changed = sorted(p for p in expected if p not in missing
                     and file_sha256(_path(root, p)) != expected[p])
    # Read transitive bindings only from byte-exact admitted certificates.
    # Discovery must notice changed execution sources, not only changed outputs.
    bindings = list(admission["support_files"])
    for name in expected:
        if name.endswith(".json") and name not in missing and name not in changed:
            bindings.extend(load_json_object(_path(root, name)).get("source_bindings", []))
    support_changed = sorted({r["path"] for r in bindings
        if not _path(root, r["path"]).is_file()
        or file_sha256(_path(root, r["path"])) != r["sha256"]})
    state = ("admitted_source_missing" if missing else
             "admitted_source_identity_changed" if changed or support_changed else
             "new_unprocessed_source_available" if added else "current_bundle_exact")
    value = dict(schema="grcv4_atc_cip_source_observation_v1", state=state,
        missing_admitted=missing, added_unprocessed=added, changed_admitted=changed,
        changed_support=support_changed, automatic_admission_allowed=False)
    value["observation_digest"] = digest(value)
    return value


def _checked_ref(root, ref):
    path = _path(root, ref["path"])
    _require(path.is_file(), "CIP source reference missing")
    _require(file_sha256(path) == ref["sha256"], "CIP source reference drift")
    if path.suffix == ".json":
        try:
            return _pointer(load_json_object(path), ref["json_pointer"])
        except (KeyError, IndexError, ValueError, TypeError) as exc:
            raise SourceAdmissionError("CIP source pointer does not resolve") from exc
    _require(ref["json_pointer"] == "/", "non-JSON CIP pointer")


def _validate_ledger(root, ledger):
    _require(ledger.get("schema") == "grcv4_atc_cip_claim_debt_ledger_v1"
        and ledger.get("record_id") == RECORD_ID
        and ledger.get("record_digest") == record_digest(ledger, "record_digest"),
        "CIP ledger identity/schema mismatch")
    _require(ledger.get("status") == "accepted_bounded_research_reconciliation"
        and ledger.get("profile_scope") == ["A_CI_PC"]
        and all(ledger.get(k) is False for k in ("native_authority", "ATC2_closed", "ATC3_closed")),
        "CIP research ceiling widened")
    origin = _checked_ref(root, ledger["origin_ref"])
    _checked_ref(root, ledger["accepted_scope_ref"])
    contract = _checked_ref(root, ledger["contract_ref"])
    _require(contract["realization"] == "CI+PC"
        and contract["whole_box_formation"] is False
        and contract["raw_result_promotion"] is False
        and contract["native_authority"] is False, "CIP selected contract changed")
    for ref in ledger["review_refs"]:
        _checked_ref(root, ref)
    claims = {c["claim_id"]: c for c in ledger["claims"]}
    debts = {d["origin_debt_id"]: d for d in ledger["debts"]}
    _require(tuple(c["claim_id"] for c in ledger["claims"]) == CLAIMS,
             "CIP accepted claim roster changed")
    _require(len(debts) == len(ledger["debts"]) == 28
        and set(debts) == {d["id"] for d in origin["debts"]}, "CIP debt roster changed")
    review = ledger["review_disposition"]
    _require(review == dict(scientific_core="independent_PASS",
        retained_record_integrity="local_PASS",
        independent_retained_record_comparison="not_supplied_not_claimed"),
        "CIP review evidence class widened")
    correction = _checked_ref(root, ledger["db04_correction_ref"])
    _require(correction["claim_id"] == CLAIMS[0]
        and correction["additional_debt_ref"] == "ATC7-DB-04"
        and correction["successor_claim_id"] == CLAIMS[1]
        and "ATC7-DB-04" in claims[CLAIMS[0]]["debt_ids"],
        "CIP additive DB-04 route lost")
    seen = set(INHERITED)
    parents = PARENTS
    for c in ledger["claims"]:
        _require(c["claim_class"] == "conditional" and c["profile_scope"] == ["A_CI_PC"]
            and c["native_authority"] is False and c["status"] == "accepted_bounded_A_CI_PC_research",
            "CIP claim class/scope widened")
        row = _checked_ref(root, c["source_ref"])
        _require(isinstance(row, dict) and row.get("claim_id") == c["claim_id"]
            and row.get("profile_scope") == ["A_CI_PC"],
            "CIP claim pointer mismatch")
        if "predecessor_handles" in row:
            _require(c["predecessor_claim_ids"] == row["predecessor_handles"],
                     "CIP reviewed predecessor routing changed")
        _require(set(c["predecessor_claim_ids"]) <= seen
            and c["predecessor_claim_ids"] == parents[CLAIMS.index(c["claim_id"])]
            and set(c["origin_claim_ids"]) <= {o["id"] for o in origin["claims"]},
            "CIP claim ancestry changed")
        _require(set(row.get("debt_refs", [])) <= set(c["debt_ids"]), "CIP source debt routing dropped")
        _require(len(c["debt_ids"]) == len(set(c["debt_ids"])), "duplicate CIP debt edge")
        seen.add(c["claim_id"])
        for did in c["debt_ids"]:
            _require(did in debts and c["claim_id"] in debts[did]["successor_claim_ids"],
                     "CIP claim/debt reciprocity changed")
    for d in debts.values():
        old = _checked_ref(root, d["origin_ref"])
        _require(old["id"] == d["origin_debt_id"]
            and old["status"] == d["origin_status"]
            and all(old[k] == d[k] for k in ("activation", "closure_requirement", "title"))
            and d["global_discharged"] is False and d["blocks_paired_research_acceptance"] is False,
            "CIP origin debt meaning/ceiling changed")
        _require(d["A_CI_PC_research_status"] in ("closed", "partial", "not_activated")
            and d["transformation"] == "scoped_" + d["A_CI_PC_research_status"]
            and d["admission_evidence"] == (d["origin_debt_id"] == "ATC7-DB-24"),
            "CIP debt disposition changed")
        _require(len(d["successor_claim_ids"]) == len(set(d["successor_claim_ids"])),
                 "duplicate CIP claim edge")
        for cid in d["successor_claim_ids"]:
            _require(cid in claims and d["origin_debt_id"] in claims[cid]["debt_ids"],
                     "CIP debt/claim reciprocity changed")
    _require(ledger["classifications"] == {s: sum(d["A_CI_PC_research_status"] == s for d in debts.values())
        for s in ("closed", "partial", "not_activated")}, "CIP debt counts changed")
    closed = {2,3,4,5,6,7,8,14,15,16,19,21,24,28}
    partial = {1,10,12,13,23,26}
    for number in range(1,29):
        expected = "closed" if number in closed else "partial" if number in partial else "not_activated"
        _require(debts[f"ATC7-DB-{number:02d}"]["A_CI_PC_research_status"] == expected,
                 "CIP approved debt disposition changed")
    _require(ledger["unaccepted_handles"] == [] and ledger["historical_controls"] == [],
             "CIP admission has unexpected controls or pending admitted handles")


def _build_context(root, side, admission):
    old = predecessor.load_current_forensic_context(root, side)
    _require(admission["historical_graph_digest"] == old.graph_digest
        and admission["historical_authority_extension_digest"] == old.authority_extension_digest,
        "CIP historical authority changed")
    observation = observe_sources(root, admission)
    _require(observation["state"] == "current_bundle_exact", "CIP source set: " + observation["state"])
    ledger = load_json_object(root / LEDGER)
    _validate_ledger(root, ledger)
    for name in admission["evidence_files"]:
        if not name.endswith(".json"):
            continue
        data = load_json_object(root / name)
        if "record_digest" in data:
            _require(data["record_digest"] == record_digest(data, "record_digest"), "CIP evidence digest drift")
        for ref in data.get("source_bindings", []):
            _require(file_sha256(_path(root, ref["path"])) == ref["sha256"],
                     "CIP evidence binding drift: " + ref["path"])
    row = dict(source_id=RECORD_ID, path=LEDGER, file_sha256=file_sha256(root / LEDGER))
    doc = SourceDocument(Path(LEDGER).name, root / LEDGER, ledger, row,
                         "atc_cip_research_v1", RECORD_ID, ledger["schema"], "record_digest", {})
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
        for j, cid in enumerate(c["origin_claim_ids"]):
            overlay.add_edge("proposal_claim:" + cid, target, "proposal_provenance_not_support", doc,
                             f"/claims/{i}/origin_claim_ids/{j}")
    for i, c in enumerate(ledger["historical_controls"]):
        node("historical_control", c["claim_id"], f"/historical_controls/{i}", c)
    for i, d in enumerate(ledger["debts"]):
        key = node("scoped_debt_transformation", "A_CI_PC:" + d["origin_debt_id"], f"/debts/{i}", d)
        overlay.add_edge("debt_transformation:" + d["origin_debt_id"], key,
            "parallel_scope_not_global_discharge", doc, f"/debts/{i}/origin_debt_id")
        for j, cid in enumerate(d["successor_claim_ids"]):
            overlay.add_edge(key, "current_claim:" + cid, "scoped_debt_bearing", doc,
                f"/debts/{i}/successor_claim_ids/{j}", support_semantic="conditioned")
        if d["admission_evidence"]:
            overlay.add_edge(key, source, "scoped_source_admission", doc, f"/debts/{i}/admission_evidence")
    _require(all(e[k] in overlay.nodes for e in overlay.propagation_edges.values() for k in ("source", "target")),
             "CIP graph has unresolved endpoints")
    bundle = digest(dict(historical_source_bundle_digest=old.source_bundle_digest,
        evidence_files=admission["evidence_files"], support_files=admission["support_files"]))
    graph = dict(schema="grcv4_atc_cip_research_graph_v1", historical_graph_digest=old.graph_digest,
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
    _require(value.get("schema") == "grcv4_atc_cip_research_admission_v1"
        and value.get("status") == "accepted_bounded_research_source_admission"
        and value.get("record_digest") == record_digest(value, "record_digest") == ADMISSION_DIGEST,
        "CIP admission is not pinned")
    return value


def load_current_forensic_context(root, side):
    admission = pinned_admission(side)
    context = _build_context(root, side, admission)
    _require(context.graph_digest == admission["graph_digest"], "CIP graph no longer rebuilds exactly")
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
    edges = _edges(context, lambda e:e["source"] in reached | origins and e["target"] in reached
        and e["relation"] in ("predecessor_claim", "proposal_provenance_not_support"))
    payload = dict(start_node=start, nodes=[context.nodes[n] for n in sorted(reached)],
        proposed_origins_not_support=[context.nodes[n] for n in sorted(origins)],
        claim_class="conditional", support_disposition="accepted_bounded_A_CI_PC_research",
        profile_scope=["A_CI_PC"], native_authority=False, domain_widening_inferred=False,
        verification_obligations_excluded=True, historical_controls_excluded=True,
        full_transitive_research_ancestry=True)
    n = context.nodes[start]
    return _trace(context, "reconstruction_path", {"claim_id": claim_id}, [_row(context,
        row_id=claim_id, classification="accepted_bounded_research_reconstruction", payload=payload,
        record_id=RECORD_ID, pointer=n["source_json_pointer"], edge_refs=edges)])


def debt_lifecycle(context, debt_id):
    """CIP-local disposition; original, A_OS, A_PC and A_CI stay separate."""
    key = "scoped_debt_transformation:A_CI_PC:" + debt_id
    if key not in context.nodes:
        raise KeyError("unknown A_CI_PC debt transformation: " + debt_id)
    n = context.nodes[key]
    return _trace(context, "debt_lifecycle", {"debt_id": debt_id, "profile_scope": "A_CI_PC"}, [_row(context,
        row_id=debt_id, classification=n["attributes"]["transformation"], payload=n["attributes"],
        record_id=RECORD_ID, pointer=n["source_json_pointer"],
        edge_refs=_edges(context, lambda e:key in (e["source"], e["target"])))])

"""Explicit native successor to the scientific spark claim/debt ledgers.

Historical forensic contexts keep their research-time pending obligations.
This read-only projection joins accepted research to accepted native execution;
it does not turn execution evidence into scientific authority.
"""

import sys
import json
from hashlib import sha256
from pathlib import Path
from .canonical import digest

LEDGER_DIGEST = '898de5b74437de073d901bbca798cf52bc3ca065603c528c462ac1e9b31601d4'

ACCEPTANCE_PATH = 'implementation/phase-9-grcv4/tranche-10/P9-10.5-NativeSpark-Acceptance.json'
ACCEPTANCE_DIGEST = '200d76d49e14b380f2316c7c78ee7b699fc2c4a888a46215aa0b1474120ae4ca'


def accepted_decision(value, ledger):
    body = {k: v for k, v in value.items() if k != "record_digest"}
    if (value.get("record_digest") != digest(body)
            or value["record_digest"] != ACCEPTANCE_DIGEST
            or value["ledger_record_digest"] != ledger["record_digest"]
            or value["families"] != [r["family"] for r in ledger["families"]]
            or value["counts"] != ledger["counts"]):
        raise ValueError("changed native debt acceptance")
    return value


def checker(root):
    root = Path(root).resolve()
    sys.path.insert(0, str(root / "implementation/phase-9-grcv4/verification"))
    import p9105_native_spark_debts as c

    if c.ROOT != root:
        raise ValueError("native debt checkout mismatch")
    return c


def native_spark_debts(root):
    c = checker(root)
    value = c.checked(root)
    if value["record_digest"] != LEDGER_DIGEST:
        raise ValueError("unbound native debt reconciliation")
    acceptance = accepted_decision(json.loads((Path(root) / ACCEPTANCE_PATH).read_bytes()), value)
    if sha256((Path(root) / c.LEDGER).read_bytes()).hexdigest() != acceptance["ledger_sha256"]:
        raise ValueError("accepted native debt ledger bytes changed")
    body = dict(
        schema="native-spark-debt-view-v1",
        status=acceptance["status"], user_accepted=acceptance["user_accepted"],
        acceptance=dict(path=ACCEPTANCE_PATH, **acceptance),
        ledger=value,
        check_mode="retained_identity_and_disposition_checks_no_numerical_rerun",
        ledger_url="/api/native-spark/debts/source?name=ledger",
        decision_url="/api/native-spark/debts/source?name=decision",
    )
    return dict(body, projection_digest=digest(body))


def query(view, kind, identifier):
    """Closed typed lookups on one checked view, with source and native ceilings."""
    fields = {
        "debt_lifecycle": ("debts", "debt_id"),
        "verification_obligation": ("verification_obligations", "obligation_id"),
        "scientific_claim": ("scientific_claims", "claim_id"),
    }
    collection, key = fields[kind]
    ledger = view["ledger"]
    rows = [row for row in ledger[collection] if row[key] == identifier]
    if len(rows) != 1:
        raise KeyError("unknown or ambiguous " + kind + ": " + identifier)
    row = rows[0]
    families = row.get("evidence_families", [row["family"]] if "family" in row else [])
    body = dict(
        query=kind,
        identifier=identifier,
        row=row,
        evidence=[r for r in ledger["families"] if r["family"] in families],
        ledger_digest=ledger["record_digest"],
        reconciliation_status=view.get("status", ledger["status"]),
        acceptance_record_digest=view.get("acceptance", {}).get("record_digest"),
        scope=ledger["scope"],
        support_disposition="bounded_native_conformance_not_new_scientific_authority",
        source_ref=row.get("source_ref", row.get("predecessor")),
        residual_obligations=[
            r
            for r in ledger["residual_obligations"]
            if r["obligation_id"] in row.get("residual_obligation_ids", [])
        ],
    )
    return dict(body, trace_digest=digest(body))


def debt_lifecycle(root, debt_id):
    return query(native_spark_debts(root), "debt_lifecycle", debt_id)


def verification_obligation(root, obligation_id):
    return query(native_spark_debts(root), "verification_obligation", obligation_id)


def scientific_claim(root, claim_id):
    return query(native_spark_debts(root), "scientific_claim", claim_id)


def native_spark_debt_source(root, name):
    c = checker(root)
    path = {"ledger": c.LEDGER, "decision": c.DECISION, "acceptance": ACCEPTANCE_PATH}[name]
    native_spark_debts(root)
    return (Path(root) / path).read_bytes()

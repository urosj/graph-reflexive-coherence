"""Check accepted family authority, propagation and research reconciliation only."""
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[4]
INV = "implementation/investigations/grc9v4-constitutive-design/"
SIDE = ROOT / INV / "tools/exploratory-side-tool"
sys.path.insert(0, str(SIDE / "tool/src"))
from grcv4_explorer import spark_applicability as sc
from grcv4_explorer.canonical import load_json_object, record_digest

RECONCILIATION = "implementation/phase-9-grcv4/tranche-10/P9-10.5-10.6-SparkCCIReconciliation.json"
LEDGER = INV + "evidence/spark-completion/applicability/ClaimDebtLedger.json"


def check():
    view = sc.spark_applicability_authority(ROOT, SIDE)
    authority = load_json_object(ROOT / sc.SOURCE)
    manifest = sc.checked_manifest(ROOT)
    for row in manifest["chain"]:
        if row["stage"] in ("proposal", "paper", "specification"):
            text = (ROOT / row["path"]).read_text()
            sc.need(all(c in text for c in manifest["contract_ids"]), "propagation omitted a contract")
    ledger = load_json_object(ROOT / LEDGER)
    sc.need(ledger["record_digest"] == record_digest(ledger, "record_digest"), "research ledger digest")
    sc.need(ledger["families"] == authority["family_dispositions"], "family disposition drift")
    sc.need([r["claim_id"] for r in ledger["claims"]] == [r["claim_id"] for r in authority["claims"]]
        and all(r["claim_class"] == "conditional_mathematical" and
                r["status"] == "accepted_bounded_scientific" for r in ledger["claims"]), "claim promotion drift")
    sc.need(ledger["debts"][0]["status"] == "resolved_bounded_scientific" and
        all(r["status"] == "open" for r in ledger["debts"][1:]), "research debt scope changed")
    for row in ledger["evidence_sources"]:
        sc._bound_file(ROOT, row["path"], row["sha256"])
    value = load_json_object(ROOT / RECONCILIATION)
    sc.need(value["record_digest"] == record_digest(value, "record_digest"), "reconciliation digest")
    sc.need(value["scope"] == dict(SC3_closed_for=["C_CI"],
        scientific_families=["C_OS", "C_CI"], research_reconciliation_complete=True,
        P9_10_5_aggregate_closed=False, P9_10_6_closed=False, native_completed_spark_support=False,
        hierarchy_support=False, G4_accepted=False), "research/native/aggregate scope changed")
    sc.need(value["authority_record_digest"] == sc.SOURCE_DIGEST and
        value["debt_ids"] == [r["debt_id"] for r in authority["debts"]] and
        value["forward_obligation_ids"] == [r["obligation_id"] for r in authority["verification_obligations"]]
        and value["next_research_family"] == "C_PC" and value["native_destination"] == "P9-9.1a",
        "lost debt or forward routing")
    expected = {sc.SOURCE, sc.MANIFEST, LEDGER,
        RECONCILIATION.replace(".json", ".md")}
    sc.need({r["path"] for r in value["sources"]} == expected, "reconciliation source coverage")
    for row in value["sources"]:
        sc._bound_file(ROOT, row["path"], row["sha256"])
    return dict(status="passed_family_sc3_adjudication_propagation_reconciliation",
        scientific_families=view["scope"]["scientific_families"], new_claims=len(view["claims"]),
        new_contracts=len(view["contracts"]), resolved_research_debts=len(view["debts"]),
        native_steps=0, trajectory_reruns=0, projection_digest=view["projection_digest"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", required=True)
    parser.parse_args()
    print(json.dumps(check(), indent=2))

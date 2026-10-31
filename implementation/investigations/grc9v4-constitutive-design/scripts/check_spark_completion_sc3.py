"""Check SC-3 authority/propagation and research reconciliation; no trajectory rerun."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
INV = "implementation/investigations/grc9v4-constitutive-design/"
SIDE = ROOT / INV / "tools/exploratory-side-tool"
sys.path.insert(0, str(SIDE / "tool/src"))
from grcv4_explorer import spark_completion as sc
from grcv4_explorer.canonical import file_sha256, record_digest

RECONCILIATION = "implementation/phase-9-grcv4/tranche-10/P9-10.5-10.6-SparkResearchReconciliation.json"


def check():
    view = sc.spark_completion_authority(ROOT, SIDE)
    authority = json.loads((ROOT / sc.SOURCE).read_bytes())
    manifest = sc.checked_manifest(ROOT)
    sc.need(manifest["authority_record_digest"] == authority["record_digest"], "wrong propagation authority")
    contracts = [r["equation_contract_id"] for r in authority["contracts"]]
    sc.need(contracts == manifest["contract_ids"], "missing propagated contract")
    decision = (ROOT / authority["design_path"]).read_text()
    for row in authority["contracts"]:
        body = decision.split(row["design_section"]+"\n",1)[1].split("\n## ",1)[0].strip()
        sc.need(row["normative_equation_or_contract"] == body, "contract differs from decision")
    for row in manifest["chain"]:
        if row["stage"] in ("proposal","paper","specification"):
            text = (ROOT / row["path"]).read_text()
            sc.need(all(c in text for c in contracts), "propagation omitted a contract")
    value = json.loads((ROOT / RECONCILIATION).read_bytes())
    sc.need(value["record_digest"] == record_digest(value,"record_digest"), "reconciliation digest mismatch")
    sc.need(value["scope"] == dict(SC1_closed=True,SC2_closed=True,SC3_closed=True,
        research_reconciliation_complete=True,P9_10_5_aggregate_closed=False,P9_10_6_closed=False,
        native_completed_spark_support=False,hierarchy_support=False,G4_accepted=False),
        "research/native or aggregate scope changed")
    sc.need(value["authority_record_digest"] == authority["record_digest"] and
        value["debt_ids"] == [r["debt_id"] for r in authority["debts"]] and
        value["forward_obligation_ids"] == [r["obligation_id"] for r in authority["verification_obligations"]]
        and value["next_implementation_task"] == "P9-9.1a", "lost debt/forward routing")
    for row in value["sources"]:
        sc._bound_file(ROOT,row["path"],row["sha256"])
    return dict(status="passed_scientific_authority_propagation_reconciliation",
        claims=len(view["claims"]),contracts=len(view["contracts"]),debts=len(view["debts"]),
        native_steps=0,trajectory_reruns=0,projection_digest=view["projection_digest"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check",action="store_true",required=True)
    parser.parse_args()
    print(json.dumps(check(),indent=2))

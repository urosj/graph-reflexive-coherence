"""Accepted C_PC authority, propagation and research reconciliation; no trajectories."""
from pathlib import Path
import argparse
import json
import sys

ROOT=Path(__file__).resolve().parents[4]
INV='implementation/investigations/grc9v4-constitutive-design/'
SIDE=ROOT/INV/'tools/exploratory-side-tool'
sys.path.insert(0,str(SIDE/'tool/src'))
from grcv4_explorer import spark_pc as pc
from grcv4_explorer.canonical import load_json_object,record_digest

LEDGER=INV+'evidence/spark-completion/applicability/CPCClaimDebtLedger.json'
RECONCILIATION='implementation/phase-9-grcv4/tranche-10/P9-10.5-10.6-SparkCPCReconciliation.json'


def check():
    view=pc.spark_pc_authority(ROOT,SIDE)
    authority=load_json_object(ROOT/pc.SOURCE);manifest=pc.checked_manifest(ROOT)
    for row in manifest['chain']:
        if row['stage'] in ('proposal','paper','specification'):
            text=(ROOT/row['path']).read_text()
            pc.need(all(k in text for k in manifest['contract_ids']),'propagation omitted a contract')
    ledger=load_json_object(ROOT/LEDGER)
    pc.need(ledger['record_digest']==record_digest(ledger,'record_digest'),'ledger digest')
    pc.need(ledger['families']==authority['family_dispositions'],'family disposition drift')
    pc.need([r['family'] for r in ledger['families'] if r['status']=='accepted_bounded_scientific']==['C_OS','C_CI','C_PC'],
            'scientific family widening')
    pc.need([r['debt_id'] for r in ledger['debts'] if r['status']=='resolved_bounded_scientific']==
            ['SC-APP-DEBT-C_CI','SC-APP-DEBT-C_PC'],'debt scope')
    claims={r['claim_id']:r for r in ledger['claims']}
    for row in authority['claims']:
        pc.need({k:v for k,v in claims[row['claim_id']].items() if k!='source_ref'}==row,'adjudicated claim drift')
    for ref in ledger['evidence_sources']:pc._bound_file(ROOT,ref['path'],ref['sha256'])
    value=load_json_object(ROOT/RECONCILIATION)
    pc.need(value['record_digest']==record_digest(value,'record_digest'),'reconciliation digest')
    pc.need(value['scope']==dict(SC3_closed_for=['C_PC'],scientific_families=['C_OS','C_CI','C_PC'],
        research_reconciliation_complete=True,P9_10_5_aggregate_closed=False,P9_10_6_closed=False,
        native_completed_spark_support=False,hierarchy_support=False,G4_accepted=False),'research/native scope')
    pc.need(value['authority_record_digest']==pc.SOURCE_DIGEST and
        value['debt_ids']==[r['debt_id'] for r in authority['debts']] and
        value['forward_obligation_ids']==[r['obligation_id'] for r in authority['verification_obligations']] and
        value['next_research_family']=='C_CI_PC' and value['native_destination']=='P9-9.1a','forward routing')
    for ref in value['sources']:pc._bound_file(ROOT,ref['path'],ref['sha256'])
    expected={pc.SOURCE,pc.MANIFEST,LEDGER,RECONCILIATION.replace('.json','.md')}
    pc.need({r['path'] for r in value['sources']}==expected,'reconciliation source coverage')
    return dict(status='passed_cpc_sc3_adjudication_propagation_reconciliation',
        scientific_families=view['scope']['scientific_families'],new_conditional_claims=len(view['claims']),
        new_contracts=len(view['contracts']),resolved_research_debts=len(view['debts']),
        native_steps=0,trajectory_reruns=0,repository_boundary_audit='preexisting_failure_preserved',
        projection_digest=view['projection_digest'])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true',required=True)
    p.parse_args();print(json.dumps(check(),indent=2))

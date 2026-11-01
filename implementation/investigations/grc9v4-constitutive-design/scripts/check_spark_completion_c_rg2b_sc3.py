"""Accepted C_RG2b authority, propagation and research reconciliation; no trajectories."""
from pathlib import Path
import argparse
import json
import sys

ROOT=Path(__file__).resolve().parents[4]
INV='implementation/investigations/grc9v4-constitutive-design/'
SIDE=ROOT/INV/'tools/exploratory-side-tool'
sys.path.insert(0,str(SIDE/'tool/src'))
from grcv4_explorer import spark_crg2b as pc
from grcv4_explorer.canonical import load_json_object,record_digest

LEDGER=INV+'evidence/spark-completion/applicability/CRG2bClaimDebtLedger.json'
RECONCILIATION='implementation/phase-9-grcv4/tranche-10/P9-10.5-10.6-SparkCRG2bReconciliation.json'


def check():
    view=pc.spark_crg2b_authority(ROOT,SIDE)
    authority=load_json_object(ROOT/pc.SOURCE);manifest=pc.checked_manifest(ROOT)
    acceptance=load_json_object(ROOT/authority['acceptance']['path'])
    original=load_json_object(ROOT/(INV+'evidence/spark-completion/applicability/CRG2bResearchProgress.json'))
    selected=original['direct']
    pc.need(acceptance['selected_proof']=='direct_continuous_domain' and
        acceptance['selected_certificate_digest']==selected['certificate_digest'] and
        acceptance['supporting_trajectory_steps_after_completion']==0 and
        acceptance['execution_record_digests']==selected['execution_digests'] and
        acceptance['scientific_result']==selected['decisions'] and
        selected['entry']==390 and selected['completion']==selected['last_executed_step']==392 and
        selected['ordinary_duration']=='8' and selected['proof']['relative_dimension']==14 and
        selected['proof']['trajectory_inputs_to_domain_checker']==0 and
        not selected['proof']['section_C1_claimed'] and
        not original['accepted_authority'] and not selected['accepted_authority'],
        'accepted direct subject or original execution flags changed')
    for row in manifest['chain']:
        if row['stage'] in ('proposal','paper','specification'):
            text=(ROOT/row['path']).read_text()
            pc.need(all(k in text for k in manifest['contract_ids']),'propagation omitted a contract')
            for contract in authority['contracts']:
                body=text.split(contract['design_section']+'\n',1)[1].split('\n## ',1)[0].strip()
                pc.need(body==contract['normative_equation_or_contract'],'propagation changed a contract')
    ledger=load_json_object(ROOT/LEDGER)
    pc.need(ledger['record_digest']==record_digest(ledger,'record_digest'),'ledger digest')
    pc.need(ledger['families']==authority['family_dispositions'],'family disposition drift')
    pc.need([r['family'] for r in ledger['families'] if r['status']=='accepted_bounded_scientific']==['C_OS','C_CI','C_PC','C_CI_PC','A_OS','A_CI','A_PC','A_CI_PC','C_RG2b'],
            'scientific family widening')
    pc.need([r['debt_id'] for r in ledger['debts'] if r['status']=='resolved_bounded_scientific']==
            ['SC-APP-DEBT-C_CI','SC-APP-DEBT-C_PC','SC-APP-DEBT-C_CI_PC','SC-APP-DEBT-A_OS','SC-APP-DEBT-A_CI','SC-APP-DEBT-A_PC','SC-APP-DEBT-A_CI_PC','SC-APP-DEBT-C_RG2b'],'debt scope')
    claims={r['claim_id']:r for r in ledger['claims']}
    for row in authority['claims']:
        pc.need({k:v for k,v in claims[row['claim_id']].items() if k!='source_ref'}==row,'adjudicated claim drift')
    for ref in ledger['evidence_sources']:pc.reviewed_source_bytes(ROOT,ref['path'],ref['sha256'])
    value=load_json_object(ROOT/RECONCILIATION)
    pc.need(value['record_digest']==record_digest(value,'record_digest'),'reconciliation digest')
    pc.need(value['scope']==dict(SC3_closed_for=['C_RG2b'],scientific_families=['C_OS','C_CI','C_PC','C_CI_PC','A_OS','A_CI','A_PC','A_CI_PC','C_RG2b'],
        research_reconciliation_complete=True,P9_10_5_aggregate_closed=False,P9_10_6_closed=False,
        native_completed_spark_support=False,hierarchy_support=False,G4_accepted=False),'research/native scope')
    pc.need(value['authority_record_digest']==pc.SOURCE_DIGEST and
        value['debt_ids']==[r['debt_id'] for r in authority['debts']] and
        value['forward_obligation_ids']==[r['obligation_id'] for r in authority['verification_obligations']] and
        value['next_research_family']=='A_RG2b' and value['native_destination']=='P9-9.1a','forward routing')
    for ref in value['sources']:pc._bound_file(ROOT,ref['path'],ref['sha256'])
    expected={pc.SOURCE,pc.MANIFEST,LEDGER,RECONCILIATION.replace('.json','.md')}
    pc.need({r['path'] for r in value['sources']}==expected,'reconciliation source coverage')
    return dict(status='passed_crg2b_sc3_adjudication_propagation_reconciliation',
        scientific_families=view['scope']['scientific_families'],new_conditional_claims=len(view['claims']),
        new_contracts=len(view['contracts']),resolved_research_debts=len(view['debts']),
        native_steps=0,trajectory_reruns=0,repository_boundary_audit='preexisting_failure_preserved',
        entry=390,completion=392,last_executed_step=392,supporting_trajectory_steps_after_completion=0,
        projection_digest=view['projection_digest'])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true',required=True)
    p.parse_args();print(json.dumps(check(),indent=2))

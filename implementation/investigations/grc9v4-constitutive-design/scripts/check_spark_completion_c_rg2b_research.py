"""C_RG2b retained-source and inspection check, without numerical execution."""
from pathlib import Path
import argparse,json,sys
ROOT=Path(__file__).resolve().parents[4];INV='implementation/investigations/grc9v4-constitutive-design/'
SIDE=ROOT/INV/'tools/exploratory-side-tool'
sys.path.insert(0,str(SIDE/'tool/src'))
from grcv4_explorer.spark_crg2b_research import spark_crg2b_research_status,need
from grcv4_explorer.canonical import load_json_object,record_digest


def check():
    view=spark_crg2b_research_status(ROOT,SIDE);r=view['report']
    checks=load_json_object(ROOT/(INV+'evidence/spark-completion/applicability/CRG2bChecks.json'))
    need(checks['record_digest']==record_digest(checks,'record_digest')==r['historical_checks_record_digest'],'historical check identity')
    need(checks['rejected_controls']==r['verification']['historical_rejected_controls'] and len(checks['rejected_controls'])==25 and
         checks['replay']==dict(new_gain=0,mutation=False),'historical control/replay accounting')
    historical_count=sum(c['retained_states'] for c in checks['checks'].values())
    need(historical_count==r['verification']['historical_checked_states'] and
         all(c['transition_checks']==c['retained_states'] for c in checks['checks'].values()),'historical transition coverage')
    selected=load_json_object(ROOT/(INV+'evidence/spark-completion/applicability/CRG2bDirectChecks.json'))
    need(selected['record_digest']==record_digest(selected,'record_digest')==r['direct']['checks_digest'] and
         selected['status']=='passed' and selected['replay']['complete_fresh_trajectory_replays']==2,
         'selected C_RG2b verification record')
    count=selected['replay']['retained_states']
    need(count==r['verification']['retained_states']==r['direct']['retained_states']==784,'selected state coverage')
    return dict(status='passed_crg2b_research_integrity',family='C_RG2b',scientific_status=r['status'],
        accepted_families=r['accepted_scientific_families'],retained_states=count,
        historical_summary_states=historical_count,historical_finite_union_states=4178,
        last_executed_step=392,supporting_trajectory_steps_after_completion=0,
        historical_payloads_rechecked=False,full_state_dimension=14,
        numerical_steps=0,trajectory_reruns=0,projection_digest=view['projection_digest'])



if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true',required=True);p.parse_args()
    print(json.dumps(check(),indent=2))

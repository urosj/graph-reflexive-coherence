"""A_CI_PC retained-source and inspection check, without numerical execution."""
from pathlib import Path
import argparse,json,sys
ROOT=Path(__file__).resolve().parents[4];INV='implementation/investigations/grc9v4-constitutive-design/'
SIDE=ROOT/INV/'tools/exploratory-side-tool'
sys.path.insert(0,str(SIDE/'tool/src'))
from grcv4_explorer.spark_acipc_research import spark_acipc_research_status,need
from grcv4_explorer.canonical import load_json_object,record_digest


def check():
    view=spark_acipc_research_status(ROOT,SIDE);r=view['report']
    checks=load_json_object(ROOT/(INV+'evidence/spark-completion/applicability/ACIPCChecks.json'))
    need(checks['record_digest']==record_digest(checks,'record_digest')==r['checks_record_digest'],'retained check identity')
    need(checks['rejected_controls']==r['verification']['rejected_controls'] and len(checks['rejected_controls'])==27 and
         checks['replay']==dict(new_gain=0,mutation=False),'control/replay accounting')
    count=sum(c['retained_states'] for c in checks['checks'].values())
    need(count==r['verification']['retained_states'] and all(c['transition_checks']==c['retained_states'] for c in checks['checks'].values()),'retained transition coverage')
    return dict(status='passed_acipc_research_integrity',family='A_CI_PC',scientific_status=r['status'],
        accepted_families=r['accepted_scientific_families'],retained_states=count,full_state_dimension=76,
        numerical_steps=0,trajectory_reruns=0,projection_digest=view['projection_digest'])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true',required=True);p.parse_args()
    print(json.dumps(check(),indent=2))

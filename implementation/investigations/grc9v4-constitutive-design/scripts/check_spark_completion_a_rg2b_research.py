"""Retained A_RG2b inspection integrity; no numerical execution or authority."""
from pathlib import Path
import sys,json,argparse
ROOT=Path(__file__).resolve().parents[4]
INV='implementation/investigations/grc9v4-constitutive-design/'
SIDE=ROOT/INV/'tools/exploratory-side-tool'
sys.path.insert(0,str(SIDE/'tool/src'))
from grcv4_explorer.spark_arg2b_research import spark_arg2b_research_status,need
from grcv4_explorer.canonical import load_json_object,record_digest


def check():
    view=spark_arg2b_research_status(ROOT,SIDE);r=view['report']
    checks=load_json_object(ROOT/(INV+'evidence/spark-completion/applicability/ARG2bChecks.json'))
    need(checks['record_digest']==record_digest(checks,'record_digest')==r['checks_digest'] and
        checks['status']=='passed' and checks['fresh_prefix_replays']==2 and
        checks['retained_states']==604 and checks['supporting_steps_after_completion']==0,
        'A_RG2b selected validation record')
    return dict(status='passed_arg2b_research_integrity',family='A_RG2b',scientific_status=r['status'],
        accepted_families=r['accepted_scientific_families'],retained_states=604,
        entry=300,completion=302,last_executed_step=302,supporting_trajectory_steps_after_completion=0,
        full_state_dimension=30,numerical_steps=0,trajectory_reruns=0,projection_digest=view['projection_digest'])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true',required=True);p.parse_args()
    print(json.dumps(check(),indent=2))

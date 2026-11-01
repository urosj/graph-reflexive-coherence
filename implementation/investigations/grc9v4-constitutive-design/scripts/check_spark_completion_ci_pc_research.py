"""Lean C_CI_PC research/surface restart check; no numerical execution."""
from pathlib import Path
import argparse
import json
import lzma
import sys

ROOT=Path(__file__).resolve().parents[4]
INV='implementation/investigations/grc9v4-constitutive-design/'
SIDE=ROOT/INV/'tools/exploratory-side-tool'
sys.path.insert(0,str(SIDE/'tool/src'))
from grcv4_explorer.spark_cipc_research import spark_cipc_research_status,need


def check():
    view=spark_cipc_research_status(ROOT,SIDE);r=view['report']
    base=ROOT/INV/'evidence/spark-completion/applicability'
    states=0
    for role in ('current','reset'):
        data=json.loads(lzma.decompress((base/('CCIPC-'+role+'.json.xz')).read_bytes()))
        c=data['checks'];states+=len(c['observations'])
        need(r['decisions'][role]==c['decision'] and r['proof']==c['proof'],'research projection differs from execution')
    need(states==r['verification']['retained_states'] and states>0,'retained state count')
    checks=json.loads((base/'CCIPCChecks.json').read_text())
    need(r['verification']['rejected_controls']==checks['rejected_controls'] and
         len(checks['rejected_controls'])==19 and checks['replay']['new_gain']==0,'research accounting binding')
    need(r['debt']['status']=='open_pending_scientific_adjudication' and
         r['debt']['forward_native_destination']=='P9-9.1a' and
         all(c['claim_class']=='conditional_mathematical' and c['status']=='proposed_bounded_research'
             for c in r['proposed_claims']),'unadjudicated claim/debt promoted')
    return dict(status='passed_ccipc_research_integrity',family=r['family'],
                scientific_status=r['status'],accepted_families=view['accepted_scientific_families'],
                full_state_dimension=r['full_dimension'],retained_states=states,
                numerical_steps=0,trajectory_reruns=0,projection_digest=view['projection_digest'])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true',required=True)
    p.parse_args();print(json.dumps(check(),indent=2))

"""Lean A_OS retained-source/surface check; no numerical execution."""
from pathlib import Path
import argparse,json,lzma,sys
ROOT=Path(__file__).resolve().parents[4]
INV='implementation/investigations/grc9v4-constitutive-design/'
SIDE=ROOT/INV/'tools/exploratory-side-tool'
sys.path.insert(0,str(SIDE/'tool/src'))
from grcv4_explorer.spark_aos_research import spark_aos_research_status,need

def check():
    view=spark_aos_research_status(ROOT,SIDE);r=view['report'];base=ROOT/INV/'evidence/spark-completion/applicability';count=0
    for role in ('current','reset'):
        c=json.loads(lzma.decompress((base/('AOS-'+role+'.json.xz')).read_bytes()))['checks']
        need(r['decisions'][role]==c['decision'] and r['proof']==c['proof'],'A_OS evidence projection')
        count+=len(c['observations'])
    checks=json.loads((base/'AOSChecks.json').read_text())
    need(count==r['verification']['retained_states'] and r['verification']['rejected_controls']==checks['rejected_controls'] and
         len(checks['rejected_controls'])==16 and checks['replay']['new_gain']==0,'A_OS accounting')
    need(r['debt']['status']=='open_pending_scientific_adjudication' and r['debt']['forward_native_destination']=='P9-9.1a','A_OS debt scope')
    return dict(status='passed_aos_research_integrity',family='A_OS',scientific_status=r['status'],
        accepted_families=view['accepted_scientific_families'],full_state_dimension=30,retained_states=count,
        numerical_steps=0,trajectory_reruns=0,projection_digest=view['projection_digest'])

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true',required=True);p.parse_args()
    print(json.dumps(check(),indent=2))

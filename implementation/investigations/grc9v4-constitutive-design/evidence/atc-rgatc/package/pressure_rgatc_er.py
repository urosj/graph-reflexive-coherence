#!/usr/bin/env python3
"""Fast internal consistency pressure on retained E/R evidence; not a rerun."""
from fractions import Fraction as F
from pathlib import Path
import hashlib,json
import rgatc_reference as t
BASE=Path(__file__).resolve().parent

def run():
    record=json.loads((BASE/'RGATC-ER-Certificate.json').read_text())
    t.need(record['record_digest']==t.digest({k:v for k,v in record.items() if k!='record_digest'}),'record digest')
    for row in record['source_bindings']:
        t.need(hashlib.sha256((BASE/row['path']).read_bytes()).hexdigest()==row['sha256'],'bound source '+row['path'])
    old=json.loads((BASE/'predecessor/RGATC-TA-Certificate.json').read_text())
    E=record['E'];source=E['source']
    for a,b in (('post_x','x_after'),('post_y','y_after'),('raw_dyadic_index','raw_index')):
        x,y=old['anchor'][a],source[b]
        t.need(F(x['lo'])<=F(y['lo'])<=F(y['hi'])<=F(x['hi']),'E strictly refines T/A enclosure')
    raw=source['raw_index'];k=source['k']
    margin=min(F(raw['lo'])-(F(k)-F(1,2)),F(k)+F(1,2)-F(raw['hi']))
    t.need(margin>F(48,100),'resolved dyadic-cell margin')
    allrows=[row for role in E['roles'].values() for row in role['beats']]
    for row in allrows:
        t.need(F(row['resource_ratio']['hi'])<1-F(3,4)*t.DELTA,'observed target ratio bound')
        ci=row['same_state_CI_residual'][0][0]
        t.need(F(ci['lo'])>0 or F(ci['hi'])<0,'nonzero same-state CI residual')
        t.need(all(F(x['lo'])<=0<=F(x['hi']) for r in row['invariance_residual'] for x in r),'lagged invariance encloses zero')
        # Derived section output is never an authoritative state field.
        t.need(set(row['after'])=={'graph','C','W','radius2','provenance'},'no geometry state insertion')
    R=record['R'];life=R['lifecycle']
    t.need(life['replay'] and life['failed_event_keeps_ordinary'] and F(life['automatic_event_clock'])==t.DELTA,'transaction separation')
    maximum={}
    for role in R['representation']['roles']:
        maximum[role['role']]={k:max(F(row['errors'][k]) for row in role['beats']) for k in ('C','W','J','H')}
        t.need(max(maximum[role['role']].values())<F(1,10**10),'finite representation budget')
        for row in role['beats']:
            t.need(F(row['invariance_defect_bound'])==t.L*F(row['local_exact_map_error']),'represented RG defect bound')
    return t.enc(dict(status='retained_consistency_pressure_pass',scientific_rerun=False,independent_review=False,
        record_digest=record['record_digest'],TA_envelopes_refined=True,dyadic_cell_margin=margin,
        no_H_in_authoritative_state=True,CI_and_RG_residuals_discriminated=True,
        exact_event_time=t.DELTA,finite_representation_maxima=maximum,
        negative_cases=dict(boundaries=len(R['boundaries']['negatives']),lifecycle=len(life['negatives']),representation=len(R['representation']['negatives']))))

if __name__=='__main__':print(json.dumps(run(),indent=2))

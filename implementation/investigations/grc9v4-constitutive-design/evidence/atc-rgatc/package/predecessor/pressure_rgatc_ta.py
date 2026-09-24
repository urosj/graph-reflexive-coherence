#!/usr/bin/env python3
"""Internal pressure on the theorem package; not an independent review."""
from fractions import Fraction as F
import json
from pathlib import Path
import check_rgatc_ta as t


def run():
    first=t.run(); second=t.run()
    t.require(first==second,'deterministic proof certificate')
    # Confirm the submitted certificate really equals regeneration.
    retained=json.loads((Path(__file__).resolve().parent/'RGATC-TA-Certificate.json').read_text())
    t.require(first==retained,'retained/regenerated equality')
    T=first['T']; A=first['A']; R=F(T['section_value_bound'])
    t.require(F(T['base_increment_lipschitz'])==F(17,64),'inverse exact fraction')
    t.require(F(T['graph_transform_contraction'])==F(2,47),'graph-transform exact fraction')
    t.require(F(T['section_lipschitz_image'])==F(17,47),'Lipschitz image exact fraction')
    # The old 1/8 step is NOT admitted by this *sufficient* extension budget.
    old_ell=(2**23+2**20*F(1,2))*F(1,8)
    t.require(old_ell>1,'old step fails this sufficient inverse budget')
    # A proposed concrete native-style outer chart inside C>0 cannot contain
    # the entire charge-nine positive source corridor down to zero.
    examples=[]
    for k in (4,16,64,256):
        eps=F(1,2**k); C=(eps,)*4+(9-4*eps,)
        t.require(sum(C)==9 and min(C)>0 and C[4]-eps>=3,'positive corridor sequence')
        examples.append(dict(epsilon=eps,x=C[4]-eps))
    # Fresh geometry is bounded by the generated S, not by a CI root.
    E=first['anchor']; raw=E['raw_dyadic_index']
    margin=min(F(raw['lo'])-F(65535,2), F(65537,2)-F(raw['hi']))
    t.require(margin>F(12,25),'dyadic cell has strict >0.48 margin')
    t.require(F(E['event_geometry_radius']) < R and F(E['event_H00_minus_one_lower'])>0,'active lagged event')
    # First-step <2/3 is not part of the small-beat proof: actual envelopes
    # remain near their transferred states rather than the old large-step entry.
    y0=F(1,2**24);eps=F(1,2**30)
    C,W=t.paired_source(3-t.H,y0,F(99,100)-eps,F(99,100)+eps)
    cc,ww,_=t.one_envelope('source',C,W,R)
    tc=cc[:4]+(cc[4]/2,cc[4]/2);tw=ww+(t.I(1),)
    nc,nw,_=t.one_envelope('target',tc,tw,R)
    rad=t.p.norm2(tuple(c-F(3,2) for c in nc))
    t.require(rad.lo>F(4,9)*t.GRID,'old first-entry claim is false at this small beat')
    t.require(F(A['target_factor'])>F(99,100),'do not relabel new q as old q<0.91')
    return t.enc(dict(status='internal_pressure_pass',independent_review=False,
      deterministic_regeneration=True,retained_certificate_matches=True,
      inverse_fraction='17/64',graph_transform_fraction='2/47',section_lipschitz_image='17/47',
      dyadic_cell_margin=margin,old_step_sufficient_budget=old_ell,
      old_step_impossibility_claimed=False,positive_boundary_sequence=examples,
      old_first_entry_claim_rejected=True,target_first_step_X_squared=rad,
      section_evaluation_executed=False,trajectory_search_executed=False))

if __name__=='__main__':print(json.dumps(run(),indent=2))

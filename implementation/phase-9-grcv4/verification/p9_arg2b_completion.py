"""A_RG2b connected nine-port completion: exact bounds, no native admission.

The accepted signed C/scaled-log-W law and graph-transform proof are retained.
Only the graph norm hypotheses are widened from 9/10/5 to 9/18/9.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
from pathlib import Path
from flint import fmpq as Q
import p9_crg2b_completion as graphs

ROOT, BASE = graphs.ROOT, graphs.BASE
SELF = BASE+'verification/p9_arg2b_completion.py'
TEST = BASE+'verification/test_p9_arg2b_completion.py'
NOTE = BASE+'tranche-8/P9-ARG2b-ConnectedCompletion.md'
PLAN = BASE+'tranche-8/P9-ARG2b-Tranches8-9-Plan.md'
RESULT = BASE+'tranche-8/P9-ARG2b-CompletionFeasibility.json'
INPUTS = (BASE+'tranche-8/P9-8.4c-ARG2bCases.json', BASE+'tranche-8/P9-8.4d-COSCases.json',
          BASE+'tranche-8/larger-graph-examples/A_RG2b.json')
RHO,LIP,DT,SCALE,EPS,KH,CHI,ZETA = Q(1,4096),Q(1,1024),Q(1,4096),Q(512),Q(1,2**24),Q(1,2),Q(1,16),Q(1,2)
require,seal,digest,read = graphs.require,graphs.seal,graphs.digest,graphs.read


def global_bounds(bn=Q(9),dn=Q(18),an=Q(9)):
    """Exact derivative bounds in max(C,512 log W) and induced infinity H."""
    require(0<bn<=9 and 0<dn<=18 and 0<an<=9,'nine-port graph norms out of scope')
    span,hinv=Q(6),1/(1-RHO)
    wl,wu=1-1/SCALE,1/(1-1/SCALE)
    j0=wu*dn*(wu+KH*RHO)*span
    j0x=wu*dn*((wu+KH*RHO)*2+(2*wu+KH*RHO)*span/SCALE)
    j0h=wu*KH*dn*span
    row_x=2+2*span/SCALE
    emax,emin=EPS*(10+12*span**2+j0**2)/2,-EPS
    gl,gu=1-emax,1/(1+emin)
    require(gl>Q(1,2) and -emin<1,'read floor/exp bound unresolved')
    qmax=max(abs((wl-gu)/(wl+gu)),abs((wu-gl)/(wu+gl)))
    ex,eh=EPS*(2+24*span*row_x+2*j0*j0x)/2,EPS*j0*j0h
    qx,qh=(1/SCALE+ex)/2,eh/2
    theta=CHI*ZETA*qmax
    require(0<=theta<Q(1,2),'physical inverse unresolved')
    j=j0/(1-theta)
    jx,jh=(j0x+CHI*ZETA*qx*j)/(1-theta),(j0h+CHI*ZETA*qh*j)/(1-theta)
    causal,cx,ch=CHI*qmax*j,CHI*(qx*j+qmax*jx),CHI*(qh*j+qmax*jh)
    mc=DT*bn*j
    post_span=span+2*mc
    post_x,post_h=1+DT*bn*jx,DT*bn*jh
    post_row_x,post_row_h=2*post_x+2*post_span/SCALE,2*post_h
    writer_emax=EPS*(2*(5+mc)+12*post_span**2+j**2)/2
    writer_emin=EPS*(-1-mc)
    require(1-writer_emax>Q(1,2),'writer floor bound unresolved')
    writer_ex=EPS*(2*post_x+24*post_span*post_row_x+2*j*jx)/2
    writer_eh=EPS*(2*post_h+24*post_span*post_row_h+2*j*jh)/2
    ax,ah=max(DT*bn*jx,DT*(1+SCALE*writer_ex)),max(DT*bn*jh,DT*SCALE*writer_eh)
    my=DT*(1+SCALE*max(writer_emax,-writer_emin))
    v,vx,vh=hinv*causal,hinv*cx,hinv*ch+hinv**2*causal
    ms,bx,bh=ZETA*an*v*v,2*ZETA*an*v*vx,2*ZETA*an*v*vh
    ell=ax+ah*LIP
    require(ell<1,'base inverse bound unresolved')
    inv=1/(1-ell);value=KH*ms;image_lip=KH*(bx+bh*LIP)*inv
    q=KH*(bh+(bx+bh*LIP)*inv*ah)
    values=dict(A_X=ax,A_H=ah,M_f=max(mc,my),M_C=mc,M_Y=my,M_S=ms,B_X=bx,B_H=bh,
        J=j,J_X=jx,J_H=jh,current_margin=1-theta,read_exponent_upper=emax,
        writer_exponent_upper=writer_emax,read_drive_upper=gu,weight_lower=wl,weight_upper=wu,
        ell=ell,inverse_lip=inv,value_radius=value,image_lip=image_lip,q_section=q,
        four_level_tail_upper=q**4*value)
    checks=dict(resource_chart_containment=mc<Q(1,4),history_chart_containment=my<Q(1,8),
        section_image=value<RHO,lipschitz_class=image_lip<=LIP,graph_transform=q<1,
        same_four_level_tail_budget=q**4*value<Q(1,2**48))
    return values,checks


def class_certificate():
    bounds,checks=global_bounds()
    return dict(norms=['9','18','9'],bounds={k:str(v) for k,v in bounds.items()},checks=checks)


def graph_certificate(graph):
    b,d,mask,diameter=graphs.graph_algebra(graph)
    norms=tuple(graphs.norm(x) for x in (b,d,mask))
    require(norms[0]<=9 and norms[1]<=18 and norms[2]<=9,'graph class mismatch')
    # One uniform class certificate; actual norms retained for each subject.
    certificate=class_certificate()
    return dict(graph_digest=digest(graph),vertices=b.nrows(),edges=b.ncols(),
        cycle_rank=b.ncols()-b.nrows()+1,diameter=diameter,
        actual_norms=[str(v) for v in norms],class_norms=['9','18','9'],
        class_certificate_digest=digest(certificate),checks=certificate['checks'])


def validate_large_recipe(value):
    require(value['family']=='A_RG2b' and value['reference_recipe']==dict(unit_vertex_measures=True,
        unit_edge_weights=True,K4_base='exact zero m by m in each graph edge order',
        context=dict(contract_id='constant_zero_context_v1',values={})), 'reference recipe drift')
    require(value['selected_configuration']['ordinary_dt']==float(DT),'timestep drift')
    params=dict(eta=1,kappa_c=1,W_floor=.5,alpha=float(EPS),beta=float(EPS),gamma=float(EPS),
                kappa_Ah=.5,chi_A=float(CHI),zeta_A=float(ZETA),tau_A=1)
    for role in ('source','target'):
        subject=value[role];p=subject['profile']['params_resolved']
        require(subject['profile']['identity_payload']['profile_family_id']=='A_RG2b'
            and all(p['candidate'][k]==v for k,v in params.items())
            and p['geometry']['kappa_H']==.5,'candidate parameter drift')
        n,m=len(subject['graph']['live_node_ids']),len(subject['graph']['edges'])
        require(set(subject['roles'])=={'current','reset'},'history role roster')
        for state in subject['roles'].values():
            require(len(state['C'])==n and len(state['W_A'])==m and state['Z_4'] is None
                and all(w>0 for w in state['W_A']),'wrong authoritative history')


def subjects():
    small,deep,large=map(read,INPUTS);validate_large_recipe(large)
    rows=[('accepted-small/'+v['fixture_id'],v['oracle']['target_graph']) for v in small['cases']]
    rows += [('deep/'+v['fixture_id'],v['oracle']['target_graph']) for v in deep['cases']]
    rows += [('large/'+role,large[role]['graph']) for role in ('source','target')]
    require(len(rows)==54,'graph roster mismatch')
    return rows


def bindings():
    names=(*INPUTS,SELF,TEST,NOTE,PLAN,graphs.SELF,BASE+'tranche-8/P9-8.0-RG2bCompletion.md',
           BASE+'verification/test_p980_rg2b_completion.py','src/pygrc/models/grc_9_v4_arg2b.py')
    return [dict(path=p,sha256=hashlib.sha256((ROOT/p).read_bytes()).hexdigest()) for p in names]


def scope():
    return dict(family='A_RG2b',stage='research_completion_feasibility',accepted_small_graphs=32,
        deep_graphs=20,large_graphs=2,arithmetic='FLINT_exact_rational',physical_law_changed=False,
        signed_history_coordinates='Y=512 log W_A',native_steps=0,native_events=0,
        physical_positivity_certified=False,numerical_chain_certified=False,
        C1_debt='GTRS-RG-DEBT-C1-SECTION-REGULARITY_unresolved',user_accepted=False,aggregate_closed=False)


def check(value):
    require(value==seal(value) and value['schema']=='p9-arg2b-completion-feasibility-v1','research digest/schema')
    require(value['source_bindings']==bindings() and value['scope']==scope(),'research subject/scope drift')
    require(value['class_certificate']==class_certificate(),'uniform class certificate drift')
    declared=subjects()
    require([v['subject'] for v in value['graphs']]==[s[0] for s in declared],'graph roster drift')
    for row,(_,graph) in zip(value['graphs'],declared,strict=True):
        require(row==dict(subject=row['subject'],**graph_certificate(graph)),'graph certificate drift')
    require(value['completion_theorem_passes']==all(all(v['checks'].values()) for v in value['graphs']), 'completion verdict mismatch')
    return value


def worker(subject):
    name,graph=subject;return dict(subject=name,**graph_certificate(graph))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',action='store_true');p.add_argument('--check',action='store_true')
    p.add_argument('--workers',type=int,default=4);args=p.parse_args()
    require(args.run!=args.check and 1<=args.workers<=12,'select run/check; 1..12 workers')
    if args.run:
        require(not (ROOT/RESULT).exists(),'refusing to overwrite retained result')
        with ProcessPoolExecutor(max_workers=args.workers) as pool:rows=list(pool.map(worker,subjects()))
        v=seal(dict(schema='p9-arg2b-completion-feasibility-v1',scope=scope(),source_bindings=bindings(),graphs=rows,
            class_certificate=class_certificate(),
            completion_theorem_passes=all(all(r['checks'].values()) for r in rows)))
        check(v);(ROOT/RESULT).write_text(json.dumps(v,indent=2)+'\n')
    else:v=check(read(RESULT))
    print(json.dumps(dict(graphs=len(v['graphs']),completion_theorem_passes=v['completion_theorem_passes'],scope=v['scope']),indent=2))

if __name__=='__main__':main()

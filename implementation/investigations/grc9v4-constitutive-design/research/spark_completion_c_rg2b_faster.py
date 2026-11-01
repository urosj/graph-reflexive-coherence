"""C_RG2b faster research: invariant-section reuse and a finite union trap.

The original completion and physical coefficients are unchanged. Geometry is a
computed enclosure of its unique section, never an additional physical state.
The event preparation/allocation are a separately declared, exploratory choice.
"""
from pathlib import Path
from fractions import Fraction as F
import json,lzma,time,hashlib
from flint import arb,arb_mat,fmpq,fmpq_mat,ctx
from spark_completion_c_rg2b import *
from spark_completion_c_rg2b_campaign import (prepare_source,decode,state_payload,exact_vector,section_payload)
from spark_completion_positive import fixture,content_id,norm_upper
from spark_completion_a_os_earlier import positive_definite_exact
from spark_completion_ci_campaign import exact_bounds,matrix_payload
from spark_completion_continuation import need,geometric_roster
ROOT=Path(__file__).resolve().parents[4]
BASE='implementation/investigations/grc9v4-constitutive-design/evidence/spark-completion/applicability/'
DECLARATION=BASE+'CRG2bFasterDeclaration.json'
ENTRY=390
WINDOW=2
COMPONENT_RADIUS=F(1,32768)
HORIZON=4096
TIME_LIMIT=3600


def seal(v):return {**v,'record_digest':content_id(v)}
def load(path):
    raw=(ROOT/path).read_bytes();v=json.loads(lzma.decompress(raw)if path.endswith('.xz')else raw)
    need(v['record_digest']==content_id({k:x for k,x in v.items()if k!='record_digest'}),'record digest');return v

def section_reuse(m,C,section,nextC):
    """Gamma(F(C,Gamma(C)))=G(C,Gamma(C)); account for center displacement.

The input is already an enclosure of Gamma(C). This implication establishes
an enclosure of Gamma(nextC), including every inherited initial section error.
No trajectory-dependent selection of the invariant section is made.
    """
    need(section['subject'] is C,'section reuse subject')
    read=section['read'];image=C+read['increment'];shift=maxnorm(image-nextC)
    generated=read['geometry'];scale=2**PROPOSAL_BITS
    # Quantize only the derived proposal; its complete defect enters error.
    proposal=arb_mat([[arb(fmpq((x.mid().fmpq().numerator*scale)//x.mid().fmpq().denominator,scale))for x in row]for row in generated.tolist()])
    enclosure_error=maxnorm(generated-proposal)
    error=(enclosure_error+ball(LIP)*shift).upper()
    H=arb_mat(m.m,m.m)
    for i in range(m.m):
        for j in range(i,m.m):
            if m.overlap[i][j]:H[i,j]=arb(proposal[i,j].fmpq(),error.fmpq());H[j,i]=H[i,j]
    need(maxnorm(H-m.I)<ball(RHO),'reused section leaves proved geometry class')
    return dict(subject=nextC,proposal=proposal,geometry=H,error=error,
        reuse=dict(generated_enclosure_error=exact_bounds(enclosure_error,256),
                   center_shift=exact_bounds(shift,256),section_lipschitz=str(LIP),
                   proof='fixed unique section invariance plus Lipschitz center shift'),
        read=m.lag(nextC,m.operators(H)))


def cached_payload(s):
    return dict(proposal=matrix_payload(s['proposal']),error=exact_bounds(s['error'],256),reuse=s.get('reuse'))


def prepare(role,declaration):
    source,_,raw_targets=fixture();targets={chi:dict(graph=t['graph'],module=t['module'])for chi,t in raw_targets.items()}
    _,_,_,record=prepare_source(source,targets,role,declaration['prepared_source'])
    sm=CRG2bReference(source);operand,r=decode(sm,record['actual_poststate']if role=='current'else record['reset'])
    m=CRG2bReference(targets['1']['graph']);mod=targets['1']['module'];shares=declaration['allocation_shares'];T=arb_mat(m.n,sm.n)
    for i,n in enumerate(m.nodes):
        if n in sm.nodes and n!='v':T[i,sm.nodes.index(n)]=1
        elif n in mod[1:]:T[i,sm.nodes.index('v')]=ball(shares[mod[1:].index(n)])
    need(all(sum(T[i,j]for i in range(m.n))==1 for j in range(sm.n)),'new allocation charge identity')
    value=T*operand;C=m.quantize(value);transport=(m.trace.sqrt()*norm_upper(T)*sm.sqrtamax).upper()
    radius=ball(ceil_dyadic(transport*r+m.trace.sqrt()*norm_upper(value-C)))
    need(set(geometric_roster(m.graph,m.box(C,radius),m.nodes))=={'p'},'allocation itself earns gain')
    record.update(allocation_shares=shares,transport_factor=exact_bounds(transport),target_section_rebuilt=True)
    return m,C,radius,record,targets


def fresh_check(m,C,r,cached):
    fresh=m.section(C,retain_chain=True)
    need(all(x.overlaps(y)for x,y in zip(fresh['geometry'].entries(),cached['geometry'].entries())),
         'independently rebuilt section contradicts reuse')
    return dict(section=section_payload(fresh,m,C,r),reuse_error=exact_bounds(cached['error'],256),
                overlap_consistency=True,proof_role='consistency check; reuse is justified by invariance')


def campaign(role,declaration,steps=HORIZON,complete=True):
    start=time.monotonic();source,_,targets=fixture();proof,_=trap_certificate(targets)
    with ctx.workprec(PRECISION):
        m,C,r,record,targets=prepare(role,declaration);initial=state_payload(m,C,r);s=m.section(C,retain_chain=True)
        event=section_payload(s,m,C,r);rows=[];fresh={};tail_entry=None;gap=arb(1);first=None
        for step in range(1,steps+1):
            need(time.monotonic()-start<TIME_LIMIT,'faster campaign one-hour cap')
            oldC=C;oldr=r;C,r,diag=m.advance_tube(C,r,s)
            strict=r-(diag['lipschitz']*oldr+diag['defect'])
            need(strict>0,'successor tube lacks a strict image margin');gap=min(gap,strict.lower())
            s=section_reuse(m,oldC,s,C);cb=m.box(C,r);km=list(map(ball,m.domain['K_minus']))
            need(sum(C.entries())==21 and all(km[0]<x<km[1] and x>0 for x in cb.entries()),'physical admission')
            roster={chi:geometric_roster(t['graph'],cb,m.nodes)for chi,t in targets.items()}
            if first is None and roster==proof['complete_basins']:first=step
            delta=C-m.vector(proof['center']);dist=((delta.transpose()*m.P*delta)[0,0].nonnegative_part().sqrt()+r).upper()
            finishing=dist+ball(COMPONENT_RADIUS)<ball(proof['radius'])
            if finishing:tail_entry=step
            if step in (1,ENTRY,ENTRY+WINDOW,500,1000,1500,2000,2500,3000,3500,4000)or finishing:
                fresh[str(step)]=fresh_check(m,C,r,s)
            rows.append(dict(step=step,**state_payload(m,C,r),section=cached_payload(s),complete_basins=roster,
                tube=dict(lipschitz=exact_bounds(diag['lipschitz']),defect=exact_bounds(diag['defect'],256),strict_image_margin=exact_bounds(strict,256)),
                tail_distance_upper=exact_bounds(dist)[1]))
            if step%200==0 or finishing:print(role,step,'seconds',round(time.monotonic()-start,2),'tail_distance',dist.str(5),flush=True)
            if finishing:break
        if complete:need(tail_entry is not None and tail_entry>ENTRY+WINDOW,'missing certified terminal trap')
        return dict(role=role,source=record,targets=targets,source_graph=source,initial_target=initial,event_section=event,
            observations=rows,fresh_section_checks=fresh,terminal_proof=proof,first_spatial_gain=first,terminal_entry=tail_entry,
            declared_earlier_entry=ENTRY,declared_earlier_completion=ENTRY+WINDOW,minimum_tube_image_margin=exact_bounds(gap,256),
            section_reuse=dict(initial_section_fresh=True,each_transfer_from_invariance=True,center_shifts_enclosed=True,
                physical_state=['C'],geometry_history_transported_at_event=False,geometry_is_independent_physical_state=False,
                fresh_rebuild_count=len(fresh),forward_reuse_steps=len(rows)),
            arithmetic=dict(precision_bits=PRECISION,proposal_bits=PROPOSAL_BITS,section_depth=DEPTH,radius_bits=160,
                horizon=HORIZON,time_limit_seconds=TIME_LIMIT,automatic_fallback=False),elapsed_seconds=time.monotonic()-start)


def hull_contraction(m,center,box):
    """A common full-state Lipschitz bound for every pair in the finite union.

The coordinate box is convex; geometry/edge predicates need hold only on the
actual union. Exact charge-tangent Rayleigh inequalities replace trace bounds.
No derivative of Gamma is assumed or evaluated.
    """
    n=m.n;C=m.vector(center);s=m.section(C);w=max(abs(box[i,0]-C[i,0]).upper()for i in range(n))
    L,foot=m.section_local_lipschitz(C,w/m.sqrtamax,s)
    V=min(m.bounds['section_value_radius'],maxnorm(s['proposal']-m.I)+s['error']+L*w)
    curv=[3*(x-2)**2-1 for x in box.entries()]
    low=fmpq_mat([[curv[i].lower().fmpq()if i==j else 0 for j in range(n)]for i in range(n)])-m.algebra['L']/64
    high=fmpq_mat([[curv[i].upper().fmpq()if i==j else 0 for j in range(n)]for i in range(n)])-m.algebra['L']/64
    E=fmpq_mat([[int(i==j)if i<n-1 else -1 for j in range(n-1)]for i in range(n)]);P=m.algebra['P']
    lo,hi=F(1,3),F(64)
    ldl_low=positive_definite_exact(E.transpose()*(low-fmpq(str(lo))*P)*E)
    ldl_high=positive_definite_exact(E.transpose()*(fmpq(str(hi))*P-high)*E)
    ell=ball(m.algebra['ell']);h=ball(ETA*DT);a2=(1+V)/(1-V)*m.q(4,3);q2=1+a2/4
    D0=max(abs(x).upper()for x in curv)+ell/64;partial=h*ell*(a2*V*ell/3*D0+q2*ell*V/64)
    z=norm_upper(m.Bt*box);phi=m.B*m.Bt*box/64-m.site(box)
    j0=ball(ETA)*norm_upper(m.Bt*phi)+ball(ETA)*ell*V*z/64;y=a2*j0
    hslope=ball(DT)*ell.sqrt()*(ball(ETA)*ell*z*q2/64+a2*ell*y/4);convert=(m.amax*m.trace).sqrt()
    reference=max(abs(1-h*ball(lo)),abs(1-h*ball(hi)));q=(reference+(partial+hslope*L)*convert).upper()
    need(q<1,'full physical finite-union contraction fails')
    return dict(contraction=exact_bounds(q),reference_contraction=exact_bounds(reference),
        fixed_geometry_correction=exact_bounds(partial*convert),section_difference_correction=exact_bounds(hslope*L*convert),
        section_lipschitz=exact_bounds(L),section_value_radius=exact_bounds(V),inverse_footprint={k:exact_bounds(v)for k,v in foot.items()},
        charge_tangent_rayleigh_bounds=[str(lo),str(hi)],exact_ldl_pivots=dict(lower=ldl_low,upper=ldl_high),
        relative_dimension=n-1,all_independent_coordinates=True,section_C1_claimed=False)


def union_certificate(runs):
    """Closed finite union: retained positive-radius balls plus stationary ball.

Every prefix component maps strictly into its successor; terminal components
map into the stationary trap. A single scaled norm and common q<1 apply to all
pairs, certified on the enclosing convex box. This is SC-1's original contract.
    """
    with ctx.workprec(PRECISION):
        first=runs['current'];proof=first['terminal_proof'];m=CRG2bReference(first['targets']['1']['graph']);center=m.vector(proof['center'])
        need(all(run['terminal_proof']==proof for run in runs.values()),'different stationary traps')
        terminal=m.box(center,ball(proof['radius']));lower=[x.lower().fmpq()for x in terminal.entries()];upper=[x.upper().fmpq()for x in terminal.entries()]
        minimum_order=arb(1);minimum_radius=ball(COMPONENT_RADIUS);minimum_image=ball(F(proof['strict_image_margin'][0]));components=1;defects=[]
        reference_edges=[(a,b,1 if F(proof['center'][a])>F(proof['center'][b])else -1)for a,b in m.edges]
        km=list(map(ball,m.domain['K_minus']))
        need(all(km[0]<x<km[1] and x>0 for x in terminal.entries()),'terminal physical domain')
        for chi,t in first['targets'].items():
            need([(e['tail']['node_id'],e['head']['node_id'])for e in t['graph']['edges']]==m.edges,'chiral equation graph differs')
            need(geometric_roster(t['graph'],terminal,m.nodes)==proof['complete_basins'][chi],'terminal complete roster')
        for a,b,sign in reference_edges:
            margin=sign*(terminal[m.nodes.index(a),0]-terminal[m.nodes.index(b),0]);need(margin>0,'terminal edge direction');minimum_order=min(minimum_order,margin.lower())
        for role,run in runs.items():
            need(run['terminal_entry']==len(run['observations']) and run['terminal_entry']>ENTRY+WINDOW,'terminal reach')
            need([row['step']for row in run['observations']]==list(range(1,run['terminal_entry']+1)),'noncontiguous retained trajectory')
            for row in run['observations'][ENTRY-1:]:
                C,r=decode(m,row);need(0<r<ball(COMPONENT_RADIUS),'trajectory tube outside enlarged component');box=m.box(C,ball(COMPONENT_RADIUS));components+=1
                need(r>0,'zero-dimensional trajectory component')
                need(sum(C.entries())==21 and all(km[0]<x<km[1] and x>0 for x in box.entries()),'component physical domain/charge')
                for i,x in enumerate(box.entries()):lower[i]=min(lower[i],x.lower().fmpq());upper[i]=max(upper[i],x.upper().fmpq())
                roster={chi:geometric_roster(t['graph'],box,m.nodes)for chi,t in run['targets'].items()}
                need(roster==proof['complete_basins']==row['complete_basins'],'nonuniform complete basin roster')
                for a,b,sign in reference_edges:
                    margin=sign*(box[m.nodes.index(a),0]-box[m.nodes.index(b),0]);need(margin>0,'finite union changes an edge direction');minimum_order=min(minimum_order,margin.lower())
                if row['step']<run['terminal_entry']:
                    nxt=run['observations'][row['step']];defects.append(ball(F(nxt['tube']['defect'][1])))
                else:
                    margin=ball(proof['radius'])-ball(row['tail_distance_upper'])-ball(COMPONENT_RADIUS);need(margin>0,'terminal component not inside stationary ball');minimum_image=min(minimum_image,margin.lower())
        need(minimum_image>0 and minimum_radius>0,'non-strict finite union')
        box=arb_mat([[arb((a+b)/2,(b-a)/2)]for a,b in zip(lower,upper)])
        contraction=hull_contraction(m,proof['center'],box)
        q=ball(F(contraction['contraction'][1]))
        component_margin=((1-q)*ball(COMPONENT_RADIUS)-max(defects)).lower()
        need(component_margin>0,'enlarged components lack strict successor containment')
        minimum_image=min(minimum_image,component_margin)
        return dict(schema='spark-completion-crg2b-finite-union-trap-v1',domain='finite union of certified metric balls and one stationary metric ball',
            metric=proof['metric'],entry_step=ENTRY,completion_step=ENTRY+WINDOW,ordinary_duration=str(DT),elapsed_from_event=str(DT*(ENTRY+WINDOW)),
            components=components,component_radius=str(COMPONENT_RADIUS),component_successor_margin=exact_bounds(component_margin),minimum_component_radius=exact_bounds(minimum_radius,256),minimum_strict_image_margin=exact_bounds(minimum_image,256),
            minimum_edge_order_margin=exact_bounds(minimum_order),hull={n:exact_bounds(box[i,0])for i,n in enumerate(m.nodes)},
            common_contraction=contraction,complete_basins=proof['complete_basins'],relative_dimension=m.n-1,
            convex_hull_used_for_pairwise_differences_only=True,uniform_geometry_checked_on_every_component=True,
            original_SC1_contract_unchanged=True,completion_relative=True,accepted_authority=False,native_completion=False,
            reset_earns_live_gain=False,source_preparation_and_allocation_changed=True)

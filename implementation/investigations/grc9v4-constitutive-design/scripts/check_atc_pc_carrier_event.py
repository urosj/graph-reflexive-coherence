#!/usr/bin/env python3
"""PC-2 bounded carrier-law certificate and review-hardening pressure.

Research only, stdout only. No target trajectory or target-based map choice.
"""
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[4]
INV=Path('implementation/investigations/grc9v4-constitutive-design')
sys.path.insert(0,str(ROOT/INV/'research'))
import atc_pc_carrier_event as e
r=e.r


def domain_pressure():
    rejected=[]
    def reject(name,call):
        try: call()
        except r.a.AdmissionError: rejected.append(name)
        else: raise AssertionError('admitted invalid domain: '+name)
    C=(F(6,5),F(6,5),F(6,5),F(6,5),F(21,5));W=(F(49,50),)*4
    state=r.exact_state('paired_source',C,W)
    reject('wrong_exact_charge_subgrid',lambda:r.exact_state('paired_source',C[:-1]+(C[-1]+F(1,2**300),),W))
    reject('unpaired_C_same_charge',lambda:r.exact_state('paired_source',(C[0]+F(1,100),C[1]-F(1,100))+C[2:],W))
    reject('unpaired_W',lambda:r.exact_state('paired_source',C,(F(97,100),)+W[1:]))
    reject('bare_interval_state_even_equal_boxes',lambda:r.ci_read('paired_source',state.data))
    reject('direct_domain_witness_fabrication',lambda:r.DomainState('paired_source',state.data,'Q=9'))
    reject('raw_carrier_without_exact_witness',lambda:r.pc_read(state,r.diagonal_z(F(0)).values))
    zero=tuple((F(0),)*4 for _ in range(4))
    def changed(matrix,i,j,value):
        rows=[list(row) for row in matrix];rows[i][j]=value;return tuple(map(tuple,rows))
    reject('asymmetric_carrier_subgrid',lambda:r.exact_carrier('paired_source',changed(zero,0,1,F(1,2**300))))
    reject('unpaired_carrier_diagonal',lambda:r.exact_carrier('paired_source',changed(zero,0,0,F(1,16384))))
    reject('over_radius',lambda:r.diagonal_z(F(1,1024)))
    reject('malformed_carrier',lambda:r.exact_carrier('paired_source',zero[:-1]))
    targetzero=tuple((F(0),)*5 for _ in range(5))
    wrong=changed(changed(targetzero,0,2,F(1,2**300)),2,0,F(1,2**300))
    reject('target_nonstar_subgrid',lambda:r.exact_carrier('paired_target',wrong))
    reject('wrong_role_graph',lambda:r.pc_read(state,r.exact_carrier('paired_target',targetzero)))
    reject('direct_carrier_witness_fabrication',lambda:r.Carrier('paired_source',r.diagonal_z(F(0)).values,'symmetric'))
    reject('invalid_split_share',lambda:r.transfer(state,1))
    good=r.ci_read('paired_source',state)
    other=r.paired_state(F(31,10),F(0),F(49,50),F(49,50))
    reject('stale_selected_read',lambda:r.advance('paired_source',other,good))
    reject('stale_event_root',lambda:r.event_select(other,good))
    return dict(rejected=rejected,exact_charge_not_box_containment=True,
                exact_pairing_not_box_equality=True,constructive_derived_invariants=True)


def map_pressure():
    src,tgt=r.p.SOURCE,r.p.TARGET
    lineage=tuple((i,1) for i in range(4));tests=0
    def norm2(z): return sum(x*x for row in z for x in row)
    bases=[]
    for i in range(4):
        for j in range(i,4):
            z=[[F(0)]*4 for _ in range(4)];z[i][j]=z[j][i]=F(1);bases.append(tuple(map(tuple,z)))
    # A dense signed rational matrix adds cancellation pressure beyond bases.
    bases.append(tuple(tuple(F((-1)**(i+j)*(i+j+1),19) for j in range(4)) for i in range(4)))
    generators=[]
    for ns,nt in ((4,0),(0,5)):
        n=ns or nt
        for i in range(n-1):
            q=list(range(n));q[i],q[i+1]=q[i+1],q[i]
            generators.append((tuple(q) if ns else tuple(range(4)),tuple(q) if nt else tuple(range(5)),(1,)*4,(1,)*5))
        for i in range(n):
            signs=tuple(-1 if j==i else 1 for j in range(n))
            generators.append((tuple(range(4)),tuple(range(5)),signs if ns else (1,)*4,signs if nt else (1,)*5))
    for z in bases:
        kept,dropped,embedded=e.restrict(z,src,tgt,lineage)
        r.require(norm2(z)==norm2(kept)+norm2(dropped),'orthogonal loss decomposition')
        r.require(all(kept[i][j]+dropped[i][j]==embedded[i][j] for i in range(5) for j in range(5)),
                  'complete retained/discarded decomposition')
        r.require(all(kept[4][i]==kept[i][4]==0 for i in range(5)),'no invented bridge memory')
        r.require(e.restrict(kept,tgt,tgt,tuple((i,1) for i in range(5)))[0]==kept,'idempotent target projection')
        for ps,pt,ss,st in generators:
            znew=tuple(tuple(ss[i]*ss[j]*z[ps[i]][ps[j]] for j in range(4)) for i in range(4))
            snew=tuple(src[i] for i in ps);tnew=tuple(tgt[i] for i in pt)
            mapped=tuple((pt.index(ps[i]),ss[i]*st[pt.index(ps[i])]) for i in range(4))
            kn,dn,_=e.restrict(znew,snew,tnew,mapped)
            for new,old in ((kn,kept),(dn,dropped)):
                expected=tuple(tuple(st[i]*st[j]*old[pt[i]][pt[j]] for j in range(5)) for i in range(5))
                r.require(new==expected,'signed coordinate covariance of both transport and loss')
            tests+=1
        relabel=lambda edges:tuple((11-3*u,11-3*v) for u,v in edges)
        r.require(e.restrict(z,relabel(src),relabel(tgt),lineage)==(kept,dropped,embedded),'vertex-label covariance')
    allones=tuple((F(1),)*4 for _ in range(4))
    try: e.restrict(allones,src,tgt,((0,1),(0,1),(2,1),(3,1)))
    except r.a.AdmissionError: pass
    else: raise AssertionError('noninjective lineage accepted')
    try: e.restrict(allones,src,tgt,((0,1),(1,1),(2,1),(3,0)))
    except r.a.AdmissionError: pass
    else: raise AssertionError('invalid orientation accepted')
    return dict(symmetric_basis_count=10,dense_signed_case=True,covariance_generator_cases=tests,
        vertex_relabel_cases=len(bases),pythagorean_cases=len(bases),
        target_projection_idempotent=True,no_bridge_invention=True,invalid_lineage_rejections=2,
        structural_source_dimension=10,retained_dimension=6,kernel_dimension=4,
        decorated_source_dimension=5,decorated_retained_dimension=4,operator_norm=1)


def run():
    domain=domain_pressure();linear=map_pressure()
    before,reset=r.fixtures()
    after,Z,_,_=r.pc_step(before,r.diagonal_z(F(1,16384)))
    resetZ=r.diagonal_z(F(1,24576));r.pc_read(reset,resetZ)
    roles={}
    for role,carrier in (('current',Z),('reset',resetZ)):
        transported,receipt=e.event_carrier(carrier)
        zero,reset_receipt=e.event_carrier(carrier,e.RESET)
        r.require(any(x.lo>0 for row in transported.values for x in row),'restriction preserves real history')
        r.require(all(x.lo==x.hi==0 for row in zero.values for x in row),'whole reset truly zero')
        r.require(receipt['information_loss']==('proved_nonzero' if role=='current' else 'exactly_zero'),
                  'role-specific actual loss, not conflated')
        # Carrier admission only. No resource transfer, target J or trajectory
        # is computed, so the constitutive choice cannot be fitted to restoration.
        roles[role]=dict(restriction=receipt,whole_reset=reset_receipt,
                        target_geometry_lower=1-r.a.PARAMS['kh']*r.Z_RADIUS)
    payload=r.a.encode(dict(schema='grcv4_atc_pc_carrier_event_v1',
        status='PC2_projection_valid_as_control_selection_superseded_after_pressure',
        selected_research_policy=None,control_policy=e.POLICY,
        superseded_by_candidate='pc_star_fission_relational_lift_lossless_v1',
        selection_basis='historical conditional minimizer only: nearest to zero-bridge embedding does not establish minimal information loss',
        additional_constitutive_axiom=True,not_forced_by_previous_V4_authority=True,
        whole_reset_admissible_but_not_minimum_change=True,
        unavoidable_loss_on_decorated_domain=False,
        domain_pressure=domain,linear_pressure=linear,roles=roles,
        source_postbeat=after.payload(),
        target_dynamic_restoration_claimed=False,PC3_completed=False,
        graph_admitted=False,scientific_acceptance=False,native_ATC_executed=False,ATC2_closed=False,
        claim_updates=[dict(claim_id='ATC-PC-CARRIER-02',claim_class='conditional',
            status='projection_valid_selection_superseded',profile_scope=['A_PC'],
            debt_refs=['ATC7-DB-15','ATC7-DB-06','ATC7-DB-16','ATC7-DB-26'],
            open_front=['ATC7-DB-14','ATC7-DB-16','ATC7-DB-19'],
            local_debt_discharge=False,native_authority=False)]))
    paths={Path(__file__).resolve(),ROOT/INV/'decisions/ATCCIPCRealizationNativeProgram.md',
           ROOT/INV/'evidence/atc-ci-pc/ATCCIPCAnchorCertificate.json',
           ROOT/INV/'evidence/atc-ci-pc/CI1PC1ReviewResolution.json',ROOT/'specs/grc-v4-spec.md',
           ROOT/'src/pygrc/models/grc_v4_geometry.py'}
    for module in list(sys.modules.values()):
        name=getattr(module,'__file__',None)
        if name:
            path=Path(name).resolve()
            if path.is_relative_to(ROOT/INV) and path.suffix=='.py':paths.add(path)
    payload['source_bindings']=[dict(path=p.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
                                for p in sorted(paths)]
    payload['record_digest']=r.a.digest(payload)
    return payload


if __name__=='__main__':
    print(json.dumps(run(),indent=2))

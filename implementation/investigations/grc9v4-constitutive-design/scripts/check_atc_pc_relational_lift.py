#!/usr/bin/env python3
"""Revised PC-2 falsification pressure, exact arithmetic, stdout only.

Exhaust each signed-coordinate group separately. Their commuting actions
cover the product by composition; do not call this a Cartesian brute-force
run. No PC-3 target trajectory is executed or used for policy selection.
"""
from fractions import Fraction as F
from itertools import permutations,product
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[4]
INV=Path('implementation/investigations/grc9v4-constitutive-design')
sys.path.insert(0,str(ROOT/INV/'research'))
import atc_pc_relational_lift as l
r=l.r


def decorated(a,b,c,d,e):
    return ((a,b,c,c),(b,a,c,c),(c,c,d,e),(c,c,e,d))


def norm2(z): return sum(x*x for row in z for x in row)


def transform(z,perm,signs):
    return tuple(tuple(signs[i]*signs[j]*z[perm[i]][perm[j]] for j in range(len(perm))) for i in range(len(perm)))


def changed_frame(ps,pt,ss,st):
    base=l.CANONICAL
    edges=lambda es,p,s:tuple(es[k] if sign==1 else tuple(reversed(es[k])) for k,sign in zip(p,s))
    return dict(source=edges(base['source'],ps,ss),target=edges(base['target'],pt,st),
        U=tuple(ps.index(i) for i in (0,1)),V=tuple(ps.index(i) for i in (2,3)),parent=4,children=(4,5),
        lineage=tuple((pt.index(ps[i]),ss[i]*st[pt.index(ps[i])]) for i in range(4)),bridge=pt.index(4))


def covariance_case(z,ps,pt,ss,st,polarity=1):
    expected,_=l.lift(z,polarity=polarity,**l.CANONICAL)
    transformed=transform(z,ps,ss);op=changed_frame(ps,pt,ss,st)
    actual,cs=l.lift(transformed,polarity=polarity,**op)
    r.require(actual==transform(expected,pt,st),'signed edge-coordinate covariance')
    r.require(l.inverse(actual,polarity=polarity,**op)==transformed,'exact inverse in changed coordinates')
    r.require(norm2(actual)==norm2(transformed),'Frobenius isometry in changed coordinates')
    r.require(l.relational_readout(actual,**op)==polarity*cs,'orientation-invariant signed target observable')
    if polarity==1: l.sign_fidelity(transformed,actual,**op)


def coordinate_pressure():
    bases=[decorated(*(int(i==j) for i in range(5))) for j in range(5)]
    def orbit_dimension(n,edges):
        pu=(1,0,2,3,4)[:n];pv=(0,1,3,2,4)[:n];pg=(1,0,3,2,4)[:n]
        actions=(tuple(range(n)),pu,pv,pg)
        return len({frozenset(tuple(sorted((p[i],p[j]))) for p in actions)
                    for i in range(n) for j in range(i,n) if l.control.supported(edges,i,j)})
    r.require(orbit_dimension(4,l.CANONICAL['source'])==5 and orbit_dimension(5,l.CANONICAL['target'])==7,
              'exact decorated source/target dimensions')
    mapped=[l.lift(z,**l.CANONICAL)[0] for z in bases]
    inner=lambda x,y:sum(a*b for row,other in zip(x,y) for a,b in zip(row,other))
    for i in range(5):
        for j in range(5):r.require(inner(bases[i],bases[j])==inner(mapped[i],mapped[j]),'complete Gram isometry')
    p4,p5=tuple(range(4)),tuple(range(5));s4,s5=(1,)*4,(1,)*5
    generators=[]
    for n in (4,5):
        for i in range(n-1):
            p=list(range(n));p[i],p[i+1]=p[i+1],p[i]
            generators.append((tuple(p) if n==4 else p4,tuple(p) if n==5 else p5,s4,s5))
        for i in range(n):
            s=tuple(-1 if j==i else 1 for j in range(n))
            generators.append((p4,p5,s if n==4 else s4,s if n==5 else s5))
    count=0
    for z in bases:
        for polarity in (1,-1):
            for args in generators: covariance_case(z,*args,polarity=polarity);count+=1
    # Exhaust each finite group on a dense signed point. The basis/generator
    # checks above and commuting left/right actions justify every combination.
    dense=decorated(1,2,-3,5,7);source_count=target_count=0
    for ps in permutations(range(4)):
        for ss in product((-1,1),repeat=4):
            covariance_case(dense,ps,p5,ss,s5);source_count+=1
    for pt in permutations(range(5)):
        for st in product((-1,1),repeat=5):
            covariance_case(dense,p4,pt,s4,st);target_count+=1
    base,_=l.lift(dense,**l.CANONICAL)
    a,b,c,d,e=1,2,-3,5,7
    r.require(base==((a,b,0,0,-c),(b,a,0,0,-c),(0,0,d,e,c),(0,0,e,d,c),(-c,-c,c,c,0)),
              'independent canonical matrix oracle')
    swapped=dict(l.CANONICAL,U=(2,3),V=(0,1),children=(5,4))
    r.require(l.lift(dense,**swapped)[0]==base,'unordered child/sector exchange')
    labels={i:'vertex-'+str(13-5*i) for i in range(6)}
    relabel=lambda edges:tuple(tuple(labels[v] for v in edge) for edge in edges)
    op=dict(l.CANONICAL,source=relabel(l.CANONICAL['source']),target=relabel(l.CANONICAL['target']),
            parent=labels[4],children=(labels[4],labels[5]))
    r.require(l.lift(dense,**op)[0]==base,'vertex-label covariance')
    minus,_=l.lift(dense,polarity=-1,**l.CANONICAL)
    r.require(minus!=base and l.inverse(minus,polarity=-1,**l.CANONICAL)==dense,
              'opposite polarity is a distinct equally covariant isometry')
    return dict(decorated_source_basis_count=5,target_decorated_dimension=7,gram_entries_checked=25,
        canonical_matrix_oracle=True,
        signed_generator_basis_cases=count,source_signed_frames_exhausted=source_count,
        target_signed_frames_exhausted=target_count,cartesian_brute_force=False,
        product_coverage='algebraic composition of independent commuting source/target actions',
        child_exchange=True,vertex_relabel=True,polarity_not_fixed_by_covariance=True,
        positive_polarity_fixed_by_sign_fidelity=True,target_observable_checked_in_every_frame=True)


def continuity_domain_pressure():
    cases=[]
    for c in (F(-1,65536),F(0),F(1,65536)):
        source=decorated(F(1,16384),0,c,F(1,16384),0)
        plus,_=l.lift(source,**l.CANONICAL);minus,_=l.lift(source,polarity=-1,**l.CANONICAL)
        l.sign_fidelity(source,plus,**l.CANONICAL)
        r.require(l.relational_readout(minus,**l.CANONICAL)==-c,'negative branch inverts physical readout')
        rejected=False
        try:l.sign_fidelity(source,minus,**l.CANONICAL)
        except r.a.AdmissionError:rejected=True
        r.require(rejected==(c!=0),'nonzero opposite polarity fails; zero branches coincide')
        cases.append(dict(c=c,opposite_polarity_rejected=rejected))
    # Carrier-admitted is not synonymous with being in the five-dimensional
    # event image. Both positive and negative bridge diagonals demonstrate it.
    off_image=[]
    for diagonal in (F(-1,16384),F(1,16384)):
        values=tuple(tuple(diagonal if i==j==4 else F(0) for j in range(5)) for i in range(5))
        carrier=r.exact_carrier('paired_target',values)
        try:l.inverse(carrier.values,token=r._DOMAIN_TOKEN,**l.CANONICAL)
        except r.a.AdmissionError:pass
        else:raise AssertionError('admissible off-image carrier accepted as event preimage')
        r.require(1+r.a.PARAMS['kh']*diagonal>0,'off-image signed example has SPD geometry')
        off_image.append(dict(bridge_diagonal=diagonal,carrier_admitted=True,inverse_image_rejected=True))
    # The preregistered PSD alternative is injective, but does NOT obey this
    # same linear relational readout. A=9q,D=16q,c=q gives c_target=7c/10.
    q=F(1,2**18);source=decorated(9*q,0,q,16*q,0)
    f,g,h=-3*q/5,4*q/5,4*q/25
    psd=((9*q,0,0,0,f),(0,9*q,0,0,f),(0,0,16*q,0,g),(0,0,0,16*q,g),(f,f,g,g,h))
    r.exact_carrier('paired_target',psd)
    readout=l.relational_readout(psd,**l.CANONICAL)
    r.require(readout==7*q/10 and readout!=q,'PSD alternative attenuates fixed target observable')
    r.require(-f*F(5,3)==q and g*F(5,4)==q,'nonlinear alternative still encodes source relation injectively')
    try:l.sign_fidelity(source,psd,**l.CANONICAL)
    except r.a.AdmissionError:pass
    else:raise AssertionError('PSD alternative silently substituted into sign-fidelity contract')
    return dict(sign_cases=cases,admitted_but_off_image=off_image,
        image_dimension=5,target_decorated_dimension=7,image_is_full_ball=False,
        PSD_control_readout_ratio=F(7,10),PSD_control_passes_same_sign_fidelity=False,
        PSD_control_requires_distinct_observable_contract=True,
        PC3_signed_target_continuation_proved=False)


def no_go_pressure():
    pu=(1,0,2,3,4);pv=(0,1,3,2,4);pg=(1,0,3,2,4)
    target=l.CANONICAL['target'];count=0
    for i in range(5):
        for j in range(i,5):
            if not l.control.supported(target,i,j): continue
            z=[[0]*5 for _ in range(5)];z[i][j]=z[j][i]=1;z=tuple(map(tuple,z))
            u=transform(z,pu,(1,)*5);v=transform(z,pv,(1,)*5);uv=transform(z,pg,(1,)*5)
            r.require(all(z[a][b]-u[a][b]-v[a][b]+uv[a][b]==0 for a in range(5) for b in range(5)),
                      'target has no double-odd representation');count+=1
    mixed=((0,0,1,-1),(0,0,-1,1),(1,-1,0,0),(-1,1,0,0))
    negative=tuple(tuple(-x for x in row) for row in mixed)
    r.require(transform(mixed,pu[:4],(1,)*4)==negative and transform(mixed,pv[:4],(1,)*4)==negative,
              'source mixed mode odd under either sector swap')
    r.require(transform(mixed,pg[:4],(1,)*4)==mixed,'source mixed mode fixed by product')
    try: l.lift(mixed,**l.CANONICAL)
    except r.a.AdmissionError: pass
    else: raise AssertionError('mixed mode silently averaged into lossless map')
    return dict(target_symmetric_star_basis_count=count,target_double_odd_multiplicity=0,
        source_mixed_mode=mixed,rejected_by_decorated_lift=True,
        ceiling='no injective equivariant carrier-only map on full unrestricted source space with this fixed target/action, even nonlinear')


def negative_pressure():
    z=decorated(1,2,3,4,5);target,_=l.lift(z,**l.CANONICAL);rejected=[]
    def reject(name,fn):
        try:fn()
        except r.a.AdmissionError:rejected.append(name)
        else:raise AssertionError('unexpected admission: '+name)
    def change(matrix,i,j,x):
        rows=[list(row) for row in matrix];rows[i][j]=x;return tuple(map(tuple,rows))
    reject('symmetry_breaking_cross_mode',lambda:l.lift(change(change(z,0,2,4),2,0,4),**l.CANONICAL))
    reject('unpaired_diagonal',lambda:l.lift(change(z,0,0,2),**l.CANONICAL))
    reject('false_lineage_orientation',lambda:l.lift(z,**dict(l.CANONICAL,lineage=((0,-1),(1,1),(2,1),(3,1)))))
    reject('bool_lineage_sign',lambda:l.lift(z,**dict(l.CANONICAL,lineage=((0,True),(1,1),(2,1),(3,1)))))
    reject('noninjective_lineage',lambda:l.lift(z,**dict(l.CANONICAL,lineage=((0,1),(0,1),(2,1),(3,1)))))
    reject('wrong_bridge',lambda:l.lift(z,**dict(l.CANONICAL,bridge=0)))
    reject('wrong_child_attachment',lambda:l.lift(z,**dict(l.CANONICAL,children=(5,4))))
    reject('overlapping_sectors',lambda:l.lift(z,**dict(l.CANONICAL,V=(1,3))))
    reject('off_image_bridge_diagonal',lambda:l.inverse(change(target,4,4,1),**l.CANONICAL))
    reject('off_image_bridge_coupling',lambda:l.inverse(change(change(target,0,4,4),4,0,4),**l.CANONICAL))
    reject('unwitnessed_interval_domain',lambda:l.lift(tuple(tuple(r.I(x) for x in row) for row in z),**l.CANONICAL))
    return rejected


def psd_pressure():
    # Exact PSD source: sector eigenvalues 2,2 and 2 +/- 2c with c=1.
    z=decorated(2,0,1,2,0);t,_=l.lift(z,**l.CANONICAL)
    minor=t[0][0]*t[4][4]-t[0][4]**2
    r.require(minor==-1,'linear isometry need not preserve PSD')
    # Optional nonlinear control, checked through exact squares: no sampling
    # eigensolver or tolerance substitutes for the Schur/norm inequalities.
    cases=0
    for s,t in product((F(0),F(1,1000),F(1),F(1000)),repeat=2):
        A,D=s*s,t*t
        for rho in (F(-1),F(-1,2),F(0),F(1,2),F(1)):
            c=rho*s*t/2;total=A+D
            f2=c*c*A/total if total else 0;g2=c*c*D/total if total else 0
            h=4*c*c/total if total else 0
            r.require(A*D>=4*c*c,'PSD input')
            schur=h-(2*f2/A if A else 0)-(2*g2/D if D else 0)
            r.require(schur==0 and 4*f2+4*g2+h*h<=8*c*c,'nonlinear PSD control is nonexpansive')
            cases+=1
    return dict(linear_PSD_preservation=False,exact_negative_principal_minor=minor,
        nonlinear_control_squared_algebra_cases=cases,
        nonlinear_control_selected=False,nonlinear_zero_sector_boundaries_included=True,
        qualifier='PSD is not the declared signed-carrier admission; geometry SPD remains certified')


def run():
    coords=coordinate_pressure();nog=no_go_pressure();negative=negative_pressure();psd=psd_pressure()
    continuity=continuity_domain_pressure()
    before,reset=r.fixtures();after,Z,_,_=r.pc_step(before,r.diagonal_z(F(1,16384)))
    resetZ=r.diagonal_z(F(1,24576));roles={}
    for name,z in (('current',Z),('reset',resetZ)):
        target,receipt=l.event_carrier(z)
        restricted,restriction=l.control.event_carrier(z)
        zero,erasure=l.control.event_carrier(z,l.control.RESET)
        c=receipt['relational_scalar']
        minor=target.values[0][0]*target.values[4][4]-c.square()
        if name=='current': r.require(c.lo>0 and minor.hi<0,'actual live carrier becomes indefinite, geometry remains SPD')
        else: r.require(c.lo==c.hi==0 and all(l.equal(x,y) for a,b in zip(target.values,restricted.values) for x,y in zip(a,b)),
                        'zero-cross-memory reset reduces to restriction')
        roles[name]=dict(lossless=receipt,projection_control=restriction,whole_reset_control=erasure,
            principal_minor=minor,target_geometry_lower=1-r.RHO,
            complete_target_readmission_claimed=False)
    value=r.a.encode(dict(schema='grcv4_atc_pc_relational_lift_v1',
        status='revised_PC2_lossless_decorated_candidate_survives_pressure_pending_review',
        proposed_policy=l.POLICY,supersedes_selection=l.control.POLICY,
        projection_status='valid_explicit_loss_control_not_preferred_on_decorated_domain',
        selection_basis='relational sign-fidelity condition c_target=c_source resolves polarity beyond covariance',
        continuity_principle_is_new_constitutive_authority=True,continuity_and_domain_pressure=continuity,
        domain_semantics=dict(event_carriers='exact decorated symmetric target-star ball; norm<=1/3072; H=I+(3/4)Z SPD',
            PSD_required=False,ordinary_PSD_reachability='subset of PSD intersection; not every PSD carrier proved reachable',
            event_image='proper five-dimensional subset of seven-dimensional decorated carrier ball',
            PC3_obligation='prove continuation from signed event image in a justified invariant signed domain',
            sole_PC3_policy=l.POLICY,PSD_fallback_allowed_in_PC3=False,
            failure_route='retain genuine PC3 failure; PSD control is not a fallback; any successor requires a separately preregistered relational-continuity contract and new bounded PC-2b investigation'),
        uniqueness_from_covariance_claimed=False,coordinate_pressure=coords,no_go=nog,
        rejected_inputs=negative,PSD_pressure=psd,roles=roles,source_postbeat=after.payload(),
        mathematical_scope='fixed decorated 2+2 domain; carrier/geometry admission only',
        PC3_completed=False,native_ATC_executed=False,ATC2_closed=False,graph_admitted=False,scientific_acceptance=False,
        claim_updates=[dict(claim_id='ATC-PC-CARRIER-02',status='projection_valid_selection_superseded',
                            claim_class='conditional',local_debt_discharge=False),
                       dict(claim_id='ATC-PC-CARRIER-03',status='lossless_sign_fidelity_signed_domain_candidate_pending_review',
                            claim_class='conditional',profile_scope=['A_PC'],
                            debt_refs=['ATC7-DB-15','ATC7-DB-06','ATC7-DB-16','ATC7-DB-26'],
                            open_front=['ATC7-DB-14','ATC7-DB-16','ATC7-DB-19'],
                            local_debt_discharge=False,native_authority=False)]))
    paths={Path(__file__).resolve(),ROOT/INV/'decisions/ATCCIPCRealizationNativeProgram.md',
        ROOT/INV/'evidence/atc-ci-pc/ATCCIPCAnchorCertificate.json',
        ROOT/INV/'evidence/atc-ci-pc/ATCPCCarrierEventCertificate.json',
        ROOT/INV/'evidence/atc-ci-pc/PC2-RelationalLift-PressureReview.md',ROOT/'src/pygrc/models/grc_v4_geometry.py'}
    paths.add(ROOT/INV/'evidence/atc-ci-pc/PC2-SignFidelity-And-SignedDomain-Review.md')
    paths.add(ROOT/INV/'evidence/atc-ci-pc/PC3-SolePolicy-ScopeReview.md')
    for module in list(sys.modules.values()):
        path=getattr(module,'__file__',None)
        if path:
            p=Path(path).resolve()
            if p.is_relative_to(ROOT/INV) and p.suffix=='.py': paths.add(p)
    value['source_bindings']=[dict(path=p.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(paths)]
    value['record_digest']=r.a.digest(value)
    return value


if __name__=='__main__':
    print(json.dumps(run(),indent=2))

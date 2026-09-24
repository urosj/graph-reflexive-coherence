"""Revised PC-2: lossless relational lift on the exact decorated 2+2 domain.

Research only. Lineage transports the within-sector blocks; incidence moves
the single cross-sector scalar to bridge couplings. The bridge diagonal is
zero. Relational sign fidelity c_target=c_source selects the plus polarity;
this is new cross-topology continuity authority, not a consequence of
covariance alone. No target dynamics enter policy selection.
"""
from fractions import Fraction as F
import atc_pc_carrier_event as control
r=control.r
POLICY='pc_star_fission_relational_lift_lossless_v1'


def incidence(vertex,edge):
    return int(edge[1]==vertex)-int(edge[0]==vertex)


def equal(x,y):
    return r.same(x,y) if isinstance(x,r.I) else x==y


def diagram(source,target,U,V,parent,children,lineage,bridge):
    """Validate the actual fission and signed lineage, not just dimensions."""
    r.require(len(source)==4 and len(target)==5 and len(U)==len(V)==2,'exact 2+2 fission')
    r.require(set(U)|set(V)==set(range(4)) and not set(U)&set(V),'complete disjoint sectors')
    r.require(len(children)==2 and children[0]!=children[1],'distinct children')
    r.require(type(bridge) is int and 0<=bridge<5 and set(target[bridge])==set(children),'child-child bridge')
    r.require(len(lineage)==4 and all(type(j) is int and 0<=j<5 and type(s) is int and s in (-1,1)
                                    for j,s in lineage),'signed old-edge lineage')
    r.require({j for j,s in lineage}==set(range(5))-{bridge},'bijective surviving-edge lineage')
    r.require(all(len(edge)==2 and edge[0]!=edge[1] for edge in (*source,*target)),'nonloop edges')
    sigma=tuple(incidence(parent,edge) for edge in source)
    r.require(all(s in (-1,1) for s in sigma),'source parent star')
    leaves=[next(v for v in edge if v!=parent) for edge in source]
    r.require(len(set(leaves))==4 and not set(leaves)&set(children),'four surviving leaves distinct from children')
    factors={}
    for sector,child in zip((U,V),children):
        for i in sector:
            j,sign=lineage[i]
            r.require(set(target[j])=={leaves[i],child},'incidence-consistent leaf lineage')
            tau=incidence(child,target[j])
            r.require(sign==sigma[i]*tau,'lineage orientation inconsistent with endpoint transport')
            factors[i]=tau*incidence(child,target[bridge])
    return sigma,factors


CANONICAL=dict(source=r.p.SOURCE,target=r.p.TARGET,U=(0,1),V=(2,3),
               parent=4,children=(4,5),lineage=tuple((i,1) for i in range(4)),bridge=4)


def matrix_check(z,n,token):
    r.require(len(z)==n and all(len(row)==n for row in z),'complete carrier matrix')
    exact=all(type(x) in (int,F) for row in z for x in row)
    r.require(exact or (token is r._DOMAIN_TOKEN and all(isinstance(x,r.I) for row in z for x in row)),
              'exact input or internal constructive carrier witness required')
    r.require(all(equal(z[i][j],z[j][i]) for i in range(n) for j in range(n)),'symmetric carrier')


def source_form(z,sigma,U,V):
    """Exact invariant form in parent-normalized coordinates, not a fit."""
    normalized=tuple(tuple(sigma[i]*sigma[j]*z[i][j] for j in range(4)) for i in range(4))
    for sector in (U,V):
        i,j=sector
        r.require(equal(normalized[i][i],normalized[j][j]),'decorated diagonal symmetry')
    c=normalized[U[0]][V[0]]
    r.require(all(equal(normalized[i][j],c) for i in U for j in V),'exact trivial cross-sector mode required')
    # Summation explicitly implements incidence normalization; integer
    # arithmetic stays rational, and no interval averaging infers symmetry.
    return sum((normalized[i][j] for i in U for j in V),c*0)*F(1,4)


def lift(z,*,polarity=1,token=None,**operation):
    r.require(type(polarity) is int and polarity in (-1,1),'declared relational polarity')
    matrix_check(z,4,token)
    sigma,factors=diagram(**operation)
    U,V,lineage,bridge=(operation[k] for k in ('U','V','lineage','bridge'))
    c=source_form(z,sigma,U,V)
    zero=c*0;out=[[zero for _ in range(5)] for _ in range(5)]
    for sector in (U,V):
        for i in sector:
            j,si=lineage[i]
            for k in sector:
                l,sk=lineage[k];out[j][l]=si*sk*z[i][k]
            out[j][bridge]=out[bridge][j]=polarity*factors[i]*c
    return tuple(map(tuple,out)),c


def relational_readout(z,*,token=None,**operation):
    """Orientation-invariant target observable, independent of chosen polarity.

    Defined on the target matrix, not only on the lift image. This observable
    is not by itself a carrier-admission or inverse-image certificate.
    """
    matrix_check(z,5,token)
    _,factors=diagram(**operation)
    U,V,lineage,bridge=(operation[k] for k in ('U','V','lineage','bridge'))
    return sum((factors[i]*z[lineage[i][0]][bridge] for i in (*U,*V)),z[bridge][bridge]*0)*F(1,4)


def sign_fidelity(source_values,target_values,*,token=None,**operation):
    """Executable continuity condition in addition to covariance/isometry.

    Exact identities follow from the declared linear law. For internal typed
    enclosures this checks consistency, not physical equality inferred from
    overlapping interval boxes.
    """
    matrix_check(source_values,4,token)
    sigma,_=diagram(**operation)
    cs=source_form(source_values,sigma,operation['U'],operation['V'])
    ct=relational_readout(target_values,token=token,**operation)
    r.require(equal(cs,ct),'event must preserve the incidence-normalized signed relational observable')
    return dict(source_observable=cs,target_observable=ct,condition='c_target=c_source',passed=True)


def inverse(z,*,polarity=1,token=None,**operation):
    """Inverse on the image; reject arbitrary target histories off that image."""
    r.require(type(polarity) is int and polarity in (-1,1),'declared relational polarity')
    matrix_check(z,5,token)
    sigma,factors=diagram(**operation)
    U,V,lineage,bridge=(operation[k] for k in ('U','V','lineage','bridge'))
    c=polarity*relational_readout(z,token=token,**operation)
    out=[[c*0 for _ in range(4)] for _ in range(4)]
    for sector in (U,V):
        for i in sector:
            for j in sector:
                ti,si=lineage[i];tj,sj=lineage[j];out[i][j]=si*sj*z[ti][tj]
    for i in U:
        for j in V: out[i][j]=out[j][i]=sigma[i]*sigma[j]*c
    out=tuple(map(tuple,out))
    rebuilt,_=lift(out,polarity=polarity,token=token,**operation)
    r.require(all(equal(rebuilt[i][j],z[i][j]) for i in range(5) for j in range(5)),
              'target carrier outside relational-lift image')
    return out


def event_carrier(carrier):
    r.require(type(carrier) is r.Carrier and carrier.graph=='paired_source','admitted paired source carrier')
    values,c=lift(carrier.values,token=r._DOMAIN_TOKEN,**CANONICAL)
    target=r.Carrier('paired_target',values,POLICY+':'+carrier.basis,token=r._DOMAIN_TOKEN)
    fidelity=sign_fidelity(carrier.values,target.values,token=r._DOMAIN_TOKEN,**CANONICAL)
    recovered=inverse(target.values,token=r._DOMAIN_TOKEN,**CANONICAL)
    r.require(all(equal(x,y) for row,other in zip(carrier.values,recovered) for x,y in zip(row,other)),
              'actual role roundtrip enclosure identity')
    source_norm=r.norm_upper(x for row in carrier.values for x in row)
    target_norm=r.norm_upper(x for row in values for x in row)
    r.require(source_norm==target_norm,'actual interval norm bound is preserved')
    receipt=dict(policy_id=POLICY,channel='carrier',disposition='lossless_relational_transport_on_decorated_domain',
        source_graph='paired_source',target_graph='paired_target',source_carrier=carrier.values,
        source_digest=r.a.digest(r.a.encode(carrier.values)),target_carrier=values,
        target_digest=r.a.digest(r.a.encode(values)),relational_scalar=c,
        recovered_source_digest=r.a.digest(r.a.encode(recovered)),
        source_norm_upper=source_norm,target_norm_upper=target_norm,
        information_loss='exactly_zero_on_declared_domain',bridge_diagonal='exact_zero',
        bridge_couplings='inherited_parent_relation_via_target_incidence',
        polarity=1,polarity_resolved_by='incidence_normalized_signed_relation_continuity',
        continuity_principle_is_new_constitutive_authority=True,relational_sign_fidelity=fidelity,
        event_carrier_domain='decorated_signed_target_star_Frobenius_ball_with_SPD_geometry',
        event_image_dimension=5,target_decorated_dimension=7,event_image_is_full_ball=False,
        generic_lossless_authority=False,PSD_preservation_claimed=False,
        W_disposition='separate channel: old edges exact lineage, new bridge W=1',
        target_dynamic_restoration_claimed=False,native_authority=False)
    return target,receipt

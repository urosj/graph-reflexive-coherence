"""Independent fixed-row A_CI_PC joint-root bounds on saved finite operands.

Reuse the A fixed-row scalar equations, adding fixed old Z to the joint map.
The translated map has the same derivative as CI at fixed C,W,Z. Carrier
admission and the translated self-map are checked separately; no CI acceptance
is transferred. FLINT/Arb enclosures, never production roots or flat solves.
"""
from copy import deepcopy
from flint import arb, arb_mat, ctx
import p984g_aci_investigation as ci
import p984g_aci_staged as staged
import p984g_apc_investigation as pc

b=__import__('p984b_acipc_runtime').b
q,a,lo,hi=pc.q,pc.a,pc.lo,pc.hi
SELF=b.HERE+'p984g_acipc.py'
PREPARED=b.BASE+'larger-graph-examples/A_CI_PC.json'
BITS=192
ROLES=('current','reset')


def carrier(subject,role,m):
    z=subject['roles'][role]['Z_4']
    if isinstance(z,dict):
        diagonal=pc.carrier(subject,role,m)
        return [[diagonal[i] if i==j else q(0) for j in range(m)] for i in range(m)]
    b.require(len(z)==m*m,'whole carrier dimension')
    return [[q(z[i*m+j]) for j in range(m)] for i in range(m)]


def ci_operand(subject,role):
    p=subject['profile'];params=p['params_resolved'];real=params['realization']
    b.require(p['identity_payload']['profile_family_id']=='A_CI_PC'
              and real['schema_version']=='grcv4-cipc-params-v1'
              and real['rho_inst']==1,'fixed composite law')
    out=deepcopy(subject)
    out['profile']['identity_payload']['profile_family_id']='A_CI'
    out['profile']['params_resolved']['realization']['schema_version']='grcv4-ci-params-v1'
    out['roles'][role]['Z_4']=None
    return out


def local_bounds(subject,role):
    fixed=ci_operand(subject,role)
    bounds=ci.certificate(fixed,role,1)['bounds']
    p=subject['profile']['params_resolved'];m=len(subject['graph']['edges'])
    z=carrier(subject,role,m);r=q(bounds['radius']);kh=abs(q(p['geometry']['kappa_H']))
    pc_operand=deepcopy(subject)
    pc_operand['profile']['identity_payload']['profile_family_id']='A_PC'
    pc_operand['profile']['params_resolved']['realization']['schema_version']='grcv4-pc-params-v1'
    M,wl,wu,R,tau=pc.chart(pc_operand)
    _,_,C,W,_=ci.operands(fixed,role)
    zn=ci.norm([x for row in z for x in row])
    pc.admit_state(C,W,[x for row in z for x in row],(M,wl,wu,R,tau))
    b.require(all(z[i][j]==z[j][i] for i in range(m) for j in range(i)),'symmetric carrier')
    B,*_=ci.operands(fixed,role);mask=abs(B).T@abs(B)
    b.require(all(z[i][j]==0 for i in range(m) for j in range(m) if not mask[i,j]),'star-supported carrier')
    displacement=q(bounds['displacement_upper'])+kh*zn
    b.require(displacement<=r,'translated composite self-map')
    bounds=dict(bounds,displacement_upper=str(displacement),carrier_norm_upper=str(zn),
        carrier_radius=str(R),root_radius=str(r),fixed_old_carrier=True)
    return bounds


def model(subject,role):
    result=staged.model(ci_operand(subject,role),role)
    result['params']=subject['profile']['params_resolved']
    result['z']=carrier(subject,role,len(result['w']))
    return result


def image(md,flat,*,represented=False):
    n=len(md['w']);h=staged.eye(n);p=md['p']
    zeta,kh=q(p['zeta_A']),q(md['params']['geometry']['kappa_H'])
    source=staged.eye(n)*0
    for i in range(n):
        for j in range(n):
            k=q(float(md['mask'][i,j]))
            if represented:
                star=staged.rn(k*q(flat[i])*q(flat[j]))
                inc=staged.rn(zeta*q(star))
                mixed=staged.rn(md['z'][i][j]+q(inc))
                h[i,j]=a(staged.rn(q(int(i==j))+kh*q(mixed)))
                source[i,j]=a(inc)
            else:
                source[i,j]=a(zeta*k)*flat[i,0]*flat[j,0]
                h[i,j]+=a(kh)*(a(md['z'][i][j])+source[i,j])
    return h,source


def analytic(md,h,trial=None):
    out=staged.analytic(md,h,trial)
    out['generated'],out['source']=image(md,out['flat'])
    return out


def enclosed_root(subject,role):
    md=model(subject,role);bounds=local_bounds(subject,role);n=len(md['w'])
    identity=staged.eye(n)
    ref=analytic(md,identity)
    h1=ref['generated'];one=analytic(md,h1)
    displ=staged.norm(h1-identity);contraction=q(bounds['contraction_upper'])
    tail=contraction*displ/(1-contraction)
    jtail=q(bounds['current_lipschitz_upper'])*tail
    currents=[staged.feasible.inflate(one['J'][i,0],jtail) for i in range(n)]
    return md,bounds,dict(H=h1,J=currents,geometry_tail=tail,current_tail=jtail,reference=ref)


def first_step(subject,role,dt):
    md,bounds,root=enclosed_root(subject,role)
    resources=[a(c)-a(dt)*sum((int(x)*j for x,j in zip(row,root['J'])),arb(0))
               for c,row in zip(md['c'],md['bv'])]
    return dict(role=role,local_joint_bounds=bounds,
        current_tail_upper=str(root['current_tail']),geometry_tail_upper=str(root['geometry_tail']),
        resources=[dict(lower=str(lo(x)),upper=str(hi(x))) for x in resources],
        minimum_lower=str(min(lo(x) for x in resources)),
        negative_vertices=[subject['graph']['live_node_ids'][i] for i,x in enumerate(resources) if hi(x)<0],
        unresolved_vertices=[subject['graph']['live_node_ids'][i] for i,x in enumerate(resources) if lo(x)<=0<=hi(x)],
        native_steps=0,native_events=0,uniform_trajectory_enclosure=False)

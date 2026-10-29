"""Independent composite-ball bounds and vertex-reduced C_CI+PC feasibility.

Only FLINT/Arb equations are evaluated here; native roots and steps are not
inputs. Old Z is fixed inside the joint solve and gain two is never folded
into the instantaneous source. First-step signs are pointwise, not a uniform
trajectory enclosure or a native execution result.
"""
import argparse
import json
import lzma
import time
from flint import arb,ctx
import p984g_cpc as pc
import p984g_cos_bounds as iv

b,q,a,lo,hi=pc.b,iv.q,iv.a,iv.lo,iv.hi
SELF=b.HERE+'p984g_ccipc.py'
PREPARED=b.BASE+'larger-graph-examples/C_CI_PC.json'
RESULTS=b.BASE+'P9-8.4g-CCIPCOriginalFeasibility.json.xz'
BITS=192
ROLES=('current','reset')


def frobenius_upper(matrix):
    squared=sum((iv.magnitude(matrix[i,j])**2 for i in range(matrix.nrows())
                 for j in range(matrix.ncols())),q(0))
    return hi(a(squared).sqrt())


def whole_chart(subject):
    bv,params=pc.graph_math.graph_data(subject)
    p,real,g=(params[k] for k in ('candidate','realization','geometry'))
    identity=subject['profile']['identity_payload']
    b.require(identity['profile_family_id']=='C_CI_PC' and identity['composition_gain']==2
        and real['schema_version']=='grcv4-cipc-params-v1' and real['rho_inst']==1,
        'composite declaration required')
    prefix='pc_compact_base_chart_v1:'
    name=real['source_envelope_id'];b.require(name.startswith(prefix),'compact chart required')
    values=[float.fromhex(x) for x in name[len(prefix):].split(':')]
    b.require(len(values)==3 and name==prefix+':'.join(x.hex() for x in values),'canonical chart')
    M,wl,wu=map(q,values);R=q(real['radius']);gain=abs(q(g['kappa_H']))
    prefix='ci_reference_frobenius_ball_v1:';domain=real['contraction_domain_id']
    b.require(domain.startswith(prefix),'reference ball required')
    radius=q(float.fromhex(domain[len(prefix):]));lower,upper=1-radius,1+radius
    b.require(M>0 and wl==wu==1 and R>0 and q(real['tau_PC'])>0 and 0<=radius<1
        and radius>=2*gain*R,'strict composite B_2R coverage')
    b.require(p['transport_id']=='C-HM-STIFFNESS-BASELINE-v1'
        and p['potential_evaluator_id']=='quadratic_site_potential_zero_derivative_v1'
        and g['star_cover_id']=='vertex_star_exact_overlap_v1'
        and g['overlap_normalization_id']=='edge_multiplicity_inverse_sqrt_v1'
        and g['candidate_adapter_id']=='candidate_c_exact_star_adapter_v1'
        and real['writer_id']=='zero_order_hold_exponential_v1'
        and real['carrier_norm_id']=='symmetric_star_frobenius_v1'
        and p['C_ref']>0 and p['tau_C']>=0,'equation hypotheses')
    n,m=bv.shape;dnorm=q(2*max(sum(abs(int(x)) for x in row) for row in bv))
    gap=lower/q(n*(n-1))-q(p['Lambda_C'])
    beta=q(p['zeta_C'])*q(p['chi_C'])
    b.require(gap>0 and q(p['Lambda_C'])>0 and 0<=beta<1 and p['zeta_C']>=0,'selector/feedback hypotheses')
    with ctx.workprec(BITS):
        t=hi(a(abs(q(p['kappa_M_C']))).exp());response=hi(a(upper/lower).sqrt())
        margin=1-beta*response;b.require(margin>0,'current inverse margin')
        baseline_lip=abs(q(p['eta_C'])*q(p['kappa_Phi_C']))*t*dnorm*hi(a(dnorm).sqrt())*M
        baseline=baseline_lip*upper
        response_lip=response**2*q(p['tau_C'])*t*dnorm
        current=baseline/margin
        current_lip=baseline_lip/margin+baseline*beta*response_lip/margin**2
        flat=abs(q(p['chi_C']))*response*current/lower
        flat_lip=abs(q(p['chi_C']))*(response*current/lower**2
            +(response_lip*current+response*current_lip)/lower)
        source=q(p['zeta_C'])*flat**2
        contraction=2*gain*q(p['zeta_C'])*flat*flat_lip
        displacement=gain*(R+source)
        condition=(1+beta*response)/margin
    limit=q(params['solver']['conditioning_limit'])
    b.require(source<R and contraction<1 and displacement<=radius
        and condition<=limit and upper/lower<=limit,'whole-chart composite certificate failed')
    return bv,params,{k:str(v) for k,v in dict(resource_norm_upper=M,carrier_radius=R,
        root_radius=radius,hodge_lower=lower,hodge_upper=upper,selector_gap_lower=gap,
        current_upper=current,current_lipschitz_upper=current_lip,flat_upper=flat,
        flat_lipschitz_upper=flat_lip,source_upper=source,source_slack=R-source,
        contraction_upper=contraction,displacement_upper=displacement,
        current_condition_upper=condition).items()}


def root(subject,role):
    bv,params,bounds=whole_chart(subject);p=params['candidate'];n,m=bv.shape
    cs=list(map(q,subject['roles'][role]['C']));z=pc.carrier(subject,role,m)
    b.require(subject['roles'][role]['W_A'] is None and len(cs)==n and min(cs)>=0
        and sum((x*x for x in cs),q(0))<=q(bounds['resource_norm_upper'])**2
        and sum((x*x for row in z for x in row),q(0))<=q(bounds['carrier_radius'])**2
        and all(z[i][j]==z[j][i] for i in range(m) for j in range(i)),'actual chart membership')
    bm=iv.matrix(bv);c=iv.matrix([[x] for x in cs]);identity=iv.eye(m)
    overlap=iv.matrix(abs(bv)).transpose()*iv.matrix(abs(bv))/2
    support=[(i,j) for i in range(m) for j in range(m) if not overlap[i,j].is_zero()]
    b.require(all(z[i][j]==0 for i in range(m) for j in range(m) if overlap[i,j].is_zero()),'old carrier star support')
    gain=a(params['geometry']['kappa_H']);base=identity+gain*iv.matrix(z);h=identity
    mean=sum(cs,q(0))/n;t=(a(p['kappa_M_C'])*(a(mean)/a(p['C_ref'])).tanh()).exp()
    contraction=q(bounds['contraction_upper'])
    for index in range(12):
        b.require(frobenius_upper(h-identity)<=q(bounds['root_radius']),'trial outside certified root ball')
        current,readback,flat,domain=iv.real_read(bm,c,h,p,t)
        source=iv.eye(m)*0
        for i,j in support:source[i,j]=a(p['zeta_C'])*overlap[i,j]*flat[i,0]*flat[j,0]
        following=base+gain*source
        residual=frobenius_upper(h-following);error=residual/(1-contraction)
        if error<q('1/1000000000000000000000000000000'):
            padding=q(bounds['current_lipschitz_upper'])*error
            currents=[arb(current[i,0].mid(),current[i,0].rad()+a(padding)) for i in range(m)]
            return dict(b=bm,c=cs,J=currents,
                H=h,source=source,readback=readback,flat=flat,bounds=bounds,
                iterations=index+1,geometry_error=error,current_tail=padding)
        h=type(h)([[arb(following[i,j].mid()) for j in range(m)] for i in range(m)])
    raise ValueError('independent root enclosure unresolved')


def first_step(subject,role,dt):
    started=time.monotonic()
    with ctx.workprec(BITS):
        value=root(subject,role);bm=value['b'];currents=value['J']
        after=[a(c)-a(dt)*sum((bm[i,j]*currents[j] for j in range(bm.ncols())),arb(0))
            for i,c in enumerate(value['c'])]
        negative=[dict(vertex=subject['graph']['live_node_ids'][i],lower=str(lo(x)),upper=str(hi(x)))
            for i,x in enumerate(after) if hi(x)<0]
        unresolved=[subject['graph']['live_node_ids'][i] for i,x in enumerate(after) if lo(x)<0<=hi(x)]
        encode=lambda values:[dict(lower=str(lo(x)),upper=str(hi(x))) for x in values]
        result=dict(subject_digest=b.digest(subject),role=role,dt=dt,whole_chart=value['bounds'],
            iterations=value['iterations'],root_geometry_error_upper=str(value['geometry_error']),
            root_current_tail_upper=str(value['current_tail']),current=encode(currents),
            next_resources=encode(after),negative_resources=negative,unresolved_resources=unresolved,
            first_step_nonnegative=not negative and not unresolved)
    return dict(result,seconds=time.monotonic()-started)


def calculate(declaration):
    return [dict(graph=graph,**first_step(declaration[graph],role,
        declaration['selected_configuration']['ordinary_dt'])) for graph in ('source','target') for role in ROLES]


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=('chart','run'))
    args=parser.parse_args();declaration=b.read(PREPARED)
    if args.action=='chart':
        print(json.dumps({graph:whole_chart(declaration[graph])[2] for graph in ('source','target')},indent=2))
    else:
        names={SELF,PREPARED,pc.SELF,pc.graph_math.SELF,iv.SELF,b.HERE+'test_p984g_ccipc.py'}
        refs=b.bind(names);rows=[]
        for graph in ('source','target'):
            for role in ROLES:
                row=dict(graph=graph,**first_step(declaration[graph],role,declaration['selected_configuration']['ordinary_dt']))
                rows.append(row);print(json.dumps({k:row[k] for k in ('graph','role','iterations','seconds','first_step_nonnegative','negative_resources','unresolved_resources')}),flush=True)
        b.check_bindings(refs)
        record=b.seal(dict(schema='p984g-ccipc-original-feasibility-v1',family='C_CI_PC',source_bindings=refs,
            precision_bits=BITS,scalar_backend='FLINT_rational_Arb',cases=rows,
            ready_for_native=all(r['first_step_nonnegative'] for r in rows),native_steps=0,native_events=0,
            user_accepted=False,aggregate_closed=False,uniform_trajectory_enclosure=False))
        with (b.ROOT/RESULTS).open('xb') as stream:stream.write(lzma.compress(json.dumps(record,separators=(',',':')).encode()+b'\n'))

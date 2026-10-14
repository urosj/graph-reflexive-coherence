"""Derived A_CI allocation companion and interval-input joint-root feasibility."""
import argparse
from copy import deepcopy
import hashlib
import json
from flint import arb, ctx, fmpq_mat
import p984g_aci_investigation as prior
import prepare_p983_all_realizations as prepared

ROOT,BASE,HERE=prior.ROOT,prior.BASE,prior.HERE
SELF=HERE+'p984g_aci_feasibility.py'
TEST=HERE+'test_p984g_aci_feasibility.py'
PLAN=BASE+'P9-8.4g-ACIFeasibilityPlan.md'
NOTE=BASE+'P9-8.4g-ACIFeasibility.md'
RESULTS=BASE+'P9-8.4g-ACIFeasibilityResults.json'
SHARES=('5/16','5/16','3/8')
DEFICIT='1/1024'
q,lo,hi,require=prior.q,prior.lower,prior.upper,prior.require


def a(x):
    return x if isinstance(x,arb) else arb(q(x))


def inflate(x,r):
    return x+arb(0,a(r))


def norm(xs):
    return prior.norm([max(abs(lo(x)),abs(hi(x))) for x in xs])


def square(x):
    # Arb's general power on a zero-crossing ball can return NaN. Use the
    # exact endpoint range of the real square, not exp(2*log(x)).
    left,right=lo(x),hi(x)
    low=q(0) if left<=0<=right else min(left*left,right*right)
    return a(low).union(a(max(left*left,right*right)))


def pack(xs):
    return [dict(lower=str(lo(x)),upper=str(hi(x))) for x in xs]


def descriptors(subject,c,w):
    nodes=subject['graph']['live_node_ids'];index={n:i for i,n in enumerate(nodes)}
    numerator=[[arb(0) for _ in range(3)] for _ in nodes]
    denominator=[[arb(0) for _ in range(3)] for _ in nodes]
    require(len(c)==len(nodes) and len(w)==len(subject['graph']['edges']),'box coordinate coverage')
    require(all(lo(x)>=0 for x in c) and all(lo(x)>0 for x in w),'nonnegative C / positive W boxes')
    for k,e in enumerate(subject['graph']['edges']):
        for end,other in ((e['tail'],e['head']),(e['head'],e['tail'])):
            i,j=index[end['node_id']],index[other['node_id']];row=(end['port']-1)//3
            numerator[i][row]+=w[k]*(c[j]-c[i]);denominator[i][row]+=w[k]
    return [[x/y if not y.is_zero() else arb(0) for x,y in zip(n,d)] for n,d in zip(numerator,denominator)]


def drive(p,ends,c,rows,j):
    out=[]
    for k,(u,v) in enumerate(ends):
        exponent=-(a(p['alpha'])*(c[u]+c[v])+a(p['beta'])*sum((square(x-y) for x,y in zip(rows[u],rows[v])),arb(0))+a(p['gamma'])*square(j[k]))/2
        g=exponent.exp()
        require(lo(g)>q(p['W_floor']),'uniform inactive floor unproved')
        out.append(g)
    return out


def joint_box(subject,role,c=None,w=None):
    """Uniform version of the prior proof, not a point bound reused on a box."""
    b,ends,cs,ws,_=prior.operands(subject,role)
    c=[a(x) for x in cs] if c is None else c
    w=[a(x) for x in ws] if w is None else w
    params=subject['profile']['params_resolved'];p=params['candidate']
    # Validate the same fixed recipe/domain before extending its operands.
    prior.certificate(subject,role,1)
    r=q(float.fromhex(params['realization']['contraction_domain_id'].split(':',1)[1]))
    rows=descriptors(subject,c,w);dc=[c[u]-c[v] for u,v in ends]
    phi=[arb(0) for _ in c]
    for (u,v),weight,d in zip(ends,w,dc):
        term=weight*d;phi[u]+=term;phi[v]-=term
    j0=[-a(p['eta'])*weight*a(p['kappa_c'])*(phi[u]-phi[v]) for (u,v),weight in zip(ends,w)]
    gram=b.T@b;dnorm=norm(dc)
    lips=[abs(q(p['eta'])*q(p['kappa_Ah']))*hi(weight)*prior.norm([q(int(x)) for x in row])*dnorm for weight,row in zip(w,gram)]
    jbox=[inflate(x,lip*r) for x,lip in zip(j0,lips)]
    gs=drive(p,ends,c,rows,jbox)
    contrast=[(weight-g)/(weight+g) for weight,g in zip(w,gs)]
    beta=q(p['zeta_A'])*q(p['chi_A'])
    blocks=[1-a(beta)*x for x in contrast]
    margin=min(lo(x) for x in blocks);require(margin>0,'uniform current margin')
    jbound=norm(jbox)
    qm=max(hi(abs(x)) for x in contrast)
    lq=max(abs(q(p['gamma']))*hi(abs(j))*lip/2 for j,lip in zip(jbox,lips))
    current=jbound/margin;lj=prior.norm(lips)/margin+jbound*abs(beta)*lq/margin**2
    chi=abs(q(p['chi_A']));flat=chi*qm*current/(1-r)
    lf=chi*(qm*current/(1-r)**2+(lq*current+qm*lj)/(1-r))
    gain=abs(q(params['geometry']['kappa_H'])*q(p['zeta_A']))
    displacement,contraction=gain*flat**2,2*gain*flat*lf
    condition=max(hi(x) for x in blocks)/margin
    prior.domain(r,displacement,contraction,margin,condition,q(params['solver']['conditioning_limit']))
    g0=drive(p,ends,c,rows,j0)
    q0=[(weight-g)/(weight+g) for weight,g in zip(w,g0)]
    jref=[j/(1-a(beta)*x) for j,x in zip(j0,q0)]
    f0=[a(p['chi_A'])*x*j for x,j in zip(q0,jref)]
    residual=gain*hi(sum((x*x for x in f0),arb(0)))
    herror=min(displacement,residual/(1-contraction));jerror=lj*herror
    bounds=dict(contraction_upper=contraction,displacement_upper=displacement,
        current_margin_lower=margin,current_condition_upper=condition,
        conductance_lower=min(lo(g) for g in gs),root_geometry_error_upper=herror,
        root_current_error_upper=jerror)
    return dict(b=b,ends=ends,C=c,W=w,Jref=jref,J=[inflate(x,jerror) for x in jref],
        jerror=jerror,bounds={k:str(v) for k,v in bounds.items()})


def step(subject,role,dt,c=None,w=None,*,writer=False):
    require(q(dt)>0,'positive duration')
    root=joint_box(subject,role,c,w);b=root['b']
    after=[inflate(x-a(dt)*sum((int(z)*j for z,j in zip(row,root['Jref'])),arb(0)),
        q(dt)*prior.norm([q(int(z)) for z in row])*root['jerror']) for x,row in zip(root['C'],b)]
    summary=dict(bounds=root['bounds'],minimum_resource_lower=str(min(lo(x) for x in after)),
        all_positive=all(lo(x)>0 for x in after),resource_bounds=pack(after))
    wn=None
    if writer:
        p=subject['profile']['params_resolved']['candidate']
        require(q(p['tau_A'])>0,'positive history timescale')
        rows=descriptors(subject,after,root['W'])
        g=drive(p,root['ends'],after,rows,root['J'])
        wn=log_writer(root['W'],g,dt,p['tau_A'])
        require(all(lo(x)>0 for x in wn),'positive written history')
        summary.update(history_bounds=pack(wn),writer_target_lower=str(min(lo(x) for x in g)),
            writer='log_relaxation_final_C_incoming_W_selected_J')
    return summary,after,wn


def log_writer(w,drive_values,dt,tau):
    require(q(dt)>0 and q(tau)>0 and len(w)==len(drive_values),'writer domain/coverage')
    require(all(lo(x)>0 for x in (*w,*drive_values)),'positive log operands')
    decay=(-a(dt)/a(tau)).exp()
    return [(decay*x.log()+(1-decay)*y.log()).exp() for x,y in zip(w,drive_values)]


def leading_constraints(subject,role):
    bv,_,c,w,_=prior.operands(subject,role);b=fmpq_mat(bv.tolist())
    l=fmpq_mat(b.nrows(),b.nrows())
    for e,weight in enumerate(w):
        ends=[(i,int(bv[i,e])) for i in range(len(c)) if bv[i,e]]
        for i,x in ends:
            for j,y in ends:l[i,j]+=weight*x*y
    square=l*l;nodes=subject['graph']['live_node_ids']
    sats=[next(i for i,n in enumerate(nodes) if isinstance(n,str) and n.endswith('/satellite/'+str(k))) for k in (1,2,3)]
    total=sum((c[i] for i in sats),q(0));out=[]
    for i,ci in enumerate(c):
        if ci!=0:continue
        offset=sum((square[i,j]*c[j] for j in range(len(c)) if j not in sats),q(0))
        coeff=[square[i,j]*total for j in sats]
        out.append(dict(node=nodes[i].split('/',1)[1],offset=str(offset),coefficients=list(map(str,coeff)),
            selected_rate=str(offset+sum((x*q(s) for x,s in zip(coeff,SHARES)),q(0)))))
    return out


def companion(shares=SHARES,source_deficit=0):
    old=prior.read(prior.PREPARED);shares=tuple(q(s) for s in shares)
    require(len(shares)==3 and min(shares)>=0 and sum(shares,q(0))==1,'nonnegative exact simplex')
    graph=prepared.GRC9V4PortGraph.from_envelope(old['source']['graph'])
    deficit=q(source_deficit)
    require(0<=deficit<q('1/4'),'bounded source perturbation')
    if deficit:
        for role in ('current','reset'):
            values=old['source']['roles'][role]['C']
            for node,delta in ((0,-deficit),(60,deficit)):
                i=graph.live_node_ids.index(node);value=q(values[i])+delta
                require(q(float(value))==value,'exact source companion')
                values[i]=float(value)
        profile=prepared.GRCV4Profile.from_canonical_bytes(prepared.canonical_json_bytes(old['source']['profile']))
        spec=prepared.native.GRC9V4Specialization(prepared.FrozenJSONMap(old['specialization']['resolved']),prepared.FrozenJSONMap(old['specialization']['identity_payload']))
        roles={role:prepared.authority(state,len(graph.edges)) for role,state in old['source']['roles'].items()}
        state=prepared.make_state(graph,profile,spec,roles,'A_CI')
        old['source'].update(prepared.identities(state))
    request=deepcopy(old['event_request'])
    request.update(operation_id='p984g-aci-source-allocation-companion-v1' if deficit else 'p984g-aci-allocation-companion-v1',
        source_state_digest=old['source']['scientific_digest'],resource_distribution=[float(x) for x in shares])
    require(all(q(float(x))==x for x in shares),'exactly represented allocation')
    plan=prepared.expansion.GRC9V4ExpansionPlan(graph,old['source']['scientific_digest'],
        prepared.expansion.GRC9V4ExpansionRequestInput.from_payload(request),
        prepared.expansion.GRC9ExpansionPolicy.from_payload(old['specialization']['resolved']['expansion']))
    newnodes=plan.target_graph.live_node_ids;oldnodes=graph.live_node_ids
    mapping={plan.event_id+f'/satellite/{k+1}':x for k,x in enumerate(shares)}
    matrix=[[mapping.get(n,q(0)) if v==request['source_node_id'] else q(int(n==v)) for v in oldnodes] for n in newnodes]
    require(all(sum(col,q(0))==1 for col in zip(*matrix)),'charge-preserving transfer')
    actual=prepared.expansion._resource_transform(plan)
    require([q(x) for x in actual['row_major_coefficients']]==[x for row in matrix for x in row]
        and all(x==0 for x in actual['target_increment']),'mechanical resource map mismatch')
    oldedges=[e['edge_id'] for e in old['source']['graph']['edges']]
    target=dict(graph=plan.target_graph.to_envelope(),profile=prepared.profile_for(plan.target_graph,'A_CI',old['selected_configuration']).to_payload(),roles={})
    for role,state in old['source']['roles'].items():
        cs=[sum((x*q(y) for x,y in zip(row,state['C'])),q(0)) for row in matrix]
        require(all(q(float(x))==x for x in cs) and sum(cs,q(0))==sum(map(q,state['C']),q(0)),'exact resource transfer')
        weights=dict(zip(oldedges,state['W_A']))
        target['roles'][role]=dict(C=list(map(float,cs)),W_A=[weights.get(e.edge_id,plan.policy.bond_seed) for e in plan.target_graph.edges],Z_4=None)
    return old,target,matrix,dict(request=request,event_id=plan.event_id,target_graph_digest=plan.target_graph.graph_digest,
        target_profile_id=target['profile']['complete_profile_id'] if 'complete_profile_id' in target['profile'] else prepared.profile_for(plan.target_graph,'A_CI',old['selected_configuration']).complete_profile_id,
        shares=list(map(str,shares)),source_unchanged=(deficit==0),history_policy_unchanged=True,
        source_deficit=str(deficit),source_compensation_node=60,source_scientific_digest=old['source']['scientific_digest'],
        identity_scope='prebeat_declaration_not_fresh_event_receipt')


def transfer_boxes(old,target,matrix,c,w):
    cs=[sum((a(x)*v for x,v in zip(row,c)),arb(0)) for row in matrix]
    lineage={e['edge_id']:x for e,x in zip(old['source']['graph']['edges'],w)}
    ws=[lineage.get(e['edge_id'],a(old['specialization']['resolved']['expansion']['bond_seed'])) for e in target['graph']['edges']]
    return cs,ws


def trigger(old,c,w):
    source=old['source'];rows=descriptors(source,c,w)
    i=source['graph']['live_node_ids'].index(old['event_request']['source_node_id'])
    ports=[e[k]['port'] for e in source['graph']['edges'] for k in ('tail','head') if e[k]['node_id']==old['event_request']['source_node_id']]
    require(sorted(ports)==list(range(1,10)),'saturated source')
    policy=old['specialization']['resolved']['spark'];sign=old['specialization']['identity_payload']['hessian_sign']
    g=rows[i];gn=norm(g);hu=min(hi(sign*x) for x in g)
    return dict(gradient=pack(g),gradient_norm_upper=str(gn),minimum_signed_hessian_upper=str(hu),
        saturated=True,small_gradient=gn<q(policy['gradient_tolerance']),
        strict_hessian_condition=hu<q(policy['spark_hessian_tolerance']),native_trigger_receipt=False)


def calculate():
    original=prior.check();allocation,atarget,amatrix,aid=companion()
    old,target,matrix,identity=companion(source_deficit=DEFICIT)
    dt=old['selected_configuration']['ordinary_dt'];cases=[]
    with ctx.workprec(prior.BITS):
        constraints={r:leading_constraints(allocation['target'],r) for r in ('current','reset')}
        require(all(q(x['selected_rate'])>0 for rows in constraints.values() for x in rows),'selected leading inequalities')
        diagnostics=[]
        for role in ('current','reset'):
            initial,_,_=step(atarget,role,dt)
            src,c,w=step(allocation['source'],role,dt,writer=True)
            # A rounded-exact control is not a native ordinary step. Its
            # fixed-row values diagnose the source's missing strict margin.
            rounded=trigger(allocation,[a(float(x.mid())) for x in c],[a(float(x.mid())) for x in w])
            diagnostics.append(dict(role=role,initial_target_minimum_lower=initial['minimum_resource_lower'],
                source_trigger=trigger(allocation,c,w),rounded_exact_postbeat_control=rounded))
        for role in ('current','reset'):
            initial,_,_=step(target,role,dt)
            source,c,w=step(old['source'],role,dt,writer=True)
            tc,tw=transfer_boxes(old,target,matrix,c,w)
            fresh,_,_=step(target,role,dt,tc,tw)
            signal=trigger(old,c,w)
            cases.append(dict(role=role,initial_target=initial,source_postbeat=source,
                source_trigger=signal,postbeat_transfer_target=fresh,
                postbeat_role_use='live_current' if role=='current' else 'reset_as_current_control_not_event_reset'))
        require(all(c['initial_target']['all_positive'] and c['source_postbeat']['all_positive']
            and c['postbeat_transfer_target']['all_positive'] and c['source_trigger']['small_gradient']
            and c['source_trigger']['strict_hessian_condition'] for c in cases),'companion feasibility not established')
    paths=[SELF,TEST,PLAN,NOTE,prior.SELF,prior.RESULTS,prior.PREPARED,
        HERE+'prepare_p983_all_realizations.py','src/pygrc/models/grc_9_v4_expansion.py',
        'src/pygrc/models/grc_9_v4_topology.py','src/pygrc/models/grc_v4_candidate_a.py']
    return prior.seal(dict(schema='p984g-aci-feasibility-v1',family='A_CI',companion=identity,
        source=old['source'],target=target,leading_constraints=constraints,cases=cases,
        allocation_only=dict(companion=aid,cases=diagnostics),
        original_research_digest=original['record_digest'],original_reset_exclusion_preserved=True,
        event_pair=dict(current='postbeat_transfer_target/current',reset='initial_target/reset',reset_evolves=False),
        scope='bounded_exact_real_resource_writer_trigger_feasibility_not_native_conformance',
        source_bindings={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in paths},
        precision_bits=prior.BITS,scalar_backend='FLINT rational and Arb outward enclosures',
        native_roots=0,native_steps=0,native_events=0,user_accepted=False,ready_for_8_4h=False,
        open_obligations=['staged joint-root/error and mechanism bridge',
            'native stopping, charge and target history/final-C readmission',
            'fresh postbeat event identity/commit and multistep continuation in 8.4h']))


def check_retained(value=None):
    """Authenticated retained content, not a new interval calculation."""
    value=prior.read(RESULTS) if value is None else value
    require(value['record_digest']==prior.seal(value)['record_digest'],'feasibility digest')
    require(value['schema']=='p984g-aci-feasibility-v1' and value['family']=='A_CI','feasibility schema')
    require(all(hashlib.sha256((ROOT/s).read_bytes()).hexdigest()==h for s,h in value['source_bindings'].items()),'feasibility source drift')
    require(value['companion']['shares']==list(SHARES) and value['companion']['source_deficit']==DEFICIT,'companion identity')
    require(value['original_research_digest']==prior.read(prior.RESULTS)['record_digest'] and value['original_reset_exclusion_preserved'],'lost exclusion')
    require(value['event_pair']==dict(current='postbeat_transfer_target/current',reset='initial_target/reset',reset_evolves=False),'event chronology')
    require([c['role'] for c in value['cases']]==['current','reset'],'role coverage')
    for c in value['cases']:
        require(c['source_trigger']['small_gradient'] and c['source_trigger']['strict_hessian_condition'],'trigger feasibility')
        for stage in ('initial_target','source_postbeat','postbeat_transfer_target'):
            require(c[stage]['all_positive'] and q(c[stage]['minimum_resource_lower'])>0,'resource feasibility')
    require(all(value[k]==0 for k in ('native_roots','native_steps','native_events'))
        and not value['ready_for_8_4h'] and not value['user_accepted'],'research scope widened')
    return value


def check(value=None):
    value=prior.read(RESULTS) if value is None else value
    require(value==calculate(),'A_CI feasibility/source/scope drift');return value


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=('run','check'))
    args=parser.parse_args()
    if args.mode=='run':
        require(not (ROOT/RESULTS).exists(),'no evidence overwrite')
        raw=json.dumps(calculate(),indent=2)+'\n';require(len(raw.encode())<=1000000,'compress evidence above 1 MB')
        (ROOT/RESULTS).write_text(raw)
    else:check()


if __name__=='__main__':main()

"""Lawful allocation and exact-real first-step feasibility, never native admission."""
import argparse
from copy import deepcopy
import hashlib
import json
import math
from flint import arb, fmpq_mat
import p984g_cci_staged as staged
import p984g_cci_continuation as continuation
import prepare_p983_all_realizations as prepared

prior, iv = staged.prior, staged.iv
ROOT, BASE, HERE = staged.ROOT, staged.BASE, staged.HERE
SELF = HERE + 'p984g_cci_feasibility.py'
TEST = HERE + 'test_p984g_cci_feasibility.py'
PLAN = BASE + 'P9-8.4g-CCIFeasibilityPlan.md'
RESULTS = BASE + 'P9-8.4g-CCIFeasibilityResults.json'
REVIEW = BASE + 'P9-8.4g-CCIFeasibility.md'
SHARES = ('5/16', '5/16', '3/8')
DEFICIT = '1/1024'
q, require, read, seal = staged.q, staged.require, staged.read, staged.seal


def transfer_matrix(source_nodes, target_nodes, event_id, source_node, shares):
    shares = tuple(q(x) for x in shares)
    require(len(shares) == 3 and min(shares) >= 0 and sum(shares, q(0)) == 1,
            'exact nonnegative simplex required')
    require(source_node in source_nodes and source_node not in target_nodes,
            'expanded source must be replaced')
    satellites = {event_id + f'/satellite/{i+1}': x for i, x in enumerate(shares)}
    require(set(satellites) <= set(target_nodes), 'missing satellite')
    out = [[satellites.get(node, q(0)) if old == source_node else q(int(node == old))
            for old in source_nodes] for node in target_nodes]
    require(all(sum(col, q(0)) == 1 for col in zip(*out)), 'nonconservative transfer')
    return out


def companion(source_deficit=0):
    old = read(prior.PREPARED)
    graph = prepared.GRC9V4PortGraph.from_envelope(old['source']['graph'])
    deficit=q(source_deficit)
    require(0<=deficit<q('1/4'),'bounded source deficit required')
    if deficit:
        for role in ('current','reset'):
            cs=old['source']['roles'][role]['C']
            for node,delta in ((0,-deficit),(60,deficit)):
                index=graph.live_node_ids.index(node);value=q(cs[index])+delta
                require(q(float(value))==value,'exactly represented source change required')
                cs[index]=float(value)
        profile=prepared.GRCV4Profile.from_canonical_bytes(prepared.canonical_json_bytes(old['source']['profile']))
        spec=prepared.native.GRC9V4Specialization(prepared.FrozenJSONMap(old['specialization']['resolved']),
                                               prepared.FrozenJSONMap(old['specialization']['identity_payload']))
        roles={r:prepared.authority(old['source']['roles'][r],len(graph.edges)) for r in ('current','reset')}
        state=prepared.make_state(graph,profile,spec,roles,'C_CI')
        old['source'].update(prepared.identities(state))
    request = deepcopy(old['event_request'])
    request.update(operation_id='p984g-cci-feasibility-companion-v1' if deficit else 'p984g-cci-allocation-only-v1',
                   source_state_digest=old['source']['scientific_digest'],
                   resource_distribution=[float(q(x)) for x in SHARES])
    policy = prepared.expansion.GRC9ExpansionPolicy.from_payload(old['specialization']['resolved']['expansion'])
    plan = prepared.expansion.GRC9V4ExpansionPlan(graph, old['source']['scientific_digest'],
        prepared.expansion.GRC9V4ExpansionRequestInput.from_payload(request), policy)
    matrix = transfer_matrix(graph.live_node_ids, plan.target_graph.live_node_ids,
                             plan.event_id, request['source_node_id'], SHARES)
    actual = prepared.expansion._resource_transform(plan)
    require([q(x) for x in actual['row_major_coefficients']] == [x for row in matrix for x in row]
            and all(x == 0 for x in actual['target_increment']), 'allocator differs from derived transfer')
    profile = prepared.profile_for(plan.target_graph, 'C_CI', old['selected_configuration'])
    roles = {}
    for role in ('current', 'reset'):
        values = [sum((v*q(c) for v,c in zip(row,old['source']['roles'][role]['C'],strict=True)),q(0)) for row in matrix]
        require(all(q(float(x)) == x for x in values), 'prepared transfer not exactly representable')
        require(sum(values,q(0)) == 200, 'resource conservation')
        roles[role] = dict(C=[float(x) for x in values], W_A=None, Z_4=None)
    target = dict(graph=plan.target_graph.to_envelope(),profile=profile.to_payload(),roles=roles)
    return old, target, matrix, dict(event_request=request,event_id=plan.event_id,
        target_graph_digest=plan.target_graph.graph_digest,
        target_profile_id=profile.complete_profile_id,shares=list(SHARES),
        source_unchanged=(deficit==0),source_declaration=prior.PREPARED,
        source_deficit=str(deficit),source_compensation_node=60,
        source_roles=old['source']['roles'],source_scientific_digest=old['source']['scientific_digest'],
        identity_scope='pure_prebeat_companion_declaration_not_a_fresh_event_receipt')


def leading_constraints(subject, role):
    bv,_ = prior.shared.graph_data(subject)
    b = fmpq_mat([[int(x) for x in row] for row in bv]); l = b*b.transpose()
    nodes = subject['graph']['live_node_ids']; c = subject['roles'][role]['C']
    sats = [next(i for i,n in enumerate(nodes) if isinstance(n,str) and n.endswith('/satellite/'+str(k))) for k in (1,2,3)]
    total = sum((q(c[i]) for i in sats),q(0)); l2 = l*l
    rows = []
    for i,ci in enumerate(c):
        if ci != 0: continue
        offset = sum((l2[i,j]*q(c[j]) for j in range(len(c)) if j not in sats),q(0))
        coeff = [l2[i,j]*total for j in sats]
        rows.append(dict(node=nodes[i].split('/',1)[1],offset=str(offset),
                         coefficients=[str(x) for x in coeff]))
    return rows


def reference_divergence(b, c, p, t):
    """Full constant-selector law at I, using only a vertex-system solve."""
    l=b*b.transpose(); v=l*l*c; beta=iv.a(p['zeta_C'])*iv.a(p['chi_C'])
    return -iv.a(p['eta_C'])*iv.a(p['kappa_Phi_C'])*t*(
        v+beta*((1-beta)*iv.eye(b.nrows())+iv.a(p['tau_C'])*t*l).solve(v))


def source_postbeat(old, role):
    evidence = read(staged.case_path('source',role))
    # Authenticate and recompute the inexpensive retained evidence checks, not solves.
    staged.check_case(evidence)
    b,_=prior.shared.graph_data(old['source']); r=evidence['result']
    intervals=continuation.enclose(b,old['source']['roles'][role]['C'],r['reference_current'],
        old['selected_configuration']['ordinary_dt'],r['reference_to_root_current_error_upper'])
    return [iv.a(lo).union(iv.a(hi)) for lo,hi in intervals]


def trigger_envelope(old, values):
    graph=old['source']['graph']; nodes=graph['live_node_ids']; source=old['event_request']['source_node_id']
    local=nodes.index(source); rows=[[],[],[]];ports=[]
    for e in graph['edges']:
        for here,there in ((e['tail'],e['head']),(e['head'],e['tail'])):
            if here['node_id']==source:
                ports.append(here['port'])
                row,_=prepared.expansion.port_to_row_column(here['port'])
                rows[row-1].append(values[nodes.index(there['node_id'])]-values[local])
    require(sorted(ports)==list(range(1,10)), 'source saturation changed')
    gradient=[sum(row,arb(0))/len(row) for row in rows]
    policy=old['specialization']['resolved']['spark']
    sign=old['specialization']['identity_payload']['hessian_sign']
    norm_upper=iv.hi(sum((x*x for x in gradient),arb(0)).sqrt())
    signed=[sign*x for x in gradient]
    return dict(gradient=iv.encode_column(iv.arb_mat([[x] for x in gradient])),
        gradient_norm_upper=str(norm_upper),
        minimum_signed_hessian_upper=str(min(iv.hi(x) for x in signed)),
        saturated=True,small_gradient=norm_upper<q(policy['gradient_tolerance']),
        strict_hessian_condition=any(iv.hi(x)<q(policy['spark_hessian_tolerance']) for x in signed),
        native_fresh_trigger_receipt=False)


def step_bound(subject, role, values=None, factor=q(1)):
    bv,params=prior.shared.graph_data(subject);p=params['candidate'];b=iv.matrix(bv)
    cs=subject['roles'][role]['C']; original=values is None
    values=[iv.a(x) for x in cs] if original else values
    require(sum((q(x) for x in cs),q(0))==200 and
            all(iv.lo(x)>=0 for x in values) and sum(values,arb(0)).contains(200),
            'nonnegative conserved-200 resource envelope required')
    c=iv.arb_mat([[x] for x in values]); bounds=prior.certificate(subject,role)['bounds']
    # These bounds depend homogeneously on ||B^T C||: A,q quadratic; L_J linear.
    dc=[sum((q(int(w))*q(x) for w,x in zip(col,cs,strict=True)),q(0)) for col in bv.T]
    d0=prior.upper(iv.a(sum((x*x for x in dc),q(0))).sqrt())
    d=staged.norm2(b.transpose()*c)
    require(factor>=1 and (original or iv.hi(d)<=d0*factor),'gradient envelope exceeds declared scale')
    A=q(bounds['displacement_upper'])*factor**2
    contraction=q(bounds['contraction_upper'])*factor**2
    lj=q(bounds['current_lipschitz_upper'])*factor
    beta=q(p['zeta_C'])*q(p['chi_C'])
    prior.conditions(len(values),q(bounds['radius']),q(p['Lambda_C']),beta,A,contraction,
                     q(bounds['physical_condition_upper']),q(params['solver']['conditioning_limit']))
    # Transfer and incidence continuity conserve the exact total, even though
    # independently boxed coordinates do not encode that correlation.
    t=(iv.a(p['kappa_M_C'])*(iv.a(q(200)/len(values))/iv.a(p['C_ref'])).tanh()).exp()
    rate=reference_divergence(b,c,p,t);dt=read(prior.PREPARED)['selected_configuration']['ordinary_dt']
    after=[];radii=[]
    for i in range(len(values)):
        r=iv.hi(iv.a(sum(int(x)**2 for x in bv[i])).sqrt())*lj*A
        center=values[i]-iv.a(dt)*rate[i,0]
        after.append(center+arb(0,iv.a(q(dt)*r)));radii.append(r)
    zero=[i for i,x in enumerate(values) if x.is_zero()]
    return dict(all_positive=all(iv.lo(x)>0 for x in after),
        minimum_lower=str(min(iv.lo(x) for x in after)),
        resource_bounds=iv.encode_column(iv.arb_mat([[x] for x in after])),
        zero_resource_vertices=[dict(index=i,node=subject['graph']['live_node_ids'][i].split('/',1)[1],
            next_resource_lower=str(iv.lo(after[i])),outward_rate_upper=str(iv.hi(rate[i,0])+radii[i])) for i in zero],
        gradient_scale=str(factor),gradient_norm_upper=str(iv.hi(d)),
        scaled_displacement_upper=str(A),scaled_contraction_upper=str(contraction),
        reference_to_root_current_error_upper=str(lj*A))


def decoded_bounds(result):
    return [iv.a(x['lower']).union(iv.a(x['upper'])) for x in result['resource_bounds']]


def rounding_pressure(values):
    # A full ulp is deliberately conservative; no claim about native stage order.
    return [x+arb(0,iv.a(max(math.ulp(float(iv.lo(x))),math.ulp(float(iv.hi(x)))))) for x in values]


def bindings():
    paths=[SELF,TEST,PLAN,prior.PREPARED,prior.SELF,staged.SELF,iv.SELF,continuation.SELF,
        continuation.RESULTS,HERE+'prepare_p983_all_realizations.py',
        prior.shared.SELF,HERE+'prepare_p983_graph_admission.py',
        'src/pygrc/models/grc_9_v4_expansion.py','src/pygrc/models/grc_9_v4_topology.py',
        'src/pygrc/models/grc_9_v4_lifecycle.py','specs/grc-9-v4-spec.md']
    paths += [staged.case_path('source',r) for r in ('current','reset')]
    return {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}


def calculate():
    old,target,transfer,declaration=companion(DEFICIT);cases=[];diagnosis=[]
    with staged.ctx.workprec(iv.BITS):
        original,allocation_target,_,allocation=companion()
        for role in ('current','reset'):
            diagnostic=step_bound(allocation_target,role)
            original_post=source_postbeat(original,role)
            original_staged=read(staged.case_path('source',role))['result']['reference_continuity_proposal']
            diagnosis.append(dict(role=role,allocation_only_target_minimum_lower=diagnostic['minimum_lower'],
                exact_postbeat_trigger=trigger_envelope(original,original_post),
                retained_staged_postbeat_trigger=trigger_envelope(original,[iv.a(x) for x in original_staged])))
            initial=step_bound(target,role)
            source_step=step_bound(old['source'],role)
            post=decoded_bounds(source_step);trigger=trigger_envelope(old,post)
            moved=[sum((iv.a(w)*x for w,x in zip(row,post,strict=True)),arb(0)) for row in transfer]
            fresh=step_bound(target,role,moved,q(5)/4)
            cases.append(dict(role=role,leading_constraints=leading_constraints(target,role),
                source_step_role='live_current' if role=='current' else 'reset_as_current_control_not_reset_mutation',
                initial_transfer=initial,source_step=source_step,
                source_postbeat_trigger=trigger,
                rounded_exact_postbeat_control=trigger_envelope(old,rounding_pressure(post)),
                fresh_postbeat_transfer=fresh))
    return seal(dict(schema='p984g-cci-feasibility-v1',family='C_CI',source_bindings=bindings(),
        companion=declaration,cases=cases,precision_bits=iv.BITS,
        allocation_only_diagnostic=dict(companion=allocation,cases=diagnosis),
        event_pair=dict(current='current/fresh_postbeat_transfer',reset='reset/initial_transfer',
                        reset_evolves=False,native_event_record=False),
        original_exclusions=continuation.RESULTS,
        scope='exact_real_first_step_feasibility_and_postbeat_envelope_not_native_admission',
        native_roots=0,native_steps=0,native_events=0,ready_for_8_4h=False,user_accepted=False,
        changed_timestep=False,changed_tolerances=False,injected_resource=False))


def check(value=None):
    value=read(RESULTS) if value is None else value
    require(value==calculate(),'feasibility source/derivation/result drift')
    return value


def check_retained(value=None):
    """Authenticated retained content only; no interval solve or new experiment."""
    value=read(RESULTS) if value is None else value
    require(value==seal(value) and value['source_bindings']==bindings(),'feasibility identity/source drift')
    require(value['schema']=='p984g-cci-feasibility-v1' and value['family']=='C_CI'
            and value['precision_bits']==iv.BITS,'feasibility schema/policy drift')
    require(value['scope']=='exact_real_first_step_feasibility_and_postbeat_envelope_not_native_admission',
            'feasibility scope promotion')
    for field in ('native_roots','native_steps','native_events','ready_for_8_4h','user_accepted',
                  'changed_timestep','changed_tolerances','injected_resource'):
        require(value[field]==0,'feasibility scope promotion')
    require(value['companion']['shares']==list(SHARES) and value['companion']['source_deficit']==DEFICIT
            and value['companion']['source_compensation_node']==60 and not value['companion']['source_unchanged'],
            'companion selection drift')
    require(value['event_pair']==dict(current='current/fresh_postbeat_transfer',reset='reset/initial_transfer',
                                     reset_evolves=False,native_event_record=False),'reset chronology drift')
    require([x['role'] for x in value['cases']]==['current','reset'],'role roster drift')
    for row in value['cases']:
        for stage,n in (('source_step',100),('initial_transfer',107),('fresh_postbeat_transfer',107)):
            case=row[stage]; bounds=case['resource_bounds']
            require(len(bounds)==n and all(q(x['upper'])>=q(x['lower'])>0 for x in bounds),
                    'unproved resource sign')
            require(case['all_positive'] is True and q(case['minimum_lower'])==min(q(x['lower']) for x in bounds),
                    'resource minimum drift')
            require(0<=q(case['scaled_contraction_upper'])<1,'contraction not proved')
        for stage in ('source_postbeat_trigger','rounded_exact_postbeat_control'):
            require(all(row[stage][k] is True for k in ('saturated','small_gradient','strict_hessian_condition'))
                    and row[stage]['native_fresh_trigger_receipt'] is False,'trigger scope drift')
    require([r['role'] for r in value['allocation_only_diagnostic']['cases']]==['current','reset'],
            'diagnostic role drift')
    require(all(r['retained_staged_postbeat_trigger']['strict_hessian_condition'] is False
                for r in value['allocation_only_diagnostic']['cases']),'original trigger failure erased')
    return value


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=('run','check'))
    args=parser.parse_args()
    if args.mode=='run':
        require(not (ROOT/RESULTS).exists(),'no overwrite')
        raw=json.dumps(calculate(),indent=2)+'\n'
        require(len(raw.encode())<=1000000,'compress evidence before retaining')
        (ROOT/RESULTS).write_text(raw)
    else:check()


if __name__=='__main__':main()

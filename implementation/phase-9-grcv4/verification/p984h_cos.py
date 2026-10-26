"""Two-beat C_OS event preparation; certified first steps, dense horizon screen."""

import argparse
from copy import deepcopy
from dataclasses import replace
from fractions import Fraction
import hashlib
import json
import lzma
import math
import signal
import subprocess
import time

from flint import ctx, fmpq
from pygrc.models.grc_v4_numerics import exact_backend, ExactBackend, numerical_policy, NumericalPolicy
import p984g_cos as old
import p984g_cos_bounds as bounds

ROOT, BASE, HERE = old.ROOT, old.BASE, old.HERE
SELF = HERE + 'p984h_cos.py'
TEST = HERE + 'test_p984h_cos.py'
PLAN = BASE + 'P9-8.4h-COSPlan.md'
REVIEW = BASE + 'P9-8.4h-COSReview.md'
INPUTS = BASE + 'P9-8.4h-COSInputs.json'
RESULTS = BASE + 'P9-8.4h-COSOracle.json.xz'
PREFIX = BASE + 'P9-8.4g-COSNative/source-current.json'
ACCEPTANCE = BASE + 'P9-8.4g-COSNativeReview.md'
REVISION = '718f95be'
STEPS, BITS = 10, 256
require, seal, digest = old.require, old.seal, old.digest
ROLES = ('current', 'reset')


def sha(name):
    return hashlib.sha256((ROOT / name).read_bytes()).hexdigest()


def historical(name):
    data = subprocess.check_output(['git', 'show', REVISION + ':' + name], cwd=ROOT)
    require((ROOT / name).read_bytes() == data, 'historical source changed: ' + name)
    return data


@exact_backend(ExactBackend.FLINT)
@numerical_policy(NumericalPolicy.CERTIFIED_ARB_256)
def source():
    """Restore the actual historical numerical postbeat, never forge chronology."""
    from prepare_p983_all_realizations import materialize
    from pygrc.models.grc_9_v4_lifecycle import GRC9V4COSState
    from pygrc.models.grc_v4_state import GRCV4AuthoritativeState
    from pygrc.models.grc_v4_geometry import GeometryStageInputs
    declaration = json.loads(historical(old.PREPARED))
    saved = json.loads(historical(PREFIX))
    require(saved == seal(saved) and saved['outcome'] == 'completed'
            and saved['graph'] == 'source' and saved['role'] == 'current', 'invalid source prefix')
    require(b'## Scoped user acceptance' in historical(ACCEPTANCE), 'missing prerequisite acceptance')
    seed = materialize(declaration, 'source')
    r = saved['result']
    before = replace(seed.inputs, dt=declaration['selected_configuration']['ordinary_dt'])
    require(digest(before.to_payload()) == r['before_digest'], 'prefix input identity')
    captured = GeometryStageInputs.from_payload(before.to_payload())
    after = replace(captured, current=GRCV4AuthoritativeState(tuple(r['after_C']), None, None),
                    step_index=r['after_step_index'], time=r['after_time'])
    require(digest(after.to_payload()) == r['after_digest'], 'prefix postbeat identity')
    require(after.reset == before.reset and after.step_index == before.step_index + 1
            and after.time == before.time + before.dt, 'prefix chronology/reset')
    return declaration, GRC9V4COSState(replace(after, dt=0), seed.specialization)


@exact_backend(ExactBackend.FLINT)
@numerical_policy(NumericalPolicy.CERTIFIED_ARB_256)
def second_source_input():
    """Continue the unchanged accepted prefix for one more ordinary beat."""
    declaration,state=source()
    return declaration,replace(state,inputs=replace(state.inputs,dt=declaration['selected_configuration']['ordinary_dt']))


def postbeat(initial, resources):
    from pygrc.models.grc_v4_geometry import GeometryStageInputs
    from pygrc.models.grc_v4_state import GRCV4AuthoritativeState
    before=GeometryStageInputs.from_payload(initial.inputs.to_payload())
    return replace(initial,inputs=replace(before,current=GRCV4AuthoritativeState(tuple(resources),None,None),
        step_index=before.step_index+1,time=before.time+before.dt,dt=0))


def subject_for_state(state, side='source'):
    declaration=old.read(old.PREPARED);value=deepcopy(declaration[side])
    value={k:value[k] for k in ('graph','profile','roles')}
    for role in ROLES:value['roles'][role]['C']=list(getattr(state.inputs,role).C)
    return value


@exact_backend(ExactBackend.FLINT)
@numerical_policy(NumericalPolicy.CERTIFIED_ARB_256)
def fresh_subject(state=None):
    """New namespace + literal resource map, not a target read from production."""
    from pygrc.models.grc_9_v4_expansion import GRC9ExpansionPolicy, cos_profile_template
    from pygrc.models.grc_v4_codec import payload_identity
    if state is None:declaration,state=source()
    else:declaration=old.read(old.PREPARED)
    request = deepcopy(declaration['event_request'])
    request.update(operation_id='p984h-cos-base', source_state_digest=state.scientific_digest)
    require(request['target_profile_template_id'] == cos_profile_template(state.inputs.geometry.reference).profile_template_id,
            'source template drift')
    policy = GRC9ExpansionPolicy.from_payload(declaration['specialization']['resolved']['expansion'])
    keys = ('source_state_digest', 'source_graph_digest', 'source_node_id', 'target_profile_template_id',
            'target_specialization_id', 'target_effective_degree', 'module_chirality', 'growth_phase',
            'expansion_policy_id', 'resource_distribution')
    identity = dict(schema_version='grc9v4-expansion-event-identity-v1', **{k: request[k] for k in keys},
                    canonical_module_node_count=8, expansion_policy_digest=policy.identity, bond_seed=policy.bond_seed,
                    **{k + '_history_policy_digest': request['history_policy'][k + '_history_policy_digest']
                       for k in ('candidate', 'carrier')})
    event = payload_identity('expansion_event_identity_payload', identity)
    old_event = declaration['event_id']
    require(event != old_event, 'prepared event was reused as fresh event')
    def rename(x):
        return event + x[len(old_event):] if isinstance(x, str) and x.startswith(old_event + '/') else x
    target = deepcopy(declaration['target'])
    graph = target['graph']
    graph['live_node_ids'] = [rename(x) for x in graph['live_node_ids']]
    for edge in graph['edges']:
        edge['edge_id'] = rename(edge['edge_id'])
        for end in ('tail', 'head'): edge[end]['node_id'] = rename(edge[end]['node_id'])
    # Rebuild identity-bearing graph envelope, not just its visible node labels.
    from pygrc.models.grc_9_v4_topology import GRC9V4PortGraph
    graph = GRC9V4PortGraph.from_payload({k: graph[k] for k in ('schema_version','live_node_ids','edges')}).to_payload()
    target['graph'] = graph
    for role in ROLES:
        authority = getattr(state.inputs, role)
        old_c = dict(zip(state.inputs.geometry.reference.graph.live_node_ids, authority.C, strict=True))
        image = {node: old_c.get(node, 0.) for node in graph['live_node_ids']}
        for i, share in enumerate(request['resource_distribution'], 1):
            image[event + f'/satellite/{i}'] = float(Fraction(old_c[0]) * Fraction(share))
        target['roles'][role]['C'] = [image[n] for n in graph['live_node_ids']]
    weights = {e['edge_id']: 1 for e in graph['edges']}
    m = len(weights)
    ref = dict(profile=target['profile'], reference_hodge=deepcopy(state.inputs.geometry.reference.to_payload()['reference_hodge']),
               K4_base=[[0.] * m for _ in range(m)])
    ref['reference_hodge']['edge_weights'] = weights.copy()
    ref['profile']['params_resolved']['candidate']['W_C_tr'] = weights.copy()
    params=ref['profile']['params_resolved'];profile_identity=ref['profile']['identity_payload']
    params['candidate']['W_C_tr_content_digest']=payload_identity('wctr_identity_payload',
        dict(schema_version='grcv4-wctr-identity-v1',W_C_tr=weights))
    params['geometry']['reference_hodge_digest']=payload_identity('reference_hodge_identity_payload',ref['reference_hodge'])
    params['geometry']['K4_base_digest']=payload_identity('k4_identity_payload',
        dict(schema_version='grcv4-k4-identity-v1',K4_base=ref['K4_base']))
    profile_identity['params_hash']=payload_identity('resolved_params',params)
    from pygrc.models.grc_v4_profile import resolve_profile
    ref['profile']=resolve_profile(params,profile_identity).to_payload()
    target['profile'] = ref['profile']
    # Remove stale prepared-state identity/recipe fields: this is an oracle subject.
    target = {k: target[k] for k in ('graph','profile','roles')}
    return declaration, state, request, identity, event, target


def trigger(state):
    """Independent exact fixed-row gradient; no production detection call."""
    values = dict(zip(state.inputs.geometry.reference.graph.live_node_ids, state.inputs.current.C, strict=True))
    rows = [[], [], []]
    graph = state.inputs.geometry.reference.graph.port_graph
    for edge in graph.edges:
        for here, there in ((edge.tail, edge.head), (edge.head, edge.tail)):
            if here.node_id == 0:
                rows[(here.port - 1) // 3].append(Fraction(values[there.node_id]) - Fraction(values[0]))
    gradient = [float(sum(row, Fraction()) / len(row)) for row in rows]
    norm2 = sum((Fraction(x)**2 for x in gradient), Fraction())
    policy = state.specialization.resolved['spark']
    signed = min(-x for x in gradient)
    eligible = sum(map(len, rows)) == 9 and norm2 < Fraction(policy['gradient_tolerance'])**2 and signed < policy['spark_hessian_tolerance']
    return dict(gradient=gradient, gradient_squared=str(norm2), minimum_signed_hessian=signed,
                source_node=0, eligible=eligible, source_state_digest=state.scientific_digest)


def manifest():
    declaration,initial=second_source_input();original=initial
    negative=trigger(original)
    require(not negative['eligible'] and negative['gradient']==[0.,0.,0.], 'original trigger control changed')
    paths = {SELF, TEST, PLAN, old.SELF, bounds.SELF, bounds.RESULTS, old.PREPARED, PREFIX, ACCEPTANCE,
             HERE+'prepare_p983_all_realizations.py', HERE+'prepare_p983_graph_admission.py',
             'specs/grc-9-v4-spec.md', 'specs/grc-v4-numerical-policy.md'}
    paths.update(str(p.relative_to(ROOT)) for p in (ROOT/'src/pygrc/models').glob('*grc*v4*.py'))
    return seal(dict(schema='p984h-cos-inputs-v1', family='C_OS', source_bindings={p: sha(p) for p in sorted(paths)},
        historical_prefix=dict(path=PREFIX, revision=REVISION, sha256=sha(PREFIX), current_tree_execution=False),
        original_postbeat_trigger=negative,source_beats_before_request=2,initial_conditions_unchanged=True,
        initial_inputs_digest=digest(initial.inputs.to_payload()),
        initial_trigger=trigger(initial),dt=declaration['selected_configuration']['ordinary_dt'],
        planned_native_steps_per_role=STEPS,certified_target_steps_per_role=1,dense_steps_per_role=STEPS,
        bits=BITS, roles=list(ROLES), raw_budget_bytes=5000000,
        compressed_budget_bytes=2000000,run_cap_seconds=600,native_events=0, native_steps=0, user_accepted=False,
        aggregate_closed=False, scope='event_bound_staged_oracle_not_native_campaign'))


def pairwise(values):
    values = list(values)
    while len(values)>1:
        values = [values[i]+values[i+1] if i+1<len(values) else values[i] for i in range(0,len(values),2)]
    return values[0]


def charge(before, after, params, target=200.):
    exact = lambda xs: sum((bounds.q(x) for x in xs), fmpq(0))
    actual = pairwise(after);residual=bounds.q(actual)-bounds.q(target)
    tolerance=bounds.q(params['absolute_tolerance'])+bounds.q(params['relative_tolerance'])*max(abs(bounds.q(target)),fmpq(1))
    require(abs(residual)<=tolerance, 'represented charge admission failed')
    return dict(pairwise=actual, residual=str(residual), tolerance=str(tolerance),
                exact_stored_delta=str(exact(after)-exact(before)), margin=str(tolerance-abs(residual)))


def step(subject, cs, dt):
    bv, params = old.graph_data(subject);b=bounds.matrix(bv);c=bounds.matrix([[x] for x in cs]);m=b.ncols()
    p=params['candidate'];mean=sum((bounds.q(x) for x in cs),fmpq(0))/len(cs)
    rho=math.tanh(float(mean)/p['C_ref']);deformation=math.exp((.5*p['kappa_M_C'])*(.5*(rho+rho)))
    predictor,_,flat,first=bounds.staged_read(b,c,bounds.eye(m),p,deformation)
    h=bounds.generated(b,flat,params,staged=True)
    current,_,flat,second=bounds.staged_read(b,c,h,p,deformation)
    regenerated=bounds.generated(b,flat,params,staged=True);split=bounds.norm(h-regenerated)
    require(split<=bounds.q(params['realization']['tolerance']), 'OS split exceeds tolerance')
    require(max(bounds.q(d['condition_squared_upper']) for d in (first,second))<=bounds.q(params['solver']['conditioning_limit'])**2,
            'conditioning exceeds limit')
    after, values = bounds.represented_continuity(b,cs,current,dt)
    output=[float(bounds.lo(after[i,0])) for i in range(after.nrows())]
    require(all(x>=0 for x in output), 'negative represented target resource')
    return dict(current=values,after_C=output,minimum_resource=min(output),split_upper=str(split),
        predictor_domain=first,corrector_domain=second,charge=charge(cs,output,params['charge']),
        uniquely_enclosed_current=True,geometry_rebuilt=True)


def reused_reset_step(target,dt):
    import numpy as np
    prepared=old.read(old.PREPARED)['target']
    b,p=old.graph_data(target);old_b,_=old.graph_data(prepared)
    require(np.array_equal(b,old_b) and target['roles']['reset']['C']==prepared['roles']['reset']['C'],
            'reset reuse requires exact coordinate operands')
    # fresh_subject changes only edge/node namespace and reidentifies references;
    # parameters, matrices and reset resources are unchanged under that bijection.
    require(target['roles']['reset']==prepared['roles']['reset'],'reset authority changed')
    def numeric_params(profile):
        value=deepcopy(profile['params_resolved'])
        for key in ('W_C_tr','W_C_tr_content_digest'):value['candidate'].pop(key)
        value['geometry'].pop('reference_hodge_digest')
        return value
    require(numeric_params(target['profile'])==numeric_params(prepared['profile']),'reset numerical policy changed')
    data=json.loads(historical(bounds.RESULTS))
    require(data==seal(data),'historical reset bounds digest')
    row=next(c for c in data['cases'] if c['graph']=='target' and c['role']=='reset')['staged']
    require(all(x['lower']==x['upper'] for x in row['resources']),'reset rounding not unique')
    c=[float(fmpq(x['lower'])) for x in row['resources']]
    return dict(current=row['uniquely_enclosed_current'],after_C=c,minimum_resource=min(c),
        split_upper=row['split_upper'],predictor_domain=row['predictor_domain'],corrector_domain=row['corrector_domain'],
        charge=charge(target['roles']['reset']['C'],c,p['charge']),uniquely_enclosed_current=True,geometry_rebuilt=True)


def dense_screen(target,role,dt):
    import numpy as np
    b,p=old.graph_data(target);c=target['roles'][role]['C'];rows=[]
    for k in range(STEPS):
        before=old.dense_point(b,np.array(c),np.eye(b.shape[1]),p['candidate'])
        h=old.generated_h(b,before['causal_flat'],p)
        j=old.dense_point(b,np.array(c),h,p['candidate'])['current']
        c=[float(x)-dt*sum(float(w)*v for w,v in zip(row,j,strict=True)) for x,row in zip(c,b,strict=True)]
        rows.append(dict(step=k+1,minimum_resource=min(c),after_C=c))
        require(all(math.isfinite(x) for x in c),'dense screen nonfinite')
    return dict(role=role,steps=rows,certifies_sign=False,native_steps=0)


def calculate(m):
    require(m==manifest(), 'input/source drift')
    _,initial=second_source_input();rows=[]
    start=time.monotonic()
    with ctx.workprec(BITS):
        source_step=step(subject_for_state(initial),list(initial.inputs.current.C),m['dt'])
        state=postbeat(initial,source_step['after_C'])
        require(trigger(state)['eligible'],'second-beat fresh trigger failed')
        _,_,request,identity,event,target=fresh_subject(state)
        print(json.dumps(dict(stage='second_source_beat',trigger=trigger(state),seconds=time.monotonic()-start)),flush=True)
        for role in ROLES:
            c=target['roles'][role]['C']
            value=step(target,c,m['dt']) if role=='current' else reused_reset_step(target,m['dt'])
            print(json.dumps(dict(role=role,step=1,minimum_resource=value['minimum_resource'],seconds=time.monotonic()-start)),flush=True)
            rows.append(dict(role=role,initial_C=c,steps=[value],exact_reused_reset_bounds=role=='reset'))
    screens=[dense_screen(target,role,m['dt']) for role in ROLES]
    return seal(dict(schema='p984h-cos-oracle-v1',inputs_digest=m['record_digest'],target_subject_digest=digest(target),
                     source_step=source_step,trigger=trigger(state),request=request,event_identity=identity,event_id=event,
                     cases=rows,dense_screens=screens,native_events=0,native_steps=0,user_accepted=False,aggregate_closed=False))


def check_steps(subject,c,steps,m):
    b,params=old.graph_data(subject)
    for value in steps:
            j=value['current'];require(len(j)==b.shape[1] and all(math.isfinite(x) for x in j),'current shape/finiteness')
            expected=[float(x)-m['dt']*sum(float(w)*v for w,v in zip(row,j,strict=True)) for x,row in zip(c,b,strict=True)]
            require(value['after_C']==expected and value['minimum_resource']==min(expected)>=0,'continuity/sign drift')
            require(value['charge']==charge(c,expected,params['charge']),'charge drift')
            require(value['uniquely_enclosed_current'] is True and value['geometry_rebuilt'] is True,'stage flags')
            require(0<=bounds.q(value['split_upper'])<=bounds.q(params['realization']['tolerance']),'split bound drift')
            for domain in (value['predictor_domain'],value['corrector_domain']):
                deviation=bounds.q(domain['geometry_deviation_upper'])
                require(0<=deviation<1 and bounds.q(domain['selector_gap_lower'])==(1-deviation)/(len(c)*(len(c)-1))-bounds.q(params['candidate']['Lambda_C'])>0,'selector bound drift')
                require(bounds.q(domain['retained_hodge_lower'])>0 and 1<=bounds.q(domain['condition_squared_upper'])<=bounds.q(params['solver']['conditioning_limit'])**2,'regularity/conditioning drift')
            c=expected
    return c


def check(m,r):
    require(m==manifest() and r==seal(r) and r['inputs_digest']==m['record_digest'], 'oracle/source identity drift')
    _,initial=second_source_input()
    after=check_steps(subject_for_state(initial),list(initial.inputs.current.C),[r['source_step']],m)
    state=postbeat(initial,after)
    _,_,request,identity,event,target=fresh_subject(state)
    require(r['trigger']==trigger(state) and r['trigger']['eligible'],'fresh trigger drift')
    require(r['request']==request and r['event_identity']==identity and r['event_id']==event,'fresh event identity drift')
    require(r['schema']=='p984h-cos-oracle-v1' and r['target_subject_digest']==digest(target), 'target identity drift')
    require([x['role'] for x in r['cases']]==list(ROLES), 'role roster drift')
    for case in r['cases']:
        c=target['roles'][case['role']]['C'];require(case['initial_C']==c and len(case['steps'])==1,'history/horizon drift')
        require(case['exact_reused_reset_bounds']==(case['role']=='reset'),'reuse scope drift')
        if case['role']=='reset':require(case['steps'][0]==reused_reset_step(target,m['dt']),'reset reuse drift')
        check_steps(target,c,case['steps'],m)
    require([s['role'] for s in r['dense_screens']]==list(ROLES),'dense role roster')
    for s in r['dense_screens']:
        require(len(s['steps'])==STEPS and s['certifies_sign'] is False and s['native_steps']==0,'dense scope drift')
        for i,x in enumerate(s['steps'],1):
            require(x['step']==i and len(x['after_C'])==len(target['graph']['live_node_ids'])
                and all(math.isfinite(y) for y in x['after_C']) and x['minimum_resource']==min(x['after_C']),'dense summary drift')
    require(r['native_events']==r['native_steps']==0 and r['user_accepted'] is False and r['aggregate_closed'] is False,'false native/acceptance credit')
    return dict(family='C_OS',checkpoint='8.4h',status='event_bound_oracle_complete_native_pending',
        oracle_steps=2,source_oracle_steps=1,exact_reused_reset_cases=1,dense_screen_steps=2*STEPS,
        planned_native_steps_per_role=STEPS,native_events=0,native_steps=0,user_accepted=False,
        aggregate_closed=False,numerics_recomputed=False,uniform_trajectory_enclosure=False,
        minima={c['role']:min(s['minimum_resource'] for s in c['steps']) for c in r['cases']})


def read_result():
    return json.loads(lzma.decompress((ROOT/RESULTS).read_bytes()))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=('prepare','run','check'))
    parser.add_argument('--recompute',action='store_true');args=parser.parse_args()
    require(not args.recompute or args.action=='check','recompute only with check')
    if args.action=='prepare':old.write_new(INPUTS,manifest());return
    m=old.read(INPUTS)
    if args.action=='run':
        require(not (ROOT/RESULTS).exists(),'refuse to overwrite evidence')
        def expired(*_):raise TimeoutError('declared oracle run cap exceeded; no result retained')
        signal.signal(signal.SIGALRM,expired);signal.alarm(m['run_cap_seconds'])
        r=calculate(m);check(m,r);raw=json.dumps(r,indent=2,allow_nan=False).encode()+b'\n'
        require(len(raw)<=m['raw_budget_bytes'],'raw budget exceeded')
        packed=lzma.compress(raw);require(len(packed)<=m['compressed_budget_bytes'],'compressed budget exceeded')
        with (ROOT/RESULTS).open('xb') as stream:stream.write(packed)
        signal.alarm(0)
    else:
        r=read_result();summary=check(m,r)
        if args.recompute:require(calculate(m)==r,'numerical reproduction drift');summary['numerics_recomputed']=True
        print(json.dumps(summary,indent=2))


if __name__=='__main__':main()

"""C_CI large event integration, reusing accepted joint-root mathematics."""
import argparse
from copy import deepcopy
from dataclasses import replace
import hashlib
import json
import lzma
import os
import signal
import time
from unittest.mock import patch

import p984g_cci_closure as prior
import p984h_cos as shared
from pygrc.models import grc_9_v4_lifecycle as native
from pygrc.models.grc_9_v4_expansion import (
    GRC9ExpansionPolicy, GRC9V4ExpansionPlan, GRC9V4ExpansionRequestInput,
    GRC9V4CCIExpansion, cci_profile_template,
)
from pygrc.models.grc_9_v4_topology import GRC9V4PortGraph
from pygrc.models.grc_v4_geometry import GeometryStageInputs
from pygrc.models.grc_v4_state import GRCV4AuthoritativeState, FrozenJSONMap
from pygrc.models.grc_v4_numerics import (
    ExactBackend, NumericalPolicy, exact_backend, numerical_policy, matrix_operation,
)

ROOT, BASE, HERE = prior.ROOT, prior.BASE, prior.HERE
SELF = HERE+'p984h_cci.py'
TEST = HERE+'test_p984h_cci.py'
PLAN = BASE+'P9-8.4h-CCIPlan.md'
INPUTS = BASE+'P9-8.4h-CCIInputs.json'
ROLES = ('current','reset')
CAPS = dict(source=600,event=1200)
require, seal, digest = shared.require, shared.seal, shared.digest


def path(segment):
    require(segment in CAPS,'unknown segment')
    return BASE+'P9-8.4h-CCI-'+segment+'.json.xz'


def read(segment):
    return json.loads(lzma.decompress((ROOT/path(segment)).read_bytes()))


def manifest():
    paths=set(prior.bindings()) | {SELF,TEST,PLAN,prior.RESULTS,prior.REVIEW,
        prior.case_path('source','current'),shared.SELF}
    return seal(dict(schema='p984h-cci-inputs-v1',family='C_CI',
        source_bindings={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(paths)},
        exact_backend='flint',numerical_policy='certified_arb_256_weighted_v1',caps=CAPS,
        source_beats=1,target_steps_per_role=10,covariance_transforms=list(
            ('edge_order','node_order','relabel','signed','combined','rotate','rotate_twice','reflect')),
        transformed_steps_per_role=1,compressed_budget=2000000,user_accepted=False,aggregate_closed=False))


def state(payload):
    spec=payload['specialization']
    return native.GRC9V4CCIState(GeometryStageInputs.from_payload(payload['inputs']),
        native.GRC9V4Specialization(FrozenJSONMap(spec['resolved']),FrozenJSONMap(spec['identity_payload'])))


def seed():
    before,subject,declaration=prior.setup.inputs_for('source','current')
    old=prior.f.read(prior.f.prior.PREPARED)
    spec=old['specialization']
    return native.GRC9V4CCIState(before,native.GRC9V4Specialization(
        FrozenJSONMap(spec['resolved']),FrozenJSONMap(spec['identity_payload']))),subject,declaration


def poststate(initial,result):
    require(digest(initial.inputs.to_payload())==result['before_digest'],'source before identity')
    after=replace(initial.inputs,current=GRCV4AuthoritativeState(tuple(result['after_C']),None,None),
        step_index=result['after_step_index'],time=result['after_time'])
    require(digest(after.to_payload())==result['after_digest'],'source after identity')
    require(after.reset==initial.inputs.reset and after.step_index==initial.inputs.step_index+1
        and after.time==initial.inputs.time+initial.inputs.dt,'source chronology/reset')
    return replace(initial,inputs=replace(after,dt=0))


def subject(value):
    ref=value.inputs.geometry.reference
    return dict(graph=ref.graph.port_graph.to_envelope(),profile=ref.profile.to_payload(),
        roles={r:dict(C=list(getattr(value.inputs,r).C),W_A=None,Z_4=None) for r in ROLES})


def fresh(post):
    """Reuse accepted graph allocation; independently map actual role resources."""
    old,prepared,_,declaration=prior.f.companion(prior.f.DEFICIT)
    request=deepcopy(declaration['event_request'])
    request.update(operation_id='p984h-cci-base',source_state_digest=post.scientific_digest)
    require(request['target_profile_template_id']==cci_profile_template(post.inputs.geometry.reference).profile_template_id,
        'profile template changed')
    plan=GRC9V4ExpansionPlan(post.inputs.geometry.reference.graph.port_graph,post.scientific_digest,
        GRC9V4ExpansionRequestInput.from_payload(request),GRC9ExpansionPolicy.from_payload(old['specialization']['resolved']['expansion']))
    require(plan.event_id!=declaration['event_id'],'stale prebeat event')
    graph=deepcopy(prepared['graph']);old_id=declaration['event_id']
    def rename(x):
        return plan.event_id+x[len(old_id):] if isinstance(x,str) and x.startswith(old_id+'/') else x
    graph['live_node_ids']=[rename(n) for n in graph['live_node_ids']]
    for edge in graph['edges']:
        edge['edge_id']=rename(edge['edge_id'])
        for end in ('tail','head'):edge[end]['node_id']=rename(edge[end]['node_id'])
    graph=GRC9V4PortGraph.from_payload({k:graph[k] for k in ('schema_version','live_node_ids','edges')})
    require(graph==plan.target_graph,'accepted graph allocation changed')
    matrix=prior.f.transfer_matrix(post.inputs.geometry.reference.graph.live_node_ids,
        graph.live_node_ids,plan.event_id,request['source_node_id'],prior.f.SHARES)
    roles={}
    expansion=GRC9V4CCIExpansion(plan,post.inputs.geometry.reference)
    for role in ROLES:
        cs=getattr(post.inputs,role).C
        values=[float(sum((w*prior.q(c) for w,c in zip(row,cs,strict=True)),prior.q(0))) for row in matrix]
        require(tuple(values)==expansion.transfer(getattr(post.inputs,role)).C,'independent resource transfer')
        roles[role]=dict(C=values,W_A=None,Z_4=None)
    # Profile construction is shared with preparation, not an independent physics oracle.
    profile=prior.f.prepared.profile_for(graph,'C_CI',old['selected_configuration'])
    require(profile==expansion.target.profile,'fresh complete target profile')
    return dict(request=request,event_id=plan.event_id,event_identity=plan.event_identity_payload(),
        target=dict(graph=graph.to_envelope(),profile=profile.to_payload(),roles=roles),
        trigger=shared.trigger(post),prepared_event_id=old_id)


def accepted_source():
    summary=prior.read(prior.RESULTS)
    require(summary==seal(summary) and summary['native_prerequisites_complete'],'prerequisite seal')
    require(summary['record_digest'] in (ROOT/prior.REVIEW).read_text()
        and '## Scoped user acceptance' in (ROOT/prior.REVIEW).read_text(),'prerequisite acceptance')
    pin=next(c for c in summary['cases'] if c['graph']=='source' and c['role']=='current')
    raw=(ROOT/pin['path']).read_bytes()
    require(hashlib.sha256(raw).hexdigest()==pin['sha256'],'historical source bytes')
    old=json.loads(lzma.decompress(raw))
    require(old==seal(old) and old['record_digest']==pin['record_digest'],'historical source digest')
    return old


def execute_source(progress):
    historical=accepted_source()
    result=prior.execute('source','current',progress)
    require(result==historical['result'],'fresh source differs from accepted numerical source')
    initial,_,_=seed();post=poststate(initial,result);event=fresh(post)
    require(event['trigger']['eligible'],'postbeat trigger ineligible')
    return dict(result=result,state=post.to_payload(),fresh=event,native_steps=1,native_events=0,
        historical_source_digest=historical['record_digest'],accepted_source_full_parity=True)


def execute_event(progress):
    prefix=check('source');post=state(prefix['execution']['state']);expected=prefix['execution']['fresh']
    progress('owner_source_readmission')
    owner=native.GRC9V4CCIOperation(post);checkpoint=owner.checkpoint();publication=owner._published
    stale=deepcopy(expected['request']);stale['source_state_digest']='grcv4-state-sha256:'+'0'*64
    rejected=owner.expand(GRC9V4ExpansionRequestInput.from_payload(stale))
    require(not rejected.committed and owner._published is publication and owner.checkpoint()==checkpoint,'stale rollback')
    real=native.ProvisionalCandidateCIStep;reads=[]
    def observed(inputs):
        progress('event_joint_read_'+str(len(reads)+1))
        step=real(inputs)
        require(owner._published is publication,'early publication')
        target_subject=subject(post) if not reads else expected['target']
        reads.append(dict(current=prior.independent_root(step.root,target_subject),
            reset=prior.independent_root(step.reset_root,target_subject),
            resources=list(inputs.current.C),reset_resources=list(inputs.reset.C),
            graph=inputs.geometry.reference.graph.port_graph.to_envelope(),old_publication_live=True))
        return step
    with patch.object(native,'ProvisionalCandidateCIStep',observed):
        outcome=owner.expand(GRC9V4ExpansionRequestInput.from_payload(expected['request']))
    require(outcome.committed,'native event failed: '+str(outcome.failure))
    require(subject(owner.state)==expected['target'],'fresh target mismatch')
    require(len(reads)==2 and owner.state.inputs.time==post.inputs.time
        and owner.state.inputs.step_index==post.inputs.step_index,'event admission/clock')
    return dict(predecessor_digest=prefix['record_digest'],checkpoint=json.loads(owner.checkpoint()),
        target=subject(owner.state),admissions=reads,event_id=expected['event_id'],
        stale_failure=rejected.failure.to_payload(),rollback_exact=True,native_events=1,native_steps=0)


def check(segment):
    m=prior.read(INPUTS);require(m==manifest(),'input/source drift')
    record=read(segment)
    require(record==seal(record) and record['manifest_digest']==m['record_digest'],'record binding')
    require(record['segment']==segment and record['outcome']=='completed'
        and record['seconds']<=CAPS[segment] and not record['user_accepted']
        and not record['aggregate_closed'],'scope/outcome')
    e=record['execution']
    if segment=='source':
        initial,_,_=seed();post=poststate(initial,e['result'])
        require(post.to_payload()==e['state'] and fresh(post)==e['fresh'],'source/fresh binding')
        require(e['result']==accepted_source()['result'] and e['accepted_source_full_parity']
            and e['fresh']['trigger']['eligible'] and e['native_steps']==1 and e['native_events']==0,'source parity/credit')
    else:
        prefix=check('source');expected=prefix['execution']['fresh'];target=state(e['checkpoint']['state'])
        require(e['predecessor_digest']==prefix['record_digest'] and e['event_id']==expected['event_id']
            and subject(target)==e['target']==expected['target'] and e['native_events']==1
            and e['native_steps']==0 and e['rollback_exact'],'event identity/target/credit')
        require(len(e['admissions'])==2,'admission coverage')
        for observed,operand in zip(e['admissions'],(subject(state(prefix['execution']['state'])),expected['target']),strict=True):
            require(observed['graph']==operand['graph'] and observed['old_publication_live'],'admission graph/order')
            for role in ROLES:
                root=observed[role]
                require(root['resource_digest']==digest(operand['roles'][role]['C']) and root['evaluations']==1
                    and root['consumed_reference_geometry'] and root['identity'].startswith('grcv4-ci-root-sha256:'),'joint root operand/identity')
                tolerance=prior.q(operand['profile']['params_resolved']['realization']['tolerance'])
                require(0<=prior.q(root['independent_residual_squared_upper'])<=tolerance**2
                    and 0<=prior.q(root['native_residual_squared'])<=tolerance**2,'joint residual')
    return record


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('prepare','run','check'))
    parser.add_argument('--segment',choices=tuple(CAPS),default='source');args=parser.parse_args()
    with exact_backend(ExactBackend.FLINT),numerical_policy(NumericalPolicy.CERTIFIED_ARB_256),matrix_operation():
        if args.action=='prepare':
            with (ROOT/INPUTS).open('x') as stream:json.dump(manifest(),stream,indent=2)
            return
        if args.action=='check':
            r=check(args.segment);print(json.dumps(dict(segment=args.segment,outcome=r['outcome'],native_rerun=False)));return
        require(not (ROOT/path(args.segment)).exists(),'refuse overwrite')
        require(all(os.environ.get(k)=='1' for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS')),'single thread')
        m=prior.read(INPUTS);require(m==manifest(),'input/source drift')
        start=time.monotonic()
        def progress(stage):print(json.dumps(dict(stage=stage,seconds=time.monotonic()-start)),flush=True)
        def expired(*_):raise TimeoutError('declared segment cap; no fallback or retry')
        signal.signal(signal.SIGALRM,expired);signal.alarm(CAPS[args.segment])
        try:e=(execute_source if args.segment=='source' else execute_event)(progress)
        finally:signal.alarm(0)
        elapsed=time.monotonic()-start
        require(elapsed<=CAPS[args.segment] and m==manifest(),'cap/source changed')
        record=seal(dict(schema='p984h-cci-native-v1',manifest_digest=m['record_digest'],segment=args.segment,
            execution=e,seconds=elapsed,outcome='completed',user_accepted=False,aggregate_closed=False))
        data=lzma.compress(json.dumps(record,separators=(',',':'),allow_nan=False).encode()+b'\n')
        require(len(data)<=m['compressed_budget'],'compressed retention budget')
        with (ROOT/path(args.segment)).open('xb') as stream:stream.write(data)
        print(json.dumps(dict(segment=args.segment,outcome='completed',seconds=elapsed,compressed_bytes=len(data))),flush=True)


if __name__=='__main__':main()

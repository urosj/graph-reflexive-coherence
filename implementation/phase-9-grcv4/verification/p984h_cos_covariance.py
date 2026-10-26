"""Large C_OS covariance, separate mechanical and native evidence.

Transport declarations are graph-size independent. Native execution starts at
the retained postbeat; it does not claim a transformed two-beat source prefix.
"""
import argparse
from copy import deepcopy
from dataclasses import replace
from functools import lru_cache
import json
import lzma
import signal
import time
from unittest.mock import patch

import p984h_cos_continuation as continuation
import p984e_cos as ordering
import p984f_cos as chart
from pygrc.models.grc_9_v4_expansion import (
    GRC9ExpansionPolicy, GRC9V4ExpansionPlan, GRC9V4ExpansionRequestInput,
    cos_profile_template,
)
from pygrc.models.grc_9_v4_topology import GRC9V4PortGraph
from pygrc.models.grc_v4_geometry import GeometryStageInputs
from pygrc.models.grc_v4_realizations import CandidateCOSPass

native=continuation.native
ROOT,BASE,HERE=native.ROOT,native.BASE,native.HERE
SELF=HERE+'p984h_cos_covariance.py'
TEST=HERE+'test_p984h_cos_covariance.py'
PLAN=BASE+'P9-8.4h-COSCovariancePlan.md'
INPUTS=BASE+'P9-8.4h-COSCovarianceInputs.json'
KINDS=('edge_order','node_order','relabel','signed','combined','rotate','rotate_twice','reflect')
require,digest,seal=native.require,native.digest,native.seal
ROLES=continuation.ROLES


def path(kind,segment):
    require(kind in KINDS or kind=='all','unknown transform')
    require(segment in ('mechanical','event','current','reset'),'unknown segment')
    require((kind=='all')==(segment=='mechanical'),'invalid segment/transform')
    return BASE+f'P9-8.4h-COSCovariance-{kind}-{segment}.json.xz'


def read(kind,segment):
    return json.loads(lzma.decompress((ROOT/path(kind,segment)).read_bytes()))


@lru_cache(maxsize=1)
def base():
    ev=continuation.event.read()
    require(ev==seal(ev) and ev['outcome']=='completed','event prerequisite')
    prefix=native.read('prefix')
    require(prefix==seal(prefix),'prefix seal')
    return prefix['execution']['state'],ev['execution']


def declaration(kind):
    require(kind in KINDS,'unknown transform')
    graph=base()[0]['inputs']['reference']['graph']
    n,m=len(graph['live_node_ids']),len(graph['edges'])
    cd=next(d for d in chart.declarations() if d['kind']==(kind if kind in ('rotate','rotate_twice','reflect') else 'base'))
    return dict(kind=kind,node_order=list(reversed(range(n))) if kind in ('node_order','combined') else list(range(n)),
        edge_order=list(reversed(range(m))) if kind in ('edge_order','combined') else list(range(m)),
        signs=[-1 if kind in ('signed','combined') and i%2==0 else 1 for i in range(m)],
        relabel=kind in ('relabel','combined'),chart=cd)


def labels(d):
    g=base()[0]['inputs']['reference']['graph']
    return ({n:f'vertex-{len(g["live_node_ids"])-i:03d}' if d['relabel'] else n for i,n in enumerate(g['live_node_ids'])},
        {e['edge_id']:f'edge-{len(g["edges"])-i:04d}' if d['relabel'] else e['edge_id'] for i,e in enumerate(g['edges'])})


def rename(x,d,old_event=None,new_event=None):
    nodes,edges=labels(d)
    if isinstance(x,str) and old_event and x.startswith(old_event+'/'):
        # Reuse accepted branch/ordinal distinction, not star-node labeling.
        return chart.label(x,d['chart'],old_event,new_event)
    return nodes.get(x,edges.get(x,x))


def graph_image(graph,d,old_event=None,new_event=None,*,source=False):
    g=deepcopy(graph);original=base()[0]['inputs']['reference']['graph']['edges']
    signs={e['edge_id']:d['signs'][i] for i,e in enumerate(original)}
    g['live_node_ids']=[rename(n,d,old_event,new_event) for n in graph['live_node_ids']]
    for e in g['edges']:
        old=e['edge_id'];e['edge_id']=rename(old,d,old_event,new_event)
        for end in ('tail','head'):
            e[end]['node_id']=rename(e[end]['node_id'],d,old_event,new_event)
            e[end]['port']=d['chart']['ports'][str(e[end]['port'])]
        if signs.get(old,1)<0:e['tail'],e['head']=e['head'],e['tail']
    if source:
        g['live_node_ids']=[g['live_node_ids'][i] for i in d['node_order']]
        g['edges']=[g['edges'][i] for i in d['edge_order']]
    else:
        g['live_node_ids'].sort(key=lambda n:(type(n)is str,ordering.b.canonical_json_bytes(n)))
        g['edges'].sort(key=lambda e:e['edge_id'].encode('utf-16-be'))
    return g


def mapping(old,new,d,old_event=None,new_event=None):
    """Independent identity and endpoint comparison, including every port."""
    expected=graph_image(old,d,old_event,new_event)
    require(set(expected['live_node_ids'])==set(new['live_node_ids']) and len(expected['live_node_ids'])==len(new['live_node_ids']),'node bijection')
    by={e['edge_id']:e for e in expected['edges']}
    require(len(by)==len(new['edges']) and by=={e['edge_id']:e for e in new['edges']},'edge/port image')
    original_nodes={rename(n,d,old_event,new_event):i for i,n in enumerate(old['live_node_ids'])}
    ni=[original_nodes[n] for n in new['live_node_ids']]
    original_edges={rename(e['edge_id'],d,old_event,new_event):i for i,e in enumerate(old['edges'])}
    ei=[original_edges[e['edge_id']] for e in new['edges']]
    source_edges=base()[0]['inputs']['reference']['graph']['edges']
    signs={e['edge_id']:d['signs'][i] for i,e in enumerate(source_edges)}
    return ni,ei,[signs.get(old['edges'][i]['edge_id'],1) for i in ei]


def input_image(original,g,d,old_event=None,new_event=None):
    ni,ei,sign=mapping(original['reference']['graph'],g,d,old_event,new_event)
    p=deepcopy(original);p['reference']['graph']=g
    for role in ROLES:p[role]['C']=[original[role]['C'][i] for i in ni]
    for owner,key in ((p['reference'],'K4_base'),(p,'H1_form')):
        a=owner[key];owner[key]=[[a[i][j]*sign[k]*sign[l] if a[i][j] else 0. for l,j in enumerate(ei)] for k,i in enumerate(ei)]
    for weights in (p['reference']['reference_hodge']['edge_weights'],p['reference']['profile']['params_resolved']['candidate']['W_C_tr']):
        saved=list(weights.items());weights.clear();weights.update({rename(k,d,old_event,new_event):v for k,v in saved})
    ordering.reidentify(p['reference'])
    return ordering.materialize(original,p)


@lru_cache(maxsize=8)
def subject(kind):
    # Process-local transport construction only; never a cached native read,
    # numerical admission or event result. Immutable inputs are source-bound.
    d=declaration(kind);source,event=base()
    inp=input_image(source['inputs'],graph_image(source['inputs']['reference']['graph'],d,source=True),d)
    seed=replace(native.state(source),inputs=inp)
    request=deepcopy(event['request']);branches=d['chart']['branches'];shares=[0.]*3
    for i,x in enumerate(request['resource_distribution'],1):shares[branches[str(i)]-1]=x
    request.update(source_node_id=rename(request['source_node_id'],d),source_state_digest=seed.scientific_digest,
        source_graph_digest=inp.geometry.reference.graph.graph_digest,
        target_profile_template_id=cos_profile_template(inp.geometry.reference).profile_template_id,
        operation_id='p984h-covariance-'+kind,resource_distribution=shares,
        module_chirality=request['module_chirality']*d['chart']['chirality_factor'],
        growth_phase=branches[str(request['growth_phase'])])
    identity=deepcopy(event['event_identity'])
    for key in identity:
        if key in request and key!='schema_version':identity[key]=request[key]
    event_id=ordering.b.payload_identity('expansion_event_identity_payload',identity)
    target=event['checkpoint']['state']['inputs']
    g=graph_image(target['reference']['graph'],d,event['event_id'],event_id)
    expected=input_image(target,g,d,event['event_id'],event_id)
    return seed,request,identity,event_id,expected


def manifest():
    upstream=native.oracle.old.read(continuation.INPUTS)
    require(upstream==continuation.manifest(),'baseline source drift')
    paths={SELF,TEST,PLAN,ordering.SELF,chart.SELF,continuation.SELF,continuation.INPUTS,
        native.path('prefix'),*[continuation.path(r,1) for r in ROLES],*upstream['source_bindings']}
    return seal(dict(schema='p984h-cos-covariance-inputs-v1',
        source_bindings={p:native.oracle.sha(p) for p in sorted(paths)},
        transforms=[declaration(k) for k in KINDS],baseline_event_digest=continuation.event.read()['record_digest'],
        numerical_policy='certified_arb_256_weighted_v1',backend='flint',
        event_cap_seconds=1200,step_cap_seconds=600,comparison=dict(atol=2e-11,rtol=2e-11),
        target_steps_per_role=1,source_prefix_rerun=False,transformed_horizon=1,
        initial_native_transform='combined',uniform_domain=False,user_accepted=False,aggregate_closed=False))


def mechanical():
    rows=[]
    for kind in KINDS:
        seed,q,identity,eid,expected=subject(kind)
        plan=GRC9V4ExpansionPlan(seed.inputs.geometry.reference.graph.port_graph,seed.scientific_digest,
            GRC9V4ExpansionRequestInput.from_payload(q),GRC9ExpansionPolicy.from_payload(seed.specialization.resolved['expansion']))
        require(plan.event_identity_payload()==identity and plan.event_id==eid,'event identity transport')
        actual=plan.target_graph.to_payload()
        require({k:actual[k] for k in ('schema_version','live_node_ids','edges')}==expected.to_payload()['reference']['graph'],'exact allocator covariance')
        for role in ROLES:
            values=dict(zip(seed.inputs.geometry.reference.graph.live_node_ids,getattr(seed.inputs,role).C,strict=True))
            image={n:values.get(n,0.) for n in plan.target_graph.live_node_ids}
            for i,share in enumerate(q['resource_distribution'],1):
                image[eid+f'/satellite/{i}']=float(native.oracle.Fraction(values[q['source_node_id']])*native.oracle.Fraction(share))
            require([image[n] for n in plan.target_graph.live_node_ids]==list(getattr(expected,role).C),'independent resource map covariance')
        rows.append(dict(kind=kind,event_id=eid,source_digest=seed.scientific_digest,
            target_digest=digest(expected.to_payload()),request=q,target_graph_digest=plan.target_graph.graph_digest,
            exact_graph_and_both_role_transfer=True,native_events=0,native_steps=0))
    return rows


def compare_point(old,new,ei,sign):
    errors={}
    for field in ('current','baseline','read_flux','causal_flat'):
        expected=native.np.asarray(old[field])[ei]*native.np.asarray(sign)
        actual=native.np.asarray(new[field])
        require(native.np.isfinite(actual).all() and native.np.allclose(actual,expected,atol=2e-11,rtol=2e-11),'covariance '+field)
        errors[field]=float(native.np.max(abs(actual-expected)))
    require(new['selector_rank']==old['selector_rank'],'selector rank covariance')
    return errors


def compare_step(kind,role,row,after,geometry):
    _,_,_,eid,expected=subject(kind);d=declaration(kind)
    original=continuation.initial(role);baseline=continuation.read(role,1)
    ni,ei,sign=mapping(original.to_payload()['reference']['graph'],expected.to_payload()['reference']['graph'],d,base()[1]['event_id'],eid)
    errors={stage:compare_point(baseline['observation'][stage],row[stage],ei,sign) for stage in ('predictor','corrector','final')}
    target=native.np.asarray(baseline['next_inputs']['current']['C'])[ni]
    require(native.np.allclose(after.current.C,target,atol=2e-11,rtol=2e-11),'resource covariance')
    require(row['split_admitted'] and min(after.current.C)>0 and after.reset==expected.reset,'target admission/reset')
    # Independent OS generated-H formula, not a comparison of only current.
    subject=dict(graph=original.geometry.reference.graph.port_graph.to_payload(),profile=original.geometry.reference.profile.to_payload())
    incidence,params=native.oracle.old.graph_data(subject)
    h=native.oracle.old.generated_h(incidence,native.np.array(baseline['observation']['predictor']['causal_flat']),params)
    transported=h[native.np.ix_(ei,ei)]*native.np.outer(sign,sign)
    actual=native.np.array(geometry['corrector'])
    require(native.np.isfinite(actual).all() and native.np.allclose(actual,transported,atol=2e-11,rtol=2e-11),'generated geometry covariance')
    for stage in ('predictor','corrector','final'):
        require(digest(geometry[stage])==row[stage]['input_hodge_digest'],'geometry capture identity')
    require(geometry['predictor']==expected.to_payload()['H1_form'] and geometry['final']==geometry['corrector'],'geometry staging')
    return dict(points=errors,resources=float(native.np.max(abs(native.np.asarray(after.current.C)-target))),
        generated_geometry=float(native.np.max(abs(actual-transported))))


def execute_event(kind):
    seed,q,identity,eid,expected=subject(kind)
    owner=native.native.GRC9V4COSOperation(seed);publication=owner._published
    checkpoint=owner.checkpoint();stale=dict(q,source_state_digest='grcv4-state-sha256:'+'0'*64)
    rejection=owner.expand(GRC9V4ExpansionRequestInput.from_payload(stale))
    require(not rejection.committed and owner._published is publication and owner.checkpoint()==checkpoint,'stale rollback')
    reads=[];real=native.native.CandidateCOSPass
    def observed(operand):
        print(json.dumps(dict(kind=kind,stage='event_read',index=len(reads)+1)),flush=True)
        passed=real(operand);require(owner._published is publication,'early publication')
        reads.append(dict(predictor=native.capture.point(passed.predictor),corrector=native.capture.point(passed.corrector),
            split_admitted=passed.residual.admitted,old_publication_live=True))
        return passed
    with patch.object(native.native,'CandidateCOSPass',observed):
        outcome=owner.expand(GRC9V4ExpansionRequestInput.from_payload(q))
    require(outcome.committed,'transformed event rejected: '+str(outcome.failure))
    actual=owner.state.inputs
    require(actual.geometry==expected.geometry and actual.current==expected.current and actual.reset==expected.reset,'transformed target differs')
    require(actual.time==seed.inputs.time and actual.step_index==seed.inputs.step_index and len(reads)==4,'event clock/read count')
    errors=[]
    for i,r in enumerate(reads):
        old=base()[0]['inputs'] if i<2 else base()[1]['checkpoint']['state']['inputs']
        new=seed.inputs if i<2 else actual
        ni,ei,sign=mapping(old['reference']['graph'],new.to_payload()['reference']['graph'],declaration(kind),base()[1]['event_id'],eid)
        errors.append({s:compare_point(base()[1]['admissions'][i][s],r[s],ei,sign) for s in ('predictor','corrector')})
    return dict(request=q,event_identity=identity,event_id=eid,target=owner.state.to_payload(),admissions=reads,
        covariance_errors=errors,rollback_exact=True,stale_failure=rejection.failure.to_payload(),
        checkpoint=json.loads(owner.checkpoint()),native_events=1,native_steps=0)


def execute_step(kind,role):
    ev=read(kind,'event');check_record(ev,native.oracle.old.read(INPUTS),kind,'event')
    target=native.state(ev['execution']['target']).inputs
    before=replace(target,current=getattr(target,role),dt=continuation.initial(role).dt)
    geometry={};real=native.ProvisionalCandidateCOSStep
    def observed(operand):
        step=real(operand)
        for name,point in (('predictor',step.os_pass.predictor),('corrector',step.os_pass.corrector),('final',step.final)):
            geometry[name]=[list(r) for r in point.inputs.geometry.one_form_hodge.matrix]
        return step
    with patch.object(native,'ProvisionalCandidateCOSStep',observed):row,after=native.observe_step(before)
    errors=compare_step(kind,role,row,after,geometry)
    return dict(event_record_digest=ev['record_digest'],role=role,observation=row,next_inputs=after.to_payload(),
        geometry=geometry,covariance_errors=errors,native_events=0,native_steps=1,detached_continuation=True)


def check_record(record,m,kind,segment):
    require(record==seal(record) and record['manifest_digest']==m['record_digest'] and record['schema']=='p984h-cos-covariance-results-v1','record identity')
    require(record['kind']==kind and record['segment']==segment and record['outcome']=='completed'
        and record['user_accepted'] is False and record['aggregate_closed'] is False,'record scope')
    e=record['execution']
    if segment=='mechanical':require(e==mechanical(),'mechanical drift');return
    cap=m['event_cap_seconds'] if segment=='event' else m['step_cap_seconds']
    require(0<=record['elapsed_seconds']<=cap,'cap')
    seed,q,identity,eid,expected=subject(kind)
    if segment=='event':
        require(e['request']==q and e['event_identity']==identity and e['event_id']==eid,'event identity')
        actual=native.state(e['target']).inputs
        require(actual.geometry==expected.geometry and actual.current==expected.current and actual.reset==expected.reset,'event target')
        require(e['native_events']==1 and e['native_steps']==0 and len(e['admissions'])==4 and e['rollback_exact'] is True,'event coverage')
        require(e['checkpoint']['state']==e['target'],'checkpoint state')
        require(e['checkpoint']['initial']==seed.to_payload() and e['checkpoint']['requests']==[q]
            and len(e['checkpoint']['receipts'])>0 and bool(e['stale_failure']),'checkpoint lineage')
        require(actual.time==seed.inputs.time and actual.step_index==seed.inputs.step_index,'event clock')
        for i,r in enumerate(e['admissions']):
            require(r['split_admitted'] and r['old_publication_live'],'admission scope')
            old=base()[0]['inputs'] if i<2 else base()[1]['checkpoint']['state']['inputs']
            new=seed.inputs if i<2 else actual
            _,ei,sign=mapping(old['reference']['graph'],new.to_payload()['reference']['graph'],declaration(kind),base()[1]['event_id'],eid)
            require(e['covariance_errors'][i]=={s:compare_point(base()[1]['admissions'][i][s],r[s],ei,sign) for s in ('predictor','corrector')},'admission errors')
    else:
        ev=read(kind,'event');require(e['event_record_digest']==ev['record_digest'] and e['role']==segment,'step predecessor')
        target=native.state(ev['execution']['target']).inputs
        before=replace(target,current=getattr(target,segment),dt=continuation.initial(segment).dt)
        after=native.validate_steps([e['observation']],before)
        require(e['next_inputs']==after.to_payload() and e['native_events']==0 and e['native_steps']==1 and e['detached_continuation'] is True,'step scope/chain')
        require(e['covariance_errors']==compare_step(kind,segment,e['observation'],after,e['geometry']),'step errors')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('prepare','run','check'))
    parser.add_argument('--kind',choices=('all',*KINDS),default='all')
    parser.add_argument('--segment',choices=('mechanical','event',*ROLES),default='mechanical')
    args=parser.parse_args()
    with native.oracle.exact_backend(native.oracle.ExactBackend.FLINT),native.oracle.numerical_policy(native.oracle.NumericalPolicy.CERTIFIED_ARB_256):
        if args.action=='prepare':native.oracle.old.write_new(INPUTS,manifest());return
        m=native.oracle.old.read(INPUTS);require(m==manifest(),'source drift')
        p=ROOT/path(args.kind,args.segment)
        if args.action=='check':
            check_record(read(args.kind,args.segment),m,args.kind,args.segment)
            print('retained covariance check passed; no native replay');return
        require(not p.exists(),'refuse overwrite')
        cap=m['event_cap_seconds'] if args.segment=='event' else m['step_cap_seconds']
        def expired(*_):raise TimeoutError('declared covariance cap; no fallback')
        signal.signal(signal.SIGALRM,expired);signal.alarm(cap);started=time.monotonic()
        try:
            with native.matrix_operation():
                execution=mechanical() if args.segment=='mechanical' else execute_event(args.kind) if args.segment=='event' else execute_step(args.kind,args.segment)
        finally:signal.alarm(0)
        elapsed=time.monotonic()-started;require(elapsed<=cap,'cap exceeded')
        r=seal(dict(schema='p984h-cos-covariance-results-v1',manifest_digest=m['record_digest'],kind=args.kind,segment=args.segment,
            outcome='completed',execution=execution,elapsed_seconds=elapsed,user_accepted=False,aggregate_closed=False))
        require(m==manifest(),'sources changed during execution');check_record(r,m,args.kind,args.segment)
        packed=lzma.compress(json.dumps(r,separators=(',',':'),allow_nan=False).encode()+b'\n')
        with p.open('xb') as stream:stream.write(packed)
        require(len(packed)<=2000000,'complete evidence retained; compressed budget exceeded')
        print(json.dumps(dict(kind=args.kind,segment=args.segment,seconds=elapsed,compressed_bytes=len(packed))),flush=True)


if __name__=='__main__':main()

"""Connected C_RG2b native observations and independent outward equations.

Only observation/checker hooks are adapted from the accepted tree harness.
Native producers execute unchanged. Retained checks never rerun trajectories.
"""
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import replace
from functools import lru_cache
import importlib.util
import json
from pathlib import Path
from unittest.mock import patch
import numpy as np
from flint import arb, arb_mat, ctx, fmpq as Q
import p9_crg2b_completion as proof
import p9_crg2b_section as oracle
from p9_cpc_compute import worker as arithmetic
from p9_cpc_covariance_compute import wire_reuse
from pygrc.models import grc_9_v4_crg2b_connected as native_completion
from pygrc.models.grc_v4_ci import _norm
from pygrc.models.grc_v4_rg2b_graph import rounded_upper

spec=importlib.util.spec_from_file_location('_connected_crg2b_observations',Path(__file__).with_name('p984b_crg2b_runtime.py'))
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
b=r.b
SELF=b.HERE+'p9_crg2b_runtime.py'
ROLES=r.ROLES
exact,ball,mat,eye,mag,norm=oracle.exact,oracle.ball,oracle.matrix,oracle.eye,oracle.magnitude,oracle.norm

@contextmanager
def worker():
    with arithmetic() as policy,wire_reuse() as wire:
        yield dict(policy,family='C_RG2b',section_bits=192,section_depth=6,section_sweeps=18,
                   serialization_reuse=wire,large_segment_cap_seconds=3600)

@lru_cache(maxsize=8)
def graph_data(raw):
    graph=json.loads(raw);cert=proof.graph_certificate(graph)
    cert.pop('elapsed_seconds',None)
    b.require(all(cert['checks'].values()),'independent connected graph hypotheses')
    bi,d,mask,_=proof.graph_algebra(graph)
    return cert,bi,mask

def data(before):return graph_data(json.dumps(before.geometry.reference.graph.port_graph.to_payload(),sort_keys=True))

def configure(before):
    return r.configure(before,changes={'realization':dict(extension_evaluator_id=native_completion.EXTENSION,
        containment_certificate_id=native_completion.CONTAINMENT,approximation_policy_id=native_completion.APPROXIMATION)})

@contextmanager
def capture_chains():
    real=native_completion.certify_chain;rows=[]
    def observed(cert,query,x,h):
        error,bounds=real(cert,query,x,h)
        rows.append(dict(input_identity=cert.inputs.identity,query=list(query),work=oracle.encode(x,h),
            native_chain_error=str(error),native_chain_bounds={k:str(v) for k,v in bounds.items()},
            native_global_bounds=cert.bounds.to_dict()))
        return error,bounds
    with patch.object(native_completion,'certify_chain',observed):yield rows


def equations(before,h,*,geometry=True,feedback=True,modulation=True):
    """Independent unreduced edge equations (Arb 192), not the native vertex kernel."""
    cert,bi,mask=data(before);bi=mat(bi.tolist());bt=bi.transpose();d=bt*bi
    n,m=bi.nrows(),bi.ncols();h=mat(h) if geometry else eye(m)
    c=arb_mat([[ball(v)] for v in before.current.C])
    t=(ball(proof.KM)*(sum((c[i,0] for i in range(n)),arb(0))/n).tanh()).exp() if modulation else arb(1)
    j0=-t*d*h*bt*c
    a=eye(m)+t*h*d
    u=(a-ball(proof.CHI*proof.ZETA if feedback else 0)*eye(m)).solve(j0)
    j=j0+ball(proof.CHI*proof.ZETA)*u if feedback else j0
    flux=a.solve(ball(16)*j);flat=h.solve(flux)
    source=arb_mat([[ball(proof.ZETA*mask[i,k])*flat[i,0]*flat[k,0] for k in range(m)] for i in range(m)])
    return dict(H=h,J=j,baseline=j0,readback=flux,flat=flat,source=source,
                increment=-ball(proof.DT)*bi*j,image=eye(m)+source/2)


def matrix_error(values,expected):
    v=np.asarray(values);a=mat(v.reshape(-1,1).tolist()) if v.ndim==1 else mat(v.tolist())
    return norm(a-expected)


def independent_certificate(before,value):
    cert,_,_=data(before);xs,hs=oracle.decode(value['chain']['work'])
    section=oracle.certify(before.geometry.reference.graph.port_graph.to_payload(),before.current.C,xs,hs,cert)
    with ctx.workprec(192):
        truth=equations(before,value['H'])
        errors={k:str(matrix_error(value[k],truth[k])) for k in ('J','baseline','readback','flat','source')}
    b.require(section['section_tolerance_passes'],'independent section residual/tail failure')
    limits=dict(J=2**-40,baseline=2**-40,readback=2**-40,flat=2**-40,source=2**-64)
    b.require(all(Q(errors[k])<=exact(v) for k,v in limits.items()),'independent fixed-H physical equations fail')
    return dict(input_identity=before.identity,selected_read_digest=value['record_digest'],section=section,
        fixed_H_errors=errors,graph_certificate_digest=b.digest(cert),
        fixed_H_read_error_is_not_infinite_section_error=True)


def check_read(before,value,*,numerics=False):
    b.check_digest({k:v for k,v in value.items() if k!='independent_certificate'})
    b.require(value['input_identity']==before.identity and value['recipe']==native_completion.APPROXIMATION
        and value['levels']==6 and value['evaluations']==222,'read identity/policy/depth')
    xs,hs=oracle.decode(value['chain']['work'])
    b.require(value['chain']['input_identity']==before.identity and value['chain']['query']==list(before.current.C)
        and np.array_equal(xs[0],before.current.C) and np.array_equal(hs[0],value['H'])
        and np.array_equal(hs[-1],np.eye(len(hs[-1]))),'section query/full geometry/terminal mismatch')
    selected=replace(before,geometry=b.GRCV4Geometry(before.geometry.reference,
        b.OneFormHodge(before.geometry.reference.graph,tuple(map(tuple,value['H'])))),stage='rg2b_section')
    b.require(selected.identity==value['selected_inputs_identity'] and value['read_current']==value['J']
        and value['read_source']==value['point_identity'],'selected point/readback identity')
    b.require(value['identity']=='grcv4-rg2b-section-sha256:'+b.digest(dict(numerics=native_completion.APPROXIMATION,
        inputs=before.to_payload(),differential_reference=None)),'full section identity')
    ce=value['independent_certificate'];sc=ce['section']
    b.require(ce['input_identity']==before.identity and ce['selected_read_digest']==value['record_digest']
        and Q(sc['section_error_upper'])<=Q(value['error_upper'])<=Q(1,2**48)
        and list(map(Q,value['enclosure']))==[-Q(value['error_upper']),Q(value['error_upper'])], 'error enclosure binding')
    b.require(before.current.W_A is None and before.current.Z_4 is None,'invented history')
    if numerics:b.require(ce==independent_certificate(before,value),'independent numerical certificate drift')


def read_record(section,point,chain):
    value=b.seal(dict(input_identity=section.inputs.identity,identity=section.identity,
        selected_inputs_identity=point.inputs.identity,point_identity=point.identity,read_source=point.read.source_identity,
        read_current=list(point.read.current.values),H=[list(row) for row in section.geometry.one_form_hodge.matrix],
        J=list(point.current.values),baseline=list(point.algebra.baseline.values),readback=list(point.read.flux.values),
        flat=list(point.read.causal_flat.values),source=[list(row) for row in r._source(point,point.current).increment],
        levels=section.levels,evaluations=section.evaluations,error_upper=section.error_upper,
        enclosure=list(section.enclosure),recipe=section.to_payload()['numerics'],chain=chain))
    value['independent_certificate']=independent_certificate(section.inputs,value);check_read(section.inputs,value)
    return value


def bridge(before,value):
    with ctx.workprec(192):
        truth=equations(before,value['read']['H']);j=truth['J'];g=truth['image']
        je=_norm(mag(ball(v)-j[i,0]) for i,v in enumerate(value['read']['J']))
        jn=_norm(mag(j[i,0]) for i in range(j.nrows()))
        after=value['poststate']['current']['C']
        xe=max(mag(ball(v)-ball(before.current.C[i])-truth['increment'][i,0]) for i,v in enumerate(after))
        he=norm(mat(value['generated'])-g)
        residual=norm(mat(value['restart']['H'])-mat(value['generated']))
        cert,_,_=data(before);gb={k:Q(v) for k,v in cert['bounds'].items()}
        e=Q(value['read']['error_upper']);last=Q(value['restart']['error_upper'])
        bound=last+he+gb['B_H']*e/2+proof.LIP*(xe+gb['A_H']*e)
        resource_error=xe+gb['A_H']*e
        positive=min(oracle.lower(ball(v))-resource_error for v in after)
    return {k:str(v) for k,v in dict(current_l2_error=je,current_l2_upper=jn,state_error=xe,geometry_error=he,
        invariance_residual=residual,invariance_error_bound=bound,resource_error=resource_error,
        exact_real_next_resource_lower=positive).items()}


def perform_step(before):
    with capture_chains() as rows:step=r.rg.ProvisionalCandidateRG2bStep(before)
    b.require(len(rows)==3 and step.writer is None,'ordinary section count/history')
    value=dict(prestate=before.to_payload(),poststate=step.next_inputs.to_payload(),
        reset_read=read_record(step.reset_section,step.reset_point,rows[0]),read=read_record(step.section,step.point,rows[1]),
        restart=read_record(step.restart,step.restart_point,rows[2]),
        generated=[list(row) for row in step.generated.one_form_hodge.matrix],diagnostics=step.diagnostics.to_dict())
    value['independent_bridge']=bridge(before,value);check_step(before,value)
    return value,step.next_inputs


def check_step(before,value,*,numerics=False):
    b.require(value['prestate']==before.to_payload() and before.dt==b.DT,'step operand')
    after=b.GeometryStageInputs.from_payload(value['poststate'])
    expected=replace(before,current=replace(before.current,C=r.represented_continuity(before,value['read']['J'])),
        time=float(exact(before.time)+exact(before.dt)),step_index=before.step_index+1)
    b.require(after==expected,'continuity/time/reset/multiple-write drift')
    for operand,key in ((replace(before,current=before.reset),'reset_read'),(before,'read'),(after,'restart')):
        check_read(operand,value[key],numerics=numerics)
    generated=[[float(Q(i==j)+exact(v)/2) for j,v in enumerate(row)] for i,row in enumerate(value['read']['source'])]
    b.require(generated==value['generated'],'same-point structural source not consumed')
    cert={k:Q(v) for k,v in value['independent_bridge'].items()};p=before.geometry.reference.profile.params_resolved.solver
    b.require(cert['current_l2_error']<=exact(p.absolute_tolerance)+exact(p.relative_tolerance)*cert['current_l2_upper']
        and cert['geometry_error']<=Q(1,2**48) and proof.LIP*cert['state_error']<=Q(1,2**48)
        and cert['invariance_residual']<=cert['invariance_error_bound'],'independent native/infinite-section bridge')
    diag=value['diagnostics']
    b.require(diag['regularity']=='Lipschitz_only' and diag['continuity_evaluations']==1 and diag['carrier_writes']==0
        and Q(diag['invariance_residual'])==cert['invariance_residual']
        and Q(diag['invariance_residual'])<=Q(diag['invariance_error_bound']),'native invariance/staging')
    if numerics:b.require(value['independent_bridge']==bridge(before,value),'bridge drift')
    return after


def independent_target(manifest,case):
    import p984e_cos as ordering
    source=b.GeometryStageInputs.from_payload(manifest['expected_source']['inputs']);v=deepcopy(source.to_payload())
    graph=case['oracle']['target_graph'];ref=v['reference'];ref['graph']=graph
    weights={e['edge_id']:1 for e in graph['edges']};m=len(weights)
    ref['K4_base']=[[0.0]*m for _ in range(m)];ref['reference_hodge']['edge_weights']=weights.copy()
    ref['profile']['params_resolved']['candidate']['W_C_tr']=weights.copy();ordering.reidentify(ref)
    reference=b.GRCV4ReferenceGeometry.from_payload(ref);roles={}
    for role in ROLES:
        old=dict(zip(source.geometry.reference.graph.live_node_ids,getattr(source,role).C,strict=True))
        image={n:old.get(n,0.) for n in graph['live_node_ids']}
        for j,share in enumerate(case['request']['resource_distribution'],1):
            image[case['oracle']['event_id']+f'/satellite/{j}']=float(exact(old[case['request']['source_node_id']])*exact(share))
        roles[role]=b.GRCV4AuthoritativeState(tuple(image[n] for n in graph['live_node_ids']),None,None)
    return replace(source,geometry=reference.geometry(),**roles,dt=0,operation_id=case['request']['operation_id'])

# Reuse only event observation, receipt/replay and transfer assertions.
r.signed=native_completion;r.capture_chains=capture_chains;r.read_record=read_record;r.check_read=check_read
r.perform_step=perform_step;r.check_step=check_step
state=r.state
native_read=r.native_read

def event_capture(seed,request):
    # The native registry stores callables. Route its readmit through the
    # observational wrapper installed by the historical event harness.
    row=r.native._FAMILY_IMPLEMENTATIONS['C_RG2b']
    with patch.dict(r.native._FAMILY_IMPLEMENTATIONS,{'C_RG2b':replace(row,readmit=lambda subject:r.native._crg2b_readmit(subject))}):
        return r.event_capture(seed,request)
def check_event(seed,case,value,*,numerics=False):
    with patch.object(b,'independent_target',independent_target):return r.check_event(seed,case,value,numerics=numerics)

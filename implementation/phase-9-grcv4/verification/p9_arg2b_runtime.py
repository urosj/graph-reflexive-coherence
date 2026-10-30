"""Connected A_RG2b observations; independent joint edge-space certificates."""
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import replace
from functools import lru_cache
import importlib.util,json,math
from pathlib import Path
from unittest.mock import patch
import numpy as np
from flint import ctx,fmpq as Rational
import p9_arg2b_completion as proof
import p9_arg2b_section as oracle
from p9_cpc_compute import worker as arithmetic
from p9_cpc_covariance_compute import wire_reuse
from pygrc.models import grc_9_v4_arg2b_connected as native_completion
from pygrc.models.grc_v4_ci import _norm

spec=importlib.util.spec_from_file_location('_connected_arg2b_observations',Path(__file__).with_name('p984b_arg2b_runtime.py'))
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
b=r.b
SELF=b.HERE+'p9_arg2b_runtime.py'
ROLES=r.ROLES
def Q(v,den=None):
 return Rational(*float(v).as_integer_ratio()) if isinstance(v,(float,np.floating)) and den is None else (Rational(v) if den is None else Rational(v,den))
exact,ball,mat,eye,mag,norm=oracle.exact,oracle.ball,oracle.matrix,oracle.eye,oracle.magnitude,oracle.norm

@contextmanager
def worker():
 with arithmetic() as policy,wire_reuse() as wire:
  yield dict(policy,family='A_RG2b',section_bits=192,section_depth=4,section_sweeps=18,
   serialization_reuse=wire,large_segment_cap_seconds=3600)

@lru_cache(maxsize=8)
def graph_data(raw):
 graph=json.loads(raw);cert=proof.graph_certificate(graph)
 b.require(all(cert['checks'].values()),'independent connected graph hypotheses')
 return cert,oracle.algebra(graph)

def data(before):return graph_data(json.dumps(before.geometry.reference.graph.port_graph.to_payload(),sort_keys=True))

def configure(before):
 from tests.models.test_grc_9_v4_arg2b import configure as old
 return old(before,{'realization':dict(extension_evaluator_id=native_completion.EXTENSION,
  containment_certificate_id=native_completion.CONTAINMENT,approximation_policy_id=native_completion.APPROXIMATION)})

def reidentify(ref):
 p=ref['profile']['params_resolved'];identity=ref['profile']['identity_payload']
 from pygrc.models.grc_9_v4_topology import GRC9V4PortGraph
 graph=GRC9V4PortGraph.from_payload(ref['graph'])
 p['candidate']['descriptor_backend_id']=r.GRC9V4CandidateADifferentialReference(graph).identity
 p['geometry']['reference_hodge_digest']=b.payload_identity('reference_hodge_identity_payload',ref['reference_hodge'])
 p['geometry']['K4_base_digest']=b.payload_identity('k4_identity_payload',dict(schema_version='grcv4-k4-identity-v1',K4_base=ref['K4_base']))
 identity['params_hash']=b.payload_identity('resolved_params',p)
 ref['profile']=b.resolve_profile(p,identity).to_payload()

@contextmanager
def capture_chains():
 real=native_completion.certify_chain;rows=[]
 def observed(cert,query,x,h,actual):
  error,bounds=real(cert,query,x,h,actual)
  rows.append(dict(input_identity=cert.inputs.identity,query=list(query),work=oracle.encode(x,h),
   native_chain_error=str(error),native_chain_bounds={k:str(v) for k,v in bounds.items()},native_global_bounds=cert.bounds.to_dict()))
  return error,bounds
 with patch.object(native_completion,'certify_chain',observed):yield rows

def equations(before,h):
 _,algebra=data(before)
 return oracle.literal(algebra,oracle.coordinates(before.current.C,before.current.W_A),mat(h),retract=False)

def matrix_error(values,expected):
 v=np.asarray(values);a=mat(v.reshape(-1,1).tolist()) if v.ndim==1 else mat(v.tolist())
 return norm(a-expected)

def independent_certificate(before,value):
 cert,_=data(before);xs,hs=oracle.decode(value['chain']['work'])
 section=oracle.certify(before.geometry.reference.graph.port_graph.to_payload(),before.current.C,before.current.W_A,xs,hs,cert)
 with ctx.workprec(192):
  truth=equations(before,value['H'])
  errors={k:str(matrix_error(value[k],truth[k])) for k in ('J','baseline','readback','flat','source')}
 b.require(section['section_tolerance_passes'],'independent section residual/tail failure')
 limits=dict(J=2**-40,baseline=2**-40,readback=2**-40,flat=2**-40,source=2**-48)
 b.require(all(Q(errors[k])<=exact(v) for k,v in limits.items()),'independent fixed-H equations fail')
 return dict(input_identity=before.identity,selected_read_digest=value['record_digest'],section=section,
  fixed_H_errors=errors,graph_certificate_digest=b.digest(cert),fixed_H_read_error_is_not_infinite_section_error=True)

def check_read(before,value,*,numerics=False):
 b.check_digest({k:v for k,v in value.items() if k!='independent_certificate'})
 b.require(value['input_identity']==before.identity and value['recipe']==native_completion.APPROXIMATION
  and value['levels']==4 and value['evaluations']==148,'read identity/policy/depth')
 xs,hs=oracle.decode(value['chain']['work']);query=list(before.current.C)+[512*math.log(w) for w in before.current.W_A]
 b.require(value['chain']['input_identity']==before.identity and value['chain']['query']==query
  and np.array_equal(xs[0],query) and np.array_equal(hs[0],value['H'])
  and np.array_equal(hs[-1],np.eye(len(hs[-1]))),'section query/full geometry/terminal mismatch')
 selected=replace(before,geometry=b.GRCV4Geometry(before.geometry.reference,
  b.OneFormHodge(before.geometry.reference.graph,tuple(map(tuple,value['H'])))),stage='rg2b_section')
 b.require(selected.identity==value['selected_inputs_identity'] and value['read_current']==value['J']
  and value['read_source']==value['point_identity'],'selected point/readback identity')
 b.require(value['identity']=='grcv4-rg2b-section-sha256:'+b.digest(dict(numerics=native_completion.APPROXIMATION,
  inputs=before.to_payload(),differential_reference=r.backend(before).to_payload())),'full section identity')
 ce=value['independent_certificate'];sc=ce['section']
 # Independent edge and factored outward evaluations can differ by their own
 # fixed-precision enclosure widths. Each must separately meet the same budget.
 b.require(ce['input_identity']==before.identity and ce['selected_read_digest']==value['record_digest']
  and Q(sc['section_error_upper'])<=Q(1,2**48) and Q(value['chain']['native_chain_error'])<=Q(value['error_upper'])<=Q(1,2**48)
  and list(map(Q,value['enclosure']))==[-Q(value['error_upper']),Q(value['error_upper'])],'error enclosure binding')
 b.require(before.current.W_A is not None and before.current.Z_4 is None,'A authoritative history')
 if numerics:b.require(ce==independent_certificate(before,value),'independent numerical certificate drift')

def bridge(before,value):
 after=r.following_inputs(before,value)
 with ctx.workprec(192):
  truth=equations(before,value['read']['H']);j=truth['J'];g=truth['image']
  je=_norm(mag(ball(v)-j[i,0]) for i,v in enumerate(value['read']['J']))
  jn=_norm(mag(z) for z in j.entries())
  old=oracle.coordinates(before.current.C,before.current.W_A);new=oracle.coordinates(after.current.C,after.current.W_A)
  n=len(before.current.C)
  errs=[mag(z-old[i]-truth['increment'][i,0]) for i,z in enumerate(new)]
  xe=max(errs);he=norm(mat(value['generated'])-g)
  residual=norm(mat(value['restart']['H'])-mat(value['generated']))
  gb,_=proof.global_bounds();e=Q(value['read']['error_upper']);last=Q(value['restart']['error_upper'])
  bound=last+he+gb['B_H']*e/2+proof.LIP*(xe+gb['A_H']*e)
  resource_error=max(errs[:n])+gb['A_H']*e
  # Literal drive at the actual writer operands: fresh represented C, old W,
  # selected represented J. Independently evaluated by the accepted dense A oracle.
  from decimal import Decimal,localcontext
  nodes=before.geometry.reference.graph.live_node_ids;graph=before.geometry.reference.graph.port_graph
  wi=before.current.W_A;cc=after.current.C;index={v:i for i,v in enumerate(nodes)}
  rows=data(before)[1][3];ends=data(before)[1][4]
  rr=[[sum((ball(wi[k])*(ball(cc[v])-ball(cc[u])) for k,v in row),ball(0))/sum((ball(wi[k]) for k,_ in row),ball(0)) if row else ball(0) for row in node] for u,node in enumerate(rows)]
  drives=[(-(ball(cc[u])+ball(cc[v])+sum((oracle.square(a-z) for a,z in zip(rr[u],rr[v])),ball(0))+oracle.square(ball(value['read']['J'][k])))/2**25).exp() for k,(u,v) in enumerate(ends)]
  de=max(mag(ball(v)-z) for v,z in zip(value['writer_targets'][0]['target'],drives,strict=True))
  positive=min(oracle.lower(ball(v))-resource_error for v in after.current.C)
 return {k:str(v) for k,v in dict(current_l2_error=je,current_l2_upper=jn,state_error=xe,geometry_error=he,
  invariance_residual=residual,invariance_error_bound=bound,resource_error=resource_error,
  history_error=max(mag(ball(w)-((old[n+i]+truth['increment'][n+i,0])/512).exp()) for i,w in enumerate(after.current.W_A))+gb['weight_upper']/512*gb['A_H']*e,writer_target_error=de,exact_real_next_resource_lower=positive).items()}

# Retain the existing complete writer/continuity/event assertions. Only the
# numerical completion certificate and independent equation evaluator change.
def check_step(before, value, *, numerics=False):
    b.require(
        value["prestate_identity"] == before.identity and before.dt == b.DT,
        "step operand/beat drift",
    )
    for role in ROLES:
        state = getattr(before, role)
        r.a_oracle.chart_admitted(state.C, state.W_A, ordinary=True)
    after = r.following_inputs(before, value)
    b.require(
        after.identity == value["poststate_identity"]
        and after.current.C == r.represented_continuity(before, value["read"]["J"]),
        "continuity/clock/reset drift",
    )
    check_read(before, value["read"], numerics=numerics)
    check_read(
        replace(before, current=before.reset), value["reset_read"], numerics=numerics
    )
    check_read(after, value["restart"], numerics=numerics)
    b.require(
        value["selection_current"] == value["read"]["J"],
        "continuity selected-current drift",
    )
    b.require(
        len(value["writer_targets"]) == len(value["log_writes"]) == 1,
        "single W writer required",
    )
    target, write = value["writer_targets"][0], value["log_writes"][0]
    b.require(
        target
        == {
            "point_identity": value["read"]["point_identity"],
            "C": list(after.current.C),
            "W_A": list(before.current.W_A),
            "J": value["read"]["J"],
            "target": target["target"],
        },
        "fresh-C/selected-J/incoming-W writer operands drift",
    )
    b.require(
        write
        == {
            "old": list(before.current.W_A),
            "target": target["target"],
            "dt": before.dt,
            "tau": 1,
            "result": list(after.current.W_A),
        },
        "W log interpolation operands drift",
    )
    with r.localcontext() as context:
        context.prec = 150
        a = (-r.Decimal.from_float(before.dt)).exp()
        expected = tuple(
            float(
                (
                    a * r.Decimal.from_float(w).ln()
                    + (1 - a) * r.Decimal.from_float(g).ln()
                ).exp()
            )
            for w, g in zip(before.current.W_A, target["target"], strict=True)
        )
    b.require(after.current.W_A == expected, "log writer output drift")
    size = len(value["read"]["H"])
    generated = [
        [
            float(Q(i == j) + Q(1, 2) * Q(value["read"]["source"][i][j]))
            for j in range(size)
        ]
        for i in range(size)
    ]
    b.require(
        value["generated"] == generated,
        "generated geometry must consume same selected source",
    )
    diag = value["diagnostics"]
    independent = value["independent_bridge"]
    b.require(
        diag["regularity"] == "Lipschitz_only"
        and diag["continuity_evaluations"] == 1
        and diag["carrier_writes"] == 0
        and diag["section_error_upper"] == value["read"]["error_upper"],
        "ordinary stage counts drift",
    )
    b.require(
        all(Q(v) >= 0 for k,v in independent.items() if k != "exact_real_next_resource_lower")
        and Q(independent["resource_error"]) < Q(str(r.LIMITS["resource_error"]))
        and Q(independent["history_error"]) < Q(str(r.LIMITS["history_error"]))
        and Q(independent["writer_target_error"]) < Q(str(r.LIMITS["history_error"]))
        and Q(independent["invariance_residual"])
        <= Q(independent["invariance_error_bound"]),
        "independent invariance/C/W error unresolved",
    )
    p = before.geometry.reference.profile.params_resolved.solver
    b.require(
        Q(independent["current_l2_error"])
        <= Q(p.absolute_tolerance)
        + Q(p.relative_tolerance) * Q(independent["current_l2_upper"])
        and Q(independent["geometry_error"]) <= Q(str(r.LIMITS["geometry_error"]))
        and proof.LIP * Q(independent["state_error"])
        <= Q(str(r.LIMITS["geometry_error"])),
        "native arithmetic bridge unresolved",
    )
    b.require(
        Q(diag["invariance_residual"]) == Q(independent["invariance_residual"])
        and Q(diag["invariance_residual"]) <= Q(diag["invariance_error_bound"]),
        "native invariance residual/bound drift",
    )
    # Edge-space and factored Arb evaluations have different outward widths.
    # Their upper bounds need not order; each independently meets the published
    # admission budgets above. Preserve native diagnostics without rewriting.
    for key in ("current_l2_error", "state_error", "geometry_error"):
        b.require(Q(independent[key]) >= 0, "negative error bound")
    if numerics:
        b.require(independent == bridge(before, value), "bridge equations drift")
    return after


def independent_target(manifest,case):
 import p984e_cos as ordering
 source=b.GeometryStageInputs.from_payload(manifest['expected_source']['inputs']);v=deepcopy(source.to_payload());ref=v['reference']
 graph=case['oracle']['target_graph'];ref['graph']=graph;m=len(graph['edges'])
 ref['K4_base']=[[0.0]*m for _ in range(m)];ref['reference_hodge']['edge_weights']={e['edge_id']:1 for e in graph['edges']}
 reidentify(ref);reference=b.GRCV4ReferenceGeometry.from_payload(ref);roles={}
 for role in ROLES:
  old=getattr(source,role);cs=dict(zip(source.geometry.reference.graph.live_node_ids,old.C,strict=True));ws=dict(zip(source.geometry.reference.graph.live_edge_ids,old.W_A,strict=True))
  image={n:cs.get(n,0.) for n in graph['live_node_ids']}
  for j,share in enumerate(case['request']['resource_distribution'],1):image[case['oracle']['event_id']+f'/satellite/{j}']=float(exact(cs[case['request']['source_node_id']])*exact(share))
  roles[role]=b.GRCV4AuthoritativeState(tuple(image[n] for n in graph['live_node_ids']),tuple(ws.get(e['edge_id'],1.) for e in graph['edges']),None)
 return replace(source,geometry=reference.geometry(),**roles,dt=0,operation_id=case['request']['operation_id'])

def target_state(seed,case):return replace(seed,inputs=independent_target(dict(expected_source=seed.to_payload()),case))

r.signed=native_completion;r.capture_chains=capture_chains;r.independent_certificate=independent_certificate
r.check_read=check_read;r.bridge=bridge;r.check_step=check_step;r.independent_target=target_state
state=r.state;native_read=r.native_read;read_record=r.read_record

def perform_step(before):
 value,after=r.perform_step(before)
 value.update(prestate=before.to_payload(),poststate_full=after.to_payload())
 return value,after
check_event=r.check_event

def event_capture(seed,request):
 row=r.native._FAMILY_IMPLEMENTATIONS['A_RG2b']
 with patch.dict(r.native._FAMILY_IMPLEMENTATIONS,{'A_RG2b':replace(row,readmit=lambda subject:r.native._arg2b_readmit(subject))}):
  return r.event_capture(seed,request)

def full_poststate(before,value):return r.following_inputs(before,value).to_payload()

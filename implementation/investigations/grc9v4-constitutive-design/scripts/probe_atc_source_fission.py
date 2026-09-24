#!/usr/bin/env python3
"""CAN-F2 source-only hypothesis: algebra/controls plus one native onset step.

No target construction, supplied event, installed policy or accepted fission law.
"""
from dataclasses import replace
from fractions import Fraction as F
import importlib.util
import itertools
import json
import math
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
INV = ROOT / 'implementation/investigations/grc9v4-constitutive-design'
REFS = INV / 'evidence/autonomous-topology-change'
sys.path[:0] = [str(ROOT/'src'), str(ROOT)]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_prescription(graph, resources, currents):
    """Exact represented source rule on the declared simple degree-at-most-2 domain.

    The receiving-neighbor funding benchmark is a NEW constitutive postulate,
    not an inherited capacity, a theorem of necessity, or a target score.
    """
    if len(resources) != len(graph.live_node_ids) or len(currents) != len(graph.live_edge_ids):
        return dict(outcome='uncertified', reason='coordinate_coverage')
    if any(type(x) not in (int,float) or not math.isfinite(x) for x in (*resources,*currents)) or any(x<0 for x in resources):
        return dict(outcome='uncertified', reason='numeric_domain')
    if len(resources)>16 or len(currents)>32:
        return dict(outcome='uncertified', reason='declared_work_bound')
    if any(e.tail_node_id==e.head_node_id for e in graph.oriented_edges):
        return dict(outcome='uncertified', reason='loop_outside_F2_domain')
    pairs=[frozenset((e.tail_node_id,e.head_node_id)) for e in graph.oriented_edges]
    if len(set(pairs)) != len(pairs):
        return dict(outcome='uncertified', reason='parallel_outside_F2_domain')
    if any(len(graph.star(v))>2 for v in graph.live_node_ids):
        return dict(outcome='uncertified', reason='higher_degree_outside_F2_domain')
    c=dict(zip(graph.live_node_ids,map(F,resources),strict=True))
    diagnostics=[]; active=[]
    for v in graph.live_node_ids:
        edges=graph.star(v)
        if len(edges)!=2: continue
        halves=[]
        for index in edges:
            edge=graph.oriented_edges[index]
            tail=edge.tail_node_id==v
            halves.append(dict(edge=edge.edge_id,role='tail' if tail else 'head',
                neighbor=edge.head_node_id if tail else edge.tail_node_id,
                outward=F(currents[index])*(1 if tail else -1)))
        q=[h['outward'] for h in halves]
        row=dict(vertex=v,halves=[dict(h,outward=str(h['outward'])) for h in halves],
                 parent_tendency=str(-sum(q,F())),active=False)
        if not all(x<0 for x in q):
            row['reason']='not_two_strict_inflows'
        else:
            # Same complement-equivariant nearest-even dyadic shares as CAN
            # construction. No zero-activity fallback is used by this guard.
            grid=2**16
            k=round(grid*(-q[0])/(-sum(q,F())))
            shares=[F(k,grid),F(grid-k,grid)]
            allocated=[F(float(s*c[v])) for s in shares]
            margins=[x-c[h['neighbor']] for x,h in zip(allocated,halves,strict=True)]
            row.update(shares=list(map(str,shares)),allocated_current=list(map(str,allocated)),
                funding_margins=list(map(str,margins)))
            row['active']=all(x>0 for x in margins)
            row['reason']='resource_supported_accumulation' if row['active'] else 'child_funding_not_strict'
            if row['active']:
                active.append(dict(vertex=v,blocks=[[[h['edge'],h['role']]] for h in halves],
                    shares=list(map(str,shares)),allocated_current=list(map(str,allocated))))
        diagnostics.append(row)
    return dict(outcome='no_event' if not active else 'resolved' if len(active)==1 else 'unresolved',
        prescription=active[0] if len(active)==1 else None,
        active_loci=[row['vertex'] for row in active],diagnostics=diagnostics)


def run():
    base_path=INV/'scripts/probe_atc_refinement_discrimination.py'
    constructor_path=INV/'scripts/verify_atc2_candidates.py'
    base=load(base_path,'source_fission_oracle')
    helper=load(constructor_path,'source_fission_present_read')
    original_path=REFS/'ATCRefinementDiscriminationProbe.json'
    modal_path=REFS/'ATCModalSplitProbe.json'
    records={}
    for path in (original_path,modal_path):
        value=json.loads(path.read_text())
        assert value['record_digest']==base.sha(base.canonical({k:v for k,v in value.items() if k!='record_digest'}))
        for binding in value['source_bindings']:
            assert base.sha((ROOT/binding['path']).read_bytes())==binding['sha256'],binding['path']
        records[path.name]=value
    original=records[original_path.name]; modal=records[modal_path.name]
    from pygrc.models.grc_v4 import GRCV4
    from pygrc.models.grc_v4_candidate_a import CandidateADifferentialReference
    from pygrc.models.grc_v4_geometry import GeometryStageInputs,GRCV4Graph,OrientedEdge
    from pygrc.models.grc_v4_lifecycle import _state_inputs
    from tests.models.test_grc_v4_lifecycle import request
    before=GeometryStageInputs.from_payload(original['native_baseline']['source'])
    backend=CandidateADifferentialReference.from_payload(original['native_baseline']['backend'])
    graph=before.geometry.reference.graph

    # Review's extra source identity: exact arithmetic on retained native reads.
    signed=[]
    for row in modal['cases']:
        c=list(map(F,row['source']['current']['C']))
        j=list(map(F,row['source_read']['observed']['J']))
        q0,q1=-j[0],j[1]
        assert q1-q0==(c[2]-c[0])/8
        fiber=list(map(F,row['fiber_residual']))
        assert fiber[2:]==[2*(q1-q0),-2*(q1-q0)]
        assert F(row['child_difference'])==4*F(row['source']['dt'])*(q1-q0)
        signed.append(dict(label=row['label'],q=list(map(str,(q0,q1))),
                           net_parent_tendency=str(-q0-q1),difference=str(q1-q0)))
    controls=[]
    for row in original['native_baseline']['mode_histories']:
        src=row['source']; current=row['frames'][0]['read']['observed']['J']
        result=source_prescription(graph,src['current']['C'],current)
        assert result['outcome']=='no_event'
        controls.append(dict(label=row['label'],C=src['current']['C'],J=current,result=result,
                             evidence='new source-rule calculation on retained native inputs; no rerun'))

    # Exact threshold and equal-activity controls, not new native source claims.
    for label,c,expected in (
        ('funding_boundary',(F(3,4),F(3,2),F(3,4)),'no_event'),
        ('funded_accumulation',(F(1,2),F(2),F(1,2)),'resolved'),
        ('equal_activity_through_flow',(F(73,64),F(1),F(55,64)),'no_event')):
        c=tuple(map(float,c)); fixture=replace(before,current=replace(before.current,C=c))
        j=base.baseline_oracle(fixture)['J']
        result=source_prescription(graph,c,j)
        assert result['outcome']==expected
        controls.append(dict(label=label,C=c,J=j,result=result,evidence='literal source equations only'))

    # Covariance of the represented rule, including the unequal-activity shares.
    # This is algebraic operand covariance, not a native backend relabeling run.
    covariance=0
    for c,j in (((.5,2.,.5),(.5,-.5)),((.25,4.,.5),(.5,-1.))):
        expected=source_prescription(graph,c,j)
        assert expected['outcome']=='resolved'
        wanted=dict(zip(('ab','bc'),expected['prescription']['shares']))
        for nodes in itertools.permutations(graph.live_node_ids):
            for edge_order in ((0,1),(1,0)):
                for signs in itertools.product((-1,1),repeat=2):
                    edges=tuple(OrientedEdge(graph.oriented_edges[k].edge_id,
                        graph.oriented_edges[k].tail_node_id if signs[k]>0 else graph.oriented_edges[k].head_node_id,
                        graph.oriented_edges[k].head_node_id if signs[k]>0 else graph.oriented_edges[k].tail_node_id)
                        for k in edge_order)
                    changed=GRCV4Graph(nodes,edges)
                    result=source_prescription(changed,tuple(c[graph.node_index(v)] for v in nodes),
                                              tuple(signs[k]*j[k] for k in edge_order))
                    assert result['outcome']=='resolved' and result['prescription']['vertex']=='b'
                    assert dict(zip((block[0][0] for block in result['prescription']['blocks']),
                                    result['prescription']['shares']))==wanted
                    covariance+=1
    star=GRCV4Graph(('v','a','b','c'),tuple(OrientedEdge(e,'v',v) for e,v in zip(('x','y','z'),('a','b','c'))))
    assert source_prescription(star,(4.,1.,1.,1.),(-1.,-1.,-1.))['outcome']=='uncertified'
    twin=GRCV4Graph(('a','b','c','d','e','f'),(OrientedEdge('ab','a','b'),OrientedEdge('bc','b','c'),
        OrientedEdge('de','d','e'),OrientedEdge('ef','e','f')))
    multiple=source_prescription(twin,(.5,2.,.5,.5,2.,.5),(.5,-.5,.5,-.5))
    assert multiple['outcome']=='unresolved' and multiple['prescription'] is None
    assert source_prescription(graph,(1.,1.,1.),(float('nan'),0.))['outcome']=='uncertified'

    # One new source and one ordinary commit. No graph change is attempted.
    amplitude=F(127,512)
    c=tuple(float(x) for x in (1-amplitude,1+2*amplitude,1-amplitude))
    before=replace(before,current=replace(before.current,C=c),dt=2**-6)
    ref=before.geometry.reference
    owner=GRCV4(before,differential_reference=backend)
    source_snapshot=owner.snapshot()
    point=helper.native_read(before,backend)
    initial_oracle=base.baseline_oracle(before)
    assert list(point.current.values)==initial_oracle['J']
    initial=source_prescription(graph,before.current.C,point.current.values)
    assert initial['outcome']=='no_event' and owner.snapshot()==source_snapshot
    ordinary=owner.step_v4_input(request(before.dt,'source-fission-onset'))
    assert ordinary.committed,ordinary.failure
    after=_state_inputs(ref,owner.state.lifecycle)
    updated=amplitude*F(521,512)
    expected=tuple(float(x) for x in (1-updated,1+2*updated,1-updated))
    assert after.current.C==expected and after.current.W_A==(1.,1.) and after.reset==before.reset
    snapshot=owner.snapshot()
    post=helper.native_read(after,backend)
    post_oracle=base.baseline_oracle(after)
    assert list(post.current.values)==post_oracle['J']
    selected=source_prescription(graph,after.current.C,post.current.values)
    assert selected['outcome']=='resolved' and selected['prescription']['vertex']=='b'
    assert selected['diagnostics'][0]['funding_margins']==[str(F(631,131072))]*2
    assert owner.snapshot()==snapshot

    paths={Path(__file__).resolve(),base_path,constructor_path,original_path,modal_path}
    for module in tuple(sys.modules.values()):
        name=getattr(module,'__file__',None)
        if name:
            path=Path(name).resolve()
            if path.is_relative_to(ROOT) and '/.venv/' not in str(path) and path.suffix=='.py':paths.add(path)
    import numpy as np
    result=dict(schema='grcv4_atc_source_fission_probe_v1',status='passed',candidate_id='ATC-CAN-F2-v1',
        scientific_status='new_constitutive_hypothesis_not_accepted',
        postulate='Two strict inflows may seed two sites only when each activity-allocated child is more resourced than its adjacent exterior site.',
        domain='unit measure; already admitted profile-correct K0 current; simple finite graph degree at most two',
        work_bound=dict(vertices=16,edges=32),share_grid_bits=16,resolution='singleton_active_else_unresolved',
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),
        environment=dict(python=platform.python_version(),numpy=np.__version__),
        predecessors={name:r['record_digest'] for name,r in records.items()},
        signed_half_edge_identity=signed,controls=controls,algebraic_covariance_cases=covariance,
        multiple_active_control=multiple,
        native_onset=dict(source=before.to_payload(),backend=backend.to_payload(),initial_read=helper.witness(point),
            initial_oracle=initial_oracle,initial_prescription=initial,request_dt=before.dt,
            ordinary_receipts=[receipt.to_payload() for receipt in ordinary.emitted_receipts],
            post=after.to_payload(),post_read=helper.witness(post),post_oracle=post_oracle,
            post_prescription=selected,source_snapshot_digest=base.sha(base.canonical(source_snapshot)),
            post_snapshot_digest=base.sha(base.canonical(snapshot)),reads_and_prescriptions_do_not_publish=True),
        counts=dict(fresh_source_admissions=1,explicit_present_reads=2,ordinary_commits=1,topology_events=0),
        not_established=['fission_necessity','accepted_capacity_law','higher_degree_partition','all_ten_domains',
            'selected_target_admission','target_continuation','structural_Hessian','endogenous_runtime','scientific_acceptance'],
        production_changes=False,source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=base.sha(p.read_bytes())) for p in sorted(paths)])
    result['record_digest']=base.sha(base.canonical(result))
    return result


if __name__=='__main__':
    print(json.dumps(run(),separators=(',',':'),ensure_ascii=True,allow_nan=False))

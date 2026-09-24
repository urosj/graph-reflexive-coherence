#!/usr/bin/env python3
"""ATC-2 bounded research, stdout only; not an enabled runtime ATC profile.

Exact represented-value laws and constructors are research implementations.
Native calls use the existing supplied-event owner with a predeclared finite
target catalogue, not a new publisher, dynamic registry or atomic ATC wrapper.
"""
from __future__ import annotations

from dataclasses import replace
from fractions import Fraction as F
import hashlib
import io
import itertools
import json
import math
from pathlib import Path
import platform
import struct
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[4]
INV = ROOT / 'implementation/investigations/grc9v4-constitutive-design'
sys.path[:0] = [str(ROOT / 'src'), str(ROOT)]
from pygrc.models.grc_v4_geometry import GRCV4Graph, GRCV4ReferenceGeometry, OrientedEdge
from pygrc.models.grc_v4_codec import payload_identity
from pygrc.models.grc_v4_profile import resolve_profile

POLICY = dict(schema='atc2_research_policy_v1', envelope='ATC-K0',
    birth_score='exact_q_squared_of_admitted_stored_H', birth_threshold='1/1125899906842624',
    birth_gap='1/1152921504606846976', merge_epsilon_C='1/2', merge_epsilon_f='16',
    merge_score='1/(1+rC_squared/epsilonC_squared+rf_squared/epsilonf_squared)',
    merge_gap='1/1048576', eligible_ties='unresolved', undefined_pair='uncertified',
    arithmetic='exact_dyadic_operands_and_rational_comparisons',
    max_vertices=16, max_edges=32, max_reference_weights=32, max_rational_bits=131072,
    reference='correctly_rounded_exact_geometric_mean', structural_base='CAN-KMASK',
    A_positions='unchanged_birth; exact_sum_then_round_once_midpoint_merge; duplicate_split',
    history='CAN-HRESET', context='constant_zero_no_external_input',
    target_profile='same_base_parameters_and_domains; rebind_reference_digests_only',
    enabled_policy_transport='same_research_policy_rebound_to_target_base; not_native_archive_field',
    candidate_laws='birth_and_merge_are_separate_policies_not_ranked_together',
    split_grid_bits=16, production_support=False)
EVIDENCE = {}


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                      allow_nan=False).encode()


def digest(x):
    return hashlib.sha256(canonical(x)).hexdigest()


class Uncertified(ValueError):
    pass


def bounded(graph):
    if len(graph.live_node_ids) > POLICY['max_vertices'] or len(graph.live_edge_ids) > POLICY['max_edges']:
        raise Uncertified('declared graph work bound exceeded')


def native_read(inputs, backend=None):
    """Already-admitted source required; no zero-step, reset substitution or writer."""
    from pygrc.models.grc_v4_candidate_a import CandidateACurrent
    from pygrc.models.grc_v4_candidate_c import CandidateCCurrent
    from pygrc.models.grc_v4_ci import CandidateCIRoot
    from pygrc.models.grc_v4_pc import CandidatePCRead, carrier_geometry
    from pygrc.models.grc_v4_rg2b import CandidateRG2bSection
    ref = inputs.geometry.reference
    value = replace(inputs, geometry=ref.geometry(), dt=0, stage='pre_read',
                    evaluation_index=0, trial_current=None)
    real = ref.profile.identity_payload.realization
    if real in ('CI', 'CI+PC'):
        return CandidateCIRoot(value, backend).selected.point
    if real == 'PC':
        value = replace(value, geometry=carrier_geometry(value, value.current))
        return CandidatePCRead(value, backend).point
    if real == 'RG2b':
        section = CandidateRG2bSection(value, backend)
        value = replace(value, geometry=section.geometry, stage='rg2b_section')
    return CandidateACurrent(value, backend) if ref.profile.identity_payload.candidate == 'A' else CandidateCCurrent(value)


def witness(point):
    return dict(H=point.inputs.geometry.one_form_hodge.matrix, J=point.current.values)


def state_payload(value):
    return dict(C=value.C, W_A=value.W_A, Z_4=value.Z_4)


def select(scores, gap):
    if not scores:
        return dict(outcome='no_event', locus=None, scores=[])
    best = max(s for _, s in scores)
    winners = [locus for locus, s in scores if s == best]
    other = [s for _, s in scores if s < best]
    unique = len(winners) == 1 and (not other or best-max(other) > gap)
    return dict(outcome='resolved' if unique else 'unresolved',
                locus=list(winners[0]) if unique else None,
                scores=[dict(locus=list(l), score=str(s)) for l, s in scores])


def birth(graph, h):
    bounded(graph)
    b = graph.incidence
    n, m = len(b), len(graph.live_edge_ids)
    kv = [[sum((F(b[i][e])*F(h[e][f])*F(b[j][f])
                for e in range(m) for f in range(m)), F()) for j in range(n)] for i in range(n)]
    adjacency = {frozenset((e.tail_node_id, e.head_node_id)) for e in graph.oriented_edges}
    scores = []
    for i, j in itertools.combinations(range(n), 2):
        pair = (graph.live_node_ids[i], graph.live_node_ids[j])
        if frozenset(pair) in adjacency:
            continue
        if kv[i][i] <= 0 or kv[j][j] <= 0:
            raise Uncertified('undefined nonedge normalization; no epsilon repair')
        q2 = kv[i][j]**2/(kv[i][i]*kv[j][j])
        if not 0 <= q2 <= 1:
            raise Uncertified('node-form PSD bound not satisfied')
        if q2 > F(POLICY['birth_threshold']):
            scores.append((pair, q2))
    return select(scores, F(POLICY['birth_gap']))


def merge(graph, c, j):
    bounded(graph)
    f = [-sum((F(b)*F(v) for b, v in zip(row, j, strict=True)), F()) for row in graph.incidence]
    adjacency = {frozenset((e.tail_node_id, e.head_node_id)) for e in graph.oriented_edges
                 if e.tail_node_id != e.head_node_id}
    scores = []
    for a, b in itertools.combinations(range(len(c)), 2):
        pair = (graph.live_node_ids[a], graph.live_node_ids[b])
        if frozenset(pair) not in adjacency:
            continue
        rc2, rf2 = (F(c[a])-F(c[b]))**2/2, (f[a]-f[b])**2/2
        ac, af = rc2/F(POLICY['merge_epsilon_C'])**2, rf2/F(POLICY['merge_epsilon_f'])**2
        if ac <= 1 and af <= 1:
            scores.append((pair, 1/(1+ac+af)))
    return select(scores, F(POLICY['merge_gap']))


def root_round(product, n):
    """Adjacent-binary64 search and exact midpoint comparison, ties-to-even."""
    if not 1 <= n <= POLICY['max_reference_weights'] or product <= 0:
        raise Uncertified('invalid geometric-mean domain')
    if max(product.numerator.bit_length(), product.denominator.bit_length()) > POLICY['max_rational_bits']:
        raise Uncertified('geometric-mean rational work bound exceeded')
    def number(bits):
        return struct.unpack('>d', struct.pack('>Q', bits))[0]
    lo, hi = 1, 0x7fefffffffffffff
    if not F(number(lo))**n <= product <= F(number(hi))**n:
        raise Uncertified('root outside positive finite binary64 range')
    while lo <= hi:
        mid = (lo+hi)//2
        power = F(number(mid))**n
        if power == product:
            return number(mid)
        if power < product:
            lo = mid+1
        else:
            hi = mid-1
    boundary = ((F(number(hi))+F(number(lo)))/2)**n
    return number(hi if product < boundary or product == boundary and hi % 2 == 0 else lo)


def geometric_mean(weights):
    values = list(weights)
    if not values or len(values) > POLICY['max_reference_weights'] or any(
            type(v) not in (int, float) or not math.isfinite(v) or v <= 0 for v in values):
        raise Uncertified('positive finite reference weights and count required')
    product = F(1)
    for v in values:
        product *= F(v)
    return root_round(product, len(values))


def dyadic(a, b, bits=16):
    if not 1 <= bits <= 52 or a < 0 or b < 0:
        raise ValueError('invalid allocation domain')
    n = 2**bits
    r = F(a)/(F(a)+F(b)) if a+b else F(1, 2)
    k = round(n*r)
    return float(F(k, n)), float(F(n-k, n))


def fresh(used, kind):
    # Wire naming only, after physical selection. Never used in score ties.
    for n in range(len(used)+1):
        name = 'atc2:'+kind+':'+str(n)
        if name not in used:
            return name
    raise AssertionError('finite naming bound')


def build(ref, backend, kind, locus=(), current_flux=None):
    """Close one target preimage without changing admission domains/parameters."""
    from pygrc.models.grc_v4_candidate_a import CandidateADifferentialReference
    from pygrc.models.grc_v4_state import FrozenJSONMap
    bounded(ref.graph)
    graph = ref.graph
    nodes = list(graph.live_node_ids)
    edges = list(graph.oriented_edges)
    weights = ref.edge_weights.to_dict()
    vertex_map = {v: v for v in nodes}
    positions = dict(zip(nodes, backend.positions)) if backend is not None else None
    lineage = dict(operation=kind, locus=list(locus), dropped_edges=[], new_edges=[])
    if kind == 'birth':
        a, b = locus
        if a == b or any({e.tail_node_id, e.head_node_id} == {a, b} for e in edges):
            raise ValueError('birth requires a distinct nonadjacent pair')
        source = {e.edge_id for e in edges if a in (e.tail_node_id, e.head_node_id)
                  or b in (e.tail_node_id, e.head_node_id)}
        new = fresh(set(weights), 'edge')
        weights[new] = geometric_mean([weights[e] for e in source])
        edges.append(OrientedEdge(new, a, b))
        lineage['new_edges'] = [new]
    elif kind == 'merge':
        a, b = locus
        if a == b or not any({e.tail_node_id, e.head_node_id} == {a, b} for e in edges):
            raise ValueError('merge requires adjacent distinct vertices')
        new = fresh(set(nodes), 'vertex')
        vertex_map[a] = vertex_map[b] = new
        nodes = [v for v in nodes if v not in (a, b)] + [new]
        lineage['dropped_edges'] = [e.edge_id for e in edges
                                   if e.tail_node_id in (a,b) and e.head_node_id in (a,b)]
        edges = [OrientedEdge(e.edge_id, vertex_map[e.tail_node_id], vertex_map[e.head_node_id])
                 for e in edges if e.edge_id not in lineage['dropped_edges']]
        weights = {e.edge_id: weights[e.edge_id] for e in edges}
        if positions is not None:
            positions[new] = tuple(float((F(x)+F(y))/2) or 0.0 for x,y in zip(positions[a], positions[b], strict=True))
    elif kind == 'split':
        v, block0 = locus
        halves = {(e.edge_id, role) for e in edges for role, node in
                  (('tail', e.tail_node_id), ('head', e.head_node_id)) if node == v}
        block0 = set(block0)
        if not block0 or not block0 < halves:
            raise ValueError('complete nontrivial half-edge partition required')
        if current_flux is None or len(current_flux) != len(edges):
            raise ValueError('selected-stage current required for split allocation')
        children = [fresh(set(nodes), 'child')]
        children.append(fresh(set(nodes+children), 'child'))
        by_id = dict(zip(graph.live_edge_ids, current_flux, strict=True))
        activity = [sum((abs(F(by_id[e])) for e, role in group), F())
                    for group in (block0, halves-block0)]
        shares = dyadic(*activity, POLICY['split_grid_bits'])
        incident = {e for e, role in halves}
        new = fresh(set(weights), 'edge')
        weights[new] = geometric_mean([weights[e] for e in incident])
        edges = [OrientedEdge(e.edge_id,
                 children[int((e.edge_id,'tail') not in block0)] if e.tail_node_id == v else e.tail_node_id,
                 children[int((e.edge_id,'head') not in block0)] if e.head_node_id == v else e.head_node_id)
                 for e in edges] + [OrientedEdge(new, *children)]
        nodes = [node for node in nodes if node != v] + children
        if positions is not None:
            for child in children:positions[child] = positions[v]
        lineage.update(new_edges=[new], split_vertex=v, children=children,
            block0=sorted(map(list, block0)), shares=shares, half_edge_activities=list(map(str,activity)))
    elif kind != 'identity':
        raise ValueError('unknown research constructor')
    if not edges:
        raise Uncertified('edgeless target not claimed by this executable constructor')
    target = GRCV4Graph(tuple(nodes), tuple(edges))
    bounded(target)
    old = {e.edge_id: i for i,e in enumerate(graph.oriented_edges)}
    base = tuple(tuple(ref.K4_base[old[e.edge_id]][old[f.edge_id]]
        if e.edge_id in old and f.edge_id in old and
        {e.tail_node_id,e.head_node_id} & {f.tail_node_id,f.head_node_id} else 0.0
        for f in target.oriented_edges) for e in target.oriented_edges)
    params = ref.profile.params_resolved.to_payload()
    identity = ref.profile.identity_payload.to_payload()
    params['geometry']['K4_base_digest'] = payload_identity('k4_identity_payload',
        dict(schema_version='grcv4-k4-identity-v1', K4_base=[list(r) for r in base]))
    params['geometry']['reference_hodge_digest'] = payload_identity('reference_hodge_identity_payload',
        dict(schema_version='grcv4-reference-hodge-identity-v1', edge_weights=weights))
    new_backend = None
    if identity['candidate'] == 'A':
        new_backend = CandidateADifferentialReference(target, backend.dimension,
            tuple(positions[v] for v in target.live_node_ids), weights, backend.regularization)
        params['candidate']['descriptor_backend_id'] = new_backend.identity
    else:
        params['candidate']['W_C_tr'] = weights
        params['candidate']['W_C_tr_content_digest'] = payload_identity('wctr_identity_payload',
            dict(schema_version='grcv4-wctr-identity-v1', W_C_tr=weights))
    identity['params_hash'] = payload_identity('resolved_params', params)
    target_ref = GRCV4ReferenceGeometry(target, resolve_profile(params, identity), ref.context,
                                      base, FrozenJSONMap(weights))
    matrix = tuple(shares[children.index(w)] if kind == 'split' and v == locus[0] and w in children
                   else 0.0 if kind == 'split' and v == locus[0]
                   else float(vertex_map[v] == w)
                   for w in target.live_node_ids for v in graph.live_node_ids)
    lineage['vertex_map'] = [[v, children if kind == 'split' and v == locus[0] else vertex_map[v]]
                             for v in graph.live_node_ids]
    return target_ref, new_backend, matrix, lineage


def source(candidate, kind):
    from tests.models.test_grc_v4_pc import fixture
    from tests.models.test_grc_v4_migration import changed_reference
    from pygrc.models.grc_v4_initializer import HISTORY_POLICY
    graph = GRCV4Graph(('a','b','c'), (OrientedEdge('ab','a','b'), OrientedEdge('bc','b','c')))
    c = (1.5,1.0,.5) if kind == 'birth' else (1.5,1.5,.5)
    if candidate == 'A' and kind == 'merge':
        from tests.models.test_grc_v4_realizations import a_os_fixture
        before, backend = a_os_fixture(graph=graph,C=c,W=(1.5,1.75),gamma=.1)
    else:
        before, backend = fixture(candidate, graph=graph, C=c, W=(1.5,1.75),
                                  z=(.25,.125,.125,.25), reset_z=(0.,0.,0.,0.))
    if candidate == 'A':
        from pygrc.models.grc_v4_pc import carrier_geometry
        ref = changed_reference(before.geometry.reference, 'lifecycle', history_policy_id=HISTORY_POLICY)
        before = replace(before, geometry=ref.geometry())
        if before.current.Z_4 is not None:
            before = replace(before, geometry=carrier_geometry(before, before.current))
    reset = (1.,1.,1.) if kind == 'birth' else (1.75,1.,.75)
    return replace(before, reset=replace(before.reset, C=reset), dt=2**-16), backend


def finite_native_case(candidate, kind):
    """Detached generator + real caller-event execution; two separate locked calls."""
    from pygrc.models.grc_v4 import GRCV4
    from pygrc.models.grc_v4_lifecycle import _state_inputs
    from tests.models.test_grc_v4_events import event
    from tests.models.test_grc_v4_lifecycle import request
    from tests.models.test_grc_v4_initializer import oracle
    before, backend = source(candidate, kind)
    ref = before.geometry.reference
    # Finite catalogue depends on the initial reference, not a searched future.
    pairs = [('a','c')] if kind == 'birth' else [('a','b'),('b','c')]
    built = [build(ref, backend, kind, pair) for pair in pairs]
    targets = tuple(b[0] for b in built)
    backends = tuple(b[1] for b in built if b[1] is not None)
    owner = GRCV4(before, targets=targets, differential_reference=backend,
                  target_differential_references=backends)
    initial_point = native_read(before, backend)
    initial_decision = birth(ref.graph, initial_point.inputs.geometry.one_form_hodge.matrix) if kind == 'birth' else merge(ref.graph, before.current.C, initial_point.current.values)
    ordinary = owner.step_v4_input(request(before.dt, 'atc2-ordinary'))
    assert ordinary.committed, ordinary.failure
    post = _state_inputs(owner._operation.reference, owner.state.lifecycle)
    point = native_read(post, backend)
    decision = birth(ref.graph, point.inputs.geometry.one_form_hodge.matrix) if kind == 'birth' else merge(ref.graph, post.current.C, point.current.values)
    assert decision['outcome'] == 'resolved', decision
    index = pairs.index(tuple(decision['locus']))
    target, target_backend, matrix, lineage = built[index]
    # Generated from the real poststate too; compare exact full preimages.
    rebuilt = build(post.geometry.reference, backend, kind, tuple(decision['locus']))
    assert rebuilt[0].to_payload() == target.to_payload()
    declared = event(owner, target, matrix, (0.,)*len(target.graph.live_node_ids), operation='atc2-generated-'+kind)
    s1 = owner.snapshot()
    result = owner.reconstruct_topology_event(declared)
    assert result.committed, result.failure
    s2 = owner.snapshot()
    for old, new in ((post.current, owner.state.lifecycle.current),
                     (post.reset, owner.state.lifecycle.reset.authoritative)):
        n = len(old.C)
        expected = tuple(float(sum((F(matrix[i*n+j])*F(old.C[j]) for j in range(n)),F()))
                         for i in range(len(target.graph.live_node_ids)))
        assert new.C == expected
        assert new.Z_4 == ((0.,)*(len(target.graph.live_edge_ids)**2) if old.Z_4 is not None else None)
        if candidate == 'A':
            _, independent = oracle(target, target_backend, expected)
            assert list(new.W_A) == independent
        else:
            assert new.W_A is None
    assert owner.duplicate().snapshot() == s2
    assert owner.state.lifecycle.time == post.time and owner.state.lifecycle.step_index == post.step_index
    primary = result.emitted_receipts[0].to_payload()
    assert list(primary['identity_payload']['core']['parent_receipt_ids']) == [ordinary.emitted_receipts[0].receipt_id]
    # Matched identity-topology HRESET on the same committed ordinary source.
    control = GRCV4.from_state(s1, ref.profile.params_resolved.to_payload())
    n = len(ref.graph.live_node_ids)
    identity_event = event(control, ref, tuple(float(i==j) for i in range(n) for j in range(n)),
                           (0.,)*n, operation='atc2-identity-history-control')
    control_result = control.reconstruct_topology_event(identity_event)
    assert control_result.committed, control_result.failure
    assert control.state.lifecycle.current.C == post.current.C
    assert control.state.lifecycle.current.Z_4 == ((0.,)*len(post.current.Z_4) if post.current.Z_4 is not None else None)
    control_point = native_read(_state_inputs(ref, control.state.lifecycle), backend)
    if candidate == 'A':
        assert control.state.lifecycle.current.W_A != post.current.W_A
    assert witness(control_point) != witness(point), 'history-only control must expose a real numerical confound'
    target_point = native_read(_state_inputs(target, owner.state.lifecycle), target_backend)
    continuation = owner.step_v4_input(request(before.dt,'atc2-after-event'))
    assert continuation.committed, continuation.failure
    return dict(candidate=candidate, law=kind, source=before.to_payload(),
        backend=None if backend is None else backend.to_payload(),
        target=target.to_payload(), target_backend=None if target_backend is None else target_backend.to_payload(),
        initial_decision=initial_decision, decision=decision, lineage=lineage, request=declared.to_payload(),
        ordinary_receipts=[r.to_payload() for r in ordinary.emitted_receipts],
        event_receipts=[r.to_payload() for r in result.emitted_receipts],
        postordinary_current=state_payload(post.current), postordinary_reset=state_payload(post.reset),
        postordinary_witness=witness(point), target_witness=witness(target_point),
        identity_history_control_witness=witness(control_point),
        identity_history_control_request=identity_event.to_payload(),
        identity_history_control_receipts=[r.to_payload() for r in control_result.emitted_receipts],
        identity_history_control_current=state_payload(control.state.lifecycle.current),
        identity_history_control_reset=state_payload(control.state.lifecycle.reset.authoritative),
        target_current=s2['scientific_state'], target_reset=s2['reset'],
        postordinary_snapshot_digest=digest(s1), target_snapshot_digest=digest(s2),
        continuation_snapshot_digest=digest(owner.snapshot()), continuation_committed=True,
        scope='generated research request executed by frozen supplied-event owner; no native automatic dispatcher or K0 lock integration')


class CandidatePressure(unittest.TestCase):
    def test_conditional_binary_builder_loops_parallel_and_host_frames(self):
        from tests.models.test_grc_v4_candidate_a import current_fixture
        from tests.models.test_grc_v4_migration import changed_reference
        from pygrc.models.grc_v4_initializer import HISTORY_POLICY
        graph=GRCV4Graph(('a','v','b'),(OrientedEdge('p','v','a'),OrientedEdge('q','v','b'),
              OrientedEdge('parallel','v','b'),OrientedEdge('loop','v','v')))
        inputs,backend=current_fixture(graph=graph,C=(1.,2.,1.),W=(1.,)*4)
        ref=changed_reference(inputs.geometry.reference,'lifecycle',history_policy_id=HISTORY_POLICY)
        # The partition is a supplied builder input, NOT a native structural-mode result.
        rows=[]
        for loops_split in (False,True):
            block=[('p','tail'),('loop','tail')]
            if not loops_split:block.append(('loop','head'))
            target,new_backend,matrix,lineage=build(ref,backend,'split',('v',block),(1.,2.,3.,4.))
            self.assertEqual(len(target.graph.live_node_ids),4)
            self.assertEqual(len(target.graph.live_edge_ids),5)
            self.assertTrue(set(graph.live_edge_ids) < set(target.graph.live_edge_ids))
            loop=next(e for e in target.graph.oriented_edges if e.edge_id=='loop')
            self.assertEqual(loop.tail_node_id!=loop.head_node_id,loops_split)
            for j in range(3):self.assertEqual(sum(F(matrix[i*3+j]) for i in range(4)),1)
            for child in lineage['children']:
                self.assertEqual(new_backend.positions[target.graph.node_index(child)],backend.positions[graph.node_index('v')])
            rows.append(dict(loop_ends_separated=loops_split,target=target.to_payload(),
                target_backend=new_backend.to_payload(),matrix=matrix,lineage=lineage))
        EVIDENCE['conditional_binary_construction']=dict(cases=rows,
            structural_trigger_executed=False,scope='typed complete reference/resource/backend construction from supplied partition; no whole-target readmission claim')

    def test_reset_veto_and_late_error_preserve_real_postordinary_publication(self):
        from pygrc.models.grc_v4 import GRCV4
        from pygrc.models import grc_v4_lifecycle as lifecycle
        from tests.models.test_grc_v4_events import event
        from tests.models.test_grc_v4_lifecycle import request
        before,backend=source('C','merge')
        before=replace(before,Q_target=5.,current=replace(before.current,C=(1.25,1.25,2.5)),
                       reset=replace(before.reset,C=(2.5,2.5,0.)))
        target,_,matrix,_=build(before.geometry.reference,None,'merge',('a','b'))
        owner=GRCV4(before,targets=(target,))
        ordinary=owner.step_v4_input(request(before.dt,'atc2-veto-ordinary'))
        self.assertTrue(ordinary.committed,ordinary.failure)
        s1=owner.snapshot(); pointer=owner._operation._owned
        current=lifecycle._state_inputs(owner._operation.reference,owner.state.lifecycle)
        chosen=merge(current.geometry.reference.graph,current.current.C,native_read(current).current.values)
        self.assertEqual(chosen['locus'],['a','b'])
        declared=event(owner,target,matrix,(0.,0.),operation='atc2-reset-veto')
        rejected=owner.reconstruct_topology_event(declared)
        self.assertFalse(rejected.committed);self.assertEqual(rejected.failure.stage,'target_readmission')
        self.assertIs(owner._operation._owned,pointer);self.assertEqual(owner.snapshot(),s1)
        # Current-as-both-roles is only a matched admission control, not a generator adapter.
        control_inputs=replace(before,reset=before.current)
        control=GRCV4(control_inputs,targets=(target,))
        self.assertTrue(control.step_v4_input(request(before.dt,'control-ordinary')).committed)
        passed=control.reconstruct_topology_event(event(control,target,matrix,(0.,0.)))
        self.assertTrue(passed.committed,passed.failure)
        control=GRCV4(control_inputs,targets=(target,))
        self.assertTrue(control.step_v4_input(request(before.dt,'late-ordinary')).committed)
        snapshot=control.snapshot(); publication=control._operation._owned
        with patch.object(lifecycle,'_validate_publication',side_effect=RuntimeError('atc2 late publication')):
            with self.assertRaisesRegex(RuntimeError,'atc2 late publication'):
                control.reconstruct_topology_event(event(control,target,matrix,(0.,0.)))
        self.assertIs(control._operation._owned,publication);self.assertEqual(control.snapshot(),snapshot)
        EVIDENCE['native_event_failures']=dict(source=before.to_payload(),target=target.to_payload(),
            decision=chosen,request=declared.to_payload(),failure_stage=rejected.failure.stage,
            failure_message=rejected.failure.message,postordinary_snapshot_digest=digest(s1),
            current_as_reset_control_committed=True,late_programmer_error_preserved_publication=True,
            scope='native supplied-event rejection after separate successful ordinary call; not composite lock/concurrency proof')

    def test_exact_scores_symmetry_and_undefined_not_zero(self):
        graph = GRCV4Graph(('a','b','c'), (OrientedEdge('ab','a','b'),OrientedEdge('bc','b','c')))
        self.assertEqual(birth(graph, ((1.,0.),(0.,1.)))['outcome'], 'no_event')
        selected = birth(graph, ((1.,.25),(.25,1.)))
        self.assertEqual(selected['locus'], ['a','c'])
        self.assertEqual(selected['scores'][0]['score'], '1/16')
        self.assertEqual(merge(graph,(1.,1.,1.),(0.,0.))['outcome'],'unresolved')
        self.assertEqual(merge(graph,(1.,1.,3.),(0.,0.))['locus'],['a','b'])
        isolated = GRCV4Graph(('a','b','c','d'),graph.oriented_edges)
        with self.assertRaises(Uncertified):birth(isolated,((1.,.25),(.25,1.)))
        for ordering in itertools.permutations([(('a','b'),F(1)),(('c','d'),F(1))]):
            self.assertEqual(select(ordering,F(0))['outcome'],'unresolved')
        EVIDENCE['exact_resolution'] = dict(birth_q_squared='1/16',symmetric_merge='unresolved',
            undefined_pair='uncertified',scope='exact algebra, not native reachability')

    def test_covariance_and_noninterchangeable_mobility(self):
        graph = GRCV4Graph(('a','b','c'), (OrientedEdge('ab','a','b'),OrientedEdge('bc','b','c')))
        count = 0
        for order in itertools.permutations(graph.live_node_ids):
            for signs in itertools.product((-1,1),repeat=2):
                edges=tuple(OrientedEdge(e.edge_id,e.tail_node_id if s>0 else e.head_node_id,
                                        e.head_node_id if s>0 else e.tail_node_id)
                            for e,s in zip(graph.oriented_edges,signs))
                g=GRCV4Graph(order,edges)
                h=((1.,signs[0]*signs[1]*.25),(signs[0]*signs[1]*.25,1.))
                self.assertEqual(set(birth(g,h)['locus']),{'a','c'})
                c=tuple(dict(a=1.,b=1.,c=3.)[v] for v in order)
                self.assertEqual(set(merge(g,c,(0.,0.))['locus']),{'a','b'})
                count+=1
        EVIDENCE['covariance'] = dict(node_permutation_and_edge_sign_cases=count,
            scope='physical locus covariance; not equality of wire names/hashes')

    def test_geometric_mean_exact_rounding_and_dyadic_controls(self):
        self.assertEqual(geometric_mean([1.,4.]),2.)
        self.assertEqual(geometric_mean([2.**-1074,2.**1022]),2.**-26)
        self.assertEqual(geometric_mean([3.,3.,3.]),3.)
        lo,hi=1.,math.nextafter(1.,math.inf)
        self.assertEqual(root_round(((F(lo)+F(hi))/2)**2,2),lo)
        lo,hi=hi,math.nextafter(hi,math.inf)
        self.assertEqual(root_round(((F(lo)+F(hi))/2)**2,2),hi)
        for values in itertools.permutations([.5,2.,8.]):self.assertEqual(geometric_mean(values),2.)
        for bad in ([],[0.],[math.inf],[-1.],[1.]*33):
            with self.assertRaises(Uncertified):geometric_mean(bad)
        count=0
        for bits in (1,4,16,52):
            n=2**bits
            for a,b in ((F(0),F(0)),(F(1),F(2)),(F(1,2*n),1-F(1,2*n)),(F(1),F(0))):
                x,y=dyadic(a,b,bits);u,v=dyadic(b,a,bits)
                self.assertEqual(F(x)+F(y),1);self.assertEqual((x,y),(v,u))
                self.assertLessEqual(abs(F(x)-(a/(a+b) if a+b else F(1,2))),F(1,2*n));count+=1
        self.assertNotEqual(F(1/3)+F(2/3),1)
        tiny=F(2.**-1074)
        self.assertEqual(float(tiny/2),0.)
        self.assertEqual(float(tiny/2+tiny/2),float(tiny))
        EVIDENCE['reference_resource_arithmetic']=dict(dyadic_cases=count,midpoint_ties=2,
            thirds_exact_sum=str(F(1/3)+F(2/3)),subnormal_split_stored_loss=True,
            round_once_control_preserves_min_subnormal=True,scope='exact research arithmetic, not native event admission')

    def test_all_ten_present_reads_exclude_valid_metadata_variants(self):
        from tests.models.test_grc_v4_migration import fixture
        from pygrc.models.grc_v4 import GRCV4
        rows=[]
        for a in ('A','C'):
            for r in ('OS','CI','PC','CI_PC','RG2b'):
                family=a+'_'+r
                with self.subTest(family=family):
                    inputs,backend=fixture(family)
                    charge_offset=2**-44 if inputs.geometry.reference.profile.params_resolved.charge.absolute_tolerance > 0 else 0.
                    other=replace(inputs,time=19.,step_index=7,operation_id='atc2-alternate',
                        Q_target=inputs.Q_target+charge_offset,
                        reset=replace(inputs.reset,C=tuple(reversed(inputs.reset.C))))
                    GRCV4(inputs,differential_reference=backend)
                    GRCV4(other,differential_reference=backend)
                    before=inputs.to_payload(); one=native_read(inputs,backend); two=native_read(other,backend)
                    self.assertEqual(witness(one),witness(two));self.assertEqual(inputs.to_payload(),before)
                    rows.append(dict(family=family,source=before,variant=other.to_payload(),
                        backend=None if backend is None else backend.to_payload(),witness=witness(one),
                        current_read='bounded_native_pass',charge_target_varied=charge_offset!=0,
                        birth='no_nonedge_in_this_fixture',
                        merge='would_produce_edgeless_target_not_admitted_here',
                        structural_refinement='no_qualified_branch_supplied'))
        EVIDENCE['ten_product_reads']=rows

    def test_native_generated_birth_and_forward_merge_with_history_controls(self):
        rows=[]
        for candidate,kind in (('A','merge'),('C','birth'),('C','merge')):
            with self.subTest(candidate=candidate,kind=kind):rows.append(finite_native_case(candidate,kind))
        EVIDENCE['native_supplied_event_cases']=rows

    def test_fixed_A_PC_source_envelope_rejection_is_retained(self):
        from pygrc.models.grc_v4 import GRCV4
        from pygrc.models.grc_v4_step import ResourceBoundaryError
        before,backend=source('A','birth')
        with self.assertRaises(ResourceBoundaryError) as caught:
            GRCV4(before,differential_reference=backend)
        self.assertIn('PC uniform source envelope exceeds the carrier radius',str(caught.exception))
        EVIDENCE['A_PC_source_rejection']=dict(source=before.to_payload(),backend=backend.to_payload(),
            failure=str(caught.exception),event_attempted=False,chart_enlarged=False,
            scope='this three-node fixture is not an admitted source; no rejection of all A_PC laws')


def run():
    EVIDENCE.clear()
    stream=io.StringIO()
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(CandidatePressure)
    result=unittest.TextTestRunner(stream=stream,verbosity=1).run(suite)
    if not result.wasSuccessful():
        sys.stderr.write(stream.getvalue());raise SystemExit(1)
    import numpy as np
    paths={Path(__file__).resolve()}
    for module in tuple(sys.modules.values()):
        name=getattr(module,'__file__',None)
        if name:
            path=Path(name).resolve()
            if path.is_relative_to(ROOT) and '/.venv/' not in str(path) and path.suffix=='.py':paths.add(path)
    bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(paths)]
    record=dict(schema='grcv4_atc2_candidate_pressure_v1',status='passed',
        research_status='proposed_not_admitted',policy=POLICY,policy_digest=digest(POLICY),
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),
        environment=dict(python=platform.python_version(),numpy=np.__version__),
        tests=result.testsRun,evidence=EVIDENCE,source_bindings=bindings,
        native_automatic_ATC_executed=False,native_supplied_event_research_executed=True,
        scientific_acceptance=False,production_changed=False)
    record['record_digest']=digest(record)
    return record


if __name__=='__main__':
    print(json.dumps(run(),indent=2,ensure_ascii=False))

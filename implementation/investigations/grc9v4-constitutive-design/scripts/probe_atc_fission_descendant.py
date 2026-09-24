#!/usr/bin/env python3
"""One next eligible CAN-F2 event, not recursive same-invocation splitting.

Replays the retained weighted split, commits one ordinary update, recomputes
the prescription and attempts its sole target on that same native owner.
Research caller/catalogue wiring is explicit; no installed ATC dispatcher.
"""
from fractions import Fraction as F
import importlib.util
import json
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


def run():
    base_path = INV/'scripts/probe_atc_refinement_discrimination.py'
    helper_path = INV/'scripts/verify_atc2_candidates.py'
    rule_path = INV/'scripts/probe_atc_source_fission.py'
    predecessor_path = REFS/'ATCFissionTargetProbe.json'
    base = load(base_path, 'descendant_literal_oracle')
    helper = load(helper_path, 'descendant_constructor')
    rule = load(rule_path, 'unchanged_descendant_f2')
    predecessor = json.loads(predecessor_path.read_text())
    assert predecessor['record_digest'] == base.sha(base.canonical(
        {k:v for k,v in predecessor.items() if k != 'record_digest'}))
    for b in predecessor['source_bindings']:
        assert base.sha((ROOT/b['path']).read_bytes()) == b['sha256'], b['path']
    old = next(c for c in predecessor['cases'] if c['label'] == 'nonuniform_history_split')
    from pygrc.models.grc_v4 import GRCV4
    from pygrc.models.grc_v4_candidate_a import CandidateADifferentialReference
    from pygrc.models.grc_v4_geometry import GeometryStageInputs, GRCV4ReferenceGeometry
    from pygrc.models.grc_v4_lifecycle import _state_inputs
    from tests.models.test_grc_v4_events import event
    from tests.models.test_grc_v4_lifecycle import request

    before = GeometryStageInputs.from_payload(old['source'])
    backend = CandidateADifferentialReference.from_payload(predecessor['backend'])
    first = GRCV4ReferenceGeometry.from_payload(old['target'])
    first_backend = CandidateADifferentialReference.from_payload(old['target_backend'])
    # This is the existing caller API's target roster, not a source-law input.
    # Prepare only the retained source prescription, never search target outcomes.
    retained = old['frames'][1]['read']
    selected = retained['prescription']['prescription']
    target, target_backend, expected_matrix, expected_lineage = helper.build(
        first, first_backend, 'split',
        (selected['vertex'], [tuple(x) for x in selected['blocks'][0]]),
        retained['observed']['J'])
    owner = GRCV4(before, differential_reference=backend, targets=(first,target),
        target_differential_references=(first_backend,target_backend))
    counts = dict(fresh_source_admissions=1, explicit_present_reads=0,
                  ordinary_commits=0, supplied_event_attempts=0, supplied_event_commits=0)

    def read(inputs, differential):
        snapshot = owner.snapshot()
        point = helper.native_read(inputs,differential)
        counts['explicit_present_reads'] += 1
        oracle = base.baseline_oracle(inputs)
        assert list(point.current.values) == oracle['J']
        assert list(point.potential.values) == oracle['potential']
        value = dict(observed=helper.witness(point), independent_oracle=oracle,
            prescription=rule.source_prescription(inputs.geometry.reference.graph,
                                                   inputs.current.C,point.current.values))
        assert owner.snapshot() == snapshot
        return value

    def same_json(a,b):
        return base.canonical(a) == base.canonical(b)

    original_read = read(before,backend)
    assert same_json(original_read,old['source_read'])
    first_request = event(owner,first,old['matrix'],(0.,)*4,
                          operation='fission-meaning-nonuniform_history_split')
    assert first_request.to_payload() == old['request']
    first_result = owner.reconstruct_topology_event(first_request)
    counts['supplied_event_attempts'] += 1
    assert first_result.committed, first_result.failure
    counts['supplied_event_commits'] += 1
    assert [r.to_payload() for r in first_result.emitted_receipts] == old['event_receipts']
    first_inputs = _state_inputs(first,owner.state.lifecycle)
    assert same_json(base.state(first_inputs.current),old['frames'][0]['current'])
    assert same_json(base.state(first_inputs.reset),old['mapped_reset'])
    immediate = read(first_inputs,first_backend)
    assert same_json(immediate,old['frames'][0]['read'])
    assert immediate['prescription']['outcome'] == 'resolved'
    # Eligibility here is NOT permission for a second event in this invocation.
    ordinary = owner.step_v4_input(request(before.dt,'fission-continuation-nonuniform_history_split-1'))
    assert ordinary.committed, ordinary.failure
    counts['ordinary_commits'] += 1
    assert [r.to_payload() for r in ordinary.emitted_receipts] == old['frames'][0]['next_receipts']
    source = _state_inputs(first,owner.state.lifecycle)
    assert same_json(base.state(source.current),old['frames'][1]['current'])
    assert source.reset == first_inputs.reset
    ordinary_snapshot = owner.snapshot()
    source_read = read(source,first_backend)
    assert same_json(source_read,retained)
    prescription = source_read['prescription']
    assert prescription['outcome'] == 'resolved'
    choice = prescription['prescription']
    rebuilt, rebuilt_backend, matrix, lineage = helper.build(first,first_backend,'split',
        (choice['vertex'],[tuple(x) for x in choice['blocks'][0]]),source_read['observed']['J'])
    assert rebuilt == target and rebuilt_backend == target_backend
    assert matrix == expected_matrix and lineage == expected_lineage
    assert list(map(str,map(F,lineage['shares']))) == choice['shares']
    assert len(target.graph.live_node_ids) == 5 and len(target.graph.live_edge_ids) == 4
    assert all(len(target.graph.star(v)) <= 2 for v in target.graph.live_node_ids)
    # Independent role maps, including RN64; no copying current into reset.
    expected_roles = {}
    nsource = len(first.graph.live_node_ids)
    for name, state in (('current',source.current),('reset',source.reset)):
        expected_roles[name] = [float(sum((F(matrix[i*nsource+j])*F(state.C[j])
            for j in range(nsource)), F())) for i in range(len(target.graph.live_node_ids))]
    declared = event(owner,target,matrix,(0.,)*5,operation='fission-descendant-next-eligible')
    result = owner.reconstruct_topology_event(declared)
    counts['supplied_event_attempts'] += 1
    target_read = None
    after_payload = None
    if result.committed:
        counts['supplied_event_commits'] += 1
        after = _state_inputs(target,owner.state.lifecycle)
        for name,state in (('current',after.current),('reset',after.reset)):
            assert list(state.C) == expected_roles[name]
            assert state.W_A == (1.,)*4 and state.Z_4 is None
            assert sum(map(F,state.C)) == F(before.Q_target)
        target_read = read(after,target_backend)
        after_payload = after.to_payload()
    else:
        assert owner.snapshot() == ordinary_snapshot
        assert _state_inputs(first,owner.state.lifecycle) == source

    # Additional review identities are checked on retained data, not reruns.
    aggregate_checks = 0
    for case in predecessor['cases']:
        if case['label'] == 'nonuniform_history_only': continue
        for frame in case['frames']:
            a,c,x,y = map(F,frame['current']['C'])
            m0,m1,delta = x-a,y-c,x-y
            f = list(map(F,frame['read']['independent_oracle']['f']))
            assert f[2:] == [(3*m0-m1+3*delta)/8,(3*m1-m0-3*delta)/8]
            assert f[2]+f[3] == (m0+m1)/4 > 0
            aggregate_checks += 1
    paths = {Path(__file__).resolve(),base_path,helper_path,rule_path,predecessor_path,
             INV/'decisions/ATC1Acceptance.md'}
    for module in tuple(sys.modules.values()):
        name = getattr(module,'__file__',None)
        if name:
            path = Path(name).resolve()
            if path.is_relative_to(ROOT) and '/.venv/' not in str(path) and path.suffix == '.py': paths.add(path)
    import numpy as np
    record = dict(schema='grcv4_atc_fission_descendant_probe_v1',status='passed',
        scientific_status='bounded_next_attempt_not_automatic_ATC_or_support_closure',
        candidate_id='ATC-CAN-F2-v1',predecessor_record_digest=predecessor['record_digest'],
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),
        environment=dict(python=platform.python_version(),numpy=np.__version__),
        source=before.to_payload(),backend=backend.to_payload(),
        first_event=dict(target=first.to_payload(),target_backend=first_backend.to_payload(),
            request=first_request.to_payload(),receipts=[r.to_payload() for r in first_result.emitted_receipts],
            immediate_read=immediate),
        ordinary=dict(dt=before.dt,receipts=[r.to_payload() for r in ordinary.emitted_receipts],
            poststate=source.to_payload(),snapshot_digest=base.sha(base.canonical(ordinary_snapshot))),
        next_attempt=dict(source_read=source_read,target=target.to_payload(),target_backend=target_backend.to_payload(),
            lineage=lineage,matrix=matrix,expected_roles=expected_roles,request=declared.to_payload(),
            committed=result.committed,failure=None if result.failure is None else result.failure.to_payload(),
            receipts=[r.to_payload() for r in result.emitted_receipts],poststate=after_payload,read=target_read,
            final_snapshot_digest=base.sha(base.canonical(owner.snapshot()))),
        counts=counts,retained_aggregate_identity_frames=aggregate_checks,
        composition=dict(events_without_intervening_positive_ordinary=0,
            attempts_after_new_ordinary=1,recursive_drain=False,external_catalogue=True,
            target_policy='research F2 recipe reapplied; no installed policy transport',
            stop='one new eligible attempt; no claim of terminality or indefinite repetition'),
        production_changes=False,accepted_claims_changed=False,
        not_established=['organizational_support','automatic_dispatch','dynamic_runtime_registration',
            'all_ten_domains','arbitrary_repetition','scientific_acceptance'],
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=base.sha(p.read_bytes())) for p in sorted(paths)])
    record['record_digest'] = base.sha(base.canonical(record))
    return record


if __name__ == '__main__':
    print(json.dumps(run(),separators=(',',':'),ensure_ascii=True,allow_nan=False))

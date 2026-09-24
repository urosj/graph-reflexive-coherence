#!/usr/bin/env python3
"""Research controls for temporal growth versus graph refinement; stdout only.

No ATC selector, topology search, new law acceptance or production modification.
The split partition is supplied. Native events use the existing caller API.
"""
from __future__ import annotations

from dataclasses import replace
from fractions import Fraction as F
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
INV = ROOT / 'implementation/investigations/grc9v4-constitutive-design'
REFS = INV / 'evidence/autonomous-topology-change'
sys.path[:0] = [str(ROOT / 'src'), str(ROOT)]


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True, allow_nan=False).encode()


def sha(value):
    return hashlib.sha256(value).hexdigest()


def incidence(graph):
    # Literal outward incidence, independent of the runtime differential helper.
    return [[F(int(e.tail_node_id == v) - int(e.head_node_id == v))
             for e in graph.oriented_edges] for v in graph.live_node_ids]


def tendency(graph, current):
    return [-sum((b * F(j) for b, j in zip(row, current, strict=True)), F())
            for row in incidence(graph)]


def state(value):
    return dict(C=value.C, W_A=value.W_A, Z_4=value.Z_4)


def baseline_oracle(inputs):
    """Literal A reference equations, zero readback and zero conductance exponent.

    Retains the actual incoming W. Rounds at the specified potential/flux
    boundaries, not a single end-of-chain rounding or a production helper.
    """
    graph = inputs.geometry.reference.graph
    params = inputs.geometry.reference.profile.params_resolved.candidate
    assert params.alpha == params.beta == params.gamma == params.chi_A == params.zeta_A == 0
    b = incidence(graph)
    c = list(map(F, inputs.current.C))
    w = list(map(F, inputs.current.W_A))
    dc = [sum((b[i][e] * c[i] for i in range(len(c))), F()) for e in range(len(w))]
    phi = [float(F(params.kappa_c) * sum((row[e] * w[e] * dc[e]
                                        for e in range(len(w))), F())) for row in b]
    j = [float(-F(params.eta) * w[e] * sum((b[i][e] * F(phi[i])
                                          for i in range(len(c))), F())) for e in range(len(w))]
    return dict(potential=phi, J=j, f=list(map(str, tendency(graph, j))))


def run():
    information_path = REFS / 'ATCCapabilityInformationProbe.json'
    information = json.loads(information_path.read_text())
    assert information['record_digest'] == sha(canonical({k: v for k, v in information.items() if k != 'record_digest'}))
    for binding in information['source_bindings']:
        assert sha((ROOT / binding['path']).read_bytes()) == binding['sha256'], binding['path']

    helper_path = INV / 'scripts/verify_atc2_candidates.py'
    spec = importlib.util.spec_from_file_location('atc2_discrimination_subject', helper_path)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    from pygrc.models.grc_v4 import GRCV4
    from pygrc.models.grc_v4_candidate_a import CandidateADifferentialReference
    from pygrc.models.grc_v4_geometry import GeometryStageInputs
    from pygrc.models.grc_v4_lifecycle import _state_inputs
    from tests.models.test_grc_v4_events import event
    from tests.models.test_grc_v4_lifecycle import request
    from tests.models.test_grc_v4_migration import changed_reference

    # New exact arithmetic on retained samples, not fresh native perturbations.
    incremental = []
    for row in information['fixtures']:
        before = GeometryStageInputs.from_payload(row['source'])
        f0 = tendency(before.geometry.reference.graph, row['base_witness']['J'])
        for probe in row['probes']:
            delta = [F(x) - F(y) for x, y in zip(probe['resources'], before.current.C, strict=True)]
            f1 = tendency(before.geometry.reference.graph, probe['witness']['J'])
            norm2 = sum((x*x for x in delta), F())
            rate = sum((d*(y-x) for d, x, y in zip(delta, f0, f1, strict=True)), F()) / norm2
            assert rate > 0
            incremental.append(dict(family=row['family'], homogeneous=row['homogeneous_zero_current_control'],
                neighbor=probe['neighbor'], sign=probe['sign'], incremental_rate=str(rate),
                rate_float=float(rate), scope='fixed-history finite secant, not a derivative or full temporal stability result'))

    # Separate declared baseline control, not a repair of any reviewed input.
    uniform = next(row for row in information['fixtures'] if row['homogeneous_zero_current_control'])
    before = GeometryStageInputs.from_payload(uniform['source'])
    backend = CandidateADifferentialReference.from_payload(uniform['backend'])
    ref = changed_reference(before.geometry.reference, 'candidate', gamma=0, chi_A=0, zeta_A=0)
    before = replace(before, geometry=ref.geometry(),
        current=replace(before.current, C=(1., 1., 1.), W_A=(1., 1.)),
        reset=replace(before.reset, C=(1.25, .75, 1.), W_A=(1.25, 1.5)), dt=2**-6)
    assert before.current != before.reset and before.Q_target == 3
    traces = []
    counts = dict(source_admissions=0, present_reads=0, ordinary_steps=0, supplied_events=0)

    def read(inputs, differential):
        point = helper.native_read(inputs, differential)
        counts['present_reads'] += 1
        expected = baseline_oracle(inputs)
        assert list(point.current.values) == expected['J']
        assert list(point.potential.values) == expected['potential']
        return dict(observed=helper.witness(point), independent_oracle=expected)

    # Low/high path modes, both signs, and the unperturbed control. Both grow
    # under the frozen source equation; neither is an endogenous split policy.
    for label, mode in (('uniform', (0, 0, 0)), ('low_plus', (1, 0, -1)),
                        ('low_minus', (-1, 0, 1)), ('high_plus', (1, -2, 1)),
                        ('high_minus', (-1, 2, -1))):
        resources = tuple(float(F(1) + F(x, 64)) for x in mode)
        inputs = replace(before, current=replace(before.current, C=resources))
        owner = GRCV4(inputs, differential_reference=backend)
        counts['source_admissions'] += 1
        frames = [dict(current=state(inputs.current), read=read(inputs, backend))]
        initial_distance = sum((F(c)-1)**2 for c in resources)
        for index in range(2):
            old = _state_inputs(ref, owner.state.lifecycle)
            f = list(map(F, baseline_oracle(old)['f']))
            expected_c = tuple(float(F(c) + F(before.dt)*v) for c, v in zip(old.current.C, f, strict=True))
            result = owner.step_v4_input(request(before.dt, 'discrimination-'+label+'-'+str(index)))
            assert result.committed, result.failure
            counts['ordinary_steps'] += 1
            actual = _state_inputs(ref, owner.state.lifecycle)
            assert actual.current.C == expected_c
            assert actual.reset == inputs.reset
            distance = sum((F(c)-1)**2 for c in actual.current.C)
            assert distance > initial_distance if initial_distance else distance == 0
            frames.append(dict(current=state(actual.current), read=read(actual, backend),
                distance_squared_from_uniform=str(distance),
                distance_ratio=None if not initial_distance else str(distance / initial_distance),
                receipts=[r.to_payload() for r in result.emitted_receipts]))
        traces.append(dict(label=label, direction=mode, source=inputs.to_payload(), frames=frames,
            final_snapshot_digest=sha(canonical(owner.snapshot()))))
    # No mode-dependent writer effect is smuggled into the baseline comparison.
    for index in (1, 2):
        assert all(t['frames'][index]['current']['W_A'] == traces[0]['frames'][index]['current']['W_A'] for t in traces)

    # Matched HRESET control and one supplied equal split, both from the same
    # homogeneous current and genuinely distinct reset. No generated partition.
    events = []
    for kind in ('identity', 'split'):
        locus = ('b', [('ab', 'head')]) if kind == 'split' else ()
        target, target_backend, matrix, lineage = helper.build(ref, backend, kind, locus, (0., 0.))
        extra = () if target_backend.identity == backend.identity else (target_backend,)
        targets = () if target.identity == ref.identity else (target,)
        owner = GRCV4(before, differential_reference=backend, targets=targets,
                      target_differential_references=extra)
        counts['source_admissions'] += 1
        original_read = read(before, backend)
        declared = event(owner, target, matrix, (0.,)*len(target.graph.live_node_ids),
                         operation='discrimination-'+kind)
        result = owner.reconstruct_topology_event(declared)
        assert result.committed, result.failure
        counts['supplied_events'] += 1
        target_inputs = _state_inputs(target, owner.state.lifecycle)
        n = len(ref.graph.live_node_ids)
        for source_role, target_role in ((before.current, target_inputs.current), (before.reset, target_inputs.reset)):
            expected = tuple(float(sum((F(matrix[i*n+j])*F(source_role.C[j])
                                        for j in range(n)), F())) for i in range(len(target_role.C)))
            assert target_role.C == expected
        target_read = read(target_inputs, target_backend)
        j = target_read['observed']['J']
        assert any(x != 0 for x in j) if kind == 'split' else all(x == 0 for x in j)
        grouping = {v: [v] for v in ref.graph.live_node_ids}
        if kind == 'split': grouping['b'] = lineage['children']
        f_target = tendency(target.graph, j)
        aggregated = [sum((f_target[target.graph.node_index(w)] for w in grouping[v]), F())
                      for v in ref.graph.live_node_ids]
        assert any(aggregated) if kind == 'split' else not any(aggregated)
        fiber = None
        uniform_target = None
        if kind == 'split':
            assert lineage['shares'] == (.5, .5)
            fchildren = [f_target[target.graph.node_index(w)] for w in lineage['children']]
            fiber = [str(x - sum(fchildren, F()) / 2) for x in fchildren]
            assert list(map(F, fiber)) == [0, 0]
            # Separate target-state control, NOT a replacement event allocator.
            # Global .75 would change the untouched source neighbors as well.
            control = replace(before, geometry=target.geometry(),
                current=replace(target_inputs.current, C=(.75,)*4), reset=target_inputs.reset)
            GRCV4(control, differential_reference=target_backend)
            counts['source_admissions'] += 1
            uniform_target = dict(current=state(control.current), read=read(control, target_backend),
                                  scope='separately admitted target state, not a topology operation')
            assert all(x == 0 for x in uniform_target['read']['observed']['J'])
        continuation = owner.step_v4_input(request(before.dt, 'after-'+kind))
        assert continuation.committed, continuation.failure
        counts['ordinary_steps'] += 1
        continued = _state_inputs(target, owner.state.lifecycle)
        events.append(dict(kind=kind, target=target.to_payload(), target_backend=target_backend.to_payload(),
            matrix=matrix, lineage=lineage, source_read=original_read, request=declared.to_payload(),
            current=state(target_inputs.current), reset=state(target_inputs.reset), target_read=target_read,
            aggregated_target_tendency=list(map(str, aggregated)), child_fiber_tendency=fiber,
            event_receipts=[r.to_payload() for r in result.emitted_receipts],
            continuation_current=state(continued.current), continuation_read=read(continued, target_backend),
            continuation_receipts=[r.to_payload() for r in continuation.emitted_receipts],
            uniform_target_control=uniform_target, final_snapshot_digest=sha(canonical(owner.snapshot()))))

    # Unordered blocks matter: swapping the two children is not an ambiguity.
    # Equal three-arm source symmetry still has no invariant binary partition.
    symmetry = []
    for degree in (2, 3, 4):
        universe = frozenset(range(degree))
        partitions = {frozenset((frozenset(s), universe.difference(s)))
                      for size in range(1, degree) for s in itertools.combinations(universe, size)}
        invariant = [p for p in partitions if all(
            frozenset(frozenset(perm[i] for i in block) for block in p) == p
            for perm in itertools.permutations(range(degree)))]
        assert len(invariant) == (1 if degree == 2 else 0)
        symmetry.append(dict(degree=degree, unordered_partitions=len(partitions),
            invariant_under_all_port_permutations=len(invariant),
            scope='exact abstract fully symmetric port action; not native source reachability'))

    side = INV / 'tools/exploratory-side-tool'
    sys.path.insert(0, str(side / 'tool/src'))
    from grcv4_explorer.a_initializer import load_current_forensic_context
    from grcv4_explorer.forensic import contract_provenance
    context = load_current_forensic_context(ROOT, side)
    intake = json.loads((INV / 'evidence/autonomous-topology-change/ATCSourceIntake.json').read_text())
    assert sha(canonical(context.nodes)) == intake['forensic_context']['current_nodes_digest']
    assert sha(canonical(context.propagation_edges)) == intake['forensic_context']['propagation_edges_digest']
    authority = [dict(query=identifier, result=contract_provenance(context, identifier)) for identifier in (
        'D10.2-EC-PARENT-CORE-INCIDENCE-CONTINUITY', 'D10.2-EC-PARENT-BASE-POTENTIAL-FLOW',
        'D10.2-EC-GEOM-MOBILITY-BOUNDARY', 'D10.2-EC-PARENT-CORE-STRUCTURAL-CHARGE-PROJECTOR')]
    paths = {Path(__file__).resolve(), helper_path, information_path, INV / 'evidence/autonomous-topology-change/ATCSourceIntake.json',
             ROOT/'specs/grc-v4-spec.md', ROOT/'specs/grc-v4-topology-event-spec.md'}
    for module in tuple(sys.modules.values()):
        name = getattr(module, '__file__', None)
        if name:
            path = Path(name).resolve()
            if path.is_relative_to(ROOT) and '/.venv/' not in str(path) and path.suffix == '.py':
                paths.add(path)
    for trace in authority:
        paths.update(ROOT/row['source_ref']['path'] for row in trace['result']['rows'])
    import numpy as np
    result = dict(schema='grcv4_atc_refinement_discrimination_probe_v1', status='passed',
        scientific_status='bounded_controls_not_an_endogenous_law',
        predecessor_record_digest=information['record_digest'],
        source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip(),
        environment=dict(python=platform.python_version(), numpy=np.__version__),
        incremental_rates=incremental, native_baseline=dict(source=before.to_payload(),
            backend=backend.to_payload(), mode_histories=traces, supplied_event_controls=events),
        partition_symmetry=symmetry, counts=counts, forensic_queries=authority,
        not_established=['endogenous_trigger', 'endogenous_partition', 'completed_spark',
            'structural_Hessian', 'all_ten_native_conformance', 'nonunit_measure_extension',
            'autonomous_dispatch', 'scientific_acceptance'],
        production_changes=False, forensic_graph_unchanged=True,
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(), sha256=sha(p.read_bytes())) for p in sorted(paths)])
    result['record_digest'] = sha(canonical(result))
    return result


if __name__ == '__main__':
    print(json.dumps(run(), separators=(',', ':'), ensure_ascii=True, allow_nan=False))

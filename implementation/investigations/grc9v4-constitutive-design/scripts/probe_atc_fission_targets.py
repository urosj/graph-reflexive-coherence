#!/usr/bin/env python3
"""Fixed CAN-F2 targets: endowment, interaction and three-step continuation.

Research-only caller events. No guard revision, target search or ATC install.
Prints a fresh source-bound record; never overwrites retained evidence.
"""
from dataclasses import replace
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
sys.path[:0] = [str(ROOT / 'src'), str(ROOT)]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run():
    base_path = INV / 'scripts/probe_atc_refinement_discrimination.py'
    helper_path = INV / 'scripts/verify_atc2_candidates.py'
    rule_path = INV / 'scripts/probe_atc_source_fission.py'
    base = load(base_path, 'fission_target_oracle')
    helper = load(helper_path, 'fission_target_constructor')
    rule = load(rule_path, 'unchanged_fission_rule')
    paths = {Path(__file__).resolve(), base_path, helper_path, rule_path}
    predecessors = {}
    for name in ('ATCRefinementDiscriminationProbe.json', 'ATCSourceFissionProbe.json'):
        path = REFS / name
        paths.add(path)
        record = json.loads(path.read_text())
        assert record['record_digest'] == base.sha(base.canonical(
            {k: v for k, v in record.items() if k != 'record_digest'}))
        for binding in record['source_bindings']:
            assert base.sha((ROOT / binding['path']).read_bytes()) == binding['sha256'], binding['path']
        predecessors[name] = record
    original = predecessors['ATCRefinementDiscriminationProbe.json']
    onset = predecessors['ATCSourceFissionProbe.json']['native_onset']
    from pygrc.models.grc_v4 import GRCV4
    from pygrc.models.grc_v4_candidate_a import CandidateADifferentialReference
    from pygrc.models.grc_v4_geometry import GeometryStageInputs, GRCV4ReferenceGeometry
    from pygrc.models.grc_v4_lifecycle import _state_inputs
    from tests.models.test_grc_v4_events import event
    from tests.models.test_grc_v4_lifecycle import request

    baseline = GeometryStageInputs.from_payload(original['native_baseline']['source'])
    backend = CandidateADifferentialReference.from_payload(original['native_baseline']['backend'])
    uniform = next(row for row in original['native_baseline']['supplied_event_controls'] if row['kind'] == 'split')
    target = GRCV4ReferenceGeometry.from_payload(uniform['target'])
    target_backend = CandidateADifferentialReference.from_payload(uniform['target_backend'])
    graph = baseline.geometry.reference.graph
    assert graph.live_node_ids == ('a', 'b', 'c') and graph.live_edge_ids == ('ab', 'bc')

    # Predictions fixed from the review's literal equations, before native work.
    predictions = {
        'onset': dict(shares=['1/2', '1/2'],
            C=['195977/262144', '195977/262144', '197239/262144', '197239/262144'],
            J=['631/524288', '-631/524288', '0'],
            f=['-631/524288', '-631/524288', '631/524288', '631/524288']),
        'child_depletion': dict(shares=['17/32', '15/32'],
            C=['7/32', '25/32', '17/16', '15/16'],
            J=['29/128', '-3/128', '-15/128'],
            f=['-29/128', '-3/128', '11/32', '-3/32']),
        'exterior_reversal': dict(shares=['35/64', '29/64'],
            C=['1/64', '37/64', '2905/4096', '2407/4096'],
            J=['1545/8192', '105/8192', '-1899/16384'],
            f=['-1545/8192', '105/8192', '4989/16384', '-2109/16384']),
    }

    # Review controls: literal equations, not additional native admissions.
    algebra = []
    for w, expected_j, outcome in (
        ((1., 1.), (F(9, 16), F(-9, 16)), 'resolved'),
        ((1., 2.), (F(3, 4), F(-15, 8)), 'resolved'),
        ((1., 4.), (F(9, 8), F(-27, 4)), 'no_event'),
        ((1., 8.), (F(15, 8), F(-51, 2)), 'no_event'),
    ):
        source = replace(baseline, current=replace(baseline.current, C=(.5, 2., .5), W_A=w))
        j = base.baseline_oracle(source)['J']
        assert list(map(F, j)) == list(expected_j)
        choice = rule.source_prescription(graph, source.current.C, j)
        assert choice['outcome'] == outcome
        algebra.append(dict(C=source.current.C, W=w, J=j, prescription=choice))
    shifted = replace(baseline, current=replace(baseline.current, C=(1.5, 3., 1.5)))
    shifted_j = base.baseline_oracle(shifted)['J']
    assert shifted_j == algebra[0]['J']
    shifted_rule = rule.source_prescription(graph, shifted.current.C, shifted_j)
    assert shifted_rule['outcome'] == 'no_event'
    algebra.append(dict(C=shifted.current.C, W=shifted.current.W_A, J=shifted_j,
        prescription=shifted_rule, scope='literal physical-stock shift, Q=6; not a native Q=3 input'))

    counts = dict(fresh_source_admissions=0, explicit_present_reads=0,
        ordinary_commits=0, supplied_split_events=0, supplied_history_controls=0)

    def read(inputs, differential):
        point = helper.native_read(inputs, differential)
        counts['explicit_present_reads'] += 1
        oracle = base.baseline_oracle(inputs)
        assert list(point.current.values) == oracle['J']
        assert list(point.potential.values) == oracle['potential']
        return dict(observed=helper.witness(point), independent_oracle=oracle,
            prescription=rule.source_prescription(inputs.geometry.reference.graph,
                                                  inputs.current.C, point.current.values))

    cases = []
    for label in ('onset', 'child_depletion', 'exterior_reversal',
                  'nonuniform_history_split', 'nonuniform_history_only'):
        history_only = label == 'nonuniform_history_only'
        if label == 'onset':
            before = GeometryStageInputs.from_payload(onset['source'])
        else:
            c = (7/32, 2., 25/32) if label == 'child_depletion' else (
                (1/64, 83/64, 37/64) if label == 'exterior_reversal' else (.5, 2., .5))
            w = (1., 2.) if label.startswith('nonuniform_history') else (1., 1.)
            # The second counterexample has Q=121/64, not 3. Independently
            # declare a distinct reset with the same charge; do not rescale C.
            reset = replace(baseline.reset, C=(.5, .5, 57/64)) if label == 'exterior_reversal' else baseline.reset
            before = replace(baseline, current=replace(baseline.current, C=c, W_A=w),
                             reset=reset, Q_target=float(sum(map(F, c))))
        ref = before.geometry.reference
        chosen_target = ref if history_only else target
        chosen_backend = backend if history_only else target_backend
        owner = GRCV4(before, differential_reference=backend,
            targets=() if history_only else (target,),
            target_differential_references=() if history_only else (target_backend,))
        counts['fresh_source_admissions'] += 1
        initial_snapshot = owner.snapshot()
        initial_read = read(before, backend)
        assert owner.snapshot() == initial_snapshot
        onset_receipts = []
        source = before
        source_read = initial_read
        if label == 'onset':
            assert initial_read['prescription']['outcome'] == 'no_event'
            step = owner.step_v4_input(request(before.dt, 'source-fission-onset'))
            assert step.committed, step.failure
            counts['ordinary_commits'] += 1
            onset_receipts = [r.to_payload() for r in step.emitted_receipts]
            source = _state_inputs(ref, owner.state.lifecycle)
            assert source.to_payload() == onset['post']
            assert onset_receipts == onset['ordinary_receipts']
            # This owner additionally registers the fixed target. Its whole
            # snapshot therefore differs from the source-only predecessor;
            # compare the exact source lifecycle and ordinary receipts above.
            source_read = read(source, backend)
        assert source_read['prescription']['outcome'] == 'resolved'
        choice = source_read['prescription']['prescription']
        assert choice['vertex'] == 'b'
        assert choice['blocks'] == [[['ab', 'head']], [['bc', 'tail']]]
        assert F(source.current.C[1]) > F(source.current.C[0]) + F(source.current.C[2])
        rebuilt, rebuilt_backend, matrix, lineage = helper.build(ref, backend,
            'identity' if history_only else 'split',
            () if history_only else (choice['vertex'], [tuple(x) for x in choice['blocks'][0]]),
            source_read['observed']['J'])
        assert rebuilt.to_payload() == chosen_target.to_payload()
        assert rebuilt_backend.to_payload() == chosen_backend.to_payload()
        if not history_only:
            assert list(map(str, map(F, lineage['shares']))) == choice['shares']
        source_snapshot = owner.snapshot()
        assert read(source, backend) == source_read
        assert owner.snapshot() == source_snapshot
        declared = event(owner, chosen_target, matrix, (0.,)*len(chosen_target.graph.live_node_ids),
                         operation='fission-meaning-'+label)
        result = owner.reconstruct_topology_event(declared)
        assert result.committed, result.failure
        counts['supplied_history_controls' if history_only else 'supplied_split_events'] += 1
        after = _state_inputs(chosen_target, owner.state.lifecycle)
        for old, new in ((source.current, after.current), (source.reset, after.reset)):
            expected = [float(sum((F(matrix[i*3+j])*F(old.C[j]) for j in range(3)), F()))
                        for i in range(len(new.C))]
            assert list(new.C) == expected
            assert sum(map(F, new.C)) == F(source.Q_target)
            assert new.W_A == (1.,)*len(chosen_target.graph.live_edge_ids) and new.Z_4 is None
        if not history_only:
            assert list(map(F, after.current.C[2:])) == list(map(F, choice['allocated_current']))
        frames = []
        current = after
        for k in range(4):
            snapshot = owner.snapshot()
            observed = read(current, chosen_backend)
            assert owner.snapshot() == snapshot
            f = list(map(F, observed['independent_oracle']['f']))
            frame = dict(step=k, current=base.state(current.current), read=observed,
                         reset_unchanged=current.reset == after.reset)
            assert frame['reset_unchanged']
            if not history_only:
                j = list(map(F, observed['observed']['J']))
                margins = [F(current.current.C[i+2])-F(current.current.C[i]) for i in range(2)]
                external = [j[0], -j[1]]
                connector = [-j[2], j[2]]
                assert f[2:] == [x+y for x, y in zip(external, connector)]
                frame.update(child_margins=list(map(str, margins)),
                    exterior_inflow=list(map(str, external)), connector_inflow=list(map(str, connector)),
                    margin_tendencies=[str(f[i+2]-f[i]) for i in range(2)])
            if k == 0 and label in predictions:
                predicted = predictions[label]
                assert choice['shares'] == predicted['shares']
                assert list(map(F, current.current.C)) == list(map(F, predicted['C']))
                assert list(map(F, observed['observed']['J'])) == list(map(F, predicted['J']))
                assert f == list(map(F, predicted['f']))
            if k < 3:
                step = owner.step_v4_input(request(before.dt, 'fission-continuation-'+label+'-'+str(k+1)))
                assert step.committed, step.failure
                counts['ordinary_commits'] += 1
                updated = _state_inputs(chosen_target, owner.state.lifecycle)
                expected = tuple(float(F(c)+F(before.dt)*v) for c, v in zip(current.current.C, f, strict=True))
                assert updated.current.C == expected
                assert updated.current.W_A == current.current.W_A and updated.reset == after.reset
                frame['next_receipts'] = [r.to_payload() for r in step.emitted_receipts]
                current = updated
            frames.append(frame)
        cases.append(dict(label=label,source=before.to_payload(), initial_read=initial_read,
            onset_receipts=onset_receipts, selected_source=source.to_payload(), source_read=source_read,
            target=chosen_target.to_payload(), target_backend=chosen_backend.to_payload(),
            matrix=matrix, lineage=lineage, request=declared.to_payload(),
            event_receipts=[r.to_payload() for r in result.emitted_receipts],
            mapped_reset=base.state(after.reset), frames=frames,
            final_snapshot_digest=base.sha(base.canonical(owner.snapshot()))))

    symmetric, depletion, reversal, weighted, history = cases
    assert symmetric['frames'][0]['read']['prescription']['outcome'] == 'no_event'
    assert all(F(frame['read']['independent_oracle']['f'][3]) < 0 for frame in depletion['frames'])
    assert all(F(frame['exterior_inflow'][1]) < 0 for frame in reversal['frames'])
    assert depletion['frames'][0]['margin_tendencies'][1] == '-9/128'
    assert weighted['source_read'] == history['source_read']
    assert tuple(history['frames'][0]['read']['observed']['J']) == (9/16, -9/16)
    assert history['frames'][0]['read']['prescription']['prescription']['shares'] == ['1/2', '1/2']
    assert weighted['lineage']['shares'] != (.5, .5)
    assert list(map(F, weighted['frames'][0]['read']['independent_oracle']['f'])) == [
        F(5851,65536), F(-22235,65536), F(-53831,131072), F(86599,131072)]
    assert counts == dict(fresh_source_admissions=5, explicit_present_reads=31,
        ordinary_commits=16, supplied_split_events=4, supplied_history_controls=1)

    for module in tuple(sys.modules.values()):
        name = getattr(module, '__file__', None)
        if name:
            path = Path(name).resolve()
            if path.is_relative_to(ROOT) and '/.venv/' not in str(path) and path.suffix == '.py':
                paths.add(path)
    import numpy as np
    record = dict(schema='grcv4_atc_fission_targets_probe_v1', status='passed',
        candidate_id='ATC-CAN-F2-v1', scientific_status='initial_endowment_hypothesis_not_accepted',
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),
        environment=dict(python=platform.python_version(),numpy=np.__version__),
        predecessors={name:r['record_digest'] for name,r in predecessors.items()},
        backend=backend.to_payload(), predictions=predictions, literal_controls=algebra,
        cases=cases, counts=counts, continuation_steps_per_branch=3,
        interpretation=dict(initial_endowment='confirmed_for_selected_targets',
            symmetric_initial_accumulation='confirmed_in_restricted_control',
            general_two_child_accumulation='refuted_by_native_counterexample',
            general_exterior_inflow='refuted_by_native_counterexample',
            continuing_organization='not_established_by_three_steps'),
        not_established=['fission_necessity','stable_child_identity','all_ten_domains',
            'higher_degree_partition','repeat_event_composition','native_ATC_dispatch','scientific_acceptance'],
        authority='Predecessor typed traces retain their authority limits; new hypothesis is not graph-admitted.',
        production_changes=False,
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=base.sha(p.read_bytes())) for p in sorted(paths)])
    record['record_digest'] = base.sha(base.canonical(record))
    return record


if __name__ == '__main__':
    print(json.dumps(run(), separators=(',', ':'), ensure_ascii=True, allow_nan=False))

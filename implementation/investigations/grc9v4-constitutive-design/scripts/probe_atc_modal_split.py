#!/usr/bin/env python3
"""Three supplied modal splits: a fixed construction, never a source guard.

Reuses the retained uniform control. Emits a new record to stdout only.
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


def mm(a, b):
    return [[sum((F(x)*F(y) for x, y in zip(row, col, strict=True)), F())
             for col in zip(*b)] for row in a]


def vec(a, x):
    return [row[0] for row in mm(a, [[v] for v in x])]


def run():
    base_path = INV / 'scripts/probe_atc_refinement_discrimination.py'
    constructor_path = INV / 'scripts/verify_atc2_candidates.py'
    predecessor_path = REFS / 'ATCRefinementDiscriminationProbe.json'
    subject = json.loads(predecessor_path.read_text())
    base = load(base_path, 'modal_discrimination_oracle')
    assert subject['record_digest'] == base.sha(base.canonical({k: v for k, v in subject.items() if k != 'record_digest'}))
    for binding in subject['source_bindings']:
        assert base.sha((ROOT / binding['path']).read_bytes()) == binding['sha256'], binding['path']
    for row in subject['native_baseline']['mode_histories']:
        assert all(frame['current']['W_A'] == [1., 1.] for frame in row['frames'])
    helper = load(constructor_path, 'modal_split_constructor')
    from pygrc.models.grc_v4 import GRCV4
    from pygrc.models.grc_v4_candidate_a import CandidateADifferentialReference
    from pygrc.models.grc_v4_geometry import GeometryStageInputs, GRCV4ReferenceGeometry
    from pygrc.models.grc_v4_lifecycle import _state_inputs
    from tests.models.test_grc_v4_events import event
    from tests.models.test_grc_v4_lifecycle import request

    uniform = next(e for e in subject['native_baseline']['supplied_event_controls'] if e['kind'] == 'split')
    target = GRCV4ReferenceGeometry.from_payload(uniform['target'])
    backend = CandidateADifferentialReference.from_payload(subject['native_baseline']['backend'])
    target_backend = CandidateADifferentialReference.from_payload(uniform['target_backend'])
    # Target order (a,c,child0,child1), edge order (ab,bc,new). Algebra is literal,
    # independent of native matrix operators and any numerical eigensolver.
    b = [[1,0,0],[0,-1,0],[-1,0,1],[0,1,-1]]
    laplacian = mm(b, list(zip(*b)))
    generator = [[x/8 for x in row] for row in mm(laplacian, laplacian)]
    t = [[1,0,0],[0,0,1],[0,F(1,2),0],[0,F(1,2),0]]
    p = [[1,0,0,0],[0,0,1,1],[0,1,0,0]]
    assert mm(p,t) == [[1,0,0],[0,1,0],[0,0,1]]
    tp = mm(t,p)
    r = [[F(i==j)-tp[i][j] for j in range(4)] for i in range(4)]
    coefficient = mm(r, mm(generator,t))
    assert coefficient == [[0,0,0],[0,0,0],[F(-1,4),0,F(1,4)],[F(1,4),0,F(-1,4)]]
    assert [F(x) for x in uniform['matrix']] == [F(x) for row in t for x in row]
    assert all(sum(row[j] for row in t)==1 for j in range(3))
    assert vec(t,[1,1,1]) == [1,1,F(1,2),F(1,2)]
    rows = []
    counts = dict(fresh_source_admissions=0, explicit_present_reads=0, supplied_events=0, ordinary_steps=0)

    def read(inputs, differential):
        point = helper.native_read(inputs, differential)
        counts['explicit_present_reads'] += 1
        oracle = base.baseline_oracle(inputs)
        assert list(point.current.values) == oracle['J']
        assert list(point.potential.values) == oracle['potential']
        return dict(observed=helper.witness(point), independent_oracle=oracle)

    for label in ('high_plus', 'low_plus', 'low_minus'):
        source_row = next(row for row in subject['native_baseline']['mode_histories'] if row['label']==label)
        before = GeometryStageInputs.from_payload(source_row['source'])
        ref = before.geometry.reference
        owner = GRCV4(before, differential_reference=backend, targets=(target,),
                      target_differential_references=(target_backend,))
        counts['fresh_source_admissions'] += 1
        source_read = read(before, backend)
        # Partition and target fixed before comparing outcomes. Actual source
        # currents confirm that the original activity allocator gives 1/2,1/2.
        rebuilt, rebuilt_backend, matrix, lineage = helper.build(ref, backend, 'split',
            ('b', [('ab','head')]), source_read['observed']['J'])
        assert rebuilt.to_payload() == target.to_payload()
        assert rebuilt_backend.to_payload() == target_backend.to_payload()
        assert list(matrix) == uniform['matrix'] and lineage['shares'] == (.5,.5)
        assert lineage['half_edge_activities'][0] == lineage['half_edge_activities'][1]
        declared = event(owner, target, matrix, (0.,)*4, operation='fixed-split-'+label)
        result = owner.reconstruct_topology_event(declared)
        assert result.committed, result.failure
        counts['supplied_events'] += 1
        after = _state_inputs(target, owner.state.lifecycle)
        for old_role, new_role in ((before.current,after.current),(before.reset,after.reset)):
            assert list(map(F,new_role.C)) == vec(t,old_role.C)
            assert new_role.W_A == (1.,)*3 and new_role.Z_4 is None
        target_read = read(after,target_backend)
        f_source = list(map(F,source_read['independent_oracle']['f']))
        f_target = list(map(F,target_read['independent_oracle']['f']))
        assert f_target == vec(generator,after.current.C)
        fiber = vec(r,f_target)
        assert fiber == vec(coefficient,before.current.C)
        expected_pair = [F(0),F(0)] if label=='high_plus' else [F(-1,128),F(1,128)] if label=='low_plus' else [F(1,128),F(-1,128)]
        assert fiber[2:] == expected_pair
        coarse = [x-y for x,y in zip(vec(p,f_target),f_source,strict=True)]
        assert [x-y for x,y in zip(f_target,vec(t,f_source),strict=True)] == [x+y for x,y in zip(vec(t,coarse),fiber,strict=True)]
        continuation = owner.step_v4_input(request(before.dt,'fixed-split-next-'+label))
        assert continuation.committed, continuation.failure
        counts['ordinary_steps'] += 1
        continued = _state_inputs(target,owner.state.lifecycle)
        expected_c = [F(c)+F(before.dt)*f for c,f in zip(after.current.C,f_target,strict=True)]
        assert list(map(F,continued.current.C)) == expected_c
        difference = F(continued.current.C[2])-F(continued.current.C[3])
        expected_difference = F(0) if label=='high_plus' else F(-1,4096) if label=='low_plus' else F(1,4096)
        assert difference == expected_difference
        assert continued.current.W_A == (1.,)*3 and continued.reset == after.reset
        next_read = read(continued,target_backend)
        rows.append(dict(label=label,source=before.to_payload(),source_read=source_read,
            lineage=lineage,request=declared.to_payload(),current=base.state(after.current),
            reset=base.state(after.reset),target_read=target_read,
            coarse_residual=list(map(str,coarse)),fiber_residual=list(map(str,fiber)),
            event_receipts=[receipt.to_payload() for receipt in result.emitted_receipts],
            continuation_current=base.state(continued.current),continuation_read=next_read,
            child_difference=str(difference),
            continuation_receipts=[receipt.to_payload() for receipt in continuation.emitted_receipts],
            final_snapshot_digest=base.sha(base.canonical(owner.snapshot()))))

    paths={Path(__file__).resolve(),base_path,constructor_path,predecessor_path}
    for module in tuple(sys.modules.values()):
        name=getattr(module,'__file__',None)
        if name:
            path=Path(name).resolve()
            if path.is_relative_to(ROOT) and '/.venv/' not in str(path) and path.suffix=='.py': paths.add(path)
    import numpy as np
    record=dict(schema='grcv4_atc_modal_split_probe_v1',status='passed',
        scientific_status='fixed_construction_discrimination_not_endogenous_fission',
        predecessor_record_digest=subject['record_digest'],
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),
        environment=dict(python=platform.python_version(),numpy=np.__version__),
        target=uniform['target'],target_backend=uniform['target_backend'],backend=subject['native_baseline']['backend'],
        exact_fiber_coefficients=[[str(x) for x in row] for row in coefficient],
        reused_uniform_control=dict(record='ATCRefinementDiscriminationProbe.json',
            pointer='/native_baseline/supplied_event_controls/1',native_rerun=False,
            fiber=uniform['child_fiber_tendency'],child_difference='0'),
        prior_modal_current_W_constant_verified=True,cases=rows,counts=counts,
        authority='Predecessor typed traces retained with unchanged source bindings; no new graph reconstruction or admission.',
        not_established=['source_guard','endogenous_partition','stable_child_identity','all_ten_fission',
                         'structural_functional_closure','native_ATC_dispatch','scientific_acceptance'],
        production_changes=False,
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=base.sha(p.read_bytes())) for p in sorted(paths)])
    record['record_digest']=base.sha(base.canonical(record))
    return record


if __name__=='__main__':
    print(json.dumps(run(),separators=(',',':'),ensure_ascii=True,allow_nan=False))

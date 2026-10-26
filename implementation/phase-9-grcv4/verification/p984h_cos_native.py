"""Capped native C_OS baseline segments; no covariance or ten-step credit."""
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

import numpy as np
import p984h_cos as oracle
import p984g_cos_native as capture
from pygrc.models.grc_v4_geometry import GeometryStageInputs
from pygrc.models.grc_v4_step import ProvisionalCandidateCOSStep
from pygrc.models.grc_v4_state import FrozenJSONMap
from pygrc.models.grc_v4_numerics import matrix_operation
from pygrc.models import grc_9_v4_lifecycle as native
from pygrc.models.grc_9_v4_expansion import GRC9V4ExpansionRequestInput

ROOT, BASE, HERE = oracle.ROOT, oracle.BASE, oracle.HERE
SELF = HERE + 'p984h_cos_native.py'
PLAN = BASE + 'P9-8.4h-COSNativePlan.md'
INPUTS = BASE + 'P9-8.4h-COSNativeInputs.json'
CAPS = dict(prefix=900, event=1200, current=600, reset=600)
require, digest, seal = oracle.require, oracle.digest, oracle.seal


def path(segment):
    require(segment in CAPS, 'unknown native segment')
    return BASE + 'P9-8.4h-COSNative-' + segment + '.json.xz'


def read(segment):
    return json.loads(lzma.decompress((ROOT / path(segment)).read_bytes()))


def manifest():
    upstream = oracle.old.read(oracle.INPUTS)
    paths = set(upstream['source_bindings']) | {SELF, PLAN, oracle.INPUTS,
        oracle.RESULTS, capture.SELF, HERE + 'test_p984h_cos_native.py'}
    return seal(dict(schema='p984h-cos-native-inputs-v1',
        source_bindings={p: oracle.sha(p) for p in sorted(paths)},
        oracle_digest=oracle.read_result()['record_digest'],
        numerical_policy='certified_arb_256_weighted_v1', exact_backend='flint',
        caps=CAPS, raw_budget=12000000, compressed_budget=2000000,
        source_beats=2, target_steps_per_role=1, planned_total_steps_per_role=10,
        comparison=dict(atol=2e-11, rtol=2e-11), user_accepted=False,
        aggregate_closed=False, covariance_executed=False))


def state(value):
    spec = value['specialization']
    return native.GRC9V4COSState(GeometryStageInputs.from_payload(value['inputs']),
        native.GRC9V4Specialization(FrozenJSONMap(spec['resolved']), FrozenJSONMap(spec['identity_payload'])))


def observe_step(before, expected=None):
    started = time.monotonic()
    old_digest = digest(before.to_payload())
    step = ProvisionalCandidateCOSStep(before)
    after = step.next_inputs
    require(step.os_pass is not None and step.final is not None, 'missing native stages')
    require(old_digest == digest(before.to_payload()), 'input mutation')
    require(after.reset == before.reset and after.geometry == before.geometry, 'reset/geometry persisted incorrectly')
    require(after.step_index == before.step_index + 1 and after.time == before.time + before.dt, 'chronology')
    require(step.resource.continuity_evaluations == 1, 'multiple continuity writes')
    require(step.final.inputs.current == after.current and
            step.final.inputs.geometry == step.os_pass.corrector.inputs.geometry, 'wrong final read operand')
    result = dict(before_digest=old_digest, after_digest=digest(after.to_payload()),
        before_C=list(before.current.C), after_C=list(after.current.C), dt=before.dt,
        before_index=before.step_index, after_index=after.step_index,
        before_time=before.time, after_time=after.time,
        predictor=capture.point(step.os_pass.predictor), corrector=capture.point(step.os_pass.corrector),
        final=capture.point(step.final), split_admitted=step.os_pass.residual.admitted,
        split_certificate=step.os_pass.residual.execution_certificate.to_dict(),
        split_values_digest=digest(step.os_pass.residual.exact_values),
        reset_digest=digest(after.to_payload()['reset']), minimum_resource=min(after.current.C),
        charge=oracle.charge(before.current.C, after.current.C,
            before.geometry.reference.profile.params_resolved.to_payload()['charge'], before.Q_target),
        seconds=time.monotonic() - started)
    if expected is not None:
        require(result['corrector']['current'] == expected['current'] and
                result['after_C'] == expected['after_C'], 'native/staged first-step mismatch')
    # Dense equations own their assembly; production owns the actual values.
    subject = dict(graph=before.geometry.reference.graph.port_graph.to_payload(),
                   profile=before.geometry.reference.profile.to_payload())
    b, params = oracle.old.graph_data(subject)
    predictor = oracle.old.dense_point(b, np.array(before.current.C), np.eye(b.shape[1]), params['candidate'])
    h = oracle.old.generated_h(b, predictor['causal_flat'], params)
    corrector = oracle.old.dense_point(b, np.array(before.current.C), h, params['candidate'])
    final = oracle.old.dense_point(b, np.array(after.current.C), h, params['candidate'])
    errors = {}
    for name, reference in (('predictor', predictor), ('corrector', corrector), ('final', final)):
        for field in ('current', 'baseline', 'read_flux', 'causal_flat'):
            a, e = np.asarray(result[name][field]), np.asarray(reference[field])
            require(np.allclose(a, e, atol=2e-11, rtol=2e-11), 'dense mismatch ' + name + '/' + field)
            errors[name + '/' + field] = float(np.max(abs(a-e)))
    result['dense_errors'] = errors
    return result, after


def execute(segment, progress):
    declaration = oracle.old.read(oracle.old.PREPARED)
    dt = declaration['selected_configuration']['ordinary_dt']
    numerical = oracle.read_result()
    if segment == 'prefix':
        from prepare_p983_all_realizations import materialize
        seed = materialize(declaration, 'source')
        before = replace(seed.inputs, dt=dt)
        rows = []
        for i in range(2):
            progress('source_beat_' + str(i+1))
            row, after = observe_step(before, numerical['source_step'] if i == 1 else None)
            if i == 0:
                saved = json.loads(oracle.historical(oracle.PREFIX))['result']
                require(row['before_digest'] == saved['before_digest'] and row['after_digest'] == saved['after_digest'],
                        'accepted prefix differs')
            post = replace(seed, inputs=replace(after, dt=0))
            row['trigger'] = oracle.trigger(post)
            require(row['trigger']['eligible'] == bool(i), 'trigger chronology')
            rows.append(row); before = after
            progress('source_beat_' + str(i+1) + '_completed')
        require(post.scientific_digest == numerical['trigger']['source_state_digest'], 'beat-two source identity')
        return dict(steps=rows, state=post.to_payload(), native_steps=2, native_events=0)
    if segment == 'event':
        prefix = checked('prefix'); seed = state(prefix['execution']['state'])
        _, _, request, identity, event_id, expected = oracle.fresh_subject(seed)
        progress('owner_source_readmission')
        owner = native.GRC9V4COSOperation(seed)
        checkpoint = owner.checkpoint(); publication = owner._published
        stale = deepcopy(request); stale['source_state_digest'] = 'grcv4-state-sha256:' + '0'*64
        rejection = owner.expand(GRC9V4ExpansionRequestInput.from_payload(stale))
        require(not rejection.committed and owner._published is publication and owner.checkpoint() == checkpoint, 'stale rollback')
        reads = []
        real_pass = native.CandidateCOSPass
        def observed(operand):
            progress('event_OS_read_' + str(len(reads)+1))
            passed = real_pass(operand)
            require(owner._published is publication, 'published before both-role admission')
            reads.append(dict(resources=list(operand.current.C),
                graph_digest=digest(operand.geometry.reference.graph.port_graph.to_payload()),
                predictor=capture.point(passed.predictor), corrector=capture.point(passed.corrector),
                split_admitted=passed.residual.admitted, old_publication_live=True))
            return passed
        with patch.object(native, 'CandidateCOSPass', observed):
            outcome = owner.expand(GRC9V4ExpansionRequestInput.from_payload(request))
        require(outcome.committed, 'native event failed: ' + str(outcome.failure))
        actual = owner.state.inputs
        require(actual.geometry.reference.graph.port_graph.to_payload() == expected['graph'] and
                actual.geometry.reference.profile.to_payload() == expected['profile'], 'target graph/profile mismatch')
        for role in oracle.ROLES:
            require(list(getattr(actual, role).C) == expected['roles'][role]['C'], 'role transfer mismatch')
        require(len(reads) == 4 and actual.step_index == seed.inputs.step_index and actual.time == seed.inputs.time, 'event reads/clock')
        return dict(predecessor_digest=prefix['record_digest'], request=request, event_id=event_id,
            event_identity=identity, checkpoint=json.loads(owner.checkpoint()), admissions=reads,
            stale_failure=rejection.failure.to_payload(), rollback_exact=True,
            native_steps=0, native_events=1, ten_step_campaign_complete=False)
    event = checked('event'); target = state(event['execution']['checkpoint']['state'])
    before = replace(target.inputs, current=getattr(target.inputs, segment), dt=dt)
    expected = next(c for c in numerical['cases'] if c['role'] == segment)['steps'][0]
    progress(segment + '_target_first_step')
    row, after = observe_step(before, expected)
    return dict(predecessor_digest=event['record_digest'], role=segment, steps=[row],
                next_inputs=after.to_payload(), native_steps=1, native_events=0,
                detached_continuation=True, ten_step_campaign_complete=False)


def validate_steps(rows, initial):
    current = initial
    subject = dict(graph=current.geometry.reference.graph.port_graph.to_payload(),
                   profile=current.geometry.reference.profile.to_payload())
    for row in rows:
        require(row['before_digest'] == digest(current.to_payload()) and row['before_C'] == list(current.current.C), 'step input identity')
        result = capture.independent_continuity(dict(subject, roles={'current': {'C': row['before_C']}}),
                                               'current', row['corrector']['current'], current.dt)
        require(row['after_C'] == result and row['minimum_resource'] == min(result) >= 0, 'literal continuity/sign')
        from pygrc.models.grc_v4_state import GRCV4AuthoritativeState
        captured = GeometryStageInputs.from_payload(current.to_payload())
        after = replace(captured, current=GRCV4AuthoritativeState(tuple(result), None, None),
            step_index=current.step_index+1, time=current.time+current.dt)
        require(row['after_digest'] == digest(after.to_payload()) and row['reset_digest'] == digest(after.to_payload()['reset']), 'step output identity')
        require(row['dt'] == current.dt and row['before_index'] == current.step_index and row['after_index'] == after.step_index
                and row['before_time'] == current.time and row['after_time'] == after.time, 'clock drift')
        require(row['charge'] == oracle.charge(current.current.C,result,subject['profile']['params_resolved']['charge'],current.Q_target), 'charge drift')
        require(row['split_admitted'] is True and row['final']['input_hodge_digest'] == row['corrector']['input_hodge_digest'], 'split/final geometry')
        for stage in ('predictor','corrector','final'):
            for field in ('current','baseline','read_flux','causal_flat'):
                require(len(row[stage][field]) == len(current.geometry.reference.graph.live_edge_ids) and
                        np.isfinite(row[stage][field]).all(), 'nonfinite/dimension')
        current = after
    return current


def checked(segment):
    m = oracle.old.read(INPUTS)
    require(m == manifest(), 'native source/input binding drift')
    value = read(segment)
    require(value == seal(value) and value['manifest_digest'] == m['record_digest'] and value['segment'] == segment, 'native record identity')
    require(value['outcome'] == 'completed' and not value['user_accepted'] and not value['aggregate_closed']
            and not value['covariance_executed'], 'incomplete or widened native evidence')
    execution = value['execution']; declaration = oracle.old.read(oracle.old.PREPARED)
    dt = declaration['selected_configuration']['ordinary_dt']
    if segment == 'prefix':
        from prepare_p983_all_realizations import materialize
        seed = materialize(declaration, 'source')
        require(len(execution['steps']) == 2 and execution['native_steps'] == 2 and execution['native_events'] == 0, 'prefix scope')
        after = validate_steps(execution['steps'], replace(seed.inputs, dt=dt))
        expected = replace(seed, inputs=replace(after, dt=0))
        require(execution['state'] == expected.to_payload() and oracle.trigger(expected) == oracle.read_result()['trigger'], 'source reconstruction')
        saved = json.loads(oracle.historical(oracle.PREFIX))['result']
        require(execution['steps'][0]['after_digest'] == saved['after_digest'], 'historical prefix')
        require(execution['steps'][1]['corrector']['current'] == oracle.read_result()['source_step']['current'], 'source oracle')
    elif segment == 'event':
        prefix = checked('prefix'); seed = state(prefix['execution']['state'])
        _,_,request,identity,event_id,target = oracle.fresh_subject(seed)
        cp = execution['checkpoint']; actual = state(cp['state'])
        require(execution['predecessor_digest'] == prefix['record_digest'] and execution['request'] == request
                and execution['event_identity'] == identity and execution['event_id'] == event_id, 'event linkage')
        require(cp['initial'] == seed.to_payload() and cp['requests'] == [request] and len(cp['receipts']) > 0, 'checkpoint history')
        require(actual.inputs.geometry.reference.graph.port_graph.to_payload() == target['graph']
                and actual.inputs.geometry.reference.profile.to_payload() == target['profile'], 'event target')
        require(actual.inputs.step_index == seed.inputs.step_index and actual.inputs.time == seed.inputs.time, 'event clock')
        require(execution['native_steps'] == 0 and execution['native_events'] == 1 and not execution['ten_step_campaign_complete'], 'event scope')
        require(len(execution['admissions']) == 4 and execution['rollback_exact'], 'event admission/rollback')
        for i, role in enumerate(oracle.ROLES):
            require(list(getattr(actual.inputs,role).C) == target['roles'][role]['C'], 'transfer')
            for index, resources in ((i,list(getattr(seed.inputs,role).C)),(i+2,target['roles'][role]['C'])):
                entry=execution['admissions'][index]
                require(entry['resources'] == resources and entry['split_admitted'] and entry['old_publication_live'], 'both-role precommit')
    else:
        event = checked('event'); target = state(event['execution']['checkpoint']['state'])
        require(execution['predecessor_digest'] == event['record_digest'] and execution['role'] == segment, 'role predecessor')
        require(len(execution['steps']) == 1 and execution['native_steps'] == 1 and execution['native_events'] == 0
                and execution['detached_continuation'] and not execution['ten_step_campaign_complete'], 'role scope')
        after = validate_steps(execution['steps'], replace(target.inputs,current=getattr(target.inputs,segment),dt=dt))
        require(execution['next_inputs'] == after.to_payload(), 'continuation poststate')
        expected = next(c for c in oracle.read_result()['cases'] if c['role'] == segment)['steps'][0]
        require(execution['steps'][0]['corrector']['current'] == expected['current'] and list(after.current.C) == expected['after_C'], 'role oracle')
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare','run','check'))
    parser.add_argument('--segment', choices=tuple(CAPS))
    args = parser.parse_args()
    with oracle.exact_backend(oracle.ExactBackend.FLINT), oracle.numerical_policy(oracle.NumericalPolicy.CERTIFIED_ARB_256):
        if args.action == 'prepare': oracle.old.write_new(INPUTS,manifest()); return
        require(args.segment is not None, 'segment required')
        if args.action == 'check':
            r = checked(args.segment); print(json.dumps(dict(segment=args.segment,outcome=r['outcome'],native_numerics_rerun=False))); return
        require(not (ROOT/path(args.segment)).exists(),'refuse overwrite')
        m=oracle.old.read(INPUTS); require(m==manifest(),'source drift before run')
        require(all(os.environ.get(k)=='1' for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS')), 'single thread required')
        started=time.monotonic(); progress=lambda stage: print(json.dumps(dict(segment=args.segment,stage=stage,seconds=time.monotonic()-started)),flush=True)
        def expired(*_): raise TimeoutError('explicit native segment cap exceeded')
        signal.signal(signal.SIGALRM,expired); signal.alarm(CAPS[args.segment])
        r=dict(schema='p984h-cos-native-segment-v1',segment=args.segment,manifest_digest=m['record_digest'],
               user_accepted=False,aggregate_closed=False,covariance_executed=False)
        try:
            with matrix_operation():
                r.update(execution=execute(args.segment,progress),outcome='completed')
        except Exception as error:
            r.update(outcome='failed',failure=dict(type=type(error).__name__,message=str(error),stage=getattr(error,'stage',None)))
        finally: signal.alarm(0)
        r=seal(dict(r,elapsed_seconds=time.monotonic()-started))
        raw=json.dumps(r,indent=2,allow_nan=False).encode()+b'\n';packed=lzma.compress(raw)
        require(len(raw)<=m['raw_budget'] and len(packed)<=m['compressed_budget'],'retention budget')
        with (ROOT/path(args.segment)).open('xb') as f:f.write(packed)
        require(r['outcome']=='completed','native segment failed: '+str(r.get('failure')))
        checked(args.segment); progress('retained_integrity_passed')


if __name__ == '__main__': main()

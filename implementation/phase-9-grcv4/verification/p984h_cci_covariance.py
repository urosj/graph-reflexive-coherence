"""Eight large C_CI covariance counterparts; resumable, no baseline replay.

Reuse accepted large graph/chart transport and CI joint-root equations. Only
run executes numerical events/steps. Each transform is an independent process.
"""
import argparse
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import replace
from functools import lru_cache
import hashlib
import json
import lzma
import os
import signal
import time
from unittest.mock import patch

import numpy as np
import p984h_cci_continuation as cont
import p984h_cos_covariance as maps

event, prior = cont.event, cont.prior
ROOT, BASE, HERE = cont.ROOT, cont.BASE, cont.HERE
SELF = HERE+'p984h_cci_covariance.py'
TEST = HERE+'test_p984h_cci_covariance.py'
PLAN = BASE+'P9-8.4h-CCICovariancePlan.md'
INPUTS = BASE+'P9-8.4h-CCICovarianceInputs.json'
REVIEW = BASE+'P9-8.4h-CCICovarianceReview.md'
KINDS, ROLES = maps.KINDS, cont.ROLES
require, seal, digest, q = cont.require, cont.seal, cont.digest, cont.q
ATOL = RTOL = 2e-13  # Existing C_CI .e/.f comparison, not the looser OS policy.


def path(kind, segment):
    require(kind in KINDS and segment in ('event', *ROLES), 'unknown counterpart')
    return BASE+f'P9-8.4h-CCICovariance-{kind}-{segment}.json.xz'


def read(kind, segment):
    return json.loads(lzma.decompress((ROOT/path(kind, segment)).read_bytes()))


@lru_cache(maxsize=1)
def baseline():
    source, ev = event.read('source'), event.read('event')
    require(source == seal(source) and ev == seal(ev), 'baseline seals')
    return source['execution']['state'], ev['execution'], source['execution']['fresh']


@contextmanager
def transport():
    # Explicit, process-local dependency adapter. No native result is patched.
    # The shared mapping routines depend only on base()[0]'s source graph.
    with patch.object(maps, 'base', return_value=baseline()[:2]):
        yield


@lru_cache(maxsize=8)
def subject(kind):
    require(kind in KINDS, 'unknown transform')
    source, ev, fresh = baseline()
    with transport():
        d = maps.declaration(kind)
        inp = maps.input_image(source['inputs'], maps.graph_image(source['inputs']['reference']['graph'], d, source=True), d)
        seed = replace(event.state(source), inputs=inp)
        request = deepcopy(fresh['request']); branches = d['chart']['branches']; shares = [0.]*3
        for i, value in enumerate(request['resource_distribution'], 1): shares[branches[str(i)]-1] = value
        request.update(source_node_id=maps.rename(request['source_node_id'], d),
            source_state_digest=seed.scientific_digest, source_graph_digest=inp.geometry.reference.graph.graph_digest,
            target_profile_template_id=event.cci_profile_template(inp.geometry.reference).profile_template_id,
            operation_id='p984h-cci-covariance-'+kind, resource_distribution=shares,
            module_chirality=request['module_chirality']*d['chart']['chirality_factor'],
            growth_phase=branches[str(request['growth_phase'])])
        identity = deepcopy(fresh['event_identity'])
        for key in identity:
            if key in request and key != 'schema_version': identity[key] = request[key]
        eid = maps.ordering.b.payload_identity('expansion_event_identity_payload', identity)
        original = ev['checkpoint']['state']['inputs']
        graph = maps.graph_image(original['reference']['graph'], d, ev['event_id'], eid)
        expected = maps.input_image(original, graph, d, ev['event_id'], eid)
        expected = replace(expected, operation_id=request['operation_id'])
    plan = event.GRC9V4ExpansionPlan(inp.geometry.reference.graph.port_graph, seed.scientific_digest,
        event.GRC9V4ExpansionRequestInput.from_payload(request),
        event.GRC9ExpansionPolicy.from_payload(seed.specialization.resolved['expansion']))
    require(plan.event_identity_payload() == identity and plan.event_id == eid, 'transported event identity')
    require(plan.target_graph == expected.geometry.reference.graph.port_graph, 'exact transported allocator')
    return seed, request, identity, eid, expected


def manifest():
    upstream = prior.read(cont.INPUTS)
    require(upstream == cont.manifest(), 'baseline source drift')
    paths = {SELF, TEST, PLAN, cont.INPUTS, maps.SELF, maps.ordering.SELF, maps.chart.SELF,
        maps.chart.b.VECTORS, *upstream['source_bindings'],
        *(cont.path(r, s) for r in ROLES for s in (*range(1,11), 'final'))}
    with transport(): declarations = [maps.declaration(k) for k in KINDS]
    return seal(dict(schema='p984h-cci-covariance-inputs-v1',
        source_bindings={p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(paths)},
        baseline_event_digest=event.read('event')['record_digest'], transforms=declarations,
        numerical_policy='certified_arb_256_weighted_v1', backend='flint',
        event_cap_seconds=1200, step_cap_seconds=600, workers=8, threads_per_worker=1,
        comparison=dict(atol=ATOL, rtol=RTOL), native_events=8, target_steps=16,
        source_prefix_rerun=False, transformed_horizon=1, full_joint_roots=True,
        uniform_trajectory_enclosure=False, user_accepted=False, aggregate_closed=False))


def capture(root, operand):
    value = prior.independent_root(root, cont.subject(operand))
    t = root.selected
    value['joint'] = dict(recipe=root.to_payload()['numerics'],
        domain_id=root.inputs.geometry.reference.profile.params_resolved.realization.contraction_domain_id,
        H=[list(r) for r in t.inputs.geometry.one_form_hodge.matrix],
        generated=[list(r) for r in t.generated.one_form_hodge.matrix],
        source=[list(r) for r in t.structural_source.increment])
    return value


def compare(actual, expected, label):
    a, b = np.asarray(actual), np.asarray(expected)
    require(a.shape == b.shape and np.isfinite(a).all() and np.isfinite(b).all()
        and np.allclose(a, b, atol=ATOL, rtol=RTOL), 'covariance '+label)
    return float(np.max(abs(a-b))) if a.size else 0.


def check_joint(root, operand):
    cont.check_root(root, operand)
    joint = root['joint']; params = operand.geometry.reference.profile.params_resolved.to_payload()
    require(joint['recipe'] == 'ci_analytic_residual_enclosure_binary64_v2'
        and joint['domain_id'] == params['realization']['contraction_domain_id'], 'joint recipe/domain')
    require(digest(joint['H']) == root['point']['input_hodge_digest']
        and joint['H'] == [list(r) for r in operand.geometry.one_form_hodge.matrix], 'full selected geometry')
    b, params = prior.f.prior.shared.graph_data(cont.subject(operand))
    flat = root['point']['causal_flat']; n = len(flat); overlap = abs(b).T@abs(b)/2
    expected_source = np.zeros((n,n))
    for i,j in zip(*np.nonzero(overlap), strict=True):
        star = float(q(overlap[i,j])*q(flat[i])*q(flat[j]))
        expected_source[i,j] = float(q(params['candidate']['zeta_C'])*q(star))
    # These are own-root construction checks; covariance is checked separately.
    require(np.array_equal(joint['source'], expected_source), 'same-root structural source')
    require(np.array_equal(joint['generated'], prior.f.prior.shared.generated_h(b, flat, params)),
        'same-root generated geometry')


def baseline_hodge(inputs, root):
    # Checkpoints may spell the identity as integer 0/1. The selected geometry
    # canonicalizes those exact values to binary64 before hashing. Authenticate
    # that same representation, rejecting any lossy conversion or mutation.
    raw = inputs['H1_form']; h = np.asarray(raw, dtype=float)
    require(h.ndim == 2 and h.shape[0] == h.shape[1] and np.isfinite(h).all(), 'baseline geometry shape')
    require(all(q(x) == q(y) for row, converted in zip(raw, h.tolist(), strict=True)
        for x, y in zip(row, converted, strict=True)), 'baseline geometry conversion')
    require(digest(h.tolist()) == root['point']['input_hodge_digest'], 'baseline selected geometry')
    return h


def root_pair(old, new, old_inputs, new_inputs, kind, target):
    _, _, _, eid, _ = subject(kind)
    with transport():
        d = maps.declaration(kind)
        _, ei, signs = maps.mapping(old_inputs['reference']['graph'], new_inputs.to_payload()['reference']['graph'], d,
            baseline()[1]['event_id'] if target else None, eid if target else None)
    errors = {key: compare(new['point'][key], np.asarray(old['point'][key])[ei]*np.asarray(signs), key)
              for key in ('current', 'baseline', 'read_flux', 'causal_flat')}
    old_h = baseline_hodge(old_inputs, old); expected = old_h[np.ix_(ei,ei)]*np.outer(signs,signs)
    errors['H'] = compare(new['joint']['H'], expected, 'joint H')
    old_subject = dict(graph=old_inputs['reference']['graph'], profile=old_inputs['reference']['profile'],
        roles={r:old_inputs[r] for r in ROLES})
    b, params = prior.f.prior.shared.graph_data(old_subject)
    generated = prior.f.prior.shared.generated_h(b, old['point']['causal_flat'], params)
    errors['generated'] = compare(new['joint']['generated'], generated[np.ix_(ei,ei)]*np.outer(signs,signs), 'generated H')
    require(new['point']['selector_rank'] == old['point']['selector_rank'] == 1, 'selector covariance')
    return errors


def execute_event(kind):
    seed, request, identity, eid, expected = subject(kind)
    owner = event.native.GRC9V4CCIOperation(seed); publication = owner._published; checkpoint = owner.checkpoint()
    stale = dict(request, source_state_digest='grcv4-state-sha256:'+'0'*64)
    failed = owner.expand(event.GRC9V4ExpansionRequestInput.from_payload(stale))
    require(not failed.committed and owner._published is publication and owner.checkpoint() == checkpoint, 'stale rollback')
    real = event.native.ProvisionalCandidateCIStep; reads = []
    def observed(before):
        print(json.dumps(dict(kind=kind, stage='event_admission', pair=len(reads)+1)), flush=True)
        step = real(before); require(owner._published is publication, 'early publication')
        reads.append(dict(current=capture(step.root, before), reset=capture(step.reset_root, replace(before,current=before.reset)),
            old_publication_live=True))
        return step
    with patch.object(event.native, 'ProvisionalCandidateCIStep', observed):
        outcome = owner.expand(event.GRC9V4ExpansionRequestInput.from_payload(request))
    require(outcome.committed, 'native event rejected: '+str(outcome.failure))
    actual = owner.state.inputs
    require(actual.to_payload() == expected.to_payload(), 'complete transported target')
    require(actual.time == seed.inputs.time and actual.step_index == seed.inputs.step_index and len(reads) == 2, 'event clock/admission')
    return dict(request=request, event_identity=identity, event_id=eid, checkpoint=json.loads(owner.checkpoint()),
        admissions=reads, rollback_exact=True, stale_failure=failed.failure.to_payload(), native_events=1, native_steps=0)


def step_inputs(kind, role):
    ev = read(kind, 'event'); require(ev == seal(ev) and ev['outcome'] == 'completed', 'event predecessor')
    target = event.state(ev['execution']['checkpoint']['state']).inputs
    dt = prior.f.read(prior.f.prior.PREPARED)['selected_configuration']['ordinary_dt']
    return replace(target, current=getattr(target,role), dt=dt), ev['record_digest']


def execute_step(kind, role):
    before, predecessor = step_inputs(kind, role)
    full = {}; real = cont.ProvisionalCandidateCIStep
    def observed(operand):
        step = real(operand)
        for name, root, inputs in (('reset',step.reset_root,replace(operand,current=operand.reset)),
                ('current',step.root,operand),('final',step.restart,step.next_inputs)):
            t = root.selected
            full[name] = dict(recipe=root.to_payload()['numerics'],
                domain_id=inputs.geometry.reference.profile.params_resolved.realization.contraction_domain_id,
                H=[list(r) for r in t.inputs.geometry.one_form_hodge.matrix],
                generated=[list(r) for r in t.generated.one_form_hodge.matrix],
                source=[list(r) for r in t.structural_source.increment])
        return step
    with patch.object(cont,'ProvisionalCandidateCIStep',observed): fields, _ = cont.observe(before)
    for name in fields['roots']: fields['roots'][name]['joint'] = full[name]
    return dict(fields, event_record_digest=predecessor, role=role, native_events=0, native_steps=1,
        detached_continuation=True)


def check(record, m, kind, segment):
    require(record == seal(record) and record['manifest_digest'] == m['record_digest']
        and record['schema'] == 'p984h-cci-covariance-results-v1' and record['kind'] == kind
        and record['segment'] == segment and record['outcome'] == 'completed', 'record identity')
    require(not record['user_accepted'] and not record['aggregate_closed'], 'scope inflation')
    cap = m['event_cap_seconds'] if segment == 'event' else m['step_cap_seconds']
    require(0 <= record['elapsed_seconds'] <= cap, 'segment cap')
    e = record['execution']; seed, request, identity, eid, expected = subject(kind)
    errors = {}
    if segment == 'event':
        cp = e['checkpoint']; target = replace(seed, inputs=expected)
        require(e['request'] == request and e['event_identity'] == identity and e['event_id'] == eid, 'event identity')
        require(cp['state'] == target.to_payload() and cp['initial'] == seed.to_payload()
            and cp['requests'] == [request] and len(cp['receipts']) > 0, 'event checkpoint')
        require(e['native_events'] == 1 and e['native_steps'] == 0 and len(e['admissions']) == 2
            and e['rollback_exact'] and bool(e['stale_failure']), 'event coverage')
        for index, operand in enumerate((seed.inputs, expected)):
            observed = e['admissions'][index]; require(observed['old_publication_live'], 'admission ordering')
            old_inputs = baseline()[0]['inputs'] if index == 0 else baseline()[1]['checkpoint']['state']['inputs']
            for role in ROLES:
                root = observed[role]; actual = replace(operand,current=getattr(operand,role))
                check_joint(root, actual)
                errors[f'{index}/{role}'] = root_pair(baseline()[1]['admissions'][index][role], root,
                    old_inputs, operand, kind, index == 1)
    else:
        before, predecessor = step_inputs(kind, segment)
        require(e['event_record_digest'] == predecessor and e['role'] == segment
            and e['native_events'] == 0 and e['native_steps'] == 1 and e['detached_continuation'], 'step linkage')
        # Adapt only the record wrapper, never inputs/scientific fields, to the
        # already reviewed baseline continuation checker.
        wrapper = seal(dict(e, schema='p984h-cci-continuation-segment-v1',
            manifest_digest=m['record_digest'], predecessor_digest=predecessor,
            step=1, outcome='completed', elapsed_seconds=record['elapsed_seconds'],
            final_reads=0, covariance_executed=False, user_accepted=False, aggregate_closed=False))
        after = cont.validate(wrapper, dict(m,event_record_digest=predecessor), segment, 1, before, predecessor)
        old = cont.read(segment,1)
        old_before = cont.initial(segment).to_payload()
        for name, operand in (('current',before),('reset',replace(before,current=before.reset)),('final',after)):
            check_joint(e['roots'][name], operand)
            old_inputs = old['next_inputs'] if name == 'final' else old_before
            errors[name] = root_pair(old['roots'][name],e['roots'][name],old_inputs,operand,kind,True)
        with transport():
            ni, _, _ = maps.mapping(old_before['reference']['graph'],before.to_payload()['reference']['graph'],
                maps.declaration(kind),baseline()[1]['event_id'],eid)
        errors['resources'] = compare(after.current.C,np.asarray(old['next_inputs']['current']['C'])[ni],'resources')
    return errors


def run_one(m, kind, segment):
    destination = ROOT/path(kind,segment)
    if destination.exists():
        value = read(kind,segment); require(value['covariance_errors'] == check(value,m,kind,segment),'retained comparison')
        print(json.dumps(dict(kind=kind,segment=segment,status='retained_no_rerun')),flush=True); return
    cap = m['event_cap_seconds'] if segment == 'event' else m['step_cap_seconds']
    def expired(*_): raise TimeoutError('declared segment cap; no fallback')
    start=time.monotonic(); signal.signal(signal.SIGALRM,expired); signal.alarm(cap)
    print(json.dumps(dict(kind=kind,segment=segment,status='started')),flush=True)
    try:
        with event.matrix_operation():
            execution = execute_event(kind) if segment == 'event' else execute_step(kind,segment)
        elapsed=time.monotonic()-start; require(elapsed <= cap,'segment cap exceeded')
    except Exception as exc:
        print(json.dumps(dict(kind=kind,segment=segment,status='failed',type=type(exc).__name__,message=str(exc))),flush=True)
        raise
    finally: signal.alarm(0)
    record = seal(dict(schema='p984h-cci-covariance-results-v1',manifest_digest=m['record_digest'],kind=kind,
        segment=segment,outcome='completed',execution=execution,elapsed_seconds=elapsed,
        user_accepted=False,aggregate_closed=False))
    record['covariance_errors'] = check(record,m,kind,segment); record=seal(record)
    require(m == manifest(),'source drift during execution')
    packed=lzma.compress(json.dumps(record,separators=(',',':'),allow_nan=False).encode()+b'\n')
    require(len(packed) <= 2000000,'compressed segment budget')
    with destination.open('xb') as stream: stream.write(packed)
    print(json.dumps(dict(kind=kind,segment=segment,status='completed',seconds=elapsed,compressed_bytes=len(packed))),flush=True)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=('prepare','run','check'));p.add_argument('--kind',choices=KINDS)
    args=p.parse_args()
    with event.exact_backend(event.ExactBackend.FLINT),event.numerical_policy(event.NumericalPolicy.CERTIFIED_ARB_256):
        if args.action == 'prepare':
            require(not (ROOT/INPUTS).exists(),'refuse overwrite')
            (ROOT/INPUTS).write_text(json.dumps(manifest(),indent=2)+'\n');return
        m=prior.read(INPUTS); require(m == manifest(),'source drift')
        require(args.kind in KINDS,'select transform')
        require(all(os.environ.get(k)=='1' for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS')),'single numerical thread')
        for segment in ('event',*ROLES):
            if args.action == 'run': run_one(m,args.kind,segment)
            else:
                r=read(args.kind,segment);require(r['covariance_errors']==check(r,m,args.kind,segment),'saved comparison')
                print(json.dumps(dict(kind=args.kind,segment=segment,status='checked_no_native_rerun')),flush=True)


if __name__ == '__main__': main()

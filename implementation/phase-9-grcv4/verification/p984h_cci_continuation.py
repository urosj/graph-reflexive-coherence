"""Bounded C_CI histories from the actual .h event; no implicit retry/fallback.

Reuses the accepted joint-root residual and contraction bridge. Successful
prefixes are compressed and resumable; --check never executes native roots.
"""
import argparse
from copy import deepcopy
from dataclasses import replace
import hashlib
import json
import lzma
import math
import os
import signal
import time

import flint
import p984h_cci as event
from p984g_cci_closure_check import pairwise
from pygrc.models.grc_v4_ci import CandidateCIRoot, ProvisionalCandidateCIStep

ROOT, BASE, HERE = event.ROOT, event.BASE, event.HERE
SELF = HERE+'p984h_cci_continuation.py'
TEST = HERE+'test_p984h_cci_continuation.py'
PLAN = BASE+'P9-8.4h-CCIContinuationPlan.md'
INPUTS = BASE+'P9-8.4h-CCIContinuationInputs.json'
ROLES, CAP = event.ROLES, 600
require, seal, digest = event.require, event.seal, event.digest
prior, q = event.prior, event.prior.q


def path(role, step):
    require(role in ROLES and (type(step) is int and 1 <= step <= 10 or step == 'final'), 'unknown segment')
    return BASE+f'P9-8.4h-CCIContinuation-{role}-{step}.json.xz'


def read(role, step):
    return json.loads(lzma.decompress((ROOT/path(role, step)).read_bytes()))


def manifest():
    upstream = prior.read(event.INPUTS)
    require(upstream == event.manifest(), 'event source drift')
    result = event.read('event')
    require(result == seal(result) and result['manifest_digest'] == upstream['record_digest']
            and result['outcome'] == 'completed', 'event prerequisite')
    paths = {SELF, TEST, PLAN, event.INPUTS, event.path('source'), event.path('event'),
             HERE+'p984g_cci_closure_check.py', *upstream['source_bindings']}
    return seal(dict(schema='p984h-cci-continuation-inputs-v1',
        source_bindings={p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(paths)},
        event_record_digest=result['record_digest'], event_id=result['execution']['event_id'],
        roles=list(ROLES), steps_per_role=10, final_reads_per_role=1,
        seconds_per_step_or_final_read=CAP, max_role_workers=2, threads_per_worker=1,
        numerical_policy='certified_arb_256_weighted_v1', backend='flint',
        independent_joint_residual_bits=prior.f.iv.BITS, detached_continuation=True,
        covariance_executed=False, user_accepted=False, aggregate_closed=False))


def initial(role):
    require(role in ROLES, 'unknown role')
    target = event.state(event.read('event')['execution']['checkpoint']['state'])
    dt = prior.f.read(prior.f.prior.PREPARED)['selected_configuration']['ordinary_dt']
    return replace(target.inputs, current=getattr(target.inputs, role), dt=dt)


def subject(before):
    ref = before.geometry.reference
    return dict(graph=ref.graph.port_graph.to_envelope(), profile=ref.profile.to_payload(),
        roles={r: dict(C=list(getattr(before, r).C), W_A=None, Z_4=None) for r in ROLES})


def check_root(root, before):
    """Authenticate both halves and the domain of a retained selected CI root."""
    operand = subject(before)
    b, params = prior.f.prior.shared.graph_data(operand)
    p = params['candidate']; tolerance = q(params['realization']['tolerance'])
    require(root['resource_digest'] == digest(list(before.current.C)), 'root resource identity')
    require(root['evaluations'] == 1 and root['consumed_reference_geometry']
            and root['identity'].startswith('grcv4-ci-root-sha256:'), 'root selection/identity')
    require(root['point']['input_hodge_digest'] == digest(before.geometry.one_form_hodge.matrix),
            'joint root geometry identity')
    cert = root['certificate']
    radius = q(float.fromhex(params['realization']['contraction_domain_id'].split(':', 1)[1]))
    require(q(cert['radius']) == radius and 0 <= q(cert['displacement_upper']) <= radius
            and 0 <= q(cert['contraction_upper']) < 1 and q(cert['selector_gap_lower']) > 0
            and 0 < q(cert['conditioning_upper']) <= q(params['solver']['conditioning_limit'])
            and cert['selector_rank'] == 1 and cert['reference_connected'] and cert['regular_reduced_root']
            and cert['norm'] == 'joint_current_geometry_l2_v1'
            and cert['scope'] == 'analytic_local_reference_ball', 'whole-ball certificate')
    ej, eh = (q(root[k]) for k in ('independent_current_residual_upper', 'independent_geometry_residual_upper'))
    require(ej >= 0 and eh >= 0 and ej*ej+eh*eh == q(root['independent_residual_squared_upper'])
            and ej*ej+eh*eh <= tolerance**2 and 0 <= q(root['native_residual_squared']) <= tolerance**2,
            'joint residual')
    bounds = prior.f.prior.certificate(operand, 'current')['bounds']
    with prior.f.staged.ctx.workprec(prior.f.iv.BITS):
        bridge = prior.f.staged.bridge(bounds, p['chi_C'], q(p['chi_C'])*q(p['zeta_C']),
            q(params['geometry']['kappa_H'])*q(p['zeta_C']), ej, eh)
    require(root['joint_root_error'] == bridge, 'joint error bridge')
    for key in ('current', 'baseline', 'read_flux', 'causal_flat'):
        require(len(root['point'][key]) == b.shape[1] and all(math.isfinite(x) for x in root['point'][key]),
                'point dimension/finiteness')
    require(root['point']['selector_rank'] == 1, 'selector rank')


def resource_bounds(before, after, root):
    """Local exact-root resource enclosure plus represented continuity error.

    Each enclosure starts at this step's actual represented input, not at an
    unrounded global trajectory. It is not a uniform ten-step error tube.
    """
    b, _ = prior.f.prior.shared.graph_data(subject(before))
    j = root['point']['current']; error = q(root['joint_root_error']['current_error_upper'])
    rows = []
    with prior.f.staged.ctx.workprec(prior.f.iv.BITS):
        for c, y, row in zip(before.current.C, after.current.C, b, strict=True):
            center = q(c)-q(before.dt)*sum((q(int(w))*q(x) for w, x in zip(row, j, strict=True)), q(0))
            radius = q(before.dt)*prior.f.iv.hi(prior.f.iv.a(sum(int(w)**2 for w in row)).sqrt())*error
            rows.append(dict(lower=str(center-radius), upper=str(center+radius),
                rounding_error=str(abs(q(y)-center)), root_resource_radius=str(radius)))
    require(min(q(r['lower']) for r in rows) > 0 and min(after.current.C) > 0,
            'resource positivity not certified')
    return dict(local_exact_root_bounds=rows, minimum_exact_root_lower=str(min(q(r['lower']) for r in rows)),
        minimum_represented_resource=min(after.current.C),
        maximum_rounding_error=str(max(q(r['rounding_error']) for r in rows)),
        maximum_root_resource_radius=str(max(q(r['root_resource_radius']) for r in rows)),
        uniform_trajectory_enclosure=False)


def observe(before):
    old = digest(before.to_payload()); step = ProvisionalCandidateCIStep(before); after = step.next_inputs
    require(digest(before.to_payload()) == old, 'input mutation')
    require(after.reset == before.reset and after.geometry == before.geometry
            and after.current.W_A is None and after.current.Z_4 is None, 'authority mutation')
    require(step.carrier_writes == 0 and step.writer is None and step.resource.continuity_evaluations == 1,
            'unexpected writer/continuity count')
    require(after.time == before.time+before.dt and after.step_index == before.step_index+1, 'clock/index')
    require(step.restart.inputs.current == after.current and step.reset_root.inputs.current == before.reset,
            'root role mismatch')
    roots = {name: prior.independent_root(root, subject(before)) for name, root in
             (('reset', step.reset_root), ('current', step.root), ('final', step.restart))}
    require(list(after.current.C) == prior.cos.independent_continuity(subject(before), 'current',
            roots['current']['point']['current'], before.dt), 'literal continuity')
    return dict(input_digest=old, roots=roots, next_inputs=after.to_payload(),
        charge=step.resource.charge.receipt_values(),
        exact_resource_sum_delta=str(sum(map(q, after.current.C), q(0))-sum(map(q, before.current.C), q(0))),
        reset_unchanged=True, continuation_reference_geometry=True, continuity_evaluations=1, carrier_writes=0,
        resource_bounds=resource_bounds(before, after, roots['current'])), after


def validate(record, m, role, step, before, predecessor):
    require(record == seal(record) and record['schema'] == 'p984h-cci-continuation-segment-v1'
            and record['manifest_digest'] == m['record_digest'], 'segment identity')
    require(record['role'] == role and record['step'] == step and record['predecessor_digest'] == predecessor
            and record['event_record_digest'] == m['event_record_digest'], 'segment linkage')
    require(record['outcome'] == 'completed' and 0 <= record['elapsed_seconds'] <= CAP
            and not record['user_accepted'] and not record['aggregate_closed'] and not record['covariance_executed']
            and record['native_events'] == 0 and record['detached_continuation'] is True, 'segment scope')
    require(record['input_digest'] == digest(before.to_payload()), 'actual predecessor input')
    if step == 'final':
        require(record['native_steps'] == 0 and record['final_reads'] == 1, 'final read count')
        check_root(record['root'], before)
        return before
    require(record['native_steps'] == 1 and record['final_reads'] == 0, 'step count')
    payload = record['next_inputs']
    after = replace(before, current=event.GRCV4AuthoritativeState(tuple(payload['current']['C']), None, None),
                    time=before.time+before.dt, step_index=before.step_index+1)
    require(payload == after.to_payload(), 'complete continuation poststate')
    roots = record['roots']; require(set(roots) == {'current', 'reset', 'final'}, 'root roster')
    for name, operand in (('current', before), ('reset', replace(before, current=before.reset)), ('final', after)):
        check_root(roots[name], operand)
    require(list(after.current.C) == prior.cos.independent_continuity(subject(before), 'current',
            roots['current']['point']['current'], before.dt), 'literal continuity')
    require(record['resource_bounds'] == resource_bounds(before, after, roots['current']), 'resource sign/error bounds')
    charge = pairwise(after.current.C); target = before.Q_target
    require(record['charge'] == dict(target_charge=target, admitted_charge=charge, residual=float(q(charge)-q(target))),
            'represented charge')
    cp = before.geometry.reference.profile.params_resolved.to_payload()['charge']
    require(abs(q(charge)-q(target)) <= q(cp['absolute_tolerance'])+q(cp['relative_tolerance'])*max(abs(q(target)), q(1)),
            'charge admission')
    require(q(record['exact_resource_sum_delta']) == sum(map(q, after.current.C), q(0))-sum(map(q, before.current.C), q(0)),
            'exact stored sum drift')
    require(record['reset_unchanged'] and record['continuation_reference_geometry']
            and record['continuity_evaluations'] == 1 and record['carrier_writes'] == 0, 'lifecycle scope')
    return after


def checked_role(m, role):
    before = initial(role); predecessor = m['event_record_digest']; rows = []
    for step in range(1, 11):
        if not (ROOT/path(role, step)).exists(): break
        record = read(role, step); before = validate(record, m, role, step, before, predecessor)
        predecessor = record['record_digest']; rows.append(record)
    require(not any((ROOT/path(role, s)).exists() for s in range(len(rows)+2, 11)), 'noncontiguous continuation')
    if (ROOT/path(role, 'final')).exists():
        require(len(rows) == 10, 'final read without ten steps')
        validate(read(role, 'final'), m, role, 'final', before, predecessor)
    return before, predecessor, rows


def execute_one(m, role, step, before, predecessor):
    require(not (ROOT/path(role, step)).exists(), 'refuse overwrite')
    def expired(*_): raise TimeoutError('explicit 600-second cap; no fallback')
    start = time.monotonic(); signal.signal(signal.SIGALRM, expired); signal.alarm(CAP)
    print(json.dumps(dict(role=role, step=step, stage='started')), flush=True)
    try:
        with event.matrix_operation():
            if step == 'final':
                old = digest(before.to_payload()); root = CandidateCIRoot(before)
                fields = dict(input_digest=old, root=prior.independent_root(root, subject(before))); after = before
                require(digest(before.to_payload()) == old, 'final read mutation')
            else: fields, after = observe(before)
        elapsed = time.monotonic()-start
        require(elapsed <= CAP, 'segment cap exceeded')
    except Exception as exc:
        print(json.dumps(dict(role=role, step=step, outcome='failed', type=type(exc).__name__,
            message=str(exc), seconds=time.monotonic()-start)), flush=True)
        raise
    finally: signal.alarm(0)
    record = seal(dict(fields, schema='p984h-cci-continuation-segment-v1', manifest_digest=m['record_digest'],
        event_record_digest=m['event_record_digest'], predecessor_digest=predecessor, role=role, step=step,
        outcome='completed', elapsed_seconds=elapsed, runtime=dict(python_flint=flint.__version__, threads=1),
        native_steps=int(step != 'final'), native_events=0, final_reads=int(step == 'final'),
        detached_continuation=True, covariance_executed=False, user_accepted=False, aggregate_closed=False))
    validate(record, m, role, step, before, predecessor)
    require(m == manifest(), 'source changed during segment')
    packed = lzma.compress(json.dumps(record, separators=(',', ':'), allow_nan=False).encode()+b'\n')
    require(len(packed) <= 2000000, 'compressed budget exceeded')
    with (ROOT/path(role, step)).open('xb') as stream: stream.write(packed)
    print(json.dumps(dict(role=role, step=step, outcome='completed', seconds=elapsed,
        minimum_resource=min(after.current.C), record_digest=record['record_digest'])), flush=True)
    return after, record['record_digest']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', 'run', 'check'))
    parser.add_argument('--role', choices=ROLES)
    parser.add_argument('--through', type=int, choices=(1, 10), default=10)
    args = parser.parse_args()
    with event.exact_backend(event.ExactBackend.FLINT), event.numerical_policy(event.NumericalPolicy.CERTIFIED_ARB_256):
        if args.action == 'prepare':
            event.check('event')  # Authenticate the actual event once, not replay it.
            require(not (ROOT/INPUTS).exists(), 'refuse overwrite')
            (ROOT/INPUTS).write_text(json.dumps(manifest(), indent=2)+'\n'); return
        m = prior.read(INPUTS); require(m == manifest(), 'continuation source drift')
        if args.action == 'check':
            summary = {}
            for role in ROLES:
                _, _, rows = checked_role(m, role)
                summary[role] = dict(native_steps=len(rows), final_reads=int((ROOT/path(role, 'final')).exists()))
            print(json.dumps(dict(roles=summary, native_numerics_rerun=False))); return
        require(args.role in ROLES, 'role required')
        require(all(os.environ.get(k) == '1' for k in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS')), 'single thread')
        before, predecessor, rows = checked_role(m, args.role)
        require(len(rows) <= args.through, 'requested scope already exceeded')
        for step in range(len(rows)+1, args.through+1):
            before, predecessor = execute_one(m, args.role, step, before, predecessor)
        if args.through == 10 and not (ROOT/path(args.role, 'final')).exists():
            execute_one(m, args.role, 'final', before, predecessor)


if __name__ == '__main__': main()

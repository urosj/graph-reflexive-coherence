"""Finite D94 C_CI neighborhood and native failure pressure, not a trajectory tube.

Freeze --prepare before --run. Retained checking never runs native producers.
The original twenty-case campaign and its source bindings remain unchanged.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
from dataclasses import replace
from fractions import Fraction as Q
import json
from unittest.mock import patch

import p984d_cci as d

r, b, c = d.r, d.b, d.certificate
SELF = b.HERE + "p984d_cci_hardening.py"
TEST = b.HERE + "test_p984d_cci_hardening.py"
INPUTS = b.BASE + "P9-8.4d-CCIHardeningCases.json"
RESULTS = b.BASE + "P9-8.4d-CCIHardeningResults.json"


def center(manifest):
    return next(v for v in manifest['cases'] if
        v['request']['target_effective_degree'] == 94 and
        v['request']['growth_phase'] == 1 and v['request']['module_chirality'] == 1)


def declaration():
    manifest = b.read(d.INPUTS)
    paths = {v['path'] for v in manifest['source_bindings']} | {SELF, TEST}
    probes = [dict(label='center', kind='center')]
    probes += [dict(label=f'share_{j}_to_{i}', kind='share', receiver=i, donor=j)
        for i in range(3) for j in range(3) if i != j]
    probes += [dict(label=f'external_transfer_{sign}', kind='resource', sign=sign)
        for sign in (-1, 1)]
    return b.seal(dict(schema='p984d-cci-hardening-inputs-v1',
        source_bindings=b.bind(sorted(paths)), predecessor=b.bind((d.INPUTS, d.RESULTS)),
        layout='D94 E+1 P1', center_case_id=center(manifest)['case_id'], probes=probes,
        share_radius=1/4096, resource_radius=1/16384, beats=2, roles=list(r.ROLES),
        excluded_shares=[1/4, 1/2, 1/4], late_receipt_failure=True,
        scope='finite_target_continuation_not_uniform_tube_or_new_allocation_law',
        user_accepted=False, aggregate_closed=False))


def target_for(manifest, declared, probe):
    case = deepcopy(center(manifest))
    if probe['kind'] == 'share':
        shares = case['request']['resource_distribution']
        shares[probe['receiver']] += declared['share_radius']
        shares[probe['donor']] -= declared['share_radius']
        b.require(sum(map(Q, shares)) == 1 and min(shares) > 0, 'invalid simplex probe')
    target = b.independent_target(manifest, case)
    if probe['kind'] == 'resource':
        external = [i for i,n in enumerate(target.geometry.reference.graph.live_node_ids)
            if not (isinstance(n, str) and n.startswith('grc-event-'))][:2]
        b.require(len(external) == 2, 'external resource direction missing')
        roles = {}
        for role in r.ROLES:
            state = getattr(target, role)
            values = list(state.C)
            values[external[0]] += probe['sign'] * declared['resource_radius']
            values[external[1]] -= probe['sign'] * declared['resource_radius']
            b.require(min(values) >= 0 and sum(map(Q, values)) == sum(map(Q, state.C)),
                'resource probe does not preserve exact charge')
            roles[role] = replace(state, C=tuple(values))
        target = replace(target, **roles)
    return replace(target, dt=b.DT)


def margins(before, step):
    bounds = step['root']['independent_certificate']['bounds']
    return dict(minimum_C=min(step['poststate']['current']['C']),
        resource_error=step['resource_error'],
        positivity_lower=str(Q(min(step['poststate']['current']['C']))-Q(step['resource_error'])),
        contraction_upper=bounds['contraction'], contraction_margin=str(1-Q(bounds['contraction'])),
        current_inverse_margin=bounds['regularity'],
        selector_gap_lower=str(c.graph_bound(r.independent_model(before))),
        root_error=bounds['root_error'])


def transfer_deltas(manifest, target):
    source = b.GeometryStageInputs.from_payload(manifest['expected_source']['inputs'])
    return {role: str(sum(map(Q, getattr(target, role).C))-
        sum(map(Q, getattr(source, role).C))) for role in r.ROLES}


def run_probe(args):
    manifest, declared, probe = args
    target = target_for(manifest, declared, probe)
    row = dict(probe=probe['label'], target=target.to_payload(),
        exact_coordinate_transfer_deltas=transfer_deltas(manifest, target), roles={})
    with b.exact_backend(b.ExactBackend.FLINT), c.checker():
        for role in r.ROLES:
            before = replace(target, current=getattr(target, role))
            steps = []
            for beat in range(declared['beats']):
                native = r.ProvisionalCandidateCIStep(before)
                captured = r.capture_step(native)
                measure = margins(before, captured)
                b.require(Q(measure['positivity_lower']) > 0, 'probe lacks positive separation')
                steps.append(dict(beat=beat+1, step=captured, margins=measure))
                before = native.next_inputs
            row['roles'][role] = steps
    print(probe['label'], 'passed both histories', flush=True)
    return row


def native_failures(manifest, declared):
    seed = r.state(manifest['expected_source'])
    request = replace(b.GRC9V4ExpansionRequestInput.from_payload(center(manifest)['request']),
        resource_distribution=tuple(declared['excluded_shares']),
        operation_id='p984d-cci-hardening-excluded')
    with b.exact_backend(b.ExactBackend.FLINT):
        owner = r.native.GRC9V4CCIOperation(seed)
        outcome = owner.expand(request)
        b.require(outcome.committed, 'excluded event rejected before continuation')
        published, checkpoint = owner._published, owner.checkpoint()
        before = replace(owner.state.inputs, dt=b.DT)
        root = r.capture_root(r.CandidateCIRoot(before))
        truth = c.certify(before, root)
        expected = truth['c']-c.number(before.dt)*truth['high'].B*truth['read']['J']
        upper = min(c.n.endpoint(v, 1) for v in expected)
        b.require(upper < 0, 'excluded negative sign not independently separated')
        preimage = before.to_payload()
        try:
            r.ProvisionalCandidateCIStep(before)
        except Exception as exc:
            b.require('nonnegative' in str(exc), 'unexpected native rejection')
            failure = dict(exception=type(exc).__name__, stage=getattr(exc, 'stage', None),
                message=str(exc))
        else:
            raise ValueError('excluded continuation unexpectedly passed')
        b.require(before.to_payload() == preimage and owner._published is published
            and owner.checkpoint() == checkpoint, 'failed continuation mutated publication')
        root['independent_certificate'] = dict(input_identity=before.identity,
            selected_root_digest=root['record_digest'],
            bounds={k:str(v) for k,v in truth['certificate'].items()},
            theorem='C_CI_unit_tree23_pointwise_joint_root_v1')
        excluded = dict(request=request.to_payload(), event_committed=True,
            continuation_outcome='rejected', role='current', beat=1,
            before=preimage, root=root, exact_real_negative_coordinate_upper=str(upper),
            failure=failure, input_preserved=True, whole_event_publication_preserved=True,
            preserved_event_checkpoint_digest=b.digest(json.loads(checkpoint)))
        # A real failed event transaction, distinct from detached step rejection.
        owner = r.native.GRC9V4CCIOperation(seed)
        published, checkpoint = owner._published, owner.checkpoint()
        valid = b.GRC9V4ExpansionRequestInput.from_payload(center(manifest)['request'])
        with patch.object(r.native, 'make_commit_receipts', side_effect=ValueError('injected late receipt failure')):
            outcome = owner.expand(valid)
        b.require(not outcome.committed and outcome.failure.stage == 'commit'
            and owner._published is published and owner.checkpoint() == checkpoint,
            'late event failure mutated whole publication')
        late = dict(event_committed=False, request=valid.to_payload(),
            failure=outcome.failure.to_payload(), whole_publication_preserved=True,
            preserved_source_checkpoint_digest=b.digest(json.loads(checkpoint)))
    print('native excluded continuation and late event rollback passed', flush=True)
    return dict(excluded=excluded, late_event=late)


def check(declared, result, *, numerics=False):
    b.check_digest(declared)
    b.check_bindings(declared['source_bindings'])
    b.check_bindings(declared['predecessor'])
    b.require(declared == declaration(), 'hardening declaration drift')
    b.check_digest(result)
    b.require(result['schema'] == 'p984d-cci-hardening-results-v1'
        and result['inputs_digest'] == declared['record_digest']
        and result['user_accepted'] is False and result['aggregate_closed'] is False,
        'hardening binding/scope drift')
    manifest = b.read(d.INPUTS)
    rows = result['neighborhood']
    b.require([v['probe'] for v in rows] == [v['label'] for v in declared['probes']], 'probe roster drift')
    for probe, row in zip(declared['probes'], rows, strict=True):
        target = target_for(manifest, declared, probe)
        b.require(row['target'] == target.to_payload() and set(row['roles']) == set(r.ROLES)
            and row['exact_coordinate_transfer_deltas'] == transfer_deltas(manifest, target), 'target/role drift')
        for role in r.ROLES:
            before = replace(target, current=getattr(target, role))
            steps = row['roles'][role]
            b.require([v['beat'] for v in steps] == list(range(1, declared['beats']+1)), 'probe schedule drift')
            for saved in steps:
                with c.checker():
                    after = r.check_step(before, saved['step'], numerics=numerics)
                b.require(saved['margins'] == margins(before, saved['step'])
                    and Q(saved['margins']['positivity_lower']) > 0, 'margin drift')
                before = after
    excluded = result['failures']['excluded']
    b.require(excluded['event_committed'] is True and excluded['continuation_outcome'] == 'rejected'
        and excluded['role'] == 'current' and excluded['beat'] == 1
        and excluded['input_preserved'] is True and excluded['whole_event_publication_preserved'] is True
        and excluded['request']['resource_distribution'] == declared['excluded_shares']
        and 'nonnegative' in excluded['failure']['message']
        and Q(excluded['exact_real_negative_coordinate_upper']) < 0, 'excluded failure drift')
    before = b.GeometryStageInputs.from_payload(excluded['before'])
    with c.checker():
        r.check_root(before, excluded['root'], numerics=numerics)
    if numerics:
        truth = c.certify(before, excluded['root'])
        image = truth['c']-c.number(before.dt)*truth['high'].B*truth['read']['J']
        b.require(str(min(c.n.endpoint(v, 1) for v in image)) == excluded['exact_real_negative_coordinate_upper'],
            'excluded sign drift')
    late = result['failures']['late_event']
    b.require(late['event_committed'] is False and late['failure']['stage'] == 'commit'
        and late['whole_publication_preserved'] is True, 'late rollback drift')
    return dict(status='passed_pending_acceptance', finite_probes=9, histories=18, native_steps=36,
        native_excluded_continuations=1, injected_late_event_failures=1,
        uniform_tube=False, accumulated_exact_real_trajectory=False,
        native_trajectories_rerun=False, interval_equations_recomputed=numerics,
        user_accepted=False, aggregate_closed=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('prepare', 'run', 'check'))
    parser.add_argument('--recheck-numerics', action='store_true')
    args = parser.parse_args()
    b.require(not args.recheck_numerics or args.mode == 'check', 'numerics needs check')
    if args.mode == 'prepare':
        b.write_new(INPUTS, declaration())
        return
    declared = b.read(INPUTS)
    if args.mode == 'check':
        print(json.dumps(check(declared, b.read(RESULTS), numerics=args.recheck_numerics), indent=2))
        return
    b.require(declared == declaration() and not (b.ROOT/RESULTS).exists(), 'stale inputs or completed result exists')
    manifest = b.read(d.INPUTS)
    failures = native_failures(manifest, declared)
    with ProcessPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(run_probe, [(manifest, declared, p) for p in declared['probes']]))
    result = b.seal(dict(schema='p984d-cci-hardening-results-v1', inputs_digest=declared['record_digest'],
        neighborhood=rows, failures=failures, user_accepted=False, aggregate_closed=False))
    print(json.dumps(check(declared, result), indent=2))
    b.write_new(RESULTS, result)


if __name__ == '__main__':
    main()

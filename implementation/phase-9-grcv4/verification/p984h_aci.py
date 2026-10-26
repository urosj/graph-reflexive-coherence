"""A_CI .h preparation and source adapter; preparation never executes numerics."""
import argparse
from copy import deepcopy
from dataclasses import replace
import hashlib
import json
import lzma
import math
import subprocess
from unittest.mock import patch

import p984g_aci_native_successor as prior
from pygrc.models import grc_9_v4_lifecycle as native
from pygrc.models.grc_9_v4_expansion import aos_history_policy
from pygrc.models.grc_v4_geometry import GeometryStageInputs
from pygrc.models.grc_v4_state import GRCV4AuthoritativeState, FrozenJSONMap

base = prior.base
ROOT, BASE, HERE = base.ROOT, base.BASE, base.HERE
SELF = HERE + 'p984h_aci.py'
TEST = HERE + 'test_p984h_aci.py'
PLAN = BASE + 'P9-8.4h-ACIPlan.md'
INPUTS = BASE + 'P9-8.4h-ACIInputs.json'
SUMMARY = BASE + 'P9-8.4g-ACINativeSuccessorResults.json'
REVISION = '642bf731cad6eb34b26f0fb79e760d72b803f0af'
SUMMARY_DIGEST = '9da130df512401532e9d0379d45b83763139e564d8336164bf0f4ebf2051479c'
CHANGED = (
    'specs/grc-v4-numerical-policy.md',
    'src/pygrc/models/_grc_v4_matrix.py',
    'src/pygrc/models/grc_v4_certification.py',
    'src/pygrc/models/grc_v4_exact.py',
    'src/pygrc/models/grc_v4_linear.py',
    'src/pygrc/models/grc_v4_numerics.py',
)
CAPS = dict(source=600, event=1200, target_step=600, final_root=600)
require, seal, digest, q = base.require, base.seal, base.digest, base.q


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def accepted_source():
    """Authenticate historical bytes, never relabel them as a current execution."""
    summary = json.loads((ROOT / SUMMARY).read_text())
    require(summary == seal(summary) and summary['record_digest'] == SUMMARY_DIGEST
            and summary['native_prerequisites_complete'], 'historical summary')
    pin = next(c for c in summary['cases'] if (c['graph'], c['role']) == ('source', 'current'))
    require(sha(pin['path']) == pin['sha256'], 'historical archive bytes')
    record = json.loads(lzma.decompress((ROOT / pin['path']).read_bytes()))
    require(record == seal(record) and record['record_digest'] == pin['record_digest']
            and record['outcome'] == 'completed', 'historical execution seal')
    # Pinned committed objects, not an alternate implementation or runtime import.
    for path, expected in record['source_bindings'].items():
        data = subprocess.check_output(['git', 'show', REVISION + ':' + path], cwd=ROOT)
        require(hashlib.sha256(data).hexdigest() == expected, 'historical source: ' + path)
    changed = sorted(p for p, h in record['source_bindings'].items() if sha(p) != h)
    require(changed == list(CHANGED), 'unreviewed prerequisite source drift')
    return record


def seed():
    before, subject, backend = base.inputs_for('source', 'current')
    old = base.f.prior.read(base.f.prior.PREPARED)
    spec = old['specialization']
    state = native.GRC9V4ACIState(before, native.GRC9V4Specialization(
        FrozenJSONMap(spec['resolved']), FrozenJSONMap(spec['identity_payload'])))
    return state, subject, backend


def poststate(initial, result):
    """Reconstruct both C and W, preserving the separately bound reset."""
    require(digest(initial.inputs.to_payload()) == result['before_digest'], 'source before identity')
    after = replace(initial.inputs,
        current=GRCV4AuthoritativeState(tuple(result['after_C']), tuple(result['after_W_A']), None),
        time=result['after_time'], step_index=result['after_step_index'])
    require(digest(after.to_payload()) == result['after_digest'], 'source after identity')
    require(after.reset == initial.inputs.reset and after.time == initial.inputs.time + initial.inputs.dt
            and after.step_index == initial.inputs.step_index + 1, 'source chronology/reset')
    return replace(initial, inputs=replace(after, dt=0))


def fresh_request(post):
    """Declaration only: no trigger decision, event admission or publication."""
    old = base.f.prior.read(base.f.prior.PREPARED)
    request = deepcopy(old['event_request'])
    request.update(operation_id='p984h-aci-base', source_state_digest=post.scientific_digest,
        resource_distribution=[float(q(x)) for x in base.f.SHARES],
        history_policy=aos_history_policy(post.inputs.current, post.inputs.reset))
    return request


def canonical_hodge(rows):
    """Canonicalize JSON 0/1 versus 0.0/1.0 only if exact values survive."""
    require(len(rows) > 0 and all(len(r) == len(rows) for r in rows), 'square Hodge')
    converted = [[float(x) for x in row] for row in rows]
    require(all(math.isfinite(y) and q(x) == q(y)
                for row, out in zip(rows, converted) for x, y in zip(row, out)), 'lossy Hodge conversion')
    return converted


def canonical_input_payload(payload):
    """Comparison view only; never rewrite native state or historical hashes."""
    value = deepcopy(payload)
    value['H1_form'] = canonical_hodge(value['H1_form'])
    weights = value['reference']['reference_hodge']['edge_weights']
    for edge, x in weights.items():
        y = float(x)
        require(math.isfinite(y) and y > 0 and q(x) == q(y), 'lossy reference weight conversion')
        weights[edge] = y
    return value


def compare_source_result(actual, expected):
    # Includes full joint-point/H identities, certificate/domain, all primitive
    # fields, writer evidence, reset and clocks. This is parity, not a new proof.
    require(actual == expected, 'whole source result differs from accepted prerequisite')
    for root in actual['roots'].values():
        require(root['evaluations'] == 2 and root['native_stopping_matches_oracle']
                and root['selected_joint_point_digest'] and root['represented_geometry_digest'],
                'A_CI full-joint two-pass identity')


def source_adapter(progress):
    """For the separately authorized source run; current src/ executes unchanged."""
    expected = accepted_source()['result']
    with patch.object(base.oracle, 'check_retained', prior.history.check_staged):
        result = base.execute('source', 'current', progress)
    compare_source_result(result, expected)
    initial, _, _ = seed()
    post = poststate(initial, result)
    return dict(result=result, state=post.to_payload(), request=fresh_request(post))


def preflight():
    record = accepted_source()
    initial, _, _ = seed()
    payload = json.loads(json.dumps(initial.inputs.to_payload(), allow_nan=False))
    restored = GeometryStageInputs.from_payload(payload)
    require(digest(canonical_input_payload(restored.to_payload())) ==
            digest(canonical_input_payload(initial.inputs.to_payload())), 'input roundtrip identity')
    post = poststate(initial, record['result'])
    request = fresh_request(post)
    require(post.inputs.reset != post.inputs.current and post.inputs.reset == initial.inputs.reset,
            'distinct unchanged reset')
    require(request['history_policy'] != aos_history_policy(initial.inputs.current, initial.inputs.reset),
            'stale prebeat history declaration')
    compare_source_result(record['result'], deepcopy(record['result']))
    return dict(scope='retained_operand_rehearsal_not_native_execution',
        historical_record_digest=record['record_digest'],
        initial_digest=digest(initial.inputs.to_payload()), poststate_digest=post.scientific_digest,
        request_digest=digest(request), full_result_comparator=True,
        input_roundtrip=True, roundtrip_comparison='exact_binary64_H_and_reference_weights',
        distinct_reset_preserved=True, history_binding_refreshed=True,
        native_steps=0, native_events=0, native_roots=0)


def manifest():
    paths = set(prior.bindings()) | {SELF, TEST, PLAN, SUMMARY, prior.case_path('source', 'current')}
    return seal(dict(schema='p984h-aci-preparation-v1', family='A_CI',
        source_bindings={p: sha(p) for p in sorted(paths)},
        historical_revision=REVISION, historical_summary_digest=SUMMARY_DIGEST,
        reviewed_shared_changes=list(CHANGED), exact_backend='flint',
        numerical_policy='certified_arb_256_weighted_v1', caps_seconds=CAPS,
        planned=dict(source_steps=1, events=9, target_steps=36, final_roots=2),
        retention=dict(raw_compress_above_bytes=1000000, compressed_total_budget_bytes=20000000,
                       failure_policy='short_cause_record_no_failed_session_dumps'),
        consumers=['source_adapter', 'future_actual_target_and_covariance_checkers'],
        preflight=preflight(), user_accepted=False, aggregate_closed=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', 'check'))
    args = parser.parse_args()
    value = manifest()
    if args.action == 'prepare':
        with (ROOT / INPUTS).open('x') as stream:
            json.dump(value, stream, indent=2, allow_nan=False)
            stream.write('\n')
    else:
        require(json.loads((ROOT / INPUTS).read_text()) == value, 'preparation drift')
    print(json.dumps(dict(outcome='prepared', native_steps=0, native_events=0, native_roots=0)))


if __name__ == '__main__':
    main()

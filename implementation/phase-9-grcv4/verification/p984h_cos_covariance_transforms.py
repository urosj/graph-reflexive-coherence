"""Individual-transform continuation using the reviewed comparison successor.

Events still use p984h_cos_covariance.py and its unchanged declaration. Each
continuation manifest additionally pins its actual event. No combined evidence
is rewritten; no baseline, source prefix, or extra target horizon is replayed.
"""
import argparse
from copy import deepcopy
import json
import lzma
import signal
import time
from unittest.mock import patch
import p984h_cos_covariance_continuation as comparison

c = comparison.parent
KINDS = tuple(k for k in c.KINDS if k != 'combined')
SELF = c.HERE + 'p984h_cos_covariance_transforms.py'
TEST = c.HERE + 'test_p984h_cos_covariance_transforms.py'


def inputs(kind):
    c.require(kind in KINDS, 'select an individual transform')
    return c.BASE + f'P9-8.4h-COSCovariance-{kind}-ContinuationInputs.json'


def path(kind, role):
    inputs(kind)
    c.require(role in c.ROLES, 'select current or reset')
    return c.BASE + f'P9-8.4h-COSCovariance-{kind}-{role}-successor.json.xz'


def read(kind, role):
    return json.loads(lzma.decompress((c.ROOT / path(kind, role)).read_bytes()))


def manifest(kind):
    inputs(kind)
    old = c.native.oracle.old.read(c.INPUTS)
    c.require(old == c.manifest(), 'predecessor source drift')
    event = c.read(kind, 'event')
    c.check_record(event, old, kind, 'event')
    result = deepcopy(old)
    result.pop('record_digest')
    result.update(parent_manifest_digest=old['record_digest'], selected_transform=kind,
                  event_record_digest=event['record_digest'],
                  comparison_successor=comparison.SELF, numerical_law_changed=False,
                  parent_event_reexecuted=False)
    for name in (SELF, TEST, comparison.SELF, comparison.TEST, c.INPUTS, c.path(kind, 'event')):
        result['source_bindings'][name] = c.native.oracle.sha(name)
    return c.seal(result)


def check(record, declaration, kind, role):
    path(kind, role)
    c.require(declaration == manifest(kind), 'individual continuation source drift')
    c.require(record['execution']['event_record_digest'] == declaration['event_record_digest'],
              'individual continuation event binding')
    with patch.object(c, 'compare_step', comparison.compare_step):
        c.check_record(record, declaration, kind, role)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', 'run', 'check'))
    parser.add_argument('--kind', choices=KINDS, required=True)
    parser.add_argument('--role', choices=c.ROLES)
    args = parser.parse_args()
    with c.native.oracle.exact_backend(c.native.oracle.ExactBackend.FLINT), \
            c.native.oracle.numerical_policy(c.native.oracle.NumericalPolicy.CERTIFIED_ARB_256):
        if args.action == 'prepare':
            c.native.oracle.old.write_new(inputs(args.kind), manifest(args.kind))
            return
        destination = c.ROOT / path(args.kind, args.role)
        declaration = c.native.oracle.old.read(inputs(args.kind))
        c.require(declaration == manifest(args.kind), 'individual continuation source drift')
        if args.action == 'check':
            check(read(args.kind, args.role), declaration, args.kind, args.role)
            print('retained individual covariance check passed; no native replay')
            return
        c.require(not destination.exists(), 'refuse overwrite')

        def expired(*_):
            raise TimeoutError('unchanged 600-second cap; no fallback')

        signal.signal(signal.SIGALRM, expired)
        signal.alarm(declaration['step_cap_seconds'])
        started = time.monotonic()
        try:
            with c.native.matrix_operation(), patch.object(c, 'compare_step', comparison.compare_step):
                execution = c.execute_step(args.kind, args.role)
        finally:
            signal.alarm(0)
        elapsed = time.monotonic() - started
        c.require(elapsed <= declaration['step_cap_seconds'], 'step cap exceeded')
        record = c.seal(dict(schema='p984h-cos-covariance-results-v1',
            manifest_digest=declaration['record_digest'], kind=args.kind, segment=args.role,
            outcome='completed', execution=execution, elapsed_seconds=elapsed,
            user_accepted=False, aggregate_closed=False))
        check(record, declaration, args.kind, args.role)
        packed = lzma.compress(json.dumps(record, separators=(',', ':'), allow_nan=False).encode() + b'\n')
        with destination.open('xb') as stream:
            stream.write(packed)
        c.require(len(packed) <= 2000000, 'complete record retained; compressed budget exceeded')
        print(json.dumps(dict(kind=args.kind, role=args.role, seconds=elapsed,
            compressed_bytes=len(packed), errors=execution['covariance_errors'],
            minimum_resource=execution['observation']['minimum_resource'])), flush=True)


if __name__ == '__main__':
    main()

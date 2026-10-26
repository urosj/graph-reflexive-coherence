"""One changing-resource source step, compared to the retained second beat.

This repeats accepted prefix coverage; it adds no event/target campaign credit.
The original first beat is restored from evidence, not numerically rerun.
"""
import json
import lzma
import os
import signal
import time

import p984h_cos_dyadic_rounding as read_probe

run = read_probe.run
SELF = run.HERE + 'p984h_cos_dyadic_step.py'
OUTPUT = run.BASE + 'P9-8.4h-COSDyadicStep.json.xz'


def main():
    run.require(not (run.ROOT / OUTPUT).exists(), 'refuse overwrite')
    run.require(all(os.environ.get(k) == '1' for k in
                    ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS')), 'single thread')
    with run.oracle.exact_backend(run.oracle.ExactBackend.FLINT), run.oracle.numerical_policy(run.oracle.NumericalPolicy.CERTIFIED_ARB_256):
        read = json.loads(lzma.decompress((run.ROOT/read_probe.OUTPUT).read_bytes()))
        run.require(read == run.seal(read) and read['baseline_parity'], 'read prerequisite')
        for name, sha in read['source_bindings'].items():
            run.require(run.oracle.sha(name) == sha, 'read source drift: '+name)
        saved = run.read('prefix')
        run.require(saved == run.seal(saved) and saved['outcome'] == 'completed', 'prefix seal')
        expected = saved['execution']['steps'][1]
        _, seed = run.oracle.second_source_input()
        before = seed.inputs
        run.require(run.digest(before.to_payload()) == expected['before_digest'], 'same changing-step input')
        bindings = {p: run.oracle.sha(p) for p in {SELF, read_probe.OUTPUT, *read['source_bindings']}}
        def expired(*_):
            raise TimeoutError('600-second changing-step cap; no fallback')
        signal.signal(signal.SIGALRM, expired)
        signal.alarm(600)
        started = time.perf_counter()
        with run.matrix_operation():
            actual, after = run.observe_step(before)
        elapsed = time.perf_counter()-started
        signal.alarm(0)
        # Native stage values, split certificate, resource, chronology, reset,
        # charge and complete poststate digest must all match; not tolerances.
        excluded = {'seconds', 'dense_errors', 'trigger'}
        wanted = {k:v for k,v in expected.items() if k not in excluded}
        observed = {k:v for k,v in actual.items() if k not in excluded}
        run.require(observed == wanted, 'whole changing-step parity')
        run.require(before.current.C != after.current.C, 'not a changing input')
        run.require(bindings == {p:run.oracle.sha(p) for p in bindings}, 'source changed during step')
        record = run.seal(dict(schema='p984h-cos-dyadic-step-v1',source_bindings=bindings,
            prefix_record_digest=saved['record_digest'],compared_step_index=1,
            whole_step_parity=True,compared_fields=sorted(wanted),scientific_view_digest=run.digest(observed),
            before_digest=actual['before_digest'],after_digest=actual['after_digest'],
            baseline_step_seconds=expected['seconds'],elapsed_seconds=elapsed,
            current_resources_changed=True,reset_unchanged=True,
            dense_errors=actual['dense_errors'],minimum_resource=actual['minimum_resource'],
            native_steps=1,native_events=0,new_campaign_steps=0,
            scope='repeat_source_second_beat_not_event_or_target_continuation',
            numerical_policy='certified_arb_256_weighted_v1',backend='flint'))
        with (run.ROOT/OUTPUT).open('xb') as stream:
            stream.write(lzma.compress(json.dumps(record,indent=2,allow_nan=False).encode()+b'\n'))
        print(json.dumps(dict(elapsed_seconds=elapsed,whole_step_parity=True,
                             baseline_step_seconds=expected['seconds'])))


if __name__ == '__main__':
    main()

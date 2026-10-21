"""Explicit dyadic output proof: isolated loop comparison and one cold OS read."""
from dataclasses import replace
import json
import lzma
import os
import random
import signal
import time

import p984h_cos_kernel_profile as kernel

run = kernel.run
SELF = run.HERE + 'p984h_cos_dyadic_rounding.py'
OUTPUT = run.BASE + 'P9-8.4h-COSDyadicRounding.json.xz'


def micro():
    """Synthetic kernel timing, not a physical fixture or an admission claim."""
    import flint
    cert = kernel.probe.cert
    rng = random.Random(984)
    with flint.ctx.workprec(256):
        balls = [flint.arb(flint.fmpq(rng.randrange(-10**12, 10**12), rng.randrange(1, 10**12)))
                 for _ in range(12000)]
        start = time.perf_counter()
        endpoints = [(b.lower().fmpq(), b.upper().fmpq()) for b in balls]
        extract = time.perf_counter()-start
        start = time.perf_counter()
        candidates = [(float(a), float(b)) for a, b in endpoints]
        conversion = time.perf_counter()-start
        start = time.perf_counter()
        cells = {}
        old = [cert._round_interval(a, b, cells) for a, b in endpoints]
        rational = time.perf_counter()-start
        start = time.perf_counter()
        new = [cert._round_ball(b) for b in balls]
        dyadic = time.perf_counter()-start
        run.require(new == old and all(a == b == v for (a, b), v in zip(candidates, new)), 'micro parity')
        return dict(scope='synthetic_kernel_only', count=len(balls), seed=984,
                    rational_extraction_seconds=extract, endpoint_float_seconds=conversion,
                    rational_rounding_seconds=rational, dyadic_complete_seconds=dyadic,
                    full_equality=True, output_digest=run.digest(new))


def main():
    run.require(not (run.ROOT / OUTPUT).exists(), 'refuse overwrite')
    run.require(all(os.environ.get(k) == '1' for k in
                    ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS')), 'single thread')
    baseline = json.loads(lzma.decompress((run.ROOT / kernel.probe.OUTPUT).read_bytes()))
    run.require(baseline == run.seal(baseline), 'baseline seal')
    with run.oracle.exact_backend(run.oracle.ExactBackend.FLINT), run.oracle.numerical_policy(run.oracle.NumericalPolicy.CERTIFIED_ARB_256):
        saved = run.read('prefix')
        run.require(saved == run.seal(saved) and saved['record_digest'] == baseline['prefix_digest'], 'prefix')
        before = replace(run.state(saved['execution']['state']).inputs, dt=1.)
        run.require(run.digest(before.to_payload()) == baseline['input_digest'], 'same input')
        bindings = {p: run.oracle.sha(p) for p in
                    {SELF, kernel.SELF, kernel.previous.SELF, kernel.probe.SELF,
                     kernel.probe.OUTPUT, 'tests/models/test_grc_v4_dyadic_rounding.py',
                     *baseline['source_bindings']}}
        def expired(*_):
            raise TimeoutError('600-second dyadic read cap; no fallback')
        signal.signal(signal.SIGALRM, expired)
        signal.alarm(600)
        isolated = micro()
        timers = kernel.Timers()
        started = time.perf_counter()
        with kernel.timing(timers), run.matrix_operation():
            passed = kernel.probe.CandidateCOSPass(before)
        elapsed = time.perf_counter() - started
        signal.alarm(0)
        observed = kernel.previous.view(passed)
        run.require(observed == {k: baseline[k] for k in kernel.previous.FIELDS}, 'full read parity')
        run.require(bindings == {p: run.oracle.sha(p) for p in bindings}, 'source changed during run')
        record = run.seal(dict(schema='p984h-cos-dyadic-rounding-v1', source_bindings=bindings,
            baseline_record_digest=baseline['record_digest'], input_digest=baseline['input_digest'],
            scientific_view_digest=run.digest(observed), baseline_parity=True,
            backend='flint', numerical_policy='certified_arb_256_weighted_v1',
            scope='fresh_source_current_read_not_changing_large_step_or_event',
            micro=isolated, elapsed_seconds=elapsed, counters=dict(timers.counters),
            native_steps=0, native_events=0))
        with (run.ROOT / OUTPUT).open('xb') as stream:
            stream.write(lzma.compress(json.dumps(record, indent=2, allow_nan=False).encode()+b'\n'))
        print(json.dumps(dict(elapsed_seconds=elapsed, baseline_parity=True, micro=isolated)))


if __name__ == '__main__':
    main()

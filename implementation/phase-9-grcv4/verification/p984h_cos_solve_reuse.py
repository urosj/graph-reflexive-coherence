"""Bounded cold/warm OS-read parity against the retained pre-change profile."""
from dataclasses import replace
import json
import lzma
import os
import signal
import time

import p984h_cos_read_profile as probe
from pygrc.models.grc_v4_numerics import matrix_operation

run = probe.run
SELF = run.HERE + 'p984h_cos_solve_reuse.py'
OUTPUT = run.BASE + 'P9-8.4h-COSSolveReuse.json.xz'
FIELDS = ('predictor', 'corrector', 'predictor_identity', 'corrector_identity',
          'split_certificate', 'split_values_digest')


def view(passed):
    return dict(predictor=run.capture.point(passed.predictor),
        corrector=run.capture.point(passed.corrector),
        predictor_identity=passed.predictor.identity, corrector_identity=passed.corrector.identity,
        split_certificate=passed.residual.execution_certificate.to_dict(),
        split_values_digest=run.digest(passed.residual.exact_values))


def main():
    run.require(not (run.ROOT / OUTPUT).exists(), 'refuse overwrite')
    run.require(all(os.environ.get(k)=='1' for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS')), 'single thread')
    baseline=json.loads(lzma.decompress((run.ROOT/probe.OUTPUT).read_bytes()))
    run.require(baseline==run.seal(baseline), 'baseline identity')
    with run.oracle.exact_backend(run.oracle.ExactBackend.FLINT),run.oracle.numerical_policy(run.oracle.NumericalPolicy.CERTIFIED_ARB_256):
        saved=run.read('prefix')
        run.require(saved==run.seal(saved) and saved['record_digest']==baseline['prefix_digest'], 'prefix identity')
        before=replace(run.state(saved['execution']['state']).inputs,dt=1.)
        run.require(run.digest(before.to_payload())==baseline['input_digest'], 'same read input')
        bindings={p:run.oracle.sha(p) for p in {SELF,probe.SELF,probe.OUTPUT,*baseline['source_bindings']}}
        expected={k:baseline[k] for k in FIELDS}
        records=[]
        def expired(*_):raise TimeoutError('600-second diagnostic cap; no fallback')
        signal.signal(signal.SIGALRM,expired);signal.alarm(600)
        with matrix_operation():
            for name in ('cold','warm'):
                started=time.perf_counter()
                with probe.timing() as times:
                    passed=probe.CandidateCOSPass(before)
                elapsed=time.perf_counter()-started
                observed=view(passed)
                run.require(observed==expected,'full read differs from pre-change baseline')
                row=dict(name=name,elapsed_seconds=elapsed,counters=dict(times),
                    scientific_view_digest=run.digest(observed),baseline_parity=True)
                records.append(row)
                print(json.dumps(row),flush=True)
        signal.alarm(0)
        run.require(bindings=={p:run.oracle.sha(p) for p in bindings},'source changed during probe')
        result=run.seal(dict(schema='p984h-cos-solve-reuse-v1',source_bindings=bindings,
            baseline_record_digest=baseline['record_digest'],input_digest=baseline['input_digest'],
            backend='flint',numerical_policy='certified_arb_256_weighted_v1',matrix_reuse='automatic',
            native_events=0,native_steps=0,scope='same_source_current_read_cold_and_warm_not_event',
            baseline_elapsed_seconds=baseline['elapsed_seconds'],records=records))
        raw=json.dumps(result,indent=2,allow_nan=False).encode()+b'\n'
        run.require(len(raw)<1000000,'retention budget')
        with (run.ROOT/OUTPUT).open('xb') as stream:stream.write(lzma.compress(raw))


if __name__=='__main__':main()

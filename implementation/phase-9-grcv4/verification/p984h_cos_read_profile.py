"""Bounded timing of one real OS read; instrumentation never changes results."""
import argparse
from collections import defaultdict
from contextlib import ExitStack, contextmanager
from dataclasses import replace
from functools import wraps
import json
import lzma
import os
import signal
import sys
import time
from unittest.mock import patch

import p984h_cos_native as run
from pygrc.models import grc_v4_codec as codec, grc_v4_geometry as geometry
from pygrc.models import grc_v4_certification as cert, grc_v4_numerics as num
from pygrc.models import grc_v4_candidate_c as candidate
from pygrc.models import _grc_v4_matrix as matrix, _grc_v4_matrix_flint as fm
from pygrc.models.grc_v4_realizations import CandidateCOSPass

SELF=run.HERE+'p984h_cos_read_profile.py'
OUTPUT=run.BASE+'P9-8.4h-COSReadProfile.json.xz'


@contextmanager
def timing():
    """Time selected boundaries, including imported aliases; no per-call profiler.

    Exclusive seconds subtract only other instrumented boundaries. Thus their
    sum is disjoint, but includes uninstrumented work beneath each boundary.
    """
    targets=[(codec,n) for n in ('_validation_result','json_value','_canonical_validated_bytes','_read_contract_schema')]
    targets += [(geometry,'_capture_stage_inputs'),(geometry,'_require_positive_definite')]
    targets += [(cert,n) for n in ('rounded_solve','condition_bound','positive_definite')]
    targets += [(fm,'matmul'),(matrix,'inertia'),(num,'residual_pass')]
    counters=defaultdict(lambda:dict(calls=0,inclusive_seconds=0.,exclusive_seconds=0.))
    stack=[]
    def wrapper(fn,label):
        @wraps(fn)
        def call(*args,**kwargs):
            entry=[time.perf_counter(),0.];stack.append(entry)
            try:return fn(*args,**kwargs)
            finally:
                elapsed=time.perf_counter()-entry[0];stack.pop()
                item=counters[label];item['calls']+=1;item['inclusive_seconds']+=elapsed
                item['exclusive_seconds']+=elapsed-entry[1]
                if stack:stack[-1][1]+=elapsed
        return call
    originals={id(getattr(m,n)):(getattr(m,n),wrapper(getattr(m,n),m.__name__.split('.')[-1]+'.'+n)) for m,n in targets}
    with ExitStack() as patches:
        for name,module in list(sys.modules.items()):
            if not name.startswith('pygrc.models.') or module is None:continue
            for attr,value in list(vars(module).items()):
                pair=originals.get(id(value))
                if pair is not None and value is pair[0]:patches.enter_context(patch.object(module,attr,pair[1]))
        yield counters


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.parse_args()
    run.require(not (run.ROOT/OUTPUT).exists(),'refuse overwrite')
    run.require(all(os.environ.get(k)=='1' for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS')),'single thread required')
    with run.oracle.exact_backend(run.oracle.ExactBackend.FLINT),run.oracle.numerical_policy(run.oracle.NumericalPolicy.CERTIFIED_ARB_256):
        saved=run.read('prefix');run.require(saved==run.seal(saved) and saved['outcome']=='completed','prefix identity')
        seed=run.state(saved['execution']['state']);before=replace(seed.inputs,dt=1.)
        bindings={p:run.oracle.sha(p) for p in {SELF,*run.oracle.old.read(run.INPUTS)['source_bindings']}}
        def expired(*_):raise TimeoutError('600-second diagnostic cap; no fallback')
        signal.signal(signal.SIGALRM,expired);signal.alarm(600)
        started=time.perf_counter()
        with timing() as times,run.matrix_operation():
            passed=CandidateCOSPass(before)
        elapsed=time.perf_counter()-started;signal.alarm(0)
        result=run.seal(dict(schema='p984h-cos-read-profile-v1',source_bindings=bindings,
            prefix_digest=saved['record_digest'],input_digest=run.digest(before.to_payload()),
            elapsed_seconds=elapsed,counters=dict(times),
            uninstrumented_seconds=elapsed-sum(t['exclusive_seconds'] for t in times.values()),
            predictor=run.capture.point(passed.predictor),corrector=run.capture.point(passed.corrector),
            predictor_identity=passed.predictor.identity,corrector_identity=passed.corrector.identity,
            split_certificate=passed.residual.execution_certificate.to_dict(),
            split_values_digest=run.digest(passed.residual.exact_values),
            numerical_policy='certified_arb_256_weighted_v1',backend='flint',
            native_events=0,native_steps=0,scope='one_source_current_OS_read_not_full_event',
            timer_semantics='wall_clock_disjoint_exclusive_instrumented_boundaries'))
        raw=json.dumps(result,indent=2,allow_nan=False).encode()+b'\n'
        run.require(len(raw)<1000000,'diagnostic retention budget')
        with (run.ROOT/OUTPUT).open('xb') as f:f.write(lzma.compress(raw))
        print(json.dumps(dict(elapsed_seconds=elapsed,counters=dict(times),uninstrumented_seconds=result['uninstrumented_seconds']),indent=2))


if __name__=='__main__':main()

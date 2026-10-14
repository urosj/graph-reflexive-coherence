"""Sparse-sampled C_CI native admission; no per-call tracer or equation patch."""
import argparse
import hashlib
import json
import multiprocessing as mp
import os
import signal
import time
import traceback
import p984g_cci_native as setup

ROOT,BASE,HERE=setup.ROOT,setup.BASE,setup.HERE
SELF=HERE+'p984g_cci_native_admission.py'
CERTIFICATE=BASE+'P9-8.4g-CCINativeCertificate.json'


def bindings():
    return {**setup.bindings(),SELF:hashlib.sha256((ROOT/SELF).read_bytes()).hexdigest()}


def worker(pipe):
    from pygrc.models.grc_v4_numerics import exact_backend,ExactBackend,numerical_policy,NumericalPolicy,matrix_operation
    from pygrc.models.grc_v4_ci import CIContractionCertificate
    start=time.monotonic()
    def sample(signum, frame):
        pipe.send(('stack',dict(seconds=time.monotonic()-start,
            frames=[dict(file=f.filename.split('/graph-reflexive-coherence/')[-1],line=f.lineno,function=f.name)
                    for f in traceback.extract_stack(frame)[-8:]])))
    signal.signal(signal.SIGUSR1,sample)
    try:
        with exact_backend(ExactBackend.FLINT),numerical_policy(NumericalPolicy.CERTIFIED_ARB_256),matrix_operation():
            inputs,_,_=setup.inputs_for('source','current')
            pipe.send(('progress',dict(stage='materialized',seconds=time.monotonic()-start)))
            certificate=CIContractionCertificate(inputs)
            pipe.send(('result',dict(certificate=certificate.bounds.to_dict(),seconds=time.monotonic()-start)))
    except Exception as error:
        pipe.send(('error',dict(type=type(error).__name__,message=str(error),
            disposition=getattr(error,'disposition',None))))
    finally:pipe.close()


def run():
    setup.require(not (ROOT/CERTIFICATE).exists(),'no overwrite')
    setup.require(os.environ.get('OPENBLAS_NUM_THREADS')=='1' and os.environ.get('OMP_NUM_THREADS')=='1','single thread')
    bound=bindings();context=mp.get_context('spawn');receive,send=context.Pipe(False)
    process=context.Process(target=worker,args=(send,));start=time.monotonic();process.start();send.close()
    events=[];last_sample=0
    while process.is_alive() and time.monotonic()-start<180:
        if receive.poll(.2):
            try:kind,value=receive.recv()
            except EOFError:break
            events.append(dict(kind=kind,value=value))
            if kind in ('progress','error','stack'):print(json.dumps(events[-1]),flush=True)
        if time.monotonic()-start-last_sample>=30:
            os.kill(process.pid,signal.SIGUSR1);last_sample=time.monotonic()-start
    timed_out=process.is_alive() and time.monotonic()-start>=180
    if timed_out:process.terminate()
    process.join(5)
    if process.is_alive():process.kill();process.join()
    while receive.poll():
        try:kind,value=receive.recv();events.append(dict(kind=kind,value=value))
        except EOFError:break
    setup.require(bound==bindings(),'source drift during run')
    record=setup.seal(dict(schema='p984g-cci-native-certificate-v1',source_bindings=bound,events=events,
        cap_seconds=180,seconds=time.monotonic()-start,timed_out=timed_out,exit_code=process.exitcode,
        outcome='completed' if any(e['kind']=='result' for e in events) and process.exitcode==0 else 'incomplete',
        numerical_policy='certified_arb_256_weighted_v1',exact_backend='flint',
        native_roots=0,native_steps=0,native_events=0,ready_for_8_4h=False))
    raw=json.dumps(record,indent=2)+'\n';setup.require(len(raw.encode())<1000000,'compression required')
    (ROOT/CERTIFICATE).write_text(raw)
    print(json.dumps({k:record[k] for k in ('outcome','seconds','timed_out','exit_code')}))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=['certificate']);parser.parse_args();run()

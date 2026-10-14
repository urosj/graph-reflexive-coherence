"""Bounded native C_CI bridge on the explicitly declared feasibility companion."""
import argparse
from dataclasses import replace
import hashlib
import json
import multiprocessing as mp
import os
import time
import traceback

import p984g_cci_feasibility as feasible

ROOT, BASE, HERE = feasible.ROOT, feasible.BASE, feasible.HERE
SELF = HERE + 'p984g_cci_native.py'
PLAN = BASE + 'P9-8.4g-CCINativePlan.md'
PROBE = BASE + 'P9-8.4g-CCINativeProbe.json'
require, read, seal = feasible.require, feasible.read, feasible.seal


def bindings():
    names=[SELF,PLAN,feasible.SELF,feasible.RESULTS,feasible.prior.PREPARED,
           HERE+'prepare_p983_all_realizations.py']
    names += [str(p.relative_to(ROOT)) for p in (ROOT/'src/pygrc/models').glob('*grc*v4*.py')]
    return {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(set(names))}


def inputs_for(graph, role):
    p=feasible.prepared
    old,target,_,declaration=feasible.companion(feasible.DEFICIT)
    subject=old['source'] if graph=='source' else target
    port=p.GRC9V4PortGraph.from_envelope(subject['graph'])
    profile=p.GRCV4Profile.from_canonical_bytes(p.canonical_json_bytes(subject['profile']))
    spec=p.native.GRC9V4Specialization(p.FrozenJSONMap(old['specialization']['resolved']),
                                     p.FrozenJSONMap(old['specialization']['identity_payload']))
    roles={r:p.authority(subject['roles'][r],len(port.edges)) for r in ('current','reset')}
    state=p.make_state(port,profile,spec,roles,'C_CI')
    inputs=replace(state.inputs,current=getattr(state.inputs,role),stage='pre_read',
                   dt=old['selected_configuration']['ordinary_dt'])
    return inputs,subject,declaration


def worker(pipe):
    import cProfile
    import pstats
    import signal
    import sys
    from pygrc.models.grc_v4_numerics import exact_backend,ExactBackend,numerical_policy,NumericalPolicy,matrix_operation
    from pygrc.models.grc_v4_ci import CandidateCIRoot
    profiler=cProfile.Profile();started=time.monotonic()
    def snapshot(signum, frame):
        pipe.send(('stack',dict(seconds=time.monotonic()-started,
            frames=[dict(file=f.filename.split('/graph-reflexive-coherence/')[-1],line=f.lineno,function=f.name)
                    for f in traceback.extract_stack(frame)[-8:]])))
    signal.signal(signal.SIGUSR1,snapshot)
    try:
        with exact_backend(ExactBackend.FLINT),numerical_policy(NumericalPolicy.CERTIFIED_ARB_256),matrix_operation():
            inputs,_,declaration=inputs_for('source','current')
            pipe.send(('progress',dict(stage='materialized',seconds=time.monotonic()-started)))
            # Call tracing reports native stage entry/exit only; it substitutes
            # no equation, certificate or result.
            names={'__post_init__','_c_read_bounds','_analytic_residual'}
            def trace(frame,event,arg):
                if frame.f_code.co_filename.endswith('/grc_v4_ci.py') and frame.f_code.co_name in names:
                    if event in ('call','return'):
                        owner=type(frame.f_locals.get('self')).__name__
                        pipe.send(('progress',dict(stage=owner+'.'+frame.f_code.co_name,event=event,
                                                  seconds=time.monotonic()-started)))
                return None
            profiler.enable();sys.settrace(trace)
            root=CandidateCIRoot(inputs)
            profiler.disable();sys.settrace(None)
            pipe.send(('result',dict(evaluations=root.evaluations,root_identity=root.identity,
                certificate=root.certificate.bounds.to_dict(),residual_squared=str(root.selected.residual_squared),
                current=list(root.current.values),declaration=declaration)))
    except Exception as exc:
        profiler.disable();sys.settrace(None)
        pipe.send(('error',dict(type=type(exc).__name__,message=str(exc),disposition=getattr(exc,'disposition',None))))
    finally:
        rows=pstats.Stats(profiler).stats
        top=sorted(rows.items(),key=lambda x:x[1][3],reverse=True)[:15]
        pipe.send(('profile',[dict(file=k[0].split('/graph-reflexive-coherence/')[-1],line=k[1],function=k[2],
            calls=v[1],own_seconds=v[2],cumulative_seconds=v[3]) for k,v in top]))
        pipe.close()


def probe():
    require(not (ROOT/PROBE).exists(),'no probe overwrite')
    require(os.environ.get('OPENBLAS_NUM_THREADS')=='1' and os.environ.get('OMP_NUM_THREADS')=='1',
            'single-threaded worker required')
    feasible.check_retained()
    bound=bindings();ctx=mp.get_context('spawn');receive,send=ctx.Pipe(False)
    process=ctx.Process(target=worker,args=(send,));start=time.monotonic();process.start();send.close()
    events=[];last_signal=0
    while process.is_alive() and time.monotonic()-start<180:
        if receive.poll(.2):
            try:kind,value=receive.recv()
            except EOFError:break
            events.append(dict(kind=kind,value=value))
            if kind in ('progress','error'):print(json.dumps(events[-1]),flush=True)
        elapsed=time.monotonic()-start
        if elapsed-last_signal>=30:
            import signal
            os.kill(process.pid,signal.SIGUSR1);last_signal=elapsed
    timed_out=process.is_alive() and time.monotonic()-start>=180
    if timed_out:process.terminate()
    process.join(timeout=5)
    if process.is_alive():process.kill();process.join()
    while receive.poll():
        try:kind,value=receive.recv();events.append(dict(kind=kind,value=value))
        except EOFError:break
    require(bound==bindings(),'source changed during probe')
    value=seal(dict(schema='p984g-cci-native-probe-v1',source_bindings=bound,events=events,
        seconds=time.monotonic()-start,cap_seconds=180,timed_out=timed_out,exit_code=process.exitcode,
        outcome='completed' if any(e['kind']=='result' for e in events) and process.exitcode==0 else 'incomplete',
        exact_backend='flint',numerical_policy='certified_arb_256_weighted_v1',
        native_steps=0,native_events=0,ready_for_8_4h=False))
    raw=json.dumps(value,indent=2)+'\n';require(len(raw.encode())<1000000,'compression required')
    (ROOT/PROBE).write_text(raw);print(json.dumps({k:value[k] for k in ('outcome','seconds','timed_out','exit_code')}))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=['probe']);parser.parse_args()
    probe()

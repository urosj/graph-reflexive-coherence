"""One bounded native composite-root timing probe, with no campaign credit."""
import argparse
from contextlib import ExitStack
import json
import resource
import time
from unittest.mock import patch

import p984g_ccipc_companion as companion
import p9_ccipc_compute as compute
import p9_ccipc_capture as capture
import p984h_apc as processes
from p984h_cpc import measure_reuse
from pygrc.models import grc_v4_ci as ci
from pygrc.models import grc_v4_codec as codec
from pygrc.models import grc_v4_candidate_c as candidate

b=compute.b
SELF=b.HERE+'p9_ccipc_large_profile.py'
RESULT=b.BASE+'P9-CCIPC-LargeRootProfile.json.xz'


def child(pipe):
    started=time.monotonic();timings={}
    def measured(owner,name,label,notify=False):
        original=getattr(owner,name)
        def call(*args,**kwargs):
            start=time.monotonic()
            if notify:pipe.send(('progress',label+' entered'))
            try:return original(*args,**kwargs)
            finally:
                row=timings.setdefault(label,dict(calls=0,inclusive_seconds=0.0))
                row['calls']+=1;row['inclusive_seconds']+=time.monotonic()-start
                if notify:pipe.send(('progress',label+' finished'))
        return patch.object(owner,name,call)
    try:
        with compute.worker() as policy,measure_reuse() as cache,ExitStack() as stack:
            for owner,name,label,notify in (
                (ci.CIContractionCertificate,'__post_init__','domain_certificate',True),
                (ci.CITrial,'__post_init__','joint_trial',True),
                (ci,'_analytic_residual','analytic_joint_residual',True),
                (ci,'_point','point',False),
                (candidate.CandidateCCurrent,'__post_init__','candidate_current',False),
                (codec,'canonical_json_bytes','codec_canonical_entry',False)):
                stack.enter_context(measured(owner,name,label,notify))
            declaration=companion.g.pc.storage.read(companion.INPUTS)['adjusted']
            subject=declaration['source'];p=companion.mechanical
            graph=p.GRC9V4PortGraph.from_envelope(subject['graph'])
            profile=p.GRCV4Profile.from_canonical_bytes(p.canonical_json_bytes(subject['profile']))
            spec=declaration['specialization']
            specialization=p.native.GRC9V4Specialization(p.FrozenJSONMap(spec['resolved']),p.FrozenJSONMap(spec['identity_payload']))
            roles={role:p.authority(value,len(graph.edges)) for role,value in subject['roles'].items()}
            state=p.make_state(graph,profile,specialization,roles,'C_CI_PC')
            prepared_seconds=time.monotonic()-started;pipe.send(('progress','prepared native source'))
            begin=time.monotonic();root=ci.CandidateCIRoot(state.inputs);root_seconds=time.monotonic()-begin
            pipe.send(('progress','native root completed; retaining capture'))
            captured=compute.r.capture_root(root)
            inputs=state.inputs.to_payload()
        value=dict(inputs=inputs,root=captured,prepared_seconds=prepared_seconds,
            root_seconds=root_seconds,evaluations=root.evaluations,stage_timings=timings,
            timing_scope='inclusive_nested_entry_times_do_not_sum',cache=cache,policy=policy,
            max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        pipe.send(('result',capture.portable(value)))
    except Exception as exc:
        pipe.send(('error',dict(type=type(exc).__name__,message=str(exc),timings=timings)))
    finally:pipe.close()


def run():
    preflight=companion.g.pc.storage.read(compute.PREFLIGHT)
    b.check_digest(preflight);b.check_bindings(preflight['source_bindings'])
    b.require(preflight['outcome']=='passed' and preflight['small_root_byte_parity'],'compute preflight required')
    declaration=companion.g.pc.storage.read(companion.INPUTS)
    feasibility=companion.g.pc.storage.read(companion.RESULTS)
    b.check_digest(feasibility);b.check_bindings(declaration['source_bindings'])
    b.require(feasibility['manifest_digest']==declaration['record_digest'] and feasibility['ready_for_native'],
              'independent companion feasibility required')
    paths={SELF,capture.SELF,compute.SELF,compute.PREFLIGHT,companion.SELF,companion.INPUTS,companion.RESULTS,processes.SELF}
    paths|={ref['path'] for ref in preflight['source_bindings']}
    refs=b.bind(paths);start=time.monotonic()
    try:
        execution,seconds=processes.capped(child,(),compute.LARGE_CAP_SECONDS)
        outcome='completed';error=None
    except Exception as exc:
        execution=None;seconds=time.monotonic()-start;outcome='incomplete'
        error=dict(type=type(exc).__name__,message=str(exc))
    b.check_bindings(refs)
    value=b.seal(dict(schema='p9-ccipc-large-root-profile-v1',family='C_CI_PC',outcome=outcome,
        source_bindings=refs,cap_seconds=compute.LARGE_CAP_SECONDS,seconds=seconds,
        execution=execution,error=error,native_steps=0,native_events=0,campaign_credit=False,
        user_accepted=False,aggregate_closed=False))
    companion.g.pc.storage.save(RESULT,value)
    print(json.dumps(dict(outcome=outcome,seconds=seconds,root_seconds=execution['root_seconds'] if execution else None)),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=('run',))
    parser.parse_args();run()

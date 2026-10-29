"""Reuse only the verification harness's unchanged initial operation owner.

The stale request must leave its publication pointer and checkpoint unchanged.
The subsequent event then uses that very owner. Source/target admission and
fresh replay still execute all their roots; no root result is memoized here.
"""
from contextlib import contextmanager
import time
from unittest.mock import patch

import p984h_ccipc as n

b=n.b
SELF=b.HERE+'p9_ccipc_event_reuse.py'
PREFLIGHT=b.BASE+'P9-CCIPC-EventHarnessPreflight.json'


@contextmanager
def initial_owner(seed):
    original=n.native.GRC9V4CCIPCOperation
    cached=None;checkpoint=None;publication=None
    stats=dict(constructor_requests=0,native_initial_constructors=0,unchanged_owner_hits=0,
        fresh_replays=0,root_results_reused=False)
    class Factory:
        def __new__(cls,incoming):
            nonlocal cached,checkpoint,publication
            b.require(incoming is seed,'initial owner operand identity changed')
            stats['constructor_requests']+=1
            if cached is None:
                cached=original(incoming)
                checkpoint=cached.checkpoint();publication=cached._published
                stats['native_initial_constructors']+=1
                return cached
            b.require(stats['constructor_requests']==2 and cached._published is publication
                and cached.state==seed and cached.checkpoint()==checkpoint,
                'initial owner publication changed before harness reuse')
            stats['unchanged_owner_hits']+=1
            return cached

        @staticmethod
        def replay(raw):
            stats['fresh_replays']+=1
            return original.replay(raw)

    try:
        with patch.object(n.native,'GRC9V4CCIPCOperation',Factory):yield stats
    finally:
        cached=None;checkpoint=None;publication=None


def event(seed,case):
    with initial_owner(seed) as stats:execution=n.event(seed,case)
    b.require(stats==dict(constructor_requests=2,native_initial_constructors=1,
        unchanged_owner_hits=1,fresh_replays=1,root_results_reused=False),
        'event harness did not preserve one fresh replay and both native admissions')
    return execution,stats


def checked():
    value=n.storage.read(PREFLIGHT);b.check_digest(value);b.check_bindings(value['source_bindings'])
    b.require(value['outcome']=='passed' and value['complete_event_byte_parity']
        and [row['native_roots'] for row in value['measurements']]==[14,12]
        and value['campaign_credit'] is False,'event harness preflight')
    return value


def preflight():
    paths={SELF,n.SELF,n.r.SELF,n.r.INPUTS,n.math_check.SELF}
    paths|={p.relative_to(b.ROOT).as_posix() for p in (b.ROOT/'src/pygrc/models').glob('grc*v4*.py')}
    refs=b.bind(paths);rows=[];expected=None
    for reuse in (False,True):
        roots=[];original=n.r.CandidateCIRoot.__post_init__
        def observed(root):
            result=original(root);roots.append(root.inputs.identity);return result
        started=time.monotonic()
        with n.compute_worker(),patch.object(n.r.CandidateCIRoot,'__post_init__',observed):
            manifest=n.storage.read(n.r.INPUTS);seed=n.r.state(manifest['expected_source']);case=manifest['cases'][0]
            if reuse:execution,stats=event(seed,case)
            else:execution=n.event(seed,case);stats=None
            digest=b.digest(execution)
            if expected is None:expected=digest
            b.require(digest==expected,'event harness changed complete retained bytes')
        rows.append(dict(reuse=reuse,seconds=time.monotonic()-started,native_roots=len(roots),
            execution_digest=digest,observations=stats))
        print(rows[-1],flush=True)
    b.require([row['native_roots'] for row in rows]==[14,12],'unexpected native root chronology')
    b.check_bindings(refs)
    value=b.seal(dict(schema='p9-ccipc-event-harness-preflight-v1',source_bindings=refs,
        outcome='passed',complete_event_byte_parity=True,measurements=rows,
        campaign_credit=False,user_accepted=False))
    n.storage.save(PREFLIGHT,value)


if __name__=='__main__':preflight()

"""Independent actual evolved-target feasibility before the expensive event."""
import time

import p984h_acipc as n

b=n.b
SELF=b.HERE+'p984h_acipc_actual.py'
PATH=b.BASE+'P9-8.4h-ACIPC-ActualPreflight.json.xz'


def check(value=None):
    value=n.storage.read(PATH) if value is None else value
    b.check_digest(value);b.check_bindings(value['source_bindings'])
    seed,prior=n.source_state();case=n.case_for(seed)
    target=n.independent_target(seed,case).inputs
    b.require(value['source_record_digest']==prior['record_digest']
        and value['case_digest']==b.digest(case) and value['target_identity']==target.identity
        and value['ready_for_event'] and value['native_steps']==value['native_events']==0
        and [row['role'] for row in value['cases']]==list(n.ROLES)
        and all(not row['negative_vertices'] and not row['unresolved_vertices'] for row in value['cases']), 'actual target feasibility scope')
    for role in n.ROLES:
        old=sum(map(n.q,getattr(seed.inputs,role).C),n.q(0))
        new=sum(map(n.q,getattr(target,role).C),n.q(0))
        b.require(old==new and value['charge'][role]==str(old),'actual represented charge transfer')
    return value


def run():
    seed,prior=n.source_state();case=n.case_for(seed)
    target=n.independent_target(seed,case).inputs
    charge={}
    for role in n.ROLES:
        old=sum(map(n.q,getattr(seed.inputs,role).C),n.q(0))
        new=sum(map(n.q,getattr(target,role).C),n.q(0))
        b.require(old==new,'actual evolved split does not preserve represented charge')
        charge[role]=str(old)
    paths={SELF,n.SELF,n.g.SELF,n.g.pc.SELF,n.g.ci.SELF,n.g.staged.SELF,n.math_check.SELF,
           n.filename('source'),b.HERE+'p9_acipc_targets.py'}
    refs=b.bind(paths);started=time.monotonic()
    with n.g.ctx.workprec(n.g.BITS):
        rows=[n.g.first_step(n.subject(target),role,n.DT) for role in n.ROLES]
    value=b.seal(dict(schema='p984h-acipc-actual-target-preflight-v1',source_bindings=refs,
        source_record_digest=prior['record_digest'],case_digest=b.digest(case),target_identity=target.identity,
        cases=rows,charge=charge,seconds=time.monotonic()-started,
        ready_for_event=all(not row['negative_vertices'] and not row['unresolved_vertices'] for row in rows),
        native_steps=0,native_events=0,user_accepted=False,aggregate_closed=False))
    check(value);n.storage.save(PATH,value)
    print('actual target: both histories positive, exact represented charge preserved',flush=True)


if __name__=='__main__':
    with n.compute_worker():run()

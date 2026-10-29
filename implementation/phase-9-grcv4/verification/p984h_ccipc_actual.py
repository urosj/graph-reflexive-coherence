"""Independent actual evolved-target feasibility before the expensive event."""
import time

import p984h_ccipc as n
import p9_ccipc_execution_epoch as epoch

b=n.b
SELF=b.HERE+'p984h_ccipc_actual.py'
PATH=b.BASE+'P9-8.4h-CCIPC-ActualPreflight.json.xz'


def check(value=None):
    value=n.storage.read(PATH) if value is None else value
    b.check_digest(value);b.check_bindings(value['source_bindings'])
    seed,prior=n.source_state();case=n.case_for(seed)
    target=n.independent_target(dict(expected_source=seed.to_payload()),case)
    b.require(value['source_record_digest']==prior['record_digest']
        and value['case_digest']==b.digest(case) and value['target_identity']==target.identity
        and value['ready_for_event'] and value['native_steps']==value['native_events']==0
        and [row['role'] for row in value['cases']]==list(n.ROLES)
        and all(row['first_step_nonnegative'] and not row['negative_resources']
                and not row['unresolved_resources'] for row in value['cases']), 'actual target feasibility scope')
    for role in n.ROLES:
        old=sum(map(n.q,getattr(seed.inputs,role).C),n.q(0))
        new=sum(map(n.q,getattr(target,role).C),n.q(0))
        b.require(old==new and value['charge'][role]==str(old),'actual represented charge transfer')
    return value


def run():
    seed,prior=n.source_state();case=n.case_for(seed)
    target=n.independent_target(dict(expected_source=seed.to_payload()),case)
    charge={}
    for role in n.ROLES:
        old=sum(map(n.q,getattr(seed.inputs,role).C),n.q(0))
        new=sum(map(n.q,getattr(target,role).C),n.q(0))
        b.require(old==new,'actual evolved split does not preserve represented charge')
        charge[role]=str(old)
    paths={SELF,n.SELF,n.g.SELF,n.g.pc.SELF,n.g.pc.graph_math.SELF,n.g.iv.SELF,
           n.filename('source'),b.HERE+'p9_ccipc_targets.py',epoch.SELF,epoch.PATH}
    refs=b.bind(paths);started=time.monotonic()
    rows=[n.g.first_step(n.subject(target),role,n.DT) for role in n.ROLES]
    value=b.seal(dict(schema='p984h-ccipc-actual-target-preflight-v1',source_bindings=refs,
        source_record_digest=prior['record_digest'],case_digest=b.digest(case),target_identity=target.identity,
        cases=rows,charge=charge,seconds=time.monotonic()-started,
        ready_for_event=all(row['first_step_nonnegative'] for row in rows),
        native_steps=0,native_events=0,user_accepted=False,aggregate_closed=False))
    check(value);n.storage.save(PATH,value)
    print('actual target: both histories positive, exact represented charge preserved',flush=True)


if __name__=='__main__':
    with epoch.numerical_campaign(),n.compute_worker():run()

"""Propagate certified root-current error to exact-real first-step resources."""
import argparse
import hashlib
import json
import p984g_cci_staged as staged

ROOT,BASE,HERE=staged.ROOT,staged.BASE,staged.HERE
SELF=HERE+'p984g_cci_continuation.py'
TEST=HERE+'test_p984g_cci_continuation.py'
RESULTS=BASE+'P9-8.4g-CCIContinuationBounds.json'
q,require=staged.q,staged.require


def enclose(b,c,current,dt,error):
    """Exact center; |B_i delta J| <= ||B_i||_2 ||delta J||_2."""
    require(q(dt)>=0 and q(error)>=0,'nonnegative timestep/error bound required')
    rows=[]
    for ci,row in zip(c,b,strict=True):
        center=q(ci)-q(dt)*sum((q(int(w))*q(j) for w,j in zip(row,current,strict=True)),q(0))
        rownorm=staged.prior.upper(staged.iv.a(sum(int(w)**2 for w in row)).sqrt())
        radius=q(dt)*rownorm*q(error)
        rows.append((center-radius,center+radius))
    return rows


def calculate():
    summary=staged.check();declaration=staged.read(staged.prior.PREPARED)
    dt=declaration['selected_configuration']['ordinary_dt'];cases=[]
    with staged.ctx.workprec(staged.iv.BITS):
        for case in summary['cases']:
            subject=declaration[case['graph']];role=case['role'];r=staged.read(case['path'])['result']
            b,_=staged.prior.shared.graph_data(subject);c=subject['roles'][role]['C']
            rows=enclose(b,c,r['reference_current'],dt,r['reference_to_root_current_error_upper'])
            bad=[dict(index=i,node=subject['graph']['live_node_ids'][i],lower=str(lo),upper=str(hi),
                      initial_resource=c[i],
                      outward_rate_lower=str((q(c[i])-hi)/q(dt)),
                      excluded_for_every_positive_dt_at_this_state=(c[i]==0))
                 for i,(lo,hi) in enumerate(rows) if hi<0]
            counter=[float(ci)-float(dt)*sum(float(w)*j for w,j in zip(row,r['counterfactual_current'],strict=True))
                     for ci,row in zip(c,b,strict=True)]
            cases.append(dict(graph=case['graph'],role=role,
                exact_root_resource_minimum_lower=str(min(lo for lo,hi in rows)),
                exact_root_resource_minimum_upper=str(min(hi for lo,hi in rows)),
                certified_negative_vertices=bad,certified_positive_vertices=sum(lo>0 for lo,hi in rows),
                unresolved_vertices=sum(lo<=0<=hi for lo,hi in rows),
                reference_staged_minimum=min(r['reference_continuity_proposal']),
                counterfactual_staged_minimum=min(counter),
                exact_root_current_error_upper=r['reference_to_root_current_error_upper'],
                research_case=dict(path=case['path'],sha256=case['sha256'],record_digest=case['record_digest'])))
    paths=[SELF,TEST,staged.SELF,staged.RESULTS,staged.prior.PREPARED]
    return staged.seal(dict(schema='p984g-cci-continuation-bounds-v1',family='C_CI',cases=cases,
        source_bindings={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},
        scope='exact_real_first_step_at_unique_CI_root_not_native_rejection',
        native_steps=0,native_events=0,ready_for_8_4h=False,user_accepted=False,
        altered_timestep=False,clipped_resources=False))


def check(value=None):
    value=staged.read(RESULTS) if value is None else value
    require(value==calculate(),'continuation enclosure drift');return value


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=('run','check'));args=p.parse_args()
    if args.mode=='run':
        require(not (ROOT/RESULTS).exists(),'no overwrite')
        (ROOT/RESULTS).write_text(json.dumps(calculate(),indent=2)+'\n')
    else:check()


if __name__=='__main__':main()

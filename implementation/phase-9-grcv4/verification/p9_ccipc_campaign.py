"""Resume source-bound C_CI+PC numerical segments across the legacy-return fix."""
import argparse
from contextlib import nullcontext
import json
from unittest.mock import patch

import p9_ccipc_execution_epoch as epoch
import p984d_ccipc as deep
import p984h_ccipc as large


def charge_context():
    import p9_ccipc_large_charge as charge
    return charge.context() if (deep.b.ROOT/charge.NATIVE).exists() else nullcontext()


def child_in_epoch(pipe, function, args):
    import p9_ccipc_raw_store as raw_store
    raw_store.checked()
    with epoch.numerical_campaign(),charge_context(),raw_store.private_captures():
        function(pipe, *args)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('campaign',choices=('deep','small_covariance','large','continuation','covariance','lifecycle'))
    p.add_argument('--action',choices=('prepare','run','check'),default='run')
    p.add_argument('--segment',default='source')
    p.add_argument('--role',choices=large.ROLES,default='current')
    p.add_argument('--index',type=int,default=1)
    p.add_argument('--kind')
    p.add_argument('--workers',type=int,default=2)
    args=p.parse_args()
    from scripts.evidence_storage import restore
    restore(deep.b.ROOT,prefix=deep.b.BASE+'P9-8.4d-CCIPC')
    capped=large.process_budget.capped
    def guarded(function, args, seconds):
        return capped(child_in_epoch,(function,args),seconds)
    with epoch.numerical_campaign(),(charge_context() if args.campaign!='deep' else nullcontext()), \
         patch.object(large.process_budget,'capped',guarded),large.compute_worker():
        if args.campaign=='deep':
            m=deep.read(deep.INPUTS)
            result=deep.run(m,args.workers) if args.action=='run' else deep.check(m,deep.read(deep.RESULTS))
            print(json.dumps(result),flush=True)
        elif args.campaign=='small_covariance':
            import p984ef_ccipc as small_covariance
            ip,rp=small_covariance.paths(args.kind)
            if args.action=='prepare':deep.save(ip,small_covariance.make_manifest(args.kind))
            elif args.action=='check':print(json.dumps(small_covariance.check(deep.read(ip),deep.read(rp))[0]),flush=True)
            else:print(json.dumps(small_covariance.run(args.kind,args.workers)),flush=True)
        elif args.campaign=='large':
            if args.segment=='event':
                import p984h_ccipc_actual as actual
                actual.check()
            large.run(args.segment,args.role,args.index)
        elif args.campaign=='continuation':
            manifest=deep.read(large.INPUTS);large.check_manifest(manifest)
            for segment,index in [('step',i) for i in range(args.index,11)]+[('final',1)]:
                path=large.filename(segment,args.role,index)
                if (deep.b.ROOT/path).exists():
                    value=deep.read(path);deep.b.check_digest(value)
                    deep.b.require(value['manifest_digest']==manifest['record_digest']
                        and (value['segment'],value['role'],value['index'])==(segment,args.role,index)
                        and value['outcome']=='completed','continuation resume identity')
                    print('retained completed prefix',path,flush=True)
                else:large.run(segment,args.role,index)
        elif args.campaign=='covariance':
            import p984h_ccipc_covariance as cov
            if args.action=='prepare':deep.save(cov.INPUTS,cov.manifest())
            else:cov.run(args.kind,None if args.segment=='source' else (args.segment,))
        else:
            import p985_ccipc as life
            if args.action=='prepare':deep.save(life.INPUTS,life.manifest())
            else:life.run(args.segment)

"""Resume independent A_CI_PC segments without repeating completed native work."""
import argparse
import p9_acipc_large_charge as charge
from p9_acipc_execution_scope import execution_scope
n=charge.n

def continuation(role):
    for index in range(1,11):
        path=n.filename('step',role,index)
        if (n.b.ROOT/path).exists():
            row=n.read('step',role,index);n.b.check_digest(row);n.check_step(row['execution'])
        else:n.run('step',role,index)
    if not (n.b.ROOT/n.filename('final',role)).exists():n.run('final',role,1)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=('large','continuation','covariance-prepare','covariance','lifecycle-prepare','lifecycle'))
    p.add_argument('--role',choices=n.ROLES,default='current')
    p.add_argument('--kind',choices=('combined','reflect','rotate'))
    p.add_argument('--segment',choices=('small','large','prepared_target','event','step','final'),default='event')
    p.add_argument('--index',type=int,default=1)
    args=p.parse_args()
    with n.compute_worker(),execution_scope():
        if args.action=='large':
            if args.segment=='event':
                import p984h_acipc_actual as actual
                actual.check()
            n.run(args.segment,args.role,args.index)
        elif args.action=='continuation':continuation(args.role)
        elif args.action.startswith('covariance'):
            import p984h_acipc_covariance as c
            if args.action.endswith('prepare'):n.storage.save(c.INPUTS,c.manifest())
            else:c.run(args.kind)
        else:
            import p985_acipc as life
            if args.action.endswith('prepare'):n.storage.save(life.INPUTS,life.manifest())
            else:life.run(args.segment)

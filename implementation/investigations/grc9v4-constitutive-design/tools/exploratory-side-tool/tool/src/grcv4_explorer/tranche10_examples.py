"""Read-only access to the progressive native examples and their run identities."""
from pathlib import Path
import sys


def checker(root):
    root=Path(root).resolve()
    sys.path.insert(0,str(root/'implementation/phase-9-grcv4/verification'))
    import p9104_examples as c
    if root!=c.ROOT:raise ValueError('example repository mismatch')
    return root,c


def tranche10_examples_status(root):
    root,c=checker(root);v=c.check()
    return c.seal(dict(schema='p9104-example-view-v1',status=v['status'],
        families=v['families'],lessons=v['lessons'],family_runs=v['family_runs'],
        user_accepted=False,P9_10_4_closed=False,full_GRC9V4_conformance=False,G4_accepted=False,
        completed_spark=False,hierarchy_tracking=False,general_ATC=False,
        publication=c.reference(c.PATH),guide=c.reference(c.GUIDE),
        examples=[r for r in v['sources'] if r['path'].endswith('.py')],
        outputs=v['outputs'],next_work=v['next_work']))


def tranche10_examples_source(root,name):
    root,c=checker(root);v=c.check()
    refs={r['path']:r for r in [*v['sources'],*v['outputs'],c.reference(c.PATH)]}
    if name not in refs or Path(name).is_absolute() or '..' in Path(name).parts:
        raise KeyError('source is not part of the published examples')
    raw=(root/name).read_bytes()
    if c.sha(raw)!=refs[name]['sha256']:raise ValueError('example source drift')
    return raw,refs[name]

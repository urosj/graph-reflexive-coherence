"""A_RG2b completion research, visibly separate from native acceptance."""
import hashlib
import importlib.util
from pathlib import Path
import sys


def arg2b_status(repo_root):
    root=Path(repo_root).resolve()
    # Reconstitute original transport bytes for the frozen numerical readers.
    # The shared store is authenticated even when local XZ caches already exist.
    spec=importlib.util.spec_from_file_location('arg2b_evidence_storage',root/'scripts/evidence_storage.py')
    storage=importlib.util.module_from_spec(spec);spec.loader.exec_module(storage)
    storage.restore(root,prefix='implementation/phase-9-grcv4/tranche-8/arg2b-native/',expanded=False)
    directory=root/'implementation/phase-9-grcv4/verification'
    if str(directory) not in sys.path:sys.path.insert(0,str(directory))
    from p9_arg2b_review import checked
    import p9_arg2b_acceptance as acceptance
    value=checked(root)
    accepted=acceptance.decision(root)
    if accepted is not None:
        value.update(user_accepted=True,bounded_scope_closed=True,stage='bounded_accepted',
            acceptance=dict(path=acceptance.PATH,record_digest=accepted['record_digest']),
            next_work='Bounded A_RG2b Tranches 8–9 accepted. All forty source compatibility cells are accepted; aggregate conformance and Tranche 10 remain separate.')
        matrix=value['native_execution']['9.3']
        matrix['execution_counts']=matrix['counts']
        matrix['counts']=accepted['compatibility_counts']
        value['source_refs'].extend(dict(path=p,sha256=hashlib.sha256((root/p).read_bytes()).hexdigest())
            for p in (acceptance.PATH,acceptance.SELF))
    return value


def arg2b_source(repo_root,name):
    root=Path(repo_root).resolve()
    refs={r['path']:r for r in arg2b_status(root)['source_refs']}
    if name not in refs:raise KeyError('source outside A_RG2b research index')
    path=(root/name).resolve()
    if not path.is_relative_to(root):raise KeyError('source escapes repository')
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=refs[name]['sha256']:raise ValueError('research source changed during read')
    return raw,refs[name]

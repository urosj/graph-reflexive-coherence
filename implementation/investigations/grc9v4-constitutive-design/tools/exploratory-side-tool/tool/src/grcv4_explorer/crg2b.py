"""C_RG2b completion research, visibly separate from native acceptance."""
import hashlib
import importlib.util
from pathlib import Path
import sys


def crg2b_status(repo_root):
    root=Path(repo_root).resolve()
    # Reconstitute original transport bytes for the frozen numerical readers.
    # The shared store is authenticated even when local XZ caches already exist.
    spec=importlib.util.spec_from_file_location('crg2b_evidence_storage',root/'scripts/evidence_storage.py')
    storage=importlib.util.module_from_spec(spec);spec.loader.exec_module(storage)
    storage.restore(root,prefix='implementation/phase-9-grcv4/tranche-8/crg2b-native/',expanded=False)
    directory=root/'implementation/phase-9-grcv4/verification'
    if str(directory) not in sys.path:sys.path.insert(0,str(directory))
    from p9_crg2b_review import checked
    import p9_crg2b_acceptance as acceptance
    value=checked(root)
    decision=acceptance.decision(root)
    value.update(acceptance=None,bounded_scope_closed=False)
    if decision:
        value.update(user_accepted=True,bounded_scope_closed=True,stage='bounded_accepted',
                     acceptance=dict(path=acceptance.PATH,record_digest=decision['record_digest']),
                     next_work='C_RG2b bounded Tranches 8–9 accepted. A_RG2b is the remaining family; Tranche 10 remains deferred.')
        matrix=value['native_execution']['9.3']
        matrix['execution_counts']=matrix['counts']
        matrix['counts']=decision['compatibility_counts']
        for name in (acceptance.PATH,acceptance.SELF):
            value['source_refs'].append(dict(path=name,sha256=hashlib.sha256((root/name).read_bytes()).hexdigest()))
    return value


def crg2b_source(repo_root,name):
    root=Path(repo_root).resolve()
    refs={r['path']:r for r in crg2b_status(root)['source_refs']}
    if name not in refs:raise KeyError('source outside C_RG2b research index')
    path=(root/name).resolve()
    if not path.is_relative_to(root):raise KeyError('source escapes repository')
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=refs[name]['sha256']:raise ValueError('research source changed during read')
    return raw,refs[name]

"""Finite C_CI_PC research metadata successor to the accepted C_PC checkpoint.

Only enumerated presentation/planning/adapter files may differ. Every old
byte string comes from an exact Git commit; current bytes have pinned hashes.
Scientific authority, execution and original validation records are untouched.
"""
from pathlib import Path
import hashlib
import subprocess
from .basin import _bound_file
from .canonical import load_json_object, record_digest, file_sha256
from .errors import SourceAdmissionError

INV='implementation/investigations/grc9v4-constitutive-design/'
SOURCE=INV+'evidence/spark-completion/applicability/CCIPCMetadataSources.json'
DIGEST='c040b23fe813f6d719994a61065c1ea78302e20227aecfb2c3bcdc30e7837c2a'
PREDECESSOR='87d2f474b6cb4b9fe38ab516b5e0d391e59b3d44'
PATHS=frozenset({
    'implementation/Phase-9-GRCV4-Handoff.md',
    'implementation/Phase-9-GRCV4-ImplementationChecklist.md',
    INV+'GRC9V4ConstitutiveDesignChecklist.md',
    INV+'tools/exploratory-side-tool/tool/phase9-web/index.html',
    INV+'tools/exploratory-side-tool/tool/scripts/serve_phase9.py',
    INV+'tools/exploratory-side-tool/tool/notebooks/phase9_verification.ipynb',
    INV+'tools/exploratory-side-tool/tool/src/grcv4_explorer/spark_pc.py',
    'implementation/phase-9-grcv4/verification/phase9_implementation_policy.py',
})


def need(condition,message):
    if not condition: raise SourceAdmissionError(message)


def checked_successor(root):
    root=Path(root);value=load_json_object(root/SOURCE)
    need(value.get('record_digest')==record_digest(value,'record_digest')==DIGEST,
         'unbound C_CI_PC metadata successor')
    need(value['schema']=='spark-completion-ccipc-metadata-successor-v1' and
         value['predecessor_commit']==PREDECESSOR and value['native_runtime_changed'] is False and
         value['accepted_authority_changed'] is False and value['execution_relabelled'] is False,
         'metadata successor widened scientific scope')
    rows={r['path']:r for r in value['sources']}
    need(len(rows)==len(value['sources']) and set(rows)==PATHS,'metadata successor path scope')
    from .spark_cipc_sc3_metadata import bound_metadata_files as bound_acceptance_files
    bound_acceptance_files(root,{p:r['after_sha256'] for p,r in rows.items()})
    for path,row in rows.items():
        before=subprocess.check_output(['git','show',PREDECESSOR+':'+path],cwd=root)
        need(hashlib.sha256(before).hexdigest()==row['before_sha256'],'metadata predecessor bytes changed')
    return value


def bound_metadata_files(root,expected):
    root=Path(root)
    changed={path:sha for path,sha in expected.items() if file_sha256(root/path)!=sha}
    rows={r['path']:r for r in checked_successor(root)['sources']} if changed else {}
    current_epoch={}
    for path,sha in expected.items():
        if path not in changed: current_epoch[path]=sha
        else:
            row=rows.get(path)
            if row is not None:
                need(row['before_sha256']==sha,'unbound historical metadata successor')
                current_epoch[path]=row['after_sha256']
            else: current_epoch[path]=sha
    from .spark_cipc_sc3_metadata import bound_metadata_files as bound_acceptance_files
    bound_acceptance_files(root,current_epoch)

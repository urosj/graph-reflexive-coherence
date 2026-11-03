"""Exact C_CI_PC acceptance metadata transition and historical research sources."""
from pathlib import Path
import hashlib
import subprocess
from .basin import _bound_file, native_predecessor
from .canonical import load_json_object, record_digest, file_sha256
from .errors import SourceAdmissionError

INV='implementation/investigations/grc9v4-constitutive-design/'
SOURCE=INV+'evidence/spark-completion/applicability/CCIPCSC3Sources.json'
DIGEST='939a00ea304104873fd8a55a9f78b96484918841444b53df62ef61fd7122cb2e'
REVIEWED_COMMIT='d3c71d6475535e57be019eb8c0212deaa92515aa'
HISTORICAL_HELPER=INV+'tools/exploratory-side-tool/tool/src/grcv4_explorer/spark_cipc_metadata.py'
PATHS=frozenset({
    'implementation/Phase-9-GRCV4-Handoff.md',
    'implementation/Phase-9-GRCV4-ImplementationChecklist.md',
    INV+'GRC9V4ConstitutiveDesignChecklist.md',
    INV+'decisions/SparkCompletionAllTenApplicability.md',
    INV+'tools/exploratory-side-tool/tool/phase9-web/index.html',
    INV+'tools/exploratory-side-tool/tool/scripts/serve_phase9.py',
    INV+'tools/exploratory-side-tool/tool/notebooks/phase9_verification.ipynb',
    INV+'tools/exploratory-side-tool/tool/src/grcv4_explorer/spark_cipc_metadata.py',
    INV+'tools/exploratory-side-tool/tool/src/grcv4_explorer/spark_cipc_research.py',
    'implementation/phase-9-grcv4/verification/phase9_implementation_policy.py',
})


def need(ok,message):
    if not ok: raise SourceAdmissionError(message)


def checked_acceptance_epoch(root):
    root=Path(root);value=load_json_object(root/SOURCE)
    need(value.get('record_digest')==record_digest(value,'record_digest')==DIGEST,
         'unbound C_CI_PC acceptance metadata')
    need(value['schema']=='spark-completion-ccipc-acceptance-metadata-v1' and
         value['reviewed_commit']==REVIEWED_COMMIT and not value['native_runtime_changed'] and
         not value['execution_relabelled'],'acceptance metadata widened execution scope')
    rows={r['path']:r for r in value['sources']}
    need(len(rows)==len(value['sources']) and set(rows)==PATHS,'acceptance metadata paths')
    for path,row in rows.items():
        before=subprocess.check_output(['git','show',REVIEWED_COMMIT+':'+path],cwd=root)
        need(hashlib.sha256(before).hexdigest()==row['before_sha256'],'reviewed metadata preimage differs')
    from .spark_aos_metadata import bound_metadata_files as bind_next
    bind_next(root,{path:row['after_sha256'] for path,row in rows.items()})
    validation=load_json_object(root/(INV+'evidence/spark-completion/applicability/CCIPCValidation.json'))
    need(validation['record_digest']==record_digest(validation,'record_digest'),'original research validation digest')
    for ref in validation['sources']:
        current=file_sha256(root/ref['path'])
        if current!=ref['sha256'] and native_predecessor(root, ref['path'], ref['sha256']) is None:
            row=rows.get(ref['path'])
            need(row is not None and row['before_sha256']==ref['sha256'],
                 'unbound original validation successor')
    return value


def bound_metadata_files(root,expected):
    expected = {p: h for p, h in expected.items()
                if native_predecessor(root, p, h) is None}
    root=Path(root)
    changed={p:sha for p,sha in expected.items() if file_sha256(root/p)!=sha}
    rows={r['path']:r for r in checked_acceptance_epoch(root)['sources']} if changed else {}
    for path,sha in expected.items():
        if path not in changed: _bound_file(root,path,sha)
        else:
            row=rows.get(path)
            need(row is not None and row['before_sha256']==sha,'unbound acceptance metadata succession')
            from .spark_aos_metadata import bound_metadata_files as bind_next
            bind_next(root,{path:row['after_sha256']})


def reviewed_source_bytes(root,path,expected):
    from .basin import native_predecessor
    original = native_predecessor(root, path, expected)
    if original is not None:
        return original
    root=Path(root)
    if file_sha256(root/path)==expected:return _bound_file(root,path,expected).read_bytes()
    need(path==HISTORICAL_HELPER,'scientific source changed outside the finite helper successor')
    rows={r['path']:r for r in checked_acceptance_epoch(root)['sources']}
    need(rows[path]['before_sha256']==expected,'wrong reviewed helper source')
    data=subprocess.check_output(['git','show',REVIEWED_COMMIT+':'+path],cwd=root)
    need(hashlib.sha256(data).hexdigest()==expected,'historical helper bytes differ')
    return data

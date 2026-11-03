"""Exact C_RG2b acceptance metadata transition and historical research sources."""
from pathlib import Path
import hashlib
import subprocess
from .basin import _bound_file, native_predecessor
from .canonical import load_json_object, record_digest, file_sha256
from .errors import SourceAdmissionError

INV='implementation/investigations/grc9v4-constitutive-design/'
SOURCE=INV+'evidence/spark-completion/applicability/CRG2bSC3Sources.json'
DIGEST='50837ded6f678ec505d618b2506399662e74f97bf7e549d8e738fe341b95910d'
REVIEWED_COMMIT='54a8cdb3b9683fb5c9d8beddb99321ea0df6b1e4'
HISTORICAL_HELPER=INV+'tools/exploratory-side-tool/tool/src/grcv4_explorer/spark_crg2b_metadata.py'
PATHS=frozenset({
    'implementation/Phase-9-GRCV4-Handoff.md',
    'implementation/Phase-9-GRCV4-ImplementationChecklist.md',
    INV+'GRC9V4ConstitutiveDesignChecklist.md',
    INV+'decisions/SparkCompletionAllTenApplicability.md',
    INV+'tools/exploratory-side-tool/tool/phase9-web/index.html',
    INV+'tools/exploratory-side-tool/tool/scripts/serve_phase9.py',
    INV+'tools/exploratory-side-tool/tool/notebooks/phase9_verification.ipynb',
    INV+'tools/exploratory-side-tool/tool/src/grcv4_explorer/spark_crg2b_metadata.py',
    INV+'tools/exploratory-side-tool/tool/src/grcv4_explorer/spark_crg2b_research.py',
    'implementation/phase-9-grcv4/verification/phase9_implementation_policy.py',
})


def need(ok,message):
    if not ok: raise SourceAdmissionError(message)


def checked_preimages(root,rows):
    """One Git process for the finite preimage batch; current files stay fresh."""
    requests=''.join(REVIEWED_COMMIT+':'+path+'\n' for path in rows).encode()
    data=subprocess.check_output(['git','cat-file','--batch'],input=requests,cwd=root)
    offset=0
    for path,row in rows.items():
        end=data.find(b'\n',offset);need(end>=offset,'invalid metadata preimage response')
        header=data[offset:end].split()
        need(len(header)==3 and header[1]==b'blob' and header[2].isdigit(),'missing metadata preimage blob')
        size=int(header[2]);offset=end+1;before=data[offset:offset+size];offset+=size
        need(len(before)==size and data[offset:offset+1]==b'\n','truncated metadata preimage')
        offset+=1
        need(hashlib.sha256(before).hexdigest()==row['before_sha256'],'C_RG2b metadata preimage differs')
    need(offset==len(data),'extra metadata preimage response')


def checked_acceptance_epoch(root):
    root=Path(root);value=load_json_object(root/SOURCE)
    need(value.get('record_digest')==record_digest(value,'record_digest')==DIGEST,
         'unbound C_RG2b acceptance metadata')
    need(value['schema']=='spark-completion-crg2b-acceptance-metadata-v1' and
         value['reviewed_commit']==REVIEWED_COMMIT and not value['native_runtime_changed'] and
         not value['execution_relabelled'],'acceptance metadata widened execution scope')
    rows={r['path']:r for r in value['sources']}
    need(len(rows)==len(value['sources']) and set(rows)==PATHS,'acceptance metadata paths')
    checked_preimages(root,rows)
    from .spark_arg2b_metadata import bound_metadata_files as successor_files
    successor_files(root,{p:r['after_sha256'] for p,r in rows.items()})
    validation=load_json_object(root/(INV+'evidence/spark-completion/applicability/CRG2bValidation.json'))
    need(validation['record_digest']==record_digest(validation,'record_digest'),'original research validation digest')
    for ref in validation['sources']:
        current=file_sha256(root/ref['path'])
        if current!=ref['sha256'] and native_predecessor(root, ref['path'], ref['sha256']) is None:
            row=rows.get(ref['path'])
            need(row is not None and row['before_sha256']==ref['sha256'],
                 'unbound original validation successor')
            # Every acceptance postimage or its finite A_RG2b research successor was authenticated above.
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
            # checked_acceptance_epoch already verified this exact postimage
            # for the whole batch.


def reviewed_source_bytes(root,path,expected):
    from .basin import native_predecessor
    original = native_predecessor(root, path, expected)
    if original is not None:
        return original
    root=Path(root)
    if file_sha256(root/path)==expected:return _bound_file(root,path,expected).read_bytes()
    if path!=HISTORICAL_HELPER:
        from .spark_crg2b_metadata import HISTORICAL_HELPER as earlier_helper, reviewed_source_bytes as earlier_bytes
        if path==earlier_helper:return earlier_bytes(root,path,expected)
        from .spark_acipc_sc3_metadata import reviewed_source_bytes as previous_bytes
        return previous_bytes(root,path,expected)
    need(path==HISTORICAL_HELPER,'scientific source changed outside the finite helper successor')
    rows={r['path']:r for r in checked_acceptance_epoch(root)['sources']}
    need(rows[path]['before_sha256']==expected,'wrong reviewed helper source')
    data=subprocess.check_output(['git','show',REVIEWED_COMMIT+':'+path],cwd=root)
    need(hashlib.sha256(data).hexdigest()==expected,'historical helper bytes differ')
    return data

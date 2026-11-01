"""Finite C_RG2b research successor; older scientific evidence stays immutable."""
from pathlib import Path
import hashlib,subprocess
from .basin import _bound_file, native_predecessor
from .canonical import load_json_object,record_digest,file_sha256
from .errors import SourceAdmissionError
INV='implementation/investigations/grc9v4-constitutive-design/'
SOURCE=INV+'evidence/spark-completion/applicability/CRG2bMetadataSources.json'
DIGEST='d2ea1b92aaf6ced9ff8c86b53e98588c8dad38863a99aed99abf947f18c89049'
BASELINE='abb9e1ce975124a98377c3f803805b4453a4aa60'
HISTORICAL_HELPER=INV+'tools/exploratory-side-tool/tool/src/grcv4_explorer/spark_acipc_sc3_metadata.py'
PATHS=frozenset({
    'implementation/Phase-9-GRCV4-Handoff.md',
    'implementation/Phase-9-GRCV4-ImplementationChecklist.md',
    INV+'GRC9V4ConstitutiveDesignChecklist.md',
    INV+'decisions/SparkCompletionAllTenApplicability.md',
    INV+'tools/exploratory-side-tool/tool/phase9-web/index.html',
    INV+'tools/exploratory-side-tool/tool/scripts/serve_phase9.py',
    INV+'tools/exploratory-side-tool/tool/notebooks/phase9_verification.ipynb',
    HISTORICAL_HELPER,
    'implementation/phase-9-grcv4/verification/phase9_implementation_policy.py',
})


def need(ok,message):
    if not ok:raise SourceAdmissionError(message)


def checked_preimages(root,rows):
    """One Git process for the finite preimage batch; current files stay fresh."""
    requests=''.join(BASELINE+':'+path+'\n' for path in rows).encode()
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


def checked_epoch(root):
    root=Path(root);v=load_json_object(root/SOURCE)
    need(v.get('record_digest')==record_digest(v,'record_digest')==DIGEST,'unbound C_RG2b metadata')
    need(v['schema']=='spark-completion-crg2b-metadata-v1' and v['baseline_commit']==BASELINE and
         not v['accepted_authority'] and not v['execution_relabelled'] and not v['native_runtime_changed'],'C_RG2b metadata scope')
    rows={r['path']:r for r in v['sources']}
    need(len(rows)==len(v['sources']) and set(rows)==PATHS,'C_RG2b metadata paths')
    checked_preimages(root,rows)
    from .spark_crg2b_sc3_metadata import bound_metadata_files as acceptance_files
    acceptance_files(root,{p:r['after_sha256'] for p,r in rows.items()})
    validation=load_json_object(root/(INV+'evidence/spark-completion/applicability/ACIPCSC3Validation.json'))
    need(validation['record_digest']==record_digest(validation,'record_digest')=='7ddcddb0149697fc547bbfd49e90d9c03a602c022b570f2c79ed749e6e573478','accepted A_CI_PC validation digest')
    for ref in validation['sources']:
        current=file_sha256(root/ref['path'])
        if current!=ref['sha256'] and native_predecessor(root, ref['path'], ref['sha256']) is None:
            row=rows.get(ref['path'])
            need(row is not None and row['before_sha256']==ref['sha256'],'unbound acceptance validation successor')
    return v


def bound_metadata_files(root,expected):
    expected = {p: h for p, h in expected.items()
                if native_predecessor(root, p, h) is None}
    root=Path(root);changed={p:h for p,h in expected.items() if file_sha256(root/p)!=h}
    rows={r['path']:r for r in checked_epoch(root)['sources']} if changed else {}
    for path,sha in expected.items():
        if path not in changed:_bound_file(root,path,sha)
        else:
            row=rows.get(path)
            need(row is not None and row['before_sha256']==sha,'unbound C_RG2b metadata succession')
            # checked_epoch verifies the finite postimages through acceptance.


def reviewed_source_bytes(root,path,expected):
    from .basin import native_predecessor
    original = native_predecessor(root, path, expected)
    if original is not None:
        return original
    root=Path(root)
    if file_sha256(root/path)==expected:return _bound_file(root,path,expected).read_bytes()
    need(path==HISTORICAL_HELPER,'source changed outside the finite C_RG2b helper successor')
    rows={r['path']:r for r in checked_epoch(root)['sources']}
    need(rows[path]['before_sha256']==expected,'wrong historical helper subject')
    data=subprocess.check_output(['git','show',BASELINE+':'+path],cwd=root)
    need(hashlib.sha256(data).hexdigest()==expected,'historical A_CI_PC helper bytes differ')
    return data
